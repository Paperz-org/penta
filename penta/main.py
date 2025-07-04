import os
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from django.http import HttpRequest, HttpResponse
from django.urls import URLPattern, URLResolver, reverse
from django.utils.module_loading import import_string

from penta.constants import NOT_SET, NOT_SET_TYPE
from penta.errors import (
    ConfigError,
    ValidationError,
    ValidationErrorContext,
    set_default_exc_handlers,
)
from penta.openapi import get_schema
from penta.openapi.docs import DocsBase, Swagger
from penta.openapi.schema import OpenAPISchema
from penta.openapi.urls import get_openapi_urls, get_root_url
from penta.parser import Parser
from penta.renderers import BaseRenderer, JSONRenderer
from penta.router import Router
from penta.throttling import BaseThrottle
from penta.types import DictStrAny, TCallable
from penta.utils import is_debug_server, normalize_path

if TYPE_CHECKING:
    from .operation import Operation  # pragma: no cover

__all__ = ["Penta"]

_E = TypeVar("_E", bound=Exception)
Exc = Union[_E, Type[_E]]
ExcHandler = Callable[[HttpRequest, Exc[_E]], HttpResponse]


class Penta:
    _registry: List[str] = []

    def __init__(
        self,
        *,
        title: str = "Penta",
        version: str = "1.0.0",
        description: str = "",
        openapi_url: Optional[str] = "/openapi.json",
        docs: DocsBase = Swagger(),
        docs_url: Optional[str] = "/docs",
        docs_decorator: Optional[Callable[[TCallable], TCallable]] = None,
        servers: Optional[List[DictStrAny]] = None,
        urls_namespace: Optional[str] = None,
        csrf: bool = False,
        auth: Optional[Union[Sequence[Callable], Callable, NOT_SET_TYPE]] = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        renderer: Optional[BaseRenderer] = None,
        parser: Optional[Parser] = None,
        default_router: Optional[Router] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            title: A title for the api.
            description: A description for the api.
            version: The API version.
            urls_namespace: The Django URL namespace for the API. If not provided, the namespace will be ``"api-" + self.version``.
            openapi_url: The relative URL to serve the openAPI spec.
            openapi_extra: Additional attributes for the openAPI spec.
            docs_url: The relative URL to serve the API docs.
            servers: List of target hosts used in openAPI spec.
            csrf: Require a CSRF token for unsafe request types. See <a href="../csrf">CSRF</a> docs.
            auth (Callable | Sequence[Callable] | NOT_SET | None): Authentication class
            renderer: Default response renderer
            parser: Default request parser
        """
        self.title = title
        self.version = version
        self.description = description
        self.openapi_url = openapi_url
        self.docs = docs
        self.docs_url = docs_url
        self.docs_decorator = docs_decorator
        self.servers = servers or []
        self.urls_namespace = urls_namespace or f"api-{self.version}"
        self.csrf = csrf  # TODO: Check if used or at least throw Deprecation warning
        if self.csrf:
            warnings.warn(
                "csrf argument is deprecated, auth is handling csrf automatically now",
                DeprecationWarning,
                stacklevel=2,
            )
        self.renderer = renderer or JSONRenderer()
        self.parser = parser or Parser()
        self.openapi_extra = openapi_extra or {}

        self._exception_handlers: Dict[Exc, ExcHandler] = {}
        self.set_default_exception_handlers()

        self.auth: Optional[Union[Sequence[Callable], NOT_SET_TYPE]]

        if callable(auth):
            self.auth = [auth]
        else:
            self.auth = auth

        self.throttle = throttle

        self._routers: List[Tuple[str, Router]] = []
        self.default_router = default_router or Router()
        self.add_router("", self.default_router)

    def get(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `GET` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.get(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def post(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `POST` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.post(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def delete(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `DELETE` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.delete(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def patch(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `PATCH` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.patch(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def put(
        self,
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        """
        `PUT` operation. See <a href="../operations-parameters">operations
        parameters</a> reference.
        """
        return self.default_router.put(
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def api_operation(
        self,
        methods: List[str],
        path: str,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,
        openapi_extra: Optional[Dict[str, Any]] = None,
    ) -> Callable[[TCallable], TCallable]:
        return self.default_router.api_operation(
            methods,
            path,
            auth=auth is NOT_SET and self.auth or auth,
            throttle=throttle is NOT_SET and self.throttle or throttle,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags,
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
            openapi_extra=openapi_extra,
        )

    def add_router(
        self,
        prefix: str,
        router: Union[Router, str],
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        tags: Optional[List[str]] = None,
        parent_router: Optional[Router] = None,
    ) -> None:
        if isinstance(router, str):
            router = import_string(router)
            assert isinstance(router, Router)

        if auth is not NOT_SET:
            router.auth = auth

        if throttle is not NOT_SET:
            router.throttle = throttle

        if tags is not None:
            router.tags = tags

        if parent_router:
            parent_prefix = next(
                (path for path, r in self._routers if r is parent_router), None
            )  # pragma: no cover
            assert parent_prefix is not None
            prefix = normalize_path("/".join((parent_prefix, prefix))).lstrip("/")

        self._routers.extend(router.build_routers(prefix))
        router.set_api_instance(self, parent_router)

    @property
    def urls(self) -> Tuple[List[Union[URLResolver, URLPattern]], str, str]:
        """
        str: URL configuration

        Returns:

            Django URL configuration
        """
        self._validate()
        return (
            self._get_urls(),
            "penta",
            self.urls_namespace.split(":")[-1],
            # ^ if api included into nested urls, we only care about last bit here
        )

    def _get_urls(self) -> List[Union[URLResolver, URLPattern]]:
        result = get_openapi_urls(self)

        for prefix, router in self._routers:
            result.extend(router.urls_paths(prefix))

        result.append(get_root_url(self))
        return result

    def get_root_path(self, path_params: DictStrAny) -> str:
        name = f"{self.urls_namespace}:api-root"
        return reverse(name, kwargs=path_params)

    def create_response(
        self,
        request: HttpRequest,
        data: Any,
        *,
        status: Optional[int] = None,
        temporal_response: Optional[HttpResponse] = None,
    ) -> HttpResponse:
        if temporal_response:
            status = temporal_response.status_code
        assert status

        content = self.renderer.render(request, data, response_status=status)

        if temporal_response:
            response = temporal_response
            response.content = content
        else:
            response = HttpResponse(
                content, status=status, content_type=self.get_content_type()
            )

        return response

    def create_temporal_response(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("", content_type=self.get_content_type())

    def get_content_type(self) -> str:
        return f"{self.renderer.media_type}; charset={self.renderer.charset}"

    def get_openapi_schema(
        self,
        *,
        path_prefix: Optional[str] = None,
        path_params: Optional[DictStrAny] = None,
    ) -> OpenAPISchema:
        if path_prefix is None:
            path_prefix = self.get_root_path(path_params or {})
        return get_schema(api=self, path_prefix=path_prefix)

    def get_openapi_operation_id(self, operation: "Operation") -> str:
        name = operation.view_func.__name__
        module = operation.view_func.__module__
        return (module + "_" + name).replace(".", "_")

    def get_operation_url_name(self, operation: "Operation", router: Router) -> str:
        """
        Get the default URL name to use for an operation if it wasn't
        explicitly provided.
        """
        return operation.view_func.__name__

    def add_exception_handler(
        self, exc_class: Type[_E], handler: ExcHandler[_E]
    ) -> None:
        assert issubclass(exc_class, Exception)
        self._exception_handlers[exc_class] = handler

    def exception_handler(
        self, exc_class: Type[Exception]
    ) -> Callable[[TCallable], TCallable]:
        def decorator(func: TCallable) -> TCallable:
            self.add_exception_handler(exc_class, func)
            return func

        return decorator

    def set_default_exception_handlers(self) -> None:
        set_default_exc_handlers(self)

    def on_exception(self, request: HttpRequest, exc: Exc[_E]) -> HttpResponse:
        handler = self._lookup_exception_handler(exc)
        if handler is None:
            raise exc
        return handler(request, exc)

    def validation_error_from_error_contexts(
        self, error_contexts: List[ValidationErrorContext]
    ) -> ValidationError:
        errors: List[Dict[str, Any]] = []
        for context in error_contexts:
            model = context.model
            e = context.pydantic_validation_error
            for i in e.errors(include_url=False):
                i["loc"] = (
                    model.__penta_param_source__,
                ) + model.__penta_flatten_map_reverse__.get(i["loc"], i["loc"])
                # removing pydantic hints
                del i["input"]  # type: ignore
                if (
                    "ctx" in i
                    and "error" in i["ctx"]
                    and isinstance(i["ctx"]["error"], Exception)
                ):
                    i["ctx"]["error"] = str(i["ctx"]["error"])
                errors.append(dict(i))
        return ValidationError(errors)

    def _lookup_exception_handler(self, exc: Exc[_E]) -> Optional[ExcHandler[_E]]:
        for cls in type(exc).__mro__:
            if cls in self._exception_handlers:
                return self._exception_handlers[cls]

        return None

    def _validate(self) -> None:
        # urls namespacing validation
        skip_registry = os.environ.get("PENTA_SKIP_REGISTRY", False)
        if (
            not skip_registry
            and self.urls_namespace in Penta._registry
            and is_debug_server()
        ):
            msg = f"""
Looks like you created multiple Pentas or TestClients
To let penta distinguish them you need to set either unique version or urls_namespace
 - Penta(..., version='2.0.0')
 - Penta(..., urls_namespace='otherapi')
Already registered: {Penta._registry}
"""
            raise ConfigError(msg.strip())
        Penta._registry.append(self.urls_namespace)
