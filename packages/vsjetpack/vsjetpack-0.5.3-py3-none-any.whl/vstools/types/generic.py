from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterable, Protocol, TypeVar, Union

import vapoursynth as vs

from jetpytools import MISSING, DataType, FuncExceptT, MissingT, PassthroughC, SingleOrSeq, StrArr, StrArrOpt

__all__ = [
    'MissingT', 'MISSING',

    'FuncExceptT',

    'VideoNodeT', 'VideoNodeIterableT',

    'DataType', 'VSMapValue', 'BoundVSMapValue', 'VSMapValueCallback',

    'VideoFormatT',

    'HoldsVideoFormatT', 'HoldsPropValueT',

    'VSFunction', 'VSFunctionNoArgs', 'VSFunctionArgs', 'VSFunctionKwArgs', 'VSFunctionAllArgs', 'GenericVSFunction',

    'StrArr', 'StrArrOpt',

    'PassthroughC',

    'ConstantFormatVideoNode',

    'F_VD'
]


VideoNodeT = TypeVar("VideoNodeT", bound=vs.VideoNode)
VideoNodeT_contra = TypeVar("VideoNodeT_contra", bound=vs.VideoNode, contravariant=True)
VideoNodeT_co = TypeVar("VideoNodeT_co", bound=vs.VideoNode, covariant=True)

VideoNodeIterableT = Union[
    VideoNodeT,
    Iterable[VideoNodeT | Iterable[VideoNodeT]],
    Iterable[VideoNodeT | Iterable[VideoNodeT | Iterable[VideoNodeT]]]
]


_VSMapValue = Union[
    SingleOrSeq[int],
    SingleOrSeq[float],
    SingleOrSeq[DataType],
    SingleOrSeq[vs.VideoNode],
    SingleOrSeq[vs.VideoFrame],
    SingleOrSeq[vs.AudioNode],
    SingleOrSeq[vs.AudioFrame]
]
VSMapValue = Union[
    _VSMapValue,
    SingleOrSeq[Callable[..., _VSMapValue]]
]
"""Values that a VSMap can hold, so all that a :py:attr:`vs.Function`` can accept in args and can return."""

BoundVSMapValue = TypeVar('BoundVSMapValue', bound=VSMapValue)
"""Type variable that can be one of the types in a VSMapValue."""

BoundVSMapValue_0 = TypeVar('BoundVSMapValue_0', bound=VSMapValue)
BoundVSMapValue_1 = TypeVar('BoundVSMapValue_1', bound=VSMapValue)

VSMapValueCallback = Callable[..., VSMapValue]
"""Callback that can be held in a VSMap. It can only return values representable in a VSMap."""

VideoFormatT = vs.PresetVideoFormat | vs.VideoFormat
"""Types representing a clear VideoFormat."""

HoldsVideoFormatT = vs.VideoNode | vs.VideoFrame | vs.VideoFormat
"""Types from which a clear VideoFormat can be retrieved."""

HoldsPropValueT = vs.FrameProps | vs.VideoFrame | vs.AudioFrame | vs.VideoNode | vs.AudioNode
"""Types that can hold :py:attr:`vs.FrameProps`."""


F_VD = TypeVar("F_VD", bound=Callable[..., vs.VideoNode])


class VSFunctionNoArgs(Protocol[VideoNodeT_contra, VideoNodeT_co]):
    def __call__(self, clip: VideoNodeT_contra) -> VideoNodeT_co:
        ...


class VSFunctionArgs(Protocol[VideoNodeT_contra, VideoNodeT_co]):
    def __call__(self, clip: VideoNodeT_contra, *args: Any) -> VideoNodeT_co:
        ...


class VSFunctionKwArgs(Protocol[VideoNodeT_contra, VideoNodeT_co]):
    def __call__(self, clip: VideoNodeT_contra, **kwargs: Any) -> VideoNodeT_co:
        ...


class VSFunctionAllArgs(Protocol[VideoNodeT_contra, VideoNodeT_co]):
    def __call__(self, clip: VideoNodeT_contra, *args: Any, **kwargs: Any) -> VideoNodeT_co:
        ...


VSFunction = Union[
    VSFunctionNoArgs[VideoNodeT, VideoNodeT],
    VSFunctionArgs[VideoNodeT, VideoNodeT],
    VSFunctionKwArgs[VideoNodeT, VideoNodeT],
    VSFunctionAllArgs[VideoNodeT, VideoNodeT]
]
"""Function that takes a :py:attr:`vs.VideoNode` as its first argument and returns a :py:attr:`vs.VideoNode`."""

GenericVSFunction = Callable[..., VideoNodeT]

if TYPE_CHECKING:
    class ConstantFormatVideoNode(vs.VideoNode):
        format: vs.VideoFormat

else:
    ConstantFormatVideoNode = vs.VideoNode
