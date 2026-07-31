"""
Compatibility layer over the two lines of fast-depends penta supports.

fast-depends 3.0 renamed the class describing a dependency (`Depends` -> `Dependant`),
made all of its options required, and started casting the result of what it injects.
Everything penta needs from it is normalized here.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict

from fast_depends import inject as _inject
from fast_depends.dependencies import model

_IS_V3 = hasattr(model, "Dependant")

if TYPE_CHECKING:
    # penta is type checked against the version it locks, which is the latest one
    from fast_depends.dependencies.model import Dependant as Dependency
else:
    Dependency = model.Dependant if _IS_V3 else model.Depends

__all__ = ["Dependency", "dependency_options", "inject"]


def dependency_options(*, use_cache: bool, cast: bool) -> Dict[str, Any]:
    """The options to build a `Dependency` with."""
    options: Dict[str, Any] = {"use_cache": use_cache, "cast": cast}
    if _IS_V3:
        # penta serializes what the views and the dependencies return itself
        options["cast_result"] = False
    return options


def inject(func: Callable[..., Any]) -> Callable[..., Any]:
    """Resolve the dependencies of `func` when it is called."""
    if _IS_V3:
        return _inject(func, cast_result=False)
    return _inject(func)
