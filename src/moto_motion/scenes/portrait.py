"""Portrait Manim scene template with screen/world separation."""

import os

try:
    from manim import DOWN, FadeIn, FadeOut, Line, MovingCameraScene, Rectangle, VGroup, config
    Scene = MovingCameraScene
except ImportError:  # pragma: no cover
    Scene = object
    DOWN = FadeIn = FadeOut = Line = Rectangle = VGroup = None

from ..core.constants import PORTRAIT
from ..core.layout import DEFAULT_LAYOUT, SafeAreaLayout
from ..core.layout_allocator import LayoutAllocationReport, LayoutAllocator, LayoutRequest
from ..core.themes import DEFAULT_THEME, Theme


if Scene is not object:
    _preview = os.environ.get("MOTO_MOTION_PREVIEW", "0") == "1"
    config.pixel_width = PORTRAIT.preview_width if _preview else PORTRAIT.width
    config.pixel_height = PORTRAIT.preview_height if _preview else PORTRAIT.height
    config.frame_rate = PORTRAIT.preview_frame_rate if _preview else PORTRAIT.frame_rate
    config.frame_width = 9
    config.frame_height = 16


class PortraitScene(Scene):
    """1080x1920, 60 fps editorial canvas with fixed screen-space UI."""

    def __init__(self, *args, layout: SafeAreaLayout = DEFAULT_LAYOUT, debug_safe_area: bool = False, theme: Theme = DEFAULT_THEME, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = layout
        self.debug_safe_area = debug_safe_area
        self.theme = theme
        self.layout_allocator = LayoutAllocator(self._logical_canvas())
        self._layout_requests: list[LayoutRequest] = []
        self.world = VGroup() if VGroup is not None else None
        self.screen_ui = VGroup() if VGroup is not None else None

    def setup(self):
        config.background_color = self.theme.background
        self.camera.background_color = self.theme.background
        if self.world is not None:
            self.add(self.world)
        if self.screen_ui is not None:
            self.add(self.screen_ui)
        if self.debug_safe_area and self.screen_ui is not None:
            self.add_screen_ui(self.safe_area_overlay())

    def safe_area_overlay(self):
        if Rectangle is None:
            return None
        frame = self.layout.safe
        return Rectangle(width=frame.width, height=frame.height, stroke_color=self.theme.semantic.positive_delta, stroke_opacity=0.35, stroke_width=0.02, fill_opacity=0).move_to(((frame.left + frame.right) / 2, (frame.bottom + frame.top) / 2, 0))

    def add_world(self, *mobjects):
        if self.world is not None:
            self.world.add(*mobjects)
        return self

    def add_screen_ui(self, *mobjects):
        if self.screen_ui is not None:
            frame = self.camera.frame
            for mobject in mobjects:
                if mobject is None:
                    continue
                center = mobject.get_center()
                anchor = ((center[0] - self.layout.frame.left) / self.layout.frame.width, (center[1] - self.layout.frame.bottom) / self.layout.frame.height)
                # A screen-space object needs to counteract both parts of a
                # moving camera transform. Re-positioning alone keeps its
                # anchor fixed but makes the object visibly grow and shrink
                # whenever the camera changes zoom. Store its authored width
                # in the canonical portrait frame and derive the exact world
                # width each frame; this is absolute rather than incremental,
                # so it cannot accumulate floating-point scale drift.
                authored_width = mobject.width
                authored_frame_width = self.layout.frame.width

                def keep_in_screen_space(item, dt, anchor=anchor, authored_width=authored_width, authored_frame_width=authored_frame_width):
                    current_frame = self.camera.frame
                    current_center = current_frame.get_center()
                    if authored_width > 1e-9:
                        item.set(width=authored_width * current_frame.width / authored_frame_width)
                    item.move_to((current_center[0] + (anchor[0] - 0.5) * current_frame.width, current_center[1] + (anchor[1] - 0.5) * current_frame.height, 0))

                mobject.add_updater(keep_in_screen_space)
                # Snap before the first animated frame.  Without this, a UI
                # item created after a camera move visibly jumps to its fixed
                # screen anchor when its updater first runs.
                keep_in_screen_space(mobject, 0.0)
            self.screen_ui.add(*mobjects)
        return self

    @staticmethod
    def screen_fade_in(mobject, **kwargs):
        """Fade fixed screen UI without competing with its position updater."""
        return FadeIn(mobject, **kwargs)

    @staticmethod
    def screen_fade_out(mobject, **kwargs):
        """Fade fixed screen UI without competing with its position updater."""
        return FadeOut(mobject, **kwargs)

    def caption(self, value: str, *, font_size: int = 32):
        from ..typography import TypographySystem
        system = TypographySystem(self.layout, self.theme)
        caption = system.manim_text(value, system.body_style(font_size))
        return caption.move_to((*self.layout.point((0.5, 0.08), safe=True), 0))

    def safe_point(self, normalized):
        return self.layout.point(normalized, safe=True)

    def _logical_canvas(self):
        from ..core.safe_area import LogicalCanvas
        return LogicalCanvas(PORTRAIT.width, PORTRAIT.height)

    def register_layout_request(self, request: LayoutRequest):
        """Register a semantic UI/world bounds contract for pre-export checks."""
        self._layout_requests.append(request)
        return request

    def resolve_layout_requests(self) -> LayoutAllocationReport:
        """Resolve registered elements; unresolved critical overlaps block export."""
        return self.layout_allocator.resolve(self._layout_requests)
