"""Resolution-independent safe-area demonstration scene."""

from __future__ import annotations

import os

from manim import *  # noqa: F403

from moto_motion.core.safe_area import INSTAGRAM_REELS_V1, LayoutClass, LayoutElement, LogicalCanvas, NormalizedRect, make_safe_area_overlay, validate_scene_layout
from moto_motion.renderers.manim.captions import RaceXplainedCaption


WIDTH = int(os.environ.get("MOTO_MOTION_DEMO_WIDTH", "1080"))
HEIGHT = int(os.environ.get("MOTO_MOTION_DEMO_HEIGHT", "1920"))
config.pixel_width = WIDTH
config.pixel_height = HEIGHT
config.frame_rate = 30


class LayoutSafeAreaDemo(Scene):
    def construct(self):
        canvas = LogicalCanvas(WIDTH, HEIGHT, INSTAGRAM_REELS_V1)
        bg = Rectangle(width=canvas.manim_frame_width, height=canvas.manim_frame_height, fill_color="#0A1019", fill_opacity=1, stroke_width=0)
        self.add(bg)

        # Full-bleed continuous geometry intentionally enters/exits the frame.
        track_points = [canvas.normalized_to_manim(p) for p in ((-.10, .67), (.22, .67), (.42, .55), (.58, .34), (.82, .28), (1.10, .28))]
        track = VMobject().set_points_as_corners([(*p, 0) for p in track_points]).set_stroke("#33495B", 1.9)
        racing_line = VMobject().set_points_as_corners([(*p, 0) for p in track_points]).set_stroke("#2E8BFF", .07)
        apex = canvas.normalized_to_manim((.58, .34))
        apex_marker = Circle(radius=.15, color="#F4C95D", stroke_width=3).move_to((*apex, 0))

        title_pos = canvas.normalized_to_manim((.5, .15))
        title = Text("RESOLUTION-INDEPENDENT LAYOUT", font="Barlow Condensed", weight="BOLD", font_size=32, color="#F4F7FA").move_to((*title_pos, 0))
        label_pos = canvas.normalized_to_manim((.58, .26))
        apex_label = Text("APEX", font="Avenir Next", font_size=20, color="#F4C95D").move_to((*label_pos, 0))
        caption = RaceXplainedCaption("The protected label stays safe while the track runs full-bleed.", highlight="safe", layout=canvas).mobject()

        bike = VGroup(
            Circle(radius=.14, color="#F04444", fill_color="#F04444", fill_opacity=1),
            Line((0, -.2, 0), (0, .2, 0), color="#F4F7FA", stroke_width=3),
        ).move_to((*canvas.normalized_to_manim((.22, .67)), 0))

        # Layout registration uses normalized bounds, including an intermediate
        # sample where the bike is at the apex.
        elements = [
            LayoutElement("title", LayoutClass.STRICT_SAFE, ((0, NormalizedRect(.20, .10, .60, .08)),)),
            LayoutElement("apex", LayoutClass.SAFE_ANCHOR, ((0, NormalizedRect(.50, .30, .16, .10)),), (("apex", (.58, .34)),)),
            LayoutElement("track", LayoutClass.FULL_BLEED, ((0, NormalizedRect(-.1, .2, 1.2, .6)),)),
        ]
        violations = validate_scene_layout(canvas, elements)
        if violations:
            raise RuntimeError(f"Demo layout should be clean: {violations}")

        self.add(track, racing_line, apex_marker, title, apex_label, caption, bike)
        if os.environ.get("MOTO_MOTION_DEBUG_LAYOUT") == "1":
            self.add(make_safe_area_overlay(canvas))
        self.play(bike.animate.move_to((*canvas.normalized_to_manim((.58, .34)), 0)), run_time=1.2, rate_func=smooth)
        self.wait(.5)
