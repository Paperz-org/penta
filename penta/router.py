import re
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

from django.urls import URLPattern
from django.urls import path as django_path

from penta.constants import NOT_SET, NOT_SET_TYPE
from penta.errors import ConfigError
from penta.operation import PathView
from penta.throttling import BaseThrottle
from penta.types import TCallable
from penta.utils import normalize_path, replace_path_param_notation

if TYPE_CHECKING:
    from penta import Penta  # pragma: no cover


__all__ = ["Router"]


class Router:
    def __init__(
        self,
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        tags: Optional[List[str]] = None,
        by_alias: Optional[bool] = None,
        exclude_unset: Optional[bool] = None,
        exclude_defaults: Optional[bool] = None,
        exclude_none: Optional[bool] = None,
    ) -> None:
        self.api: Optional[Penta] = None
        self.auth = auth
        self.throttle = throttle
        self.tags = tags
        self.by_alias = by_alias
        self.exclude_unset = exclude_unset
        self.exclude_defaults = exclude_defaults
        self.exclude_none = exclude_none

        self.path_operations: Dict[str, PathView] = {}
        self._routers: List[Tuple[str, Router]] = []

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
        return self.api_operation(
            ["GET"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["POST"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["DELETE"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["PATCH"],
            path,
            auth=auth,
            throttle=throttle,
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
        return self.api_operation(
            ["PUT"],
            path,
            auth=auth,
            throttle=throttle,
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
        def decorator(view_func: TCallable) -> TCallable:
            self.add_api_operation(
                path,
                methods,
                view_func,
                auth=auth,
                throttle=throttle,
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
            return view_func

        return decorator

    def add_api_operation(
        self,
        path: str,
        methods: List[str],
        view_func: Callable,
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
    ) -> None:
        path = re.sub(r"\{uuid:(\w+)\}", r"{uuidstr:\1}", path, flags=re.IGNORECASE)
        # django by default convert strings to UUIDs
        # but we want to keep them as strings to let pydantic handle conversion/validation
        # if user whants UUID object
        # uuidstr is custom registered converter

        if path not in self.path_operations:
            path_view = PathView()
            self.path_operations[path] = path_view
        else:
            path_view = self.path_operations[path]

        by_alias = by_alias is None and self.by_alias or by_alias
        exclude_unset = exclude_unset is None and self.exclude_unset or exclude_unset
        exclude_defaults = (
            exclude_defaults is None and self.exclude_defaults or exclude_defaults
        )
        exclude_none = exclude_none is None and self.exclude_none or exclude_none

        path_view.add_operation(
            path=path,
            methods=methods,
            view_func=view_func,
            auth=auth,
            throttle=throttle,
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
        if self.api:
            path_view.set_api_instance(self.api, self)

        return None

    def set_api_instance(
        self, api: "Penta", parent_router: Optional["Router"] = None
    ) -> None:
        if self.auth is NOT_SET and parent_router:
            self.auth = parent_router.auth
        self.api = api
        for path_view in self.path_operations.values():
            path_view.set_api_instance(self.api, self)
        for _, router in self._routers:
            router.set_api_instance(api, self)

    def urls_paths(self, prefix: str) -> Iterator[URLPattern]:
        prefix = replace_path_param_notation(prefix)
        for path, path_view in self.path_operations.items():
            for operation in path_view.operations:
                path = replace_path_param_notation(path)
                route = "/".join([i for i in (prefix, path) if i])
                # to skip lot of checks we simply treat double slash as a mistake:
                route = normalize_path(route)
                route = route.lstrip("/")

                url_name = getattr(operation, "url_name", "")
                if not url_name and self.api:
                    url_name = self.api.get_operation_url_name(operation, router=self)

                yield django_path(route, path_view.get_view(), name=url_name)

    def add_router(
        self,
        prefix: str,
        router: Union["Router", str],
        *,
        auth: Any = NOT_SET,
        throttle: Union[BaseThrottle, List[BaseThrottle], NOT_SET_TYPE] = NOT_SET,
        tags: Optional[List[str]] = None,
    ) -> None:
        from django.utils.module_loading import import_string

        if isinstance(router, str):
            router = import_string(router)
            assert isinstance(router, Router)

        if self.api:
            # we are already attached to an api
            self.api.add_router(
                prefix=prefix,
                router=router,
                auth=auth,
                throttle=throttle,
                tags=tags,
                parent_router=self,
            )
        else:
            # we are not attached to an api
            if auth != NOT_SET:
                router.auth = auth
            # TODO: throttle
            if tags is not None:
                router.tags = tags
            self._routers.append((prefix, router))

    def build_routers(self, prefix: str) -> List[Tuple[str, "Router"]]:
        if self.api is not None:
            from penta.utils import is_debug_server

            if is_debug_server():
                raise ConfigError(
                    f"Router@'{prefix}' has already been attached to API"
                    f" {self.api.title}:{self.api.version} "
                )
        internal_routes = []
        for inter_prefix, inter_router in self._routers:
            _route = normalize_path("/".join((prefix, inter_prefix))).lstrip("/")
            internal_routes.extend(inter_router.build_routers(_route))

        return [(prefix, self), *internal_routes]
