"""Capture data from the Australian Bureau of Statistics (ABS) using the SDMX API."""

from importlib.metadata import PackageNotFoundError, version

from .download_cache import (
    CacheError,
    GetFileKwargs,
    HttpError,
    ModalityType,
)
from .fetch import fetch
from .fetch_gdp import fetch_gdp
from .fetch_multi import fetch_multi
from .fetch_pop import fetch_pop, fetch_state_pop
from .fetch_selection import MatchCriteria, MatchItem, MatchType, fetch_selection, make_wanted, match_item
from .flow_metadata import (
    FlowMetaDict,
    code_list_for,
    code_lists,
    data_flows,
    data_structures,
    frame,
    structure_from_flow_id,
    structure_ident,
)
from .measures import measure_names, recalibrate, recalibrate_series

# --- version and author
try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode
__author__ = "Bryan Palmer"

# --- establish the package contents
__all__ = [
    "CacheError",
    "FlowMetaDict",
    "GetFileKwargs",
    "HttpError",
    "MatchCriteria",
    "MatchItem",
    "MatchType",
    "ModalityType",
    "__author__",
    "__version__",
    "code_list_for",
    "code_lists",
    "data_flows",
    "data_structures",
    "fetch",
    "fetch_gdp",
    "fetch_multi",
    "fetch_pop",
    "fetch_selection",
    "fetch_state_pop",
    "frame",
    "make_wanted",
    "match_item",
    "measure_names",
    "recalibrate",
    "recalibrate_series",
    "structure_from_flow_id",
    "structure_ident",
]
