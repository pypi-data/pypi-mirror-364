from enum import Enum
from agentmemory.connection.longterm.collections import Collection


class CacheRetrieveType(str, Enum):
    GET = "GET"
    LIST = "LIST"
    LIST_BY_ANCHOR = "LIST_BY_ANCHOR"
    LIST_UNTIL_ID_FOUND = "LIST_UNTIL_ID_FOUND"


class ClearCacheTransactionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


def _create_rtype(rtype: CacheRetrieveType) -> str:
    if not isinstance(rtype, CacheRetrieveType):
        raise ValueError(
            f"CacheRetrieveType value must be in '{CacheRetrieveType}'"
        )
    return f"type:{rtype.value}"


def _create_col(col: Collection) -> str:
    if col not in Collection:
        raise ValueError(
            f"Collection value must be in '{Collection}'"
        )
    return f"col:{col.value}"


def _create_id(
    id: str | tuple[str, str] = None,
    rtype: CacheRetrieveType = None
) -> str | None:
    if id is None and rtype == CacheRetrieveType.GET:
        raise ValueError(
            "If the CacheRetrieveType is 'GET', you need to pass in an id."
        )
    if id is None:
        return None
    if isinstance(id, str) and len(id) > 0:
        return f"id:{id}"
    if isinstance(id, tuple) and len(id) == 2:
        ids = ",".join([_id for _id in id])
        return f"id:{ids}"
    raise ValueError(
        "id must be None, a string with length >= 1, or a tuple with 2 entries, "
        f"but was: {str(id)}"
    )


def _get_anchor_id(id: str | list | tuple) -> str:
    if isinstance(id, str):
        return id
    if (isinstance(id, tuple) or isinstance(id, list)) and len(id) > 0:
        return id[0]
    raise ValueError(
        f"Anchor id must be str, list or tuple but was: {id}"
    )


def _create_query(query: dict = None) -> str | None:
    if query is None:
        return None
    if isinstance(query, dict):
        return f"q:{str(query)}"
    raise ValueError("Query must be None or a dict.")


def _create_kwargs(kwargs: dict) -> str | None:
    if not kwargs:
        return None
    kwargs_ = ";".join(
        [f"{k}:{v}" for k, v in kwargs.items() if v is not None]
    )
    return kwargs_


class CacheKey:
    def __init__(
        self,
        *,
        rtype: CacheRetrieveType,
        col: Collection,
        id: str | tuple[str, str] = None,
        query: dict = None,
        **kwargs
    ):
        self._rtype = _create_rtype(rtype)
        self._col = _create_col(col)
        self._id = _create_id(id, rtype)
        self._q = _create_query(query)
        self._kwargs = _create_kwargs(kwargs)

    def key(self) -> str:
        keys = [
            self._rtype,
            self._col,
            self._id,
            self._q,
            self._kwargs
        ]
        return ";".join([k for k in keys if k is not None])

    def __str__(self):
        return self.key()


class ClearCacheKey:
    def __init__(
        self,
        *,
        ttype: ClearCacheTransactionType,
        col: Collection,
        id: str | tuple[str, str] = None,
        is_first_id_anchor: bool = False
    ):
        self._ttype = ttype
        self._col = col
        self._id = id
        self._is_first_id_anchor = is_first_id_anchor

    def clear_keys(self) -> list[str]:
        if self._ttype not in ClearCacheTransactionType:
            raise ValueError(
                f"ClearCacheTransactionType value must be in '{ClearCacheTransactionType}'"
            )

        rgettype = _create_rtype(CacheRetrieveType.GET)
        rlisttype = _create_rtype(CacheRetrieveType.LIST)
        ralisttype = _create_rtype(CacheRetrieveType.LIST_BY_ANCHOR)
        rilisttype = _create_rtype(CacheRetrieveType.LIST_UNTIL_ID_FOUND)
        col = _create_col(self._col)

        clear_list_key = f"{rlisttype};{col}*"
        clear_list_anchor_key = ""
        clear_list_until_id_found_key = ""

        if self._is_first_id_anchor:
            anchor_id = _get_anchor_id(self._id)
            clear_list_anchor_key = (
                f"{ralisttype};{col};id:{anchor_id}*"
            )
            clear_list_until_id_found_key = (
                f"{rilisttype};{col};id:{anchor_id}*"
            )

        if self._ttype == ClearCacheTransactionType.CREATE:
            return [
                clear_list_key,
                clear_list_anchor_key,
                clear_list_until_id_found_key
            ]

        id_str = _create_id(self._id, CacheRetrieveType.GET)
        clear_get_key = f"{rgettype};{col};{id_str}*"

        return [
            clear_get_key,
            clear_list_key,
            clear_list_anchor_key,
            clear_list_until_id_found_key
        ]

    def __str__(self):
        return str(self.clear_keys())
