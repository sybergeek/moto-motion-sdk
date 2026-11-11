"""Motorsport Motion: reusable Formula 1 and MotoGP motion graphics."""

from .assets import f1_car_svg, write_f1_car_svg
from .camera import CameraRig
from .choreography import SceneDirector
from .core.layout import CameraTransform, SafeAreaLayout
from .core.themes import DEFAULT_THEME, THEMES, Theme, contrast_ratio
from .geometry import Trajectory, cubic_bezier
from .icons import MotorsportIcon, icon_svg
from .models import LeanPose, equilibrium_lean_degrees
from .transitions import TransitionDirector
from .creative.conversion import ConversionPlan, ConversionPlanner
from .carousel import CarouselLayout, CarouselManifest, CarouselRenderer, CarouselSlide, VisualSpec
from .core.layout_allocator import LayoutAllocation, LayoutAllocationReport, LayoutAllocator, LayoutRequest
from .typography import AnimatedCaption, F1_PROFILE, MOTOGP_PROFILE, Headline, HighlightedText, KineticHeadline, MaskedTextReveal, NumericDelta, Subheading, TechnicalLabel, TelemetryCounter, TelemetryValue, TypographyProfile, TypographySystem, WordHighlight

__version__ = "0.1.0"
__all__ = ["Trajectory", "cubic_bezier", "f1_car_svg", "write_f1_car_svg", "CameraRig", "CameraTransform", "SafeAreaLayout", "SceneDirector", "TransitionDirector", "TypographySystem", "TypographyProfile", "F1_PROFILE", "MOTOGP_PROFILE", "Headline", "Subheading", "TechnicalLabel", "TelemetryValue", "HighlightedText", "Theme", "THEMES", "DEFAULT_THEME", "contrast_ratio", "MotorsportIcon", "icon_svg", "KineticHeadline", "WordHighlight", "MaskedTextReveal", "TelemetryCounter", "NumericDelta", "AnimatedCaption", "LeanPose", "equilibrium_lean_degrees", "ConversionPlan", "ConversionPlanner", "CarouselLayout", "CarouselManifest", "CarouselRenderer", "CarouselSlide", "VisualSpec", "LayoutAllocation", "LayoutAllocationReport", "LayoutAllocator", "LayoutRequest"]
