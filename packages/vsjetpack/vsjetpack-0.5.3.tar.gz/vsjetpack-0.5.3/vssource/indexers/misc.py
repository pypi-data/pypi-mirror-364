from __future__ import annotations

from functools import cache
from typing import Any

from jetpytools import CustomIntEnum

from vstools import core, vs

from .base import Indexer

__all__ = [
    'BestSource',

    'IMWRI',

    'LSMAS',

    'CarefulSource',

    'FFMS2'
]


@cache
def _add_handler_func_bs() -> None:
    from logging import WARNING, getLogger

    try:
        from vspreview import is_preview
    except ImportError:
        def is_preview() -> bool:
            return False

    def handler_func_best_source(m_type: vs.MessageType, msg: str) -> None:
        if all([
            m_type == vs.MESSAGE_TYPE_INFORMATION,
            msg.startswith("VideoSource "),
            getLogger().level <= WARNING,
            is_preview()
        ]):
            print(msg, end="\r")

    core.add_log_handler(handler_func_best_source)


class BestSource(Indexer):
    """BestSource indexer"""

    _source_func = core.lazy.bs.VideoSource

    class CacheMode(CustomIntEnum):
        """Cache mode"""

        NEVER = 0
        """Never read or write index to disk."""

        CACHE_PATH = 1
        """
        Always try to read index but only write index to disk when it will make a noticeable difference
        on subsequent runs and store index files in a subtree of *cachepath*.
        """

        CACHE_PATH_WRITE = 2
        """
        Always try to read and write index to disk and store index files in a subtree of *cachepath*.
        """

        ABSOLUTE = 3
        """
        Always try to read index but only write index to disk when it will make a noticeable difference
        on subsequent runs and store index files in the absolute path in *cachepath*
        with track number and index extension appended.
        """

        ABSOLUTE_WRITE = 4
        """
        Always try to read and write index to disk and store index files
        in the absolute path in *cachepath* with track number and index extension appended.
        """

    def __init__(self, *, force: bool = True, cachemode: CacheMode = CacheMode.ABSOLUTE, **kwargs: Any) -> None:
        _add_handler_func_bs()

        super().__init__(force=force, cachemode=cachemode, **kwargs)


class IMWRI(Indexer):
    """ImageMagick Writer-Reader indexer"""

    _source_func = core.lazy.imwri.Read


class LSMAS(Indexer):
    """L-SMASH-Works indexer"""

    _source_func = core.lazy.lsmas.LWLibavSource


class CarefulSource(Indexer):
    """CarefulSource indexer"""

    _source_func = core.lazy.cs.ImageSource


class FFMS2(Indexer):
    """FFmpegSource2 indexer"""

    _source_func = core.lazy.ffms2.Source


class ZipSource(Indexer):
    """vszip image reader indexer"""

    _source_func = core.lazy.vszip.ImageRead
