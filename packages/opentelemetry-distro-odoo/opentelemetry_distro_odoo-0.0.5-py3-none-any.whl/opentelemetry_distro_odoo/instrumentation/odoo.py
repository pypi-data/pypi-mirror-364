import contextlib
import threading
import timeit
from typing import Any, Callable

import psycopg2
import requests
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.metrics import (
    CallbackOptions,
    Counter,
    Histogram,
    ObservableGauge,
    Observation,
    UpDownCounter,
    get_meter,
)
from opentelemetry.semconv.attributes.error_attributes import ERROR_TYPE
from opentelemetry.trace import Span, Status, StatusCode, get_tracer
from opentelemetry.util import types

import odoo.sql_db
import odoo.tools

from opentelemetry_distro_odoo.semconv.attributes import odoo as odoo_attributes
from opentelemetry_distro_odoo.semconv.metrics import odoo as odoo_metrics
from opentelemetry_distro_odoo.version import __version__


class OdooInstrumentor(BaseInstrumentor):
    odoo_call_sql_queries_count: Counter
    odoo_call_sql_queries_duration: Histogram
    odoo_call_error: Counter
    odoo_call_duration: Histogram
    odoo_report_duration: Histogram
    odoo_send_mail: Counter
    odoo_run_cron: Counter
    worker_count: UpDownCounter
    worker_max: ObservableGauge

    def _callback_up(self, opt: CallbackOptions) -> list[Observation]:
        port = odoo.tools.config["http_port"] or "8069"
        ok = 0
        try:
            requests.post(
                f"http://localhost:{port}/web/webclient/version_info", json={}, timeout=opt.timeout_millis / 1000
            )
            ok = 1
        except requests.exceptions.RequestException:
            pass

        return [Observation(ok, {"odoo.up.type": "web"})]

    def _callback_up_wkhtml(self, opt: CallbackOptions) -> list[Observation]:
        from odoo.addons.base.models.ir_actions_report import wkhtmltopdf_state

        return [Observation(int(wkhtmltopdf_state == "ok"), {"odoo.up.type": "wkhtmltopdf"})]

    def _callback_up_pg(self, opt: CallbackOptions) -> list[Observation]:
        ok = 0
        try:
            if odoo.release.major_version >= "16.0":
                odoo.sql_db.db_connect("postgres").cursor().close()
            else:
                odoo.sql_db.db_connect("postgres").cursor(serialized=False).close()

            ok = 1
        except psycopg2.Error:
            pass
        return [Observation(ok, {"odoo.up.type": "database"})]

    def _callback_max_worker(self, opt: CallbackOptions) -> list[Observation]:
        workers = odoo.tools.config["workers"]
        if not workers:
            return [
                Observation(
                    workers,
                )
            ]

    def _instrument(self, **kwargs: Any):
        super()._instrument(**kwargs)
        self._meter = get_meter(__name__, __version__)
        self.odoo_call_error = odoo_metrics.create_odoo_call_error(self._meter)
        self.odoo_call_duration = odoo_metrics.create_odoo_call_duration(self._meter)
        self.odoo_call_sql_queries_count = odoo_metrics.create_odoo_call_sql_queries_count(self._meter)
        self.odoo_call_sql_queries_duration = odoo_metrics.create_call_sql_queries_duration(self._meter)
        self.odoo_send_mail = odoo_metrics.create_odoo_send_mail(self._meter)
        self.odoo_run_cron = odoo_metrics.create_odoo_run_cron(self._meter)
        self.worker_count = odoo_metrics.create_worker_count(self._meter)
        self.worker_max = self._meter.create_observable_gauge(
            odoo_metrics.ODOO_WORKER_MAX, callbacks=[self._callback_max_worker]
        )
        self.odoo_up = self._meter.create_observable_gauge(
            "odoo.up", callbacks=[self._callback_up, self._callback_up_wkhtml, self._callback_up_pg], unit="1"
        )

    def instrumentation_dependencies(self):
        return []

    def _uninstrument(self, **kwargs: Any):
        pass

    @property
    def meter(self):
        return get_meter(__name__, __version__)

    @property
    def tracer(self):
        return get_tracer(__name__, __version__)

    def get_attributes_metrics(self, odoo_record_name, method_name):
        current_thread = threading.current_thread()
        return {
            odoo_attributes.ODOO_MODEL_NAME: odoo_record_name,
            odoo_attributes.ODOO_MODEL_FUNCTION_NAME: method_name,
            odoo_attributes.ODOO_CURSOR_MODE: getattr(current_thread, "cursor_mode", "rw"),
        }

    @contextlib.contextmanager
    def odoo_call_wrapper(
        self,
        odoo_record_name: str,
        method_name: str,
        *,
        attrs: types.Attributes = None,
        metrics_attrs: types.Attributes = None,
        span_attrs: types.Attributes = None,
        post_span_callback: Callable[[Span], None] = None,
    ):
        if not self.is_instrumented_by_opentelemetry:
            yield

        odoo_attr = self.get_attributes_metrics(odoo_record_name, method_name)

        metrics_attr = dict(odoo_attr)
        metrics_attr.update(attrs or {})
        metrics_attr.update(metrics_attrs or {})

        span_attr = dict(odoo_attr)
        span_attr.update(attrs or {})
        span_attr.update(span_attrs or {})

        start = timeit.default_timer()
        with self.tracer.start_as_current_span(f"{odoo_record_name}#{method_name}", attributes=span_attr) as span:
            try:
                yield
            except Exception as ex:
                metrics_attr[ERROR_TYPE] = type(ex).__qualname__
                self.odoo_call_error.add(1, metrics_attr)
                span.record_exception(ex)
                span.set_attribute(ERROR_TYPE, type(ex).__qualname__)
                span.set_status(Status(StatusCode.ERROR, str(ex)))
                raise ex
            finally:
                if post_span_callback:
                    post_span_callback(span)
                duration_s = timeit.default_timer() - start
                metrics = self.odoo_call_duration
                metrics.record(duration_s, metrics_attr)
                current_thread = threading.current_thread()
                if hasattr(current_thread, "query_count"):
                    self.odoo_call_sql_queries_count.add(
                        current_thread.query_count,
                        metrics_attr,
                    )
                if hasattr(current_thread, "query_time"):
                    self.odoo_call_sql_queries_duration.record(current_thread.query_time, metrics_attr)
