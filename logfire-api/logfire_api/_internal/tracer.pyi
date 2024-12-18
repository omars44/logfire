import opentelemetry.trace as trace_api
from .config import LogfireConfig as LogfireConfig
from .constants import ATTRIBUTES_MESSAGE_KEY as ATTRIBUTES_MESSAGE_KEY, ATTRIBUTES_PENDING_SPAN_REAL_PARENT_KEY as ATTRIBUTES_PENDING_SPAN_REAL_PARENT_KEY, ATTRIBUTES_SAMPLE_RATE_KEY as ATTRIBUTES_SAMPLE_RATE_KEY, ATTRIBUTES_SPAN_TYPE_KEY as ATTRIBUTES_SPAN_TYPE_KEY, PENDING_SPAN_NAME_SUFFIX as PENDING_SPAN_NAME_SUFFIX
from _typeshed import Incomplete
from dataclasses import dataclass
from opentelemetry import context as context_api
from opentelemetry.context import Context
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor, TracerProvider as SDKTracerProvider
from opentelemetry.sdk.trace.id_generator import IdGenerator
from opentelemetry.trace import Link as Link, Span, SpanContext, SpanKind, Tracer, TracerProvider
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.util import types as otel_types
from threading import Lock
from typing import Any, Callable, Mapping, Sequence
from weakref import WeakKeyDictionary

@dataclass
class ProxyTracerProvider(TracerProvider):
    """A tracer provider that wraps another internal tracer provider allowing it to be re-assigned."""
    provider: TracerProvider
    config: LogfireConfig
    tracers: WeakKeyDictionary[_ProxyTracer, Callable[[], Tracer]] = ...
    lock: Lock = ...
    suppressed_scopes: set[str] = ...
    def set_provider(self, provider: SDKTracerProvider) -> None: ...
    def suppress_scopes(self, *scopes: str) -> None: ...
    def get_tracer(self, instrumenting_module_name: str, *args: Any, is_span_tracer: bool = True, **kwargs: Any) -> _ProxyTracer: ...
    def add_span_processor(self, span_processor: Any) -> None: ...
    def shutdown(self) -> None: ...
    @property
    def resource(self) -> Resource: ...
    def force_flush(self, timeout_millis: int = 30000) -> bool: ...

@dataclass
class _MaybeDeterministicTimestampSpan(trace_api.Span, ReadableSpan):
    """Span that overrides end() to use a timestamp generator if one was provided."""
    span: Span
    ns_timestamp_generator: Callable[[], int]
    def end(self, end_time: int | None = None) -> None: ...
    def get_span_context(self) -> SpanContext: ...
    def set_attributes(self, attributes: dict[str, otel_types.AttributeValue]) -> None: ...
    def set_attribute(self, key: str, value: otel_types.AttributeValue) -> None: ...
    def add_link(self, context: SpanContext, attributes: otel_types.Attributes = None) -> None: ...
    def add_event(self, name: str, attributes: otel_types.Attributes = None, timestamp: int | None = None) -> None: ...
    def update_name(self, name: str) -> None: ...
    def is_recording(self) -> bool: ...
    def set_status(self, status: Status | StatusCode, description: str | None = None) -> None: ...
    def record_exception(self, exception: BaseException, attributes: otel_types.Attributes = None, timestamp: int | None = None, escaped: bool = False) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

@dataclass
class _ProxyTracer(Tracer):
    """A tracer that wraps another internal tracer allowing it to be re-assigned."""
    instrumenting_module_name: str
    tracer: Tracer
    provider: ProxyTracerProvider
    is_span_tracer: bool
    def __hash__(self) -> int: ...
    def __eq__(self, other: object) -> bool: ...
    def set_tracer(self, tracer: Tracer) -> None: ...
    def start_span(self, name: str, context: Context | None = None, kind: SpanKind = ..., attributes: otel_types.Attributes = None, links: Sequence[Link] | None = None, start_time: int | None = None, record_exception: bool = True, set_status_on_exception: bool = True) -> Span: ...
    start_as_current_span = ...

class SuppressedTracer(Tracer):
    def start_span(self, name: str, context: Context | None = None, *args: Any, **kwargs: Any) -> Span: ...
    start_as_current_span: Incomplete

@dataclass
class PendingSpanProcessor(SpanProcessor):
    """Span processor that emits an extra pending span for each span as it starts.

    The pending span is emitted by calling `on_end` on the inner `processor`.
    This is intentionally not a `WrapperSpanProcessor` to avoid the default implementations of `on_end`
    and `shutdown`. This processor is expected to contain processors which are already included
    elsewhere in the pipeline where `on_end` and `shutdown` are called normally.
    """
    id_generator: IdGenerator
    processor: SpanProcessor
    def on_start(self, span: Span, parent_context: context_api.Context | None = None) -> None: ...

def should_sample(span_context: SpanContext, attributes: Mapping[str, otel_types.AttributeValue]) -> bool:
    """Determine if a span should be sampled.

    This is used to sample spans that are not sampled by the OTEL sampler.
    """
def get_sample_rate_from_attributes(attributes: otel_types.Attributes) -> float | None: ...
