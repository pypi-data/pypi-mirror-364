from __future__ import annotations

from enum import auto
from math import ceil, exp, pi, sqrt
from typing import Any, Iterable, Literal, TypeVar, overload

from jetpytools import CustomEnum, CustomNotImplementedError
from typing_extensions import Self

from vsexprtools import ExprList, ExprOp, ExprToken, ExprVars
from vstools import (
    ConstantFormatVideoNode, ConvMode, CustomIntEnum, CustomValueError, KwargsT, PlanesT, check_variable,
    core, fallback, iterate, shift_clip_multi, vs
)

__all__ = [
    'LimitFilterMode',
    'BlurMatrixBase', 'BlurMatrix'
]


class LimitFilterModeMeta:
    force_expr = True


class LimitFilterMode(LimitFilterModeMeta, CustomIntEnum):
    """Two sources, one filtered"""
    SIMPLE_MIN = auto()
    SIMPLE_MAX = auto()
    """One source, two filtered"""
    SIMPLE2_MIN = auto()
    SIMPLE2_MAX = auto()
    DIFF_MIN = auto()
    DIFF_MAX = auto()
    """One/Two sources, one filtered"""
    CLAMPING = auto()

    @property
    def op(self) -> str:
        return '<' if 'MIN' in self._name_ else '>'

    def __call__(self, force_expr: bool = True) -> Self:
        self.force_expr = force_expr

        return self


_Nb = TypeVar('_Nb', bound=float | int)


class BlurMatrixBase(list[_Nb]):
    """
    Represents a convolution kernel (matrix) for spatial or temporal filtering.

    This class is typically constructed via the `BlurMatrix` enum, and encapsulates both the filter values
    and the intended convolution mode (e.g., horizontal, vertical, square, temporal).

    When called, it applies the convolution to a clip using the appropriate method (`std.Convolution`,
    `std.AverageFrames`, or a custom `ExprOp` expression), depending on the kernel's properties and context.

    Example:
        ```py
        kernel = BlurMatrix.BINOMIAL(taps=2)
        blurred = kernel(clip)
        ```
    """

    def __init__(
        self, __iterable: Iterable[_Nb], /, mode: ConvMode = ConvMode.SQUARE,
    ) -> None:
        """
        :param __iterable:  Iterable of kernel coefficients.
        :param mode:        Convolution mode to use. Default is SQUARE.
        """
        self.mode = mode
        super().__init__(__iterable)

    def __call__(
        self, clip: vs.VideoNode, planes: PlanesT = None,
        bias: float | None = None, divisor: float | None = None, saturate: bool = True,
        passes: int = 1, expr_kwargs: KwargsT | None = None, **conv_kwargs: Any
    ) -> ConstantFormatVideoNode:
        """
        Apply the blur kernel to the given clip via spatial or temporal convolution.

        Chooses the appropriate backend (`std.Convolution`, `std.AverageFrames`, or `ExprOp.convolution`)
        depending on kernel size, mode, format, and other constraints.

        :param clip:            Source clip.
        :param planes:          Planes to process. Defaults to all.
        :param bias:            Value added to result before clamping.
        :param divisor:         Divides the result of the convolution (before adding bias).
                                Defaults to sum of kernel values.
        :param saturate:        If True, negative values are clamped to zero.
                                If False, absolute values are returned.
        :param passes:          Number of convolution passes to apply.
        :param expr_kwargs:     Extra kwargs passed to ExprOp.convolution when used.
        :param **conv_kwargs:   Any other args passed to the underlying VapourSynth function.

        :return:            Processed (blurred) video clip.
        """
        assert check_variable(clip, self)

        if len(self) <= 1:
            return clip

        expr_kwargs = expr_kwargs or KwargsT()

        fp16 = clip.format.sample_type == vs.FLOAT and clip.format.bits_per_sample == 16

        if self.mode.is_spatial:
            # std.Convolution is limited to 25 numbers
            # SQUARE mode is not optimized
            # std.Convolution doesn't support float 16
            if len(self) <= 25 and self.mode != ConvMode.SQUARE and not fp16:
                return iterate(clip, core.std.Convolution, passes, self, bias, divisor, planes, saturate, self.mode)

            return iterate(
                clip, ExprOp.convolution("x", self, bias, fallback(divisor, True), saturate, self.mode, **conv_kwargs),
                passes, planes=planes, **expr_kwargs
            )

        if all([
            not fp16,
            len(self) <= 31,
            not bias,
            saturate,
            (len(conv_kwargs) == 0 or (len(conv_kwargs) == 1 and "scenechange" in conv_kwargs))
        ]):
            return iterate(clip, core.std.AverageFrames, passes, self, divisor, planes=planes, **conv_kwargs)

        return self._averageframes_akarin(clip, planes, bias, divisor, saturate, passes, expr_kwargs, **conv_kwargs)

    def _averageframes_akarin(self, *args: Any, **kwargs: Any) -> ConstantFormatVideoNode:
        clip, planes, bias, divisor, saturate, passes, expr_kwargs = args
        conv_kwargs = kwargs

        r = len(self) // 2

        if conv_kwargs.pop("scenechange", False) is False:
            expr_conv = ExprOp.convolution(
                ExprVars(len(self)), self, bias, fallback(divisor, True), saturate, self.mode, **conv_kwargs
            )
            return iterate(
                clip, lambda x: expr_conv(shift_clip_multi(x, (-r, r)), planes=planes, **expr_kwargs), passes
            ).std.CopyFrameProps(clip)

        expr = ExprList()

        vars_ = [[f"{v}"] for v in ExprOp.matrix(ExprVars(len(self), akarin=True), r, self.mode)[0]]

        back_vars = vars_[:r]

        # Constructing the expression for backward (previous) clips.
        # Each clip is weighted by its corresponding weight and multiplied by the logical NOT
        # of all `_SceneChangeNext` properties from the current and subsequent clips.
        # This ensures that the expression excludes frames that follow detected scene changes.
        for i, (var, weight) in enumerate(zip(back_vars, self[:r])):
            expr.append(
                var, weight, ExprOp.MUL,
                [[f"{back_vars[ii][0]}._SceneChangeNext", ExprOp.NOT, ExprOp.MUL]
                 for ii in range(i, len(back_vars))],
                ExprOp.DUP, f"cond{i}!"
            )

        forw_vars = vars_[r + 1:]
        forw_vars.reverse()

        # Same thing for forward (next) clips.
        for j, (var, weight) in enumerate(zip(forw_vars, reversed(self[r + 1:]))):
            expr.append(
                var, weight, ExprOp.MUL,
                [[f"{forw_vars[jj][0]}._SceneChangePrev", ExprOp.NOT, ExprOp.MUL]
                 for jj in range(j, len(forw_vars))],
                ExprOp.DUP, f"cond{len(vars_) - j - 1}!"
            )

        # If a scene change is detected, all the weights beyond it are applied
        # to the center frame.
        expr.append(vars_[r], self[r])

        for k, w in enumerate(self[:r] + ([None] + self[r + 1:])):
            if w is not None:
                expr.append(f"cond{k}@", 0, w, ExprOp.TERN)

        expr.append(ExprOp.ADD * r * 2, ExprOp.MUL, ExprOp.ADD * r * 2)

        if (premultiply := conv_kwargs.get("premultiply", None)):
            expr.append(premultiply, ExprOp.MUL)

        if divisor:
            expr.append(divisor, ExprOp.DIV)
        else:
            expr.append(sum(self), ExprOp.DIV)

        if bias:
            expr.append(bias, ExprOp.ADD)

        if not saturate:
            expr.append(ExprOp.ABS)

        if (multiply := conv_kwargs.get("multiply", None)):
            expr.append(multiply, ExprOp.MUL)

        if conv_kwargs.get("clamp", False):
            expr.append(ExprOp.clamp(ExprToken.RangeMin, ExprToken.RangeMax))

        return iterate(
            clip, lambda x: expr(shift_clip_multi(x, (-r, r)), planes=planes, **expr_kwargs), passes
        ).std.CopyFrameProps(clip)

    def outer(self) -> Self:
        """
        Convert a 1D kernel into a 2D square kernel by computing the outer product.

        :return:    New `BlurMatrixBase` instance with 2D kernel and same mode.
        """
        from numpy import outer

        return self.__class__(list[_Nb](outer(self, self).flatten()), self.mode)  # pyright: ignore[reportArgumentType]


class BlurMatrix(CustomEnum):
    """
    Enum for predefined 1D and 2D blur kernel generators.

    Provides commonly used blur kernels (e.g., mean, binomial, Gaussian) for convolution-based filtering.

    Each kernel is returned as a `BlurMatrixBase` object.
    """

    MEAN_NO_CENTER = auto()
    """Mean kernel excluding the center pixel. Also aliased as BOX_BLUR_NO_CENTER."""

    BOX_BLUR_NO_CENTER = MEAN_NO_CENTER

    MEAN = auto()
    """Standard mean/box blur kernel including the center pixel. Aliased as BOX_BLUR."""

    BOX_BLUR = MEAN

    BINOMIAL = auto()
    """Pascal triangle coefficients approximating Gaussian blur."""

    GAUSS = auto()
    """Proper Gaussian kernel defined by `sigma`."""

    @overload
    def __call__(  # type: ignore[misc]
        self: Literal[BlurMatrix.MEAN_NO_CENTER], taps: int = 1, *, mode: ConvMode = ConvMode.SQUARE
    ) -> BlurMatrixBase[int]:
        ...

    @overload
    def __call__(  # type: ignore[misc]
        self: Literal[BlurMatrix.MEAN], taps: int = 1, *, mode: ConvMode = ConvMode.SQUARE
    ) -> BlurMatrixBase[int]:
        ...

    @overload
    def __call__(  # type: ignore[misc]
        self: Literal[BlurMatrix.BINOMIAL], taps: int = 1, *, mode: ConvMode = ConvMode.HV
    ) -> BlurMatrixBase[int]:
        ...

    @overload
    def __call__(  # type: ignore[misc]
        self: Literal[BlurMatrix.GAUSS], taps: int | None = None, *, sigma: float = 0.5, mode: ConvMode = ConvMode.HV,
        **kwargs: Any
    ) -> BlurMatrixBase[float]:
        ...

    @overload
    def __call__(self, taps: int | None = None, **kwargs: Any) -> Any:
        ...

    def __call__(self, taps: int | None = None, **kwargs: Any) -> Any:
        """
        Generate the blur kernel based on the enum variant.

        :param taps:                Size of the kernel in each direction.
        :param sigma:               [GAUSS only] Standard deviation of the Gaussian kernel.
        :param mode:                Convolution mode. Default depends on kernel.
        :return:                    A `BlurMatrixBase` instance representing the kernel.
        """
        kernel: BlurMatrixBase[Any]

        match self:
            case BlurMatrix.MEAN_NO_CENTER:
                taps = fallback(taps, 1)
                mode = kwargs.pop("mode", ConvMode.SQUARE)

                matrix = [1 for _ in range(((2 * taps + 1) ** (2 if mode == ConvMode.SQUARE else 1)) - 1)]
                matrix.insert(len(matrix) // 2, 0)

                return BlurMatrixBase[int](matrix, mode)

            case BlurMatrix.MEAN:
                taps = fallback(taps, 1)
                mode = kwargs.pop("mode", ConvMode.SQUARE)

                kernel = BlurMatrixBase[int]([1 for _ in range(((2 * taps + 1)))], mode)

            case BlurMatrix.BINOMIAL:
                taps = fallback(taps, 1)
                mode = kwargs.pop("mode", ConvMode.HV)

                c = 1
                n = taps * 2 + 1

                matrix = list[int]()

                for i in range(1, taps + 2):
                    matrix.append(c)
                    c = c * (n - i) // i

                kernel = BlurMatrixBase(matrix[:-1] + matrix[::-1], mode)

            case BlurMatrix.GAUSS:
                taps = fallback(taps, 1)
                sigma = kwargs.pop("sigma", 0.5)
                mode = kwargs.pop("mode", ConvMode.HV)
                scale_value = kwargs.pop("scale_value", 1023)

                if mode == ConvMode.SQUARE:
                    scale_value = sqrt(scale_value)

                taps = self.get_taps(sigma, taps)

                if taps < 0:
                    raise CustomValueError('Taps must be >= 0!')

                if sigma > 0.0:
                    half_pisqrt = 1.0 / sqrt(2.0 * pi) * sigma
                    doub_qsigma = 2 * sigma ** 2

                    high, *mat = [half_pisqrt * exp(-x ** 2 / doub_qsigma) for x in range(taps + 1)]

                    mat = [x * scale_value / high for x in mat]
                    mat = [*mat[::-1], scale_value, *mat]
                else:
                    mat = [scale_value]

                kernel = BlurMatrixBase(mat, mode)

            case _:
                raise CustomNotImplementedError("Unsupported blur matrix enum!", self, self)

        if mode == ConvMode.SQUARE:
            kernel = kernel.outer()

        return kernel

    def from_radius(self: Literal[BlurMatrix.GAUSS], radius: int) -> BlurMatrixBase[float]:  # type: ignore[misc]
        """
        Generate a Gaussian blur kernel from an intuitive radius.

        This is a shortcut that converts a blur radius to a corresponding sigma value.

        :param radius:  Blur radius.
        :return:        Gaussian blur matrix.
        """
        assert self is BlurMatrix.GAUSS

        return BlurMatrix.GAUSS(None, sigma=(radius + 1.0) / 3)

    def get_taps(self: Literal[BlurMatrix.GAUSS], sigma: float, taps: int | None = None) -> int:  # type: ignore[misc]
        """
        Compute the number of taps required for a given sigma value.

        :param sigma:   Gaussian sigma value.
        :param taps:    Optional manual override; if not provided, it's computed from sigma.
        :return:        Number of taps.
        """
        assert self is BlurMatrix.GAUSS

        if taps is None:
            taps = ceil(abs(sigma) * 8 + 1) // 2

        return taps
