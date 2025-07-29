from typing import Literal

from mosaico.effects.crossfade import CrossFadeInEffect, CrossFadeOutEffect
from mosaico.effects.fade import FadeInEffect, FadeOutEffect
from mosaico.effects.pan import PanDownEffect, PanLeftEffect, PanRightEffect, PanUpEffect
from mosaico.effects.zoom import ZoomInEffect, ZoomOutEffect


VideoEffect = (
    ZoomInEffect
    | ZoomOutEffect
    | PanLeftEffect
    | PanRightEffect
    | PanUpEffect
    | PanDownEffect
    | FadeInEffect
    | FadeOutEffect
    | CrossFadeInEffect
    | CrossFadeOutEffect
)
"""A type representing any video effect."""

VideoEffectType = Literal[
    "zoom_in",
    "zoom_out",
    "pan_left",
    "pan_right",
    "pan_up",
    "pan_down",
    "fade_in",
    "fade_out",
    "crossfade_out",
    "crossfade_in",
]
"""A type representing the type of a video effect."""
