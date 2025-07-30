from __future__ import annotations

from functools import partial
from itertools import count
from math import sqrt
from typing import TYPE_CHECKING, Any, Callable, Generic, Literal, Sequence, Union, overload

from jetpytools import CustomIntEnum, CustomStrEnum, FuncExceptT, P, R, cround

from vsexprtools import ExprOp, ExprVars, complexpr_available, norm_expr
from vskernels import Bilinear, Gaussian, Point, Scaler, ScalerLike
from vstools import (
    ColorRange, ConstantFormatVideoNode, ConvMode, CustomValueError, KwargsT, OneDimConvModeT, PlanesT,
    SpatialConvModeT, TempConvModeT, VSFunctionNoArgs, check_ref_clip, check_variable, check_variable_format, core,
    depth, expect_bits, get_plane_sizes, join, normalize_planes, normalize_seq, split, vs
)

from .enum import BlurMatrix, BlurMatrixBase, LimitFilterMode
from .freqs import MeanMode
from .limit import limit_filter
from .rgtools import vertical_cleaner
from .util import normalize_radius

__all__ = [
    'box_blur', 'side_box_blur',
    'gauss_blur',
    'min_blur', 'sbr', 'median_blur',
    'bilateral', 'flux_smooth',
    'guided_filter'
]


def box_blur(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    passes: int = 1,
    mode: OneDimConvModeT | TempConvModeT = ConvMode.HV,
    planes: PlanesT = None, **kwargs: Any
) -> ConstantFormatVideoNode:
    """
    Applies a box blur to the input clip.

    :param clip:                Source clip.
    :param radius:              Blur radius (spatial or temporal) Can be a int or a list for per-plane control.
                                Defaults to 1
    :param passes:              Number of times the blur is applied. Defaults to 1
    :param mode:                Convolution mode (horizontal, vertical, both, or temporal). Defaults to HV.
    :param planes:              Planes to process. Defaults to all.
    :raises CustomValueError:   If square convolution mode is specified, which is unsupported.
    :return:                    Blurred clip.
    """
    assert check_variable(clip, box_blur)

    if isinstance(radius, Sequence):
        return normalize_radius(clip, box_blur, radius, planes, passes=passes, mode=mode, **kwargs)

    if not radius:
        return clip

    if mode == ConvMode.TEMPORAL:
        return BlurMatrix.MEAN(radius, mode=mode)(clip, planes, passes=passes, **kwargs)

    if not TYPE_CHECKING:
        if mode == ConvMode.SQUARE:
            raise CustomValueError("Invalid mode specified", box_blur, mode)

    box_args = (
        planes,
        radius, 0 if mode == ConvMode.VERTICAL else passes,
        radius, 0 if mode == ConvMode.HORIZONTAL else passes
    )

    return clip.vszip.BoxBlur(*box_args)


def side_box_blur(
    clip: vs.VideoNode, radius: int | list[int] = 1, planes: PlanesT = None,
    inverse: bool = False
) -> ConstantFormatVideoNode:
    assert check_variable_format(clip, side_box_blur)

    planes = normalize_planes(clip, planes)

    if isinstance(radius, list):
        return normalize_radius(clip, side_box_blur, radius, planes, inverse=inverse)

    half_kernel = [(1 if i <= 0 else 0) for i in range(-radius, radius + 1)]

    conv_m1 = partial(core.std.Convolution, matrix=half_kernel, planes=planes)
    conv_m2 = partial(core.std.Convolution, matrix=half_kernel[::-1], planes=planes)
    blur_pt = partial(box_blur, planes=planes)

    vrt_filters, hrz_filters = list[list[partial[ConstantFormatVideoNode]]](
        [
            partial(conv_m1, mode=mode), partial(conv_m2, mode=mode),
            partial(blur_pt, hradius=hr, vradius=vr, hpasses=h, vpasses=v)
        ] for h, hr, v, vr, mode in [
            (0, None, 1, radius, ConvMode.VERTICAL), (1, radius, 0, None, ConvMode.HORIZONTAL)
        ]
    )

    vrt_intermediates = (vrt_flt(clip) for vrt_flt in vrt_filters)
    intermediates = list(
        hrz_flt(vrt_intermediate)
        for i, vrt_intermediate in enumerate(vrt_intermediates)
        for j, hrz_flt in enumerate(hrz_filters) if not i == j == 2
    )

    comp_blur = None if inverse else box_blur(clip, radius, 1, planes=planes)

    if complexpr_available:
        template = '{cum} x - abs {new} x - abs < {cum} {new} ?'

        cum_expr, cumc = '', 'y'
        n_inter = len(intermediates)

        for i, newc, var in zip(count(), ExprVars[2:26], ExprVars[4:26]):
            if i == n_inter - 1:
                break

            cum_expr += template.format(cum=cumc, new=newc)

            if i != n_inter - 2:
                cumc = var.upper()
                cum_expr += f' {cumc}! '
                cumc = f'{cumc}@'

        if comp_blur:
            clips = [clip, *intermediates, comp_blur]
            cum_expr = f'x {cum_expr} - {ExprVars[n_inter + 1]} +'
        else:
            clips = [clip, *intermediates]

        cum = norm_expr(clips, cum_expr, planes, func=side_box_blur)
    else:
        cum = intermediates[0]
        for new in intermediates[1:]:
            cum = limit_filter(clip, cum, new, LimitFilterMode.SIMPLE2_MIN, planes)

        if comp_blur:
            cum = clip.std.MakeDiff(cum).std.MergeDiff(comp_blur)

    if comp_blur:
        return box_blur(cum, 1, min(radius // 2, 1))

    return cum


def gauss_blur(
    clip: vs.VideoNode,
    sigma: float | Sequence[float] = 0.5,
    taps: int | None = None,
    mode: OneDimConvModeT | TempConvModeT = ConvMode.HV,
    planes: PlanesT = None,
    **kwargs: Any
) -> ConstantFormatVideoNode:
    """
    Applies Gaussian blur to a clip, supporting spatial and temporal modes, and per-plane control.

    :param clip:                Source clip.
    :param sigma:               Standard deviation of the Gaussian kernel. Can be a float or a list for per-plane control.
    :param taps:                Number of taps in the kernel. Automatically determined if not specified.
    :param mode:                Convolution mode (horizontal, vertical, both, or temporal). Defaults to HV.
    :param planes:              Planes to process. Defaults to all.
    :param kwargs:              Additional arguments passed to the resizer or blur kernel.
                                Specifying `_fast=True` enables fast approximation.
    :raises CustomValueError:   If square convolution mode is specified, which is unsupported.
    :return:                    Blurred clip.
    """
    assert check_variable(clip, gauss_blur)

    planes = normalize_planes(clip, planes)

    if not TYPE_CHECKING:
        if mode == ConvMode.SQUARE:
            raise CustomValueError("Invalid mode specified", gauss_blur, mode)

    if isinstance(sigma, Sequence):
        return normalize_radius(clip, gauss_blur, dict(sigma=sigma), planes, mode=mode)

    fast = kwargs.pop("_fast", False)

    sigma_constant = 0.9 if fast and not mode.is_temporal else sigma
    taps = BlurMatrix.GAUSS.get_taps(sigma_constant, taps)

    if not mode.is_temporal:
        def _resize2_blur(plane: ConstantFormatVideoNode, sigma: float, taps: int) -> ConstantFormatVideoNode:
            resize_kwargs = dict[str, Any]()

            # Downscale approximation can be used by specifying _fast=True
            # Has a big speed gain when taps is large
            if fast:
                wdown, hdown = plane.width, plane.height

                if ConvMode.VERTICAL in mode:
                    hdown = round(max(round(hdown / sigma), 2) / 2) * 2

                if ConvMode.HORIZONTAL in mode:
                    wdown = round(max(round(wdown / sigma), 2) / 2) * 2

                resize_kwargs.update(width=plane.width, height=plane.height)

                plane = core.resize.Bilinear(plane, wdown, hdown)
                sigma = sigma_constant
            else:
                resize_kwargs.update({f'force_{k}': k in mode for k in 'hv'})

            return Gaussian(sigma, taps).scale(plane, **resize_kwargs | kwargs)  # type: ignore[return-value]

        if not {*range(clip.format.num_planes)} - {*planes}:
            return _resize2_blur(clip, sigma, taps)

        return join([
            _resize2_blur(p, sigma, taps) if i in planes else p
            for i, p in enumerate(split(clip))
        ])

    kernel = BlurMatrix.GAUSS(taps, sigma=sigma, mode=mode, scale_value=1023)

    return kernel(clip, planes, **kwargs)


def min_blur(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    mode: tuple[ConvMode, ConvMode] = (ConvMode.HV, ConvMode.SQUARE),
    planes: PlanesT = None,
    **kwargs: Any
) -> ConstantFormatVideoNode:
    """
    Combines binomial (Gaussian-like) blur and median filtering for a balanced smoothing effect.

    This filter blends the input clip with both a binomial blur and a median blur to achieve
    a "best of both worlds" result — combining the edge-preserving nature of median filtering
    with the smoothness of Gaussian blur. The effect is somewhat reminiscent of a bilateral filter.

    Original concept: http://avisynth.nl/index.php/MinBlur

    :param clip:      Source clip.
    :param radius:    Radius of blur to apply. Can be a single int or a list for per-plane control.
    :param mode:      A tuple of two convolution modes:
                         - First element: mode for binomial blur.
                         - Second element: mode for median blur.
                      Defaults to (HV, SQUARE).
    :param planes:    Planes to process. Defaults to all.
    :param kwargs:    Additional arguments passed to the binomial blur.
    :return:          Clip with MinBlur applied.
    """
    assert check_variable(clip, min_blur)

    planes = normalize_planes(clip, planes)

    if isinstance(radius, Sequence):
        return normalize_radius(clip, min_blur, radius, planes)

    mode_blur, mode_median = normalize_seq(mode, 2)

    blurred = BlurMatrix.BINOMIAL(radius=radius, mode=mode_blur)(clip, planes=planes, **kwargs)
    median = median_blur(clip, radius, mode_median, planes=planes)

    return MeanMode.MEDIAN([clip, blurred, median], planes=planes)


_SbrBlurT = Union[
    BlurMatrix,
    Sequence[float],
    VSFunctionNoArgs[vs.VideoNode, vs.VideoNode],
]

def sbr(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    mode: ConvMode = ConvMode.HV,
    blur: _SbrBlurT | vs.VideoNode = BlurMatrix.BINOMIAL,
    blur_diff: _SbrBlurT = BlurMatrix.BINOMIAL,
    planes: PlanesT = None,
    *,
    func: FuncExceptT | None = None,
    **kwargs: Any
) -> ConstantFormatVideoNode:
    """
    A helper function for high-pass filtering a blur difference, inspired by an AviSynth script by Didée.
    `https://forum.doom9.org/showthread.php?p=1584186#post1584186`

    :param clip:        Source clip.
    :param radius:      Specifies the size of the blur kernels if `blur` or `blur_diff` is a BlurMatrix enum.
                        Default to 1.
    :param mode:        Specifies the convolution mode. Defaults to horizontal + vertical.
    :param blur:        Blur kernel to apply to the original clip. Defaults to binomial.
    :param blur_diff:   Blur kernel to apply to the difference clip. Defaults to binomial.
    :param planes:      Which planes to process. Defaults to all.
    :param **kwargs:    Additional arguments passed to blur kernel call.
    :return:            Sbr'd clip.
    """
    func = func or sbr

    if isinstance(radius, Sequence):
        return normalize_radius(clip, min_blur, list(radius), planes)

    def _apply_blur(clip: ConstantFormatVideoNode, blur: _SbrBlurT | vs.VideoNode) -> ConstantFormatVideoNode:
        if isinstance(blur, Sequence):
            return BlurMatrixBase(blur, mode=mode)(clip, planes, **kwargs)

        if isinstance(blur, BlurMatrix):
            return blur(taps=radius, mode=mode)(clip, planes, **kwargs)

        blurred = blur(clip) if callable(blur) else blur

        assert check_variable_format(blurred, func)

        return blurred

    assert check_variable(clip, func)

    planes = normalize_planes(clip, planes)

    blurred = _apply_blur(clip, blur)

    diff = clip.std.MakeDiff(blurred, planes=planes)
    blurred_diff = _apply_blur(diff, blur_diff)

    return norm_expr(
        [clip, diff, blurred_diff],
        'y neutral - D1! y z - D2! D1@ D2@ xor x x D1@ abs D2@ abs < D1@ D2@ ? - ?',
        planes=planes, func=func
    )


@overload
def median_blur(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    mode: SpatialConvModeT = ConvMode.SQUARE,
    planes: PlanesT = None,
) -> ConstantFormatVideoNode: ...


@overload
def median_blur(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    mode: Literal[ConvMode.SQUARE] = ...,
    planes: PlanesT = None,
    smart: Literal[True] = ...,
    threshold: float | Sequence[float] | None = None,
    scalep: bool = True,
) -> ConstantFormatVideoNode: ...


@overload
def median_blur(
    clip: vs.VideoNode, radius: int = 1, mode: Literal[ConvMode.TEMPORAL] = ..., planes: PlanesT = None
) -> ConstantFormatVideoNode:
    ...


@overload
def median_blur(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    mode: ConvMode = ConvMode.SQUARE,
    planes: PlanesT = None,
    smart: bool = False,
    threshold: float | Sequence[float] | None = None,
    scalep: bool = True,
) -> ConstantFormatVideoNode: ...


def median_blur(
    clip: vs.VideoNode,
    radius: int | Sequence[int] = 1,
    mode: ConvMode = ConvMode.SQUARE,
    planes: PlanesT = None,
    smart: bool = False,
    threshold: float | Sequence[float] | None = None,
    scalep: bool = True,
) -> ConstantFormatVideoNode:
    """
    Applies a median blur to the clip using spatial or temporal neighborhood.

    - In temporal mode, each pixel is replaced by the median across multiple frames.
    - In spatial modes, each pixel is replaced with the median of its 2D neighborhood.

    :param clip:                Source clip.
    :param radius:              Blur radius per plane (list) or uniform radius (int).
                                Only int is allowed in temporal mode.
    :param mode:                Convolution mode. Defaults to SQUARE.
    :param planes:              Planes to process. Defaults to all.
    :param smart:               Enable [Smart Median by zsmooth](https://github.com/adworacz/zsmooth?tab=readme-ov-file#smart-median),
                                thresholded based on a modified form of variance.
    :param threshold:           The variance threshold when ``smart=True``.
                                Pixels with a variance under the threshold are smoothed,
                                and over the threshold are returned as is.
    :param scalep:              Parameter scaling when ``smart=True``.
                                If True, all threshold values will be automatically scaled from 8-bit range (0-255)
                                to the corresponding range of the input clip's bit depth.
    :raises CustomValueError:   If a list is passed for radius in temporal mode, which is unsupported,
                                or if smart=True and mode != ConvMode.SQUARE.
    :return:                    Median-blurred video clip.
    """
    assert check_variable(clip, median_blur)

    if mode == ConvMode.TEMPORAL:
        if isinstance(radius, int):
            return clip.zsmooth.TemporalMedian(radius, planes)

        raise CustomValueError("A list of radius isn't supported for ConvMode.TEMPORAL!", median_blur, radius)

    radius = normalize_seq(radius, clip.format.num_planes)

    if smart:
        if mode == ConvMode.SQUARE:
            return core.zsmooth.SmartMedian(clip, radius, threshold, scalep, planes)

        raise CustomValueError("When using SmartMedian, mode should be ConvMode.SQUARE!", median_blur, mode)

    if mode == ConvMode.SQUARE and max(radius) <= 3:
        return core.zsmooth.Median(clip, radius, planes)

    if mode == ConvMode.VERTICAL and max(radius) <= 1:
        return vertical_cleaner(clip, radius, planes)

    expr_plane = list[list[str]]()

    for r in radius:
        expr_passes = list[str]()

        for mat in ExprOp.matrix('x', r, mode, [(0, 0)]):
            rb = len(mat) + 1
            st = rb - 1
            sp = rb // 2 - 1
            dp = st - 2

            expr_passes.append(f"{mat} sort{st} swap{sp} min! swap{sp} max! drop{dp} x min@ max@ clip")

        expr_plane.append(expr_passes)

    for e in zip(*expr_plane):
        clip = norm_expr(clip, e, planes, func=median_blur)

    return clip


class Bilateral(Generic[P, R]):
    """
    Class decorator that wraps the [bilateral][vsrgtools.blur.bilateral] function
    and extends its functionality.

    It is not meant to be used directly.
    """

    def __init__(self, bilateral_func: Callable[P, R]) -> None:
        self._func = bilateral_func

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._func(*args, **kwargs)

    class Backend(CustomStrEnum):
        """
        Enum specifying which backend implementation of the bilateral filter to use.
        """

        CPU = 'vszip'
        """
        Uses `vszip.Bilateral` — a fast, CPU-based implementation written in Zig.
        """

        GPU = 'bilateralgpu'
        """
        Uses `bilateralgpu.Bilateral` — a CUDA-based GPU implementation.
        """

        GPU_RTC = 'bilateralgpu_rtc'
        """
        Uses `bilateralgpu_rtc.Bilateral` — a CUDA-based GPU implementation with runtime shader compilation.
        """

        def Bilateral(self, clip: vs.VideoNode, *args: Any, **kwargs: Any) -> ConstantFormatVideoNode:
            """
            Applies the bilateral filter using the plugin associated with the selected backend.

            :param clip:                    Source clip.
            :param *args:                   Positional arguments passed to the selected plugin.
            :param **kwargs:                Keyword arguments passed to the selected plugin.
            :return:                        Bilaterally filtered clip.
            """
            return getattr(clip, self.value).Bilateral(*args, **kwargs)


@Bilateral
def bilateral(
    clip: vs.VideoNode,
    ref: vs.VideoNode | None = None,
    sigmaS: float | Sequence[float] | None = None,
    sigmaR: float | Sequence[float] | None = None,
    backend: Bilateral.Backend = Bilateral.Backend.CPU,
    **kwargs: Any
) -> ConstantFormatVideoNode:
    """
    Applies a bilateral filter for edge-preserving and noise-reducing smoothing.

    This filter replaces each pixel with a weighted average of nearby pixels based on both spatial distance
    and pixel intensity similarity.
    It can be used for joint (cross) bilateral filtering when a reference clip is given.

    Example:
        ```py
        blurred = bilateral(clip, ref, 3.0, 0.02, backend=bilateral.Backend.CPU)
        ```

    For more details, see:
        - https://github.com/dnjulek/vapoursynth-zip/wiki/Bilateral
        - https://github.com/HomeOfVapourSynthEvolution/VapourSynth-Bilateral
        - https://github.com/WolframRhodium/VapourSynth-BilateralGPU

    :param clip:        Source clip.
    :param ref:         Optional reference clip for joint bilateral filtering.
    :param sigmaS:      Spatial sigma (controls the extent of spatial smoothing).
                        Can be a float or per-plane list.
    :param sigmaR:      Range sigma (controls sensitivity to intensity differences).
                        Can be a float or per-plane list.
    :param backend:     Backend implementation to use.
    :param kwargs:      Additional arguments forwarded to the backend-specific implementation.
    :return:            Bilaterally filtered clip.
    """
    assert check_variable_format(clip, bilateral)

    if backend == Bilateral.Backend.CPU:
        bilateral_args = KwargsT(ref=ref, sigmaS=sigmaS, sigmaR=sigmaR, planes=normalize_planes(clip))
    else:
        bilateral_args = KwargsT(ref=ref, sigma_spatial=sigmaS, sigma_color=sigmaR)

    return backend.Bilateral(clip, **bilateral_args | kwargs)


def flux_smooth(
    clip: vs.VideoNode,
    temporal_threshold: float | Sequence[float] = 7.0,
    spatial_threshold: float | Sequence[float] | None = None,
    planes: PlanesT = None,
    scalep: bool = True,
) -> ConstantFormatVideoNode:
    """
    FluxSmoothT examines each pixel and compares it to the corresponding pixel in the previous and next frames.
    Smoothing occurs if both the previous frame's value and the next frame's value are greater,
    or if both are less than the value in the current frame.

    Smoothing is done by averaging the pixel from the current frame with the pixels from the previous
    and/or next frames, if they are within temporal_threshold.

    FluxSmoothST does the same as FluxSmoothT, except the pixel's eight neighbours from the current frame
    are also included in the average, if they are within spatial_threshold.

    The first and last rows and the first and last columns are not processed by FluxSmoothST.

    :param clip:                    Clip to process.
    :param temporal_threshold:      Temporal neighbour pixels within this threshold from the current pixel
                                    are included in the average. Can be specified as an array,
                                    with values corresonding to each plane of the input clip.
                                    A negative value (such as -1) indicates that the plane should not be processed
                                    and will be copied from the input clip.
    :param spatial_threshold:       Spatial neighbour pixels within this threshold from the current pixel
                                    are included in the average. A negative value (such as -1) indicates that the plane
                                    should not be processed and will be copied from the input clip.
    :param planes:                  Which planes to process. Default to all.
    :param scalep:                  Parameter scaling. If set to true, all threshold values
                                    will be automatically scaled from 8-bit range (0-255) to the corresponding range
                                    of the input clip's bit depth.
    :return:                        Smoothed clip.
    """

    assert check_variable_format(clip, flux_smooth)

    if spatial_threshold:
        return core.zsmooth.FluxSmoothST(clip, temporal_threshold, spatial_threshold, planes, scalep)

    return core.zsmooth.FluxSmoothT(clip, temporal_threshold, planes, scalep)


class GuidedFilter(Generic[P, R]):
    """
    Class decorator that wraps the [guided_filter][vsrgtools.blur.guided_filter] function
    and extends its functionality.

    It is not meant to be used directly.
    """

    def __init__(self, guided_filter_func: Callable[P, R]) -> None:
        self._func = guided_filter_func

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._func(*args, **kwargs)

    class Mode(CustomIntEnum):
        ORIGINAL = 0
        """Original Guided Filter"""

        WEIGHTED = 1
        """Weighted Guided Image Filter"""

        GRADIENT = 2
        """Gradient Domain Guided Image Filter"""


@GuidedFilter
def guided_filter(
    clip: vs.VideoNode,
    guidance: vs.VideoNode | None = None,
    radius: int | Sequence[int] | None = None,
    thr: float | Sequence[float] = 1 / 3,
    mode: GuidedFilter.Mode = GuidedFilter.Mode.GRADIENT,
    use_gauss: bool = False,
    planes: PlanesT = None,
    down_ratio: int = 0,
    downscaler: ScalerLike = Point,
    upscaler: ScalerLike = Bilinear
) -> vs.VideoNode:
    assert check_variable(clip, guided_filter)

    planes = normalize_planes(clip, planes)

    downscaler = Scaler.ensure_obj(downscaler, guided_filter)
    upscaler = Scaler.ensure_obj(upscaler, guided_filter)

    width, height = clip.width, clip.height

    thr = normalize_seq(thr, clip.format.num_planes)

    size = normalize_seq(
        [220, 225, 225] if ColorRange.from_video(clip, func=guided_filter).is_full else 256,
        clip.format.num_planes
    )

    thr = [t / s for t, s in zip(thr, size)]

    if radius is None:
        radius = [
            round(max((w - 1280) / 160 + 12, (h - 720) / 90 + 12))
            for w, h in [
                get_plane_sizes(clip, i) for i in range(clip.format.num_planes)
            ]
        ]

    check_ref_clip(clip, guidance)

    p, bits = expect_bits(clip, 32)
    guidance_clip = g = depth(guidance, 32) if guidance is not None else p

    radius = normalize_seq(radius, clip.format.num_planes)

    if down_ratio:
        down_w, down_h = cround(width / down_ratio), cround(height / down_ratio)

        p = downscaler.scale(p, down_w, down_h)
        g = downscaler.scale(g, down_w, down_h) if guidance is not None else p

        radius = [cround(rad / down_ratio) for rad in radius]

    blur_filter = partial(
        gauss_blur, sigma=[rad / 2 * sqrt(2) for rad in radius], planes=planes
    ) if use_gauss else partial(
        box_blur, radius=[rad + 1 for rad in radius], planes=planes
    )

    blur_filter_corr = partial(
        gauss_blur, sigma=1 / 2 * sqrt(2), planes=planes
    ) if use_gauss else partial(box_blur, radius=2, planes=planes)

    mean_p = blur_filter(p)
    mean_I = blur_filter(g) if guidance is not None else mean_p

    I_square = norm_expr(g, 'x dup *', planes, func=guided_filter)
    corr_I = blur_filter(I_square)
    corr_Ip = blur_filter(norm_expr([g, p], 'x y *', planes, func=guided_filter)) if guidance is not None else corr_I

    var_I = norm_expr([corr_I, mean_I], 'x y dup * -', planes, func=guided_filter)
    cov_Ip = norm_expr([corr_Ip, mean_I, mean_p], 'x y z * -', planes, func=guided_filter) if guidance is not None else var_I

    if mode is GuidedFilter.Mode.ORIGINAL:
        a = norm_expr([cov_Ip, var_I], 'x y {thr} + /', planes, thr=thr, func=guided_filter)
    else:
        if set(radius) == {1}:
            var_I_1 = var_I
        else:
            mean_I_1 = blur_filter_corr(g)
            corr_I_1 = blur_filter_corr(I_square)
            var_I_1 = norm_expr([corr_I_1, mean_I_1], 'x y dup * -', planes, func=guided_filter)

        if mode is GuidedFilter.Mode.WEIGHTED:
            weight_in = var_I_1
        else:
            weight_in = norm_expr([var_I, var_I_1], 'x y * sqrt', planes, func=guided_filter)

        denominator = norm_expr([weight_in], '1 x {eps} + /', planes, eps=1e-06, func=guided_filter)

        denominator = denominator.std.PlaneStats(None, 0)

        weight = norm_expr([weight_in, denominator], 'x 1e-06 + y.PlaneStatsAverage *', planes, func=guided_filter)

        if mode is GuidedFilter.Mode.WEIGHTED:
            a = norm_expr([cov_Ip, var_I, weight], 'x y {thr} z / + /', planes, thr=thr, func=guided_filter)
        else:
            weight_in = weight_in.std.PlaneStats(None, 0)

            a = norm_expr(
                [cov_Ip, weight_in, weight, var_I],
                'x {thr} 1 1 1 -4 y.PlaneStatsMin y.PlaneStatsAverage 1e-6 - - / '
                'y y.PlaneStatsAverage - * exp + / - * z / + a {thr} z / + /',
                planes, thr=thr
            )

    b = norm_expr([mean_p, a, mean_I], 'x y z * -', planes, func=guided_filter)

    mean_a, mean_b = blur_filter(a), blur_filter(b)

    if down_ratio:
        mean_a = upscaler.scale(mean_a, width, height)
        mean_b = upscaler.scale(mean_b, width, height)

    q = norm_expr([mean_a, guidance_clip, mean_b], 'x y * z +', planes, func=guided_filter)

    return depth(q, bits)
