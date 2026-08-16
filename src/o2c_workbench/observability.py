from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from statistics import mean
from typing import Any, Iterator, Sequence

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult, SpanExporter


class JsonlSpanExporter(SpanExporter):
    """Small local exporter that keeps the demo vendor-neutral and inspectable."""

    def __init__(self, destination: Path):
        self.destination = destination
        self.destination.parent.mkdir(parents=True, exist_ok=True)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        with self.destination.open("a", encoding="utf-8") as handle:
            for span in spans:
                context = span.get_span_context()
                parent_id = f"{span.parent.span_id:016x}" if span.parent else None
                payload = {
                    "trace_id": f"{context.trace_id:032x}",
                    "span_id": f"{context.span_id:016x}",
                    "parent_span_id": parent_id,
                    "name": span.name,
                    "kind": span.kind.name,
                    "start_time_unix_nano": span.start_time,
                    "end_time_unix_nano": span.end_time,
                    "duration_ms": round(((span.end_time or 0) - (span.start_time or 0)) / 1_000_000, 3),
                    "status": span.status.status_code.name,
                    "attributes": dict(span.attributes or {}),
                    "resource": dict(span.resource.attributes),
                }
                handle.write(json.dumps(payload, default=str) + "\n")
        return SpanExportResult.SUCCESS


class Telemetry:
    def __init__(self, trace_path: str | Path, service_name: str, reset: bool = True):
        self.trace_path = Path(trace_path)
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        if reset:
            self.trace_path.unlink(missing_ok=True)
        provider = TracerProvider(resource=Resource.create({"service.name": service_name, "deployment.environment.name": "synthetic-demo"}))
        provider.add_span_processor(SimpleSpanProcessor(JsonlSpanExporter(self.trace_path)))
        self.provider = provider
        self.tracer = provider.get_tracer("o2c_workbench", "1.0.0")

    @contextmanager
    def span(self, name: str, attributes: dict[str, Any] | None = None) -> Iterator[trace.Span]:
        clean = {key: value for key, value in (attributes or {}).items() if value is not None}
        with self.tracer.start_as_current_span(name, attributes=clean) as span:
            try:
                yield span
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
                raise

    def summarize(self) -> dict[str, Any]:
        if not self.trace_path.exists():
            return {"span_count": 0, "error_span_count": 0, "agent_span_count": 0, "p95_duration_ms": 0.0}
        spans = [json.loads(line) for line in self.trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        durations = sorted(float(row["duration_ms"]) for row in spans)
        p95_index = max(0, min(len(durations) - 1, int(len(durations) * 0.95) - 1)) if durations else 0
        agent_spans = [row for row in spans if row["attributes"].get("gen_ai.operation.name") == "invoke_agent"]
        return {
            "span_count": len(spans),
            "error_span_count": sum(row["status"] == "ERROR" for row in spans),
            "agent_span_count": len(agent_spans),
            "mean_duration_ms": round(mean(durations), 3) if durations else 0.0,
            "p95_duration_ms": durations[p95_index] if durations else 0.0,
            "trace_file": str(self.trace_path),
            "content_capture_enabled": False,
        }

