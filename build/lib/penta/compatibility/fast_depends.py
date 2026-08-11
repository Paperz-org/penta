"""
Compatibility layer over the two lines of fast-depends penta supports.

fast-depends 3.0 renamed the class describing a dependency (`Depends` -> `Dependant`),
made all of its options required, and started casting the result of what it injects.
Everything penta needs from it is normalized here, and described here as well: penta is
type checked - and so is anything built on it - against whichever version is installed.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict

from fast_depends import inject as _inject
from fast_depends.dependencies import model

_IS_V3 = hasattr(model, "Dependant")

if TYPE_CHECKING:

    class Dependency:
        """
        What penta uses of the class fast-depends describes a dependency with.

        `fast_depends.dependencies.model.Dependant` (3.0 and later) and its predecessor
        `Depends` both provide it; which one is used is only known at runtime.
        """

        dependency: Callable[..., Any]
        use_cache: bool
        cast: bool

        def __init__(self, dependency: Callable[..., Any], **options: Any) -> None: ...

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
    options: Dict[str, Any] = {}
    if _IS_V3:
        # penta serializes what the views return itself
        options["cast_result"] = False
    return _inject(func, **options)
