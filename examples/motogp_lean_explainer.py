"""Moto Motion Reel #2: How MotoGP bikes lean so far without falling."""

from __future__ import annotations

from manim import *  # noqa: F403

from moto_motion.core.themes import RACING_HERITAGE
from moto_motion.effects import smoothstep
from moto_motion.models import LeanPose
from moto_motion.renderers.manim.lean import (
    MotoGPLeanRig,
    center_of_mass_overlay,
    contact_patch_closeup,
    force_vector_overlay,
    lean_angle_overlay,
)
from moto_motion.scenes.portrait import PortraitScene
from moto_motion.typography import TypographySystem


TARGET_COM_LEAN = 48.0
ALIGNED_POSE = LeanPose(bike_lean_degrees=TARGET_COM_LEAN)
HANGING_POSE = LeanPose(rider_offset=0.42, rider_relative_lean_degrees=10.0).solve_bike_lean_for_combined(TARGET_COM_LEAN)


class MotoGPLeanExplainer(PortraitScene):
    """Thirty-second portrait physics explainer with fixed right-turn direction."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, theme=RACING_HERITAGE, **kwargs)

    def construct(self):
        theme = self.theme
        # The series uses one F1-derived editorial hierarchy across disciplines.
        typography = TypographySystem(self.layout, theme, category="f1")
        road, corner_context = self._environment(theme)
        self.add_world(road, corner_context)

        # 0–4s: establish the right-hand lean around the road contact point.
        intro_rig = MotoGPLeanRig(HANGING_POSE, theme=theme, contact_position=(-0.55, -2.55), scale=1.48)
        intro_angle = lean_angle_overlay(
            intro_rig,
            label=f"{HANGING_POSE.bike_lean_degrees:.0f}° BIKE · ILLUSTRATIVE",
            label_position=(1.45, -3.10),
        )
        intro_com = center_of_mass_overlay(
            intro_rig,
            label_text="CENTER OF MASS",
            label_position=(-1.22, -1.02),
        )
        headline = self._headline(typography, ("HOW", "DOES", "IT", "NOT", "FALL?"), {"NOT": theme.semantic.focus}, 36)
        headline.move_to((*self.layout.point((0.5, 0.88)), 0))
        subtitle = self._label(typography, "RIGHT-HAND CORNER · FRONT VIEW", theme.secondary_text).move_to((*self.layout.point((0.5, 0.79)), 0))
        self.add_world(intro_rig.mobject, intro_angle, intro_com)
        self.add_screen_ui(headline, subtitle)
        self.play(FadeIn(road), FadeIn(corner_context), FadeIn(intro_rig.mobject), self.screen_fade_in(headline), self.screen_fade_in(subtitle), run_time=1.2)
        self.play(Create(intro_angle), FadeIn(intro_com), run_time=1.0)
        self.play(Indicate(intro_com[1], color=theme.semantic.positive_delta, scale_factor=1.25), run_time=0.8)
        self.wait(1.0)

        # 4–9s: gravity and tyre-generated road force share one moment balance.
        force_title = self._headline(typography, ("FORCES", "MEET", "AT", "THE", "PATCH"), {"PATCH": theme.semantic.focus}, 31)
        force_title.move_to((*self.layout.point((0.5, 0.88)), 0))
        force_note = self._label(typography, "ROAD FORCE POINTS UP + INWARD", theme.secondary_text).move_to((*self.layout.point((0.5, 0.79)), 0))
        forces = force_vector_overlay(intro_rig)
        self.add_world(forces)
        self.add_screen_ui(force_title, force_note)
        self.play(self.screen_fade_out(headline), self.screen_fade_out(subtitle), self.screen_fade_in(force_title), self.screen_fade_in(force_note), FadeOut(intro_angle), FadeOut(intro_com), run_time=0.8)
        self.play(*[Create(vector) for vector in forces[:3]], FadeIn(VGroup(*forces[3:])), run_time=0.65, rate_func=smoothstep)
        self.wait(3.55)

        # 9–14s: object-driven zoom into the actual source of lateral force.
        patch_title = self._headline(typography, ("GRIP", "STARTS", "HERE"), {"HERE": theme.semantic.acceleration}, 34)
        patch_title.move_to((*self.layout.point((0.5, 0.88)), 0))
        patch_note = self._label(typography, "TYRE CONTACT PATCH · LATERAL SHEAR", theme.secondary_text).move_to((*self.layout.point((0.5, 0.79)), 0))
        patch = contact_patch_closeup(theme).scale(1.05).move_to((0, -0.45, 0))
        patch_callout = self._label(typography, "BODY POSITION DOES NOT REMOVE TYRE FORCE", theme.text).move_to((0, -3.25, 0))
        self.add_world(patch, patch_callout)
        self.add_screen_ui(patch_title, patch_note)
        self.camera.frame.save_state()
        self.play(
            self.screen_fade_out(force_title), self.screen_fade_out(force_note), FadeOut(intro_rig.mobject), FadeOut(forces),
            self.camera.frame.animate.move_to((0, -0.65, 0)).scale(0.80),
            run_time=0.55,
            rate_func=smoothstep,
        )
        self.play(self.screen_fade_in(patch_title), self.screen_fade_in(patch_note), FadeIn(patch), run_time=0.45, rate_func=smoothstep)
        self.play(Create(patch[-1]), FadeIn(patch_callout), run_time=0.9)
        self.play(Indicate(patch[-2], color=theme.semantic.focus, scale_factor=1.12), run_time=0.8)
        self.wait(2.3)

        # 14–20s: same required combined lean, different motorcycle lean.
        compare_title = self._headline(typography, ("SAME", "CORNER.", "DIFFERENT", "BIKE", "LEAN."), {"DIFFERENT": theme.semantic.focus}, 29)
        compare_title.move_to((*self.layout.point((0.5, 0.89)), 0))
        compare_note = self._label(typography, "SAME SPEED + RADIUS · ILLUSTRATIVE GEOMETRY", theme.secondary_text).move_to((*self.layout.point((0.5, 0.80)), 0))
        left = MotoGPLeanRig(ALIGNED_POSE, theme=theme, contact_position=(-2.10, -2.25), scale=0.88)
        right = MotoGPLeanRig(HANGING_POSE, theme=theme, contact_position=(1.65, -2.25), scale=0.88)
        left_com = center_of_mass_overlay(left, compact=True, show_label=False)
        right_com = center_of_mass_overlay(right, compact=True, show_label=False)
        left_arc = lean_angle_overlay(left, show_label=False)
        right_arc = lean_angle_overlay(right, show_label=False)
        left_label = self._comparison_card(typography, "RIDER ALIGNED", f"BIKE LEAN {ALIGNED_POSE.bike_lean_degrees:.0f}°\nCENTER OF MASS {TARGET_COM_LEAN:.0f}°", theme.semantic.braking).move_to((-2.0, -4.55, 0))
        right_label = self._comparison_card(typography, "RIDER HANGS OFF", f"BIKE LEAN {HANGING_POSE.bike_lean_degrees:.0f}°\nCENTER OF MASS {TARGET_COM_LEAN:.0f}°", theme.semantic.positive_delta).move_to((2.0, -4.55, 0))
        divider = Line((0, -4.9, 0), (0, 2.3, 0), color=theme.border, stroke_width=1.4)
        comparison = VGroup(left.mobject, right.mobject, left_com, right_com, left_arc, right_arc, left_label, right_label, divider)
        self.add_world(comparison)
        self.add_screen_ui(compare_title, compare_note)
        self.play(
            self.screen_fade_out(patch_title), self.screen_fade_out(patch_note), FadeOut(patch), FadeOut(patch_callout),
            Restore(self.camera.frame),
            run_time=0.55,
            rate_func=smoothstep,
        )
        self.play(
            self.screen_fade_in(compare_title), self.screen_fade_in(compare_note),
            FadeIn(left.mobject), FadeIn(right.mobject), FadeIn(divider),
            run_time=0.45,
            rate_func=smoothstep,
        )
        self.play(Create(left_com), Create(right_com), Create(left_arc), Create(right_arc), FadeIn(left_label), FadeIn(right_label), run_time=1.0)
        self.play(Indicate(right.mobject, color=theme.semantic.positive_delta, scale_factor=1.03), run_time=1.0)
        self.wait(3.0)

        # 20–26s: return to the corner and stand the motorcycle up on exit.
        exit_title = self._headline(typography, ("STAND", "IT", "UP", "ON", "EXIT"), {"EXIT": theme.semantic.acceleration}, 32)
        exit_title.move_to((*self.layout.point((0.5, 0.88)), 0))
        exit_note = self._label(typography, "RIDER RECENTERS · CENTER OF MASS RISES", theme.secondary_text).move_to((*self.layout.point((0.5, 0.79)), 0))
        exit_group = self._exit_pose_group(HANGING_POSE, theme)
        self.add_world(exit_group)
        self.add_screen_ui(exit_title, exit_note)
        self.play(self.screen_fade_out(compare_title), self.screen_fade_out(compare_note), self.screen_fade_in(exit_title), self.screen_fade_in(exit_note), FadeOut(comparison), FadeIn(exit_group), run_time=1.0)

        def stand_up(group, alpha):
            progress = smoothstep(alpha)
            pose = LeanPose(
                bike_lean_degrees=HANGING_POSE.bike_lean_degrees + (5.0 - HANGING_POSE.bike_lean_degrees) * progress,
                rider_offset=HANGING_POSE.rider_offset * (1 - progress),
                rider_relative_lean_degrees=HANGING_POSE.rider_relative_lean_degrees * (1 - progress),
            )
            group.become(self._exit_pose_group(pose, theme, x_shift=0.70 * progress))

        self.play(UpdateFromAlphaFunc(exit_group, stand_up, rate_func=linear), run_time=4.0)
        self.wait(1.0)

        # 26–30s: restrained final payoff.
        final = VGroup(
            self._headline(typography, ("LEAN", "SMARTER."), {"SMARTER.": theme.semantic.positive_delta}, 42),
            self._headline(typography, ("NOT", "JUST", "FURTHER."), {"NOT": theme.semantic.focus}, 34),
        ).arrange(DOWN, buff=0.12).move_to((*self.layout.point((0.5, 0.70)), 0))
        final_note = self._label(typography, "CENTER OF MASS SETS THE ANGLE", theme.secondary_text).move_to((*self.layout.point((0.5, 0.58)), 0))
        streaks = VGroup(*[Line((-3.4, y, 0), (3.4, y, 0), color=theme.accent, stroke_width=1.2, stroke_opacity=0.16) for y in (-1.4, -0.8, -0.2, 0.4)])
        self.add_world(streaks)
        self.add_screen_ui(final, final_note)
        self.play(self.screen_fade_out(exit_title), self.screen_fade_out(exit_note), self.screen_fade_in(final), self.screen_fade_in(final_note), FadeOut(corner_context), FadeIn(streaks), run_time=1.0)
        self.play(LaggedStart(*[Create(line) for line in streaks], lag_ratio=0.12), run_time=1.0)
        self.wait(2.0)

    @staticmethod
    def _environment(theme):
        road = VGroup(
            Line((-5.2, -2.62, 0), (5.2, -2.62, 0), color="#0A1118", stroke_width=24),
            Line((-5.2, -2.55, 0), (5.2, -2.55, 0), color=theme.track, stroke_width=8),
        )
        grid = VGroup(*[Line((-4.5, y, 0), (4.5, y, 0), color=theme.border, stroke_width=1, stroke_opacity=0.12) for y in (-4.8, -2.4, 0.0, 2.4)])
        return road, grid

    @staticmethod
    def _headline(system, words, highlights, size):
        return system.composed_headline(words, highlights=highlights, size=size).set_max_width(6.45)

    @staticmethod
    def _label(system, value, color):
        plate_text = system.technical_label(value, size=14, color=color)
        plate = BackgroundRectangle(plate_text, fill_color="#162C39", fill_opacity=0.88, buff=0.11, stroke_width=0)
        return VGroup(plate, plate_text)

    @staticmethod
    def _comparison_card(system, title, value, color):
        title_mob = system.technical_label(title, size=13, color=color)
        value_mob = system.telemetry_value(value, size=11, color=color)
        return VGroup(title_mob, value_mob).arrange(DOWN, buff=0.06)

    @staticmethod
    def _exit_pose_group(pose, theme, *, x_shift=0.0):
        rig = MotoGPLeanRig(pose, theme=theme, contact_position=(-0.55 + x_shift, -2.55), scale=1.48)
        return VGroup(
            rig.mobject,
            center_of_mass_overlay(rig, show_label=False),
            lean_angle_overlay(
                rig,
                label=f"BIKE {pose.bike_lean_degrees:.0f}°",
                label_position=(1.55 + x_shift, -2.95),
            ),
        )


if __name__ == "__main__":
    MotoGPLeanExplainer().render()
