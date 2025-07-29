import typing
from contextlib import AbstractAsyncContextManager, AbstractContextManager

from fundi.scan import scan
from fundi.types import CallableInfo, TypeResolver


def from_(
    dependency: type | typing.Callable[..., typing.Any], caching: bool = True
) -> TypeResolver | CallableInfo[typing.Any]:
    """
    Use callable or type as dependency for parameter of function

    if dependency parameter is callable the ``fundi.scan.scan`` is used

    if dependency parameter is type the ``fundi.types.TypeResolver`` is returned (unless that type is a subclass of AbstractContextManager or AbstractAsyncContextManager)

    :param dependency: function dependency
    :param caching: Whether to use cached result of this callable or not
    :return: callable information
    """
    if isinstance(dependency, type) and not issubclass(
        dependency, (AbstractContextManager, AbstractAsyncContextManager)
    ):
        return TypeResolver(dependency)

    return scan(dependency, caching=caching)
