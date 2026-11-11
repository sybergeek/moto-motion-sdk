"""Deterministic PNG renderer for educational RaceXplained carousels."""

from __future__ import annotations

import json
import subprocess
import zipfile
from pathlib import Path

from .models import KNOWN_ASSETS, CarouselLayout, CarouselManifest, CarouselSlide
from .quality import validate_rendered_carousel
from ..core.themes import THEMES, Theme, contrast_ratio
from ..typography import F1_PROFILE

MASTERCLASS_PANEL_ALPHA = 208
MASTERCLASS_PANEL_COLOR = (10, 22, 34)


class CarouselRenderer:
    def __init__(self, manifest: CarouselManifest, output_dir: str | Path = "output/carousels"):
        self.manifest = manifest
        self.output_dir = Path(output_dir) / manifest.carousel_id

    def render(self, *, slide_index: int | None = None) -> Path:
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as exc:
            raise RuntimeError("Carousel rendering requires Pillow") from exc
        self.output_dir.mkdir(parents=True, exist_ok=True)
        indices = [slide_index] if slide_index is not None else [slide.index for slide in self.manifest.slides]
        slides = {slide.index: slide for slide in self.manifest.slides}
        for index in indices:
            if index not in slides:
                raise ValueError(f"unknown slide index: {index}")
            image = self._render_slide(slides[index], Image, ImageDraw, ImageFont)
            image.save(self.output_dir / f"slide_{index:02d}.png", format="PNG", optimize=True)
        if slide_index is None:
            self._write_preview(Image)
            (self.output_dir / "manifest.json").write_text(json.dumps(self.manifest.to_dict(), indent=2) + "\n", encoding="utf-8")
            (self.output_dir / "quality_report.json").write_text(json.dumps(validate_rendered_carousel(self.manifest, self.output_dir), indent=2) + "\n", encoding="utf-8")
        return self.output_dir

    def export(self) -> Path:
        if not self.output_dir.exists():
            self.render()
        report_path = self.output_dir / "quality_report.json"
        if report_path.exists() and json.loads(report_path.read_text(encoding="utf-8")).get("status") == "ERROR":
            raise RuntimeError("carousel export blocked by unresolved layout or technical errors; inspect quality_report.json")
        archive = self.output_dir / "carousel.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(self.output_dir.glob("slide_*.png")):
                bundle.write(path, path.name)
            for name in ("manifest.json", "preview.png", "mobile_preview.png", "quality_report.json"):
                path = self.output_dir / name
                if path.exists():
                    bundle.write(path, path.name)
        return archive

    def _render_slide(self, slide: CarouselSlide, Image, ImageDraw, ImageFont):
        self._ImageFont = ImageFont
        width, height = self.manifest.dimensions
        theme: Theme = THEMES.get(slide.theme or self.manifest.theme, THEMES["editorial_ivory"])
        image = Image.new("RGB", (width, height), theme.background)
        draw = ImageDraw.Draw(image)
        scale = width / 1080
        safe = (int(width * .106), int(height * .094), int(width * .894), int(height * .88))
        display = self._font(ImageFont, 86 * scale, family=F1_PROFILE.display_family, bold=True)
        body = self._font(ImageFont, 37 * scale, family=F1_PROFILE.secondary_family, bold=False)
        cta = self._font(ImageFont, 54 * scale, family=F1_PROFILE.display_family, bold=True)
        mono = self._font(ImageFont, 26 * scale, family=F1_PROFILE.telemetry_family, bold=True)
        if not slide.visual.type.startswith(("masterclass_", "mercedes_")):
            self._draw_header(draw, slide, safe, mono, theme)
        if slide.visual.type.startswith(("masterclass_", "mercedes_")):
            self._render_masterclass(draw, image, slide, theme, display, body, mono, cta, scale)
            return image
        if slide.visual.type == "none":
            self._draw_centered_text(draw, slide.headline, display, theme.text, width // 2, int(height * .43), width * .78)
            if slide.body:
                self._draw_centered_text(draw, slide.body, cta, theme.accent, width // 2, int(height * .59), width * .78)
        elif slide.layout == CarouselLayout.HERO:
            if slide.visual.type == "existing_asset" and slide.visual.asset_id in KNOWN_ASSETS:
                self._draw_svg_asset(image, KNOWN_ASSETS[slide.visual.asset_id], (width // 2, int(height * .60)), int(width * .62))
            else:
                self._draw_car(draw, (width // 2, int(height * .60)), scale, theme.accent)
        elif slide.layout == CarouselLayout.COMPARISON:
            self._draw_comparison(draw, width, int(height * .57), scale, theme)
        elif slide.layout in (CarouselLayout.TECHNICAL_DIAGRAM, CarouselLayout.FULL_BLEED):
            self._draw_airflow(draw, width, int(height * .56), scale, theme)
        elif slide.layout == CarouselLayout.TIMELINE:
            self._draw_timeline(draw, width, int(height * .58), scale, theme)
        elif slide.layout == CarouselLayout.DATA:
            self._draw_bars(draw, width, int(height * .58), scale, theme)
        elif slide.layout == CarouselLayout.MYTH_FACT:
            self._draw_myth_fact(draw, width, int(height * .58), scale, theme)
        elif slide.layout == CarouselLayout.CONCLUSION:
            self._draw_takeaway(draw, width, int(height * .57), scale, theme)
        if slide.visual.type != "none":
            self._draw_wrapped(draw, slide.headline, display, theme.text, (safe[0], int(height * .16), safe[2], int(height * .40)), max_lines=3)
            if slide.body:
                self._draw_wrapped(draw, slide.body, body, theme.secondary_text, (safe[0], int(height * .40), safe[2], int(height * .52)), max_lines=5)
        footer = slide.footer or "RACEXPLAINED · RACING, EXPLAINED"
        draw.text((safe[0], int(height * .94)), footer.upper(), font=mono, fill=theme.secondary_text)
        return image

    def _render_masterclass(self, draw, image, slide, theme, display, body, mono, cta, scale):
        """Render the flagship editorial package with slide-specific compositions."""
        width, height = self.manifest.dimensions
        kind = slide.visual.type
        asset = KNOWN_ASSETS.get(slide.visual.asset_id or "")
        if not kind.startswith("mercedes_"):
            draw.rectangle((0, 0, width, int(height * .075)), fill=theme.background)
            draw.text((int(width*.106), int(height*.042)), "RACEXPLAINED  ·  THE STORIES", font=mono, fill=theme.secondary_text, anchor="lm")
            draw.text((int(width*.894), int(height*.042)), f"{slide.index:02d}", font=mono, fill=theme.secondary_text, anchor="rm")
        if kind == "masterclass_cover": self._draw_cover(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "masterclass_progression": self._draw_progression(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "masterclass_pitlane": self._draw_pitlane(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "masterclass_rain": self._draw_rain(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "masterclass_three_years": self._draw_three_years(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "masterclass_conclusion": self._draw_masterclass_conclusion(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "mercedes_cover": self._draw_mercedes_cover(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "mercedes_clinch": self._draw_mercedes_clinch(draw, image, theme, display, body, mono, scale, asset)
        elif kind == "mercedes_rankings": self._draw_mercedes_rankings(draw, image, theme, display, body, mono, scale)
        elif kind == "mercedes_wolff": self._draw_mercedes_wolff(draw, image, theme, display, body, mono, scale)
        elif kind == "mercedes_dynasty": self._draw_mercedes_dynasty(draw, image, theme, display, body, mono, scale)
        elif kind == "mercedes_comeback": self._draw_mercedes_comeback(draw, image, theme, display, body, mono, scale)
        elif kind == "mercedes_conclusion": self._draw_mercedes_conclusion(draw, image, theme, display, body, mono, scale, asset)

    def _mercedes_header(self, draw, theme, mono, index):
        width, height = self.manifest.dimensions
        draw.text((int(width*.106), int(height*.045)), "RACEXPLAINED  ·  THE STORIES", font=mono, fill=theme.secondary_text, anchor="lm")
        draw.text((int(width*.894), int(height*.045)), f"{index:02d}", font=mono, fill=theme.secondary_text, anchor="rm")

    def _draw_mercedes_cover(self, draw, image, theme, display, body, mono, scale, asset):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 1)
        photo = KNOWN_ASSETS["mercedes_driver_pair"]
        self._draw_photo_fill(image, photo, (0, int(height*.40), width, height), darkness=.08, centering=(.50, .18))
        draw.rectangle((0, int(height*.09), width, int(height*.40)), fill="#101820")
        hook = self._font(self._ImageFont, 62*scale, family=F1_PROFILE.display_family, bold=True)
        self._draw_wrapped(draw, "MERCEDES JUST MADE F1 HISTORY. AGAIN.", hook, "#F1EFE9", (int(width*.106), int(height*.14), int(width*.86), int(height*.35)), max_lines=3)
        stat = self._font(self._ImageFont, 260*scale, family=F1_PROFILE.telemetry_family, bold=True)
        draw.text((int(width*.106), int(height*.50)), "9", font=stat, fill=theme.accent)
        from PIL import Image, ImageDraw
        cover_overlay = image.convert("RGBA")
        cover_overlay.alpha_composite(
            Image.new("RGBA", (int(width*.58), int(height*.14)), (16, 24, 32, 205)),
            (int(width*.30), int(height*.75)),
        )
        image.paste(cover_overlay.convert("RGB"))
        draw = ImageDraw.Draw(image)
        draw.text((int(width*.35), int(height*.775)), "CONSTRUCTORS'\nCHAMPIONSHIPS", font=self._font(self._ImageFont, 42*scale, family=F1_PROFILE.display_family, bold=True), fill="#F1EFE9", spacing=5, stroke_width=1, stroke_fill="#101820")
        draw.text((int(width*.106), int(height*.93)), "ONE INCREDIBLE COMEBACK · 2026", font=mono, fill="#F1EFE9", stroke_width=1, stroke_fill="#101820")

    def _draw_mercedes_clinch(self, draw, image, theme, display, body, mono, scale, asset):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 2)
        self._draw_photo_fill(image, KNOWN_ASSETS["mercedes_driver_pair"], (0, int(height*.075), width, height), darkness=.12, centering=(.50, .43))
        from PIL import Image, ImageDraw
        overlay = image.convert("RGBA")
        top_panel = Image.new("RGBA", (width, int(height*.29)), (16, 24, 32, 186))
        left_panel = Image.new("RGBA", (int(width*.49), int(height*.43)), (16, 24, 32, 190))
        overlay.alpha_composite(top_panel, (0, int(height*.075)))
        overlay.alpha_composite(left_panel, (int(width*.05), int(height*.43)))
        image.paste(overlay.convert("RGB")); draw = ImageDraw.Draw(image)
        title = self._font(self._ImageFont, 62*scale, family=F1_PROFILE.display_family, bold=True)
        self._draw_wrapped(draw, "THE TITLE WAS SEALED IN BRAZIL.", title, "#F1EFE9", (int(width*.106), int(height*.12), int(width*.88), int(height*.25)), max_lines=2)
        draw.text((int(width*.106), int(height*.29)), "P4 + P5 = CHAMPIONS", font=mono, fill=theme.accent)
        self._draw_badge(draw, int(width*.10), int(height*.48), "P4", theme.accent, scale)
        self._draw_badge(draw, int(width*.10), int(height*.65), "P5", theme.accent, scale)
        draw.text((int(width*.29), int(height*.505)), "GEORGE RUSSELL", font=mono, fill="#F1EFE9")
        draw.text((int(width*.29), int(height*.675)), "KIMI ANTONELLI", font=mono, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.94)), "ENOUGH FOR AN UNASSAILABLE LEAD", font=mono, fill="#F1EFE9", stroke_width=1, stroke_fill="#101820")

    def _draw_badge(self, draw, x, y, text, color, scale):
        font = self._font(self._ImageFont, 48*scale, family=F1_PROFILE.telemetry_family, bold=True)
        draw.rounded_rectangle((x, y, x+int(150*scale), y+int(82*scale)), radius=int(14*scale), fill="#101820", outline=color, width=max(2, int(4*scale)))
        draw.text((x+int(75*scale), y+int(41*scale)), text, font=font, fill=color, anchor="mm")

    def _draw_mercedes_vehicle(self, draw, center_x, center_y, target_width, theme):
        """Horizontal editorial Mercedes silhouette for minimal SDK environments."""
        scale = target_width / 720
        body, dark, silver = "#087A86", "#101820", "#D9E0E8"
        x0, x1 = center_x - int(target_width*.5), center_x + int(target_width*.5)
        y = center_y
        wheel_r = max(16, int(34*scale))
        wheel_x = (x0 + int(target_width*.22), x1 - int(target_width*.20))
        wheel_y = y + int(15*scale)
        draw.polygon(((x0, y+int(10*scale)), (x0+int(target_width*.16), y-int(18*scale)),
                      (x0+int(target_width*.36), y-int(30*scale)), (x0+int(target_width*.48), y-int(65*scale)),
                      (x0+int(target_width*.68), y-int(62*scale)), (x1-int(target_width*.10), y-int(22*scale)),
                      (x1, y+int(10*scale)), (x1-int(target_width*.10), y+int(20*scale)),
                      (x0+int(target_width*.10), y+int(20*scale))), fill=body, outline=dark)
        draw.polygon(((x0+int(target_width*.27), y-int(25*scale)), (x0+int(target_width*.40), y-int(55*scale)),
                      (x0+int(target_width*.54), y-int(53*scale)), (x0+int(target_width*.60), y-int(22*scale))), fill=dark)
        draw.line((x0+int(target_width*.12), y+int(2*scale), x1-int(target_width*.10), y+int(2*scale)), fill=silver, width=max(2, int(4*scale)))
        draw.line((x0+int(target_width*.33), y-int(20*scale), x0+int(target_width*.47), y-int(20*scale)), fill="#32C7D5", width=max(2, int(8*scale)))
        for wx in wheel_x:
            draw.ellipse((wx-wheel_r, wheel_y-wheel_r, wx+wheel_r, wheel_y+wheel_r), fill=dark, outline=silver, width=max(2, int(3*scale)))
            draw.ellipse((wx-int(wheel_r*.35), wheel_y-int(wheel_r*.35), wx+int(wheel_r*.35), wheel_y+int(wheel_r*.35)), fill="#263746")
        draw.rectangle((x0-int(18*scale), y-int(3*scale), x0+int(36*scale), y+int(4*scale)), fill=dark)
        draw.rectangle((x1-int(16*scale), y-int(8*scale), x1+int(14*scale), y-int(2*scale)), fill=dark)

    def _draw_mercedes_rankings(self, draw, image, theme, display, body, mono, scale):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 3)
        title = self._font(self._ImageFont, 66*scale, family=F1_PROFILE.display_family, bold=True)
        self._draw_wrapped(draw, "ONLY TWO TEAMS HAVE MORE.", title, theme.text, (int(width*.106), int(height*.12), int(width*.88), int(height*.25)), max_lines=2)
        draw.text((int(width*.106), int(height*.28)), "ALL-TIME CONSTRUCTORS' TITLES", font=mono, fill=theme.secondary_text)
        # Use constructor-identifying colors, darkened slightly for reliable contrast
        # against the light editorial background.
        rows = (("FERRARI", 16, "#B31217"), ("McLAREN", 10, "#D26400"), ("MERCEDES", 9, theme.accent), ("WILLIAMS", 9, "#2457A6"))
        y0 = int(height*.39); row_h = int(height*.115); max_bar = int(width*.55)
        for i, (label, value, color) in enumerate(rows):
            y = y0 + i*row_h
            draw.text((int(width*.106), y), label, font=mono, fill=color)
            draw.rounded_rectangle((int(width*.106), y+int(35*scale), int(width*.106)+max_bar, y+int(76*scale)), radius=int(8*scale), fill="#D9D8D1")
            draw.rounded_rectangle((int(width*.106), y+int(35*scale), int(width*.106)+int(max_bar*value/16), y+int(76*scale)), radius=int(8*scale), fill=color)
            draw.text((int(width*.82), y+int(55*scale)), str(value), font=self._font(self._ImageFont, 48*scale, family=F1_PROFILE.telemetry_family, bold=True), fill=color, anchor="mm")
        self._draw_trophy(draw, int(width*.14), int(height*.91), theme.accent, scale*.55)
        draw.text((int(width*.18), int(height*.91)), "MERCEDES = WILLIAMS · JOINT THIRD", font=mono, fill=theme.accent)

    def _draw_mercedes_wolff(self, draw, image, theme, display, body, mono, scale):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 4)
        self._draw_photo_fill(image, KNOWN_ASSETS["mercedes_podium_celebration"], (0, int(height*.075), width, height), darkness=.16, centering=(.50, .44))
        from PIL import Image, ImageDraw
        overlay = image.convert("RGBA")
        top_panel = Image.new("RGBA", (width, int(height*.30)), (16, 24, 32, 186))
        left_panel = Image.new("RGBA", (int(width*.68), int(height*.57)), (16, 24, 32, 190))
        overlay.alpha_composite(top_panel, (0, int(height*.075)))
        overlay.alpha_composite(left_panel, (int(width*.05), int(height*.38)))
        image.paste(overlay.convert("RGB")); draw = ImageDraw.Draw(image)
        draw.text((int(width*.106), int(height*.13)), "TOTO WOLFF.", font=display, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.23)), "NINE TITLES.", font=display, fill=theme.accent)
        draw.text((int(width*.106), int(height*.34)), "THE TEAM PRINCIPAL RECORD", font=mono, fill="#C7D0D6")
        line_y = int(height*.50); x0 = int(width*.14); gap = int(width*.085)
        for i in range(9):
            x = x0 + i*gap
            self._draw_trophy(draw, x, line_y, theme.accent, scale*.45)
            draw.text((x, line_y+55), str(i+1), font=mono, fill="#F1EFE9", anchor="ma")
        draw.line((x0, line_y, x0+8*gap, line_y), fill=theme.accent, width=5)
        draw.text((int(width*.106), int(height*.66)), "9 = 9", font=self._font(self._ImageFont, 122*scale, family=F1_PROFILE.telemetry_family, bold=True), fill="#F1EFE9")
        small_mono = self._font(self._ImageFont, 20*scale, family=F1_PROFILE.telemetry_family, bold=True)
        draw.text((int(width*.106), int(height*.78)), "TOTO WOLFF  ·  9 TITLES", font=small_mono, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.83)), "SIR FRANK WILLIAMS  ·  9 TITLES", font=small_mono, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.875)), "WILLIAMS FOUNDER", font=small_mono, fill="#C7D0D6")
        draw.text((int(width*.106), int(height*.91)), "A LEADERSHIP MILESTONE — NOT A TEAM RECORD", font=mono, fill=theme.accent)

    def _draw_mercedes_dynasty(self, draw, image, theme, display, body, mono, scale):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 5)
        draw.text((int(width*.106), int(height*.13)), "REMEMBER THE", font=display, fill=theme.text)
        draw.text((int(width*.106), int(height*.21)), "EIGHT-YEAR STREAK?", font=display, fill=theme.accent)
        draw.text((int(width*.106), int(height*.33)), "A RECORD NO OTHER F1 TEAM HAS MATCHED.", font=mono, fill=theme.secondary_text)
        x0 = int(width*.13); y = int(height*.53); line_y = y + int(27*scale)
        for i, year in enumerate(range(2014, 2022)):
            x = x0 + i*int(width*.105)
            draw.ellipse((x-10, line_y-10, x+10, line_y+10), fill=theme.accent)
            draw.text((x, line_y-42), str(year), font=mono, fill=theme.text, anchor="ms")
        draw.line((x0, line_y, x0+7*int(width*.105), line_y), fill=theme.accent, width=5)
        draw.text((int(width*.106), int(height*.75)), "2014 → 2021", font=self._font(self._ImageFont, 80*scale, family=F1_PROFILE.telemetry_family, bold=True), fill=theme.text)
        draw.text((int(width*.106), int(height*.88)), "EIGHT CONSECUTIVE CONSTRUCTORS' TITLES", font=mono, fill=theme.accent)

    def _draw_mercedes_comeback(self, draw, image, theme, display, body, mono, scale):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 6)
        draw.text((int(width*.106), int(height*.13)), "FOUR YEARS", font=display, fill=theme.text)
        draw.text((int(width*.106), int(height*.21)), "WITHOUT A TITLE.", font=display, fill=theme.accent)
        draw.text((int(width*.106), int(height*.33)), "THEN 2026.", font=self._font(self._ImageFont, 72*scale, family=F1_PROFILE.display_family, bold=True), fill=theme.text)
        y = int(height*.50); x0 = int(width*.14); x1 = int(width*.86)
        draw.line((x0, y, x1, y), fill=theme.border, width=6)
        points = ((x0, "2021", "LAST TITLE"), (int(width*.50), "2022–25", "RED BULL +\nMcLAREN"), (x1, "2026", "12 WINS\nCHAMPIONS"))
        for x, year, label in points:
            draw.ellipse((x-22, y-22, x+22, y+22), fill=theme.accent if year == "2026" else theme.secondary_text)
            draw.text((x, y-65), year, font=mono, fill=theme.text, anchor="ms")
            self._draw_centered_text(draw, label, mono, theme.secondary_text, x, y+58, width*.22)
        draw.text((int(width*.106), int(height*.78)), "THE SILVER ARROWS RETURNED", font=self._font(self._ImageFont, 55*scale, family=F1_PROFILE.display_family, bold=True), fill=theme.text)
        draw.text((int(width*.106), int(height*.89)), "A COMEBACK BUILT FOR THE NEW REGULATIONS", font=mono, fill=theme.accent)

    def _draw_trophy(self, draw, x, y, color, scale):
        """Draw a native vector trophy; avoids emoji/font rendering differences."""
        bowl_w, bowl_h = int(26*scale), int(20*scale)
        stroke = max(2, int(3*scale))
        draw.polygon(((x-bowl_w, y-bowl_h), (x+bowl_w, y-bowl_h),
                      (x+int(bowl_w*.65), y+int(3*scale)),
                      (x-int(bowl_w*.65), y+int(3*scale))), fill=color)
        draw.arc((x-bowl_w-int(13*scale), y-int(16*scale), x-bowl_w+int(13*scale), y+int(12*scale)), 70, 285, fill=color, width=stroke)
        draw.arc((x+bowl_w-int(13*scale), y-int(16*scale), x+bowl_w+int(13*scale), y+int(12*scale)), 255, 110, fill=color, width=stroke)
        draw.rectangle((x-int(4*scale), y+int(3*scale), x+int(4*scale), y+int(16*scale)), fill=color)
        draw.rectangle((x-int(16*scale), y+int(16*scale), x+int(16*scale), y+int(21*scale)), fill=color)

    def _draw_mercedes_conclusion(self, draw, image, theme, display, body, mono, scale, asset):
        width, height = self.manifest.dimensions
        self._mercedes_header(draw, theme, mono, 7)
        self._draw_photo_fill(image, KNOWN_ASSETS["mercedes_podium_celebration"], (0, int(height*.38), width, height), darkness=.18, centering=(.50, .48))
        from PIL import Image, ImageDraw
        overlay = image.convert("RGBA")
        panel = Image.new("RGBA", (width, int(height*.32)), (7, 18, 29, 212))
        overlay.alpha_composite(panel, (0, int(height*.64)))
        image.paste(overlay.convert("RGB"))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, int(height*.10), width, int(height*.38)), fill="#101820")
        draw.text((int(width*.106), int(height*.15)), "THE SILVER ARROWS", font=self._font(self._ImageFont, 55*scale, family=F1_PROFILE.display_family, bold=True), fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.24)), "ARE BACK.", font=self._font(self._ImageFont, 84*scale, family=F1_PROFILE.display_family, bold=True), fill=theme.accent)
        lines = ("9 CONSTRUCTORS' TITLES", "8 CONSECUTIVE CHAMPIONSHIPS", "TOTO WOLFF = SIR FRANK WILLIAMS")
        for i, text in enumerate(lines):
            draw.text((int(width*.106), int(height*(.68 + i*.065))), text, font=mono, fill="#F1EFE9" if i < 2 else "#A5B2C2")
        draw.text((int(width*.106), int(height*.91)), "FOLLOW @RACEXPLAINED · F1'S BIGGEST STORIES", font=mono, fill="#F1EFE9", stroke_width=1, stroke_fill="#07121D")

    def _draw_cover(self, draw, image, theme, display, body, mono, scale, asset):
        width, height = self.manifest.dimensions
        self._draw_photo_fill(image, asset, (0, 0, width, height), darkness=.16, centering=(.58, .48))
        overlay = image.convert("RGBA")
        from PIL import Image, ImageDraw
        veil = Image.new("RGBA", (width, int(height*.58)), (7, 18, 29, 190))
        overlay.alpha_composite(veil, (0, 0)); image.paste(overlay.convert("RGB"))
        draw = ImageDraw.Draw(image)
        draw.text((int(width*.106), int(height*.12)), "RACEXPLAINED · THE STORIES", font=mono, fill="#F1EFE9")
        hook_font = self._font(self._ImageFont, 68*scale, family=F1_PROFILE.display_family, bold=True)
        self._draw_wrapped(draw, "IS MAX THE MASTER OF INTERLAGOS?", hook_font, "#F1EFE9", (int(width*.106), int(height*.18), int(width*.87), int(height*.34)), max_lines=2, stroke_width=1)
        stat_font = self._font(self._ImageFont, 104*scale, family=F1_PROFILE.telemetry_family, bold=True)
        draw.text((int(width*.106), int(height*.37)), "P21 → P2", font=stat_font, fill="#F1EFE9", stroke_width=1, stroke_fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.48)), "THREE YEARS. THREE PODIUMS.", font=body, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.535)), "SÃO PAULO · 2024–2026", font=mono, fill=theme.accent)
        draw.text((int(width*.106), int(height*.93)), "SWIPE TO SEE THE THREE-YEAR PATTERN →", font=mono, fill="#F1EFE9")

    def _draw_progression(self, draw, image, theme, display, body, mono, scale, asset):
        self._draw_comeback_slide(draw, image, theme, body, mono, scale, asset, "2026", "FROM P21 TO P2.", "+19 POSITIONS", "P21", "P2", "SÃO PAULO GP · 2026")

    def _draw_pitlane(self, draw, image, theme, display, body, mono, scale, asset):
        self._draw_comeback_slide(draw, image, theme, body, mono, scale, asset, "2025", "FROM PIT LANE TO P3.", "THE PODIUM", "PIT LANE", "P3", "SÃO PAULO GP · 2025", centering=(.52, .45))

    def _draw_rain(self, draw, image, theme, display, body, mono, scale, asset):
        self._draw_comeback_slide(draw, image, theme, body, mono, scale, asset, "2024", "FROM P17 TO P1.", "THE RAIN MASTERCLASS", "P17", "P1", "SÃO PAULO GP · 2024", centering=(.50, .43))

    def _draw_comeback_slide(self, draw, image, theme, body, mono, scale, asset, year, title, subtitle, start, finish, footer, *, centering=(.55, .52)):
        """Shared photo-led structure for the three historical comeback slides."""
        from PIL import Image, ImageDraw
        width, height = self.manifest.dimensions
        self._draw_photo_fill(image, asset, (0, int(height*.075), width, height), darkness=.10, centering=centering)
        overlay = image.convert("RGBA")
        panel = Image.new("RGBA", (int(width*.54), height-int(height*.075)), (*MASTERCLASS_PANEL_COLOR, MASTERCLASS_PANEL_ALPHA))
        overlay.alpha_composite(panel, (0, int(height*.075)))
        image.paste(overlay.convert("RGB"))
        draw = ImageDraw.Draw(image)
        left = int(width*.106)
        panel_max = int(width*.46)
        title_font = self._font(self._ImageFont, 61*scale, family=F1_PROFILE.display_family, bold=True)
        subtitle_font = self._font(self._ImageFont, 37*scale, family=F1_PROFILE.display_family, bold=True)
        result_font = self._font(self._ImageFont, 47*scale, family=F1_PROFILE.telemetry_family, bold=True)
        draw.text((left, int(height*.14)), year, font=mono, fill="#A5B2C2")
        self._draw_wrapped(draw, title, title_font, "#F1EFE9", (left, int(height*.19), panel_max, int(height*.34)), max_lines=2)
        self._draw_wrapped(draw, subtitle, subtitle_font, theme.accent, (left, int(height*.35), panel_max, int(height*.46)), max_lines=2)
        self._draw_result_strip(draw, left, int(height*.51), panel_max-left, start, finish, result_font, theme)
        draw.text((left, int(height*.80)), "THE RESULT", font=mono, fill="#A5B2C2")
        draw.text((left, int(height*.84)), footer, font=mono, fill="#F1EFE9")

    def _draw_result_strip(self, draw, x, y, width, start, finish, font, theme):
        label = self._font(self._ImageFont, 22, family=F1_PROFILE.telemetry_family, bold=True)
        card_x = x + int(width*.04)
        card_w = int(width*.72)
        card_center = card_x + card_w//2
        draw.text((card_x, y), "START", font=label, fill="#A5B2C2")
        draw.rounded_rectangle((card_x, y+28, card_x+card_w, y+92), radius=8, fill="#1C2D3E", outline="#A5B2C2", width=2)
        draw.text((card_center, y+60), start, font=font, fill="#F1EFE9", anchor="mm", stroke_width=1, stroke_fill="#F1EFE9")
        draw.text((card_center, y+119), "↓", font=font, fill="#F1EFE9", anchor="mm")
        draw.text((card_x, y+148), "FINISH", font=label, fill="#A5B2C2")
        draw.rounded_rectangle((card_x, y+176, card_x+card_w, y+240), radius=8, fill="#1C2D3E", outline="#A5B2C2", width=2)
        draw.text((card_center, y+208), finish, font=font, fill=theme.accent, anchor="mm", stroke_width=1, stroke_fill=theme.accent)

    def _draw_three_years(self, draw, image, theme, display, body, mono, scale, asset):
        width, height = self.manifest.dimensions
        draw.text((int(width*.106), int(height*.12)), "THREE YEARS.", font=display, fill=theme.text)
        draw.text((int(width*.106), int(height*.20)), "THREE PODIUMS.", font=display, fill=theme.accent)
        photos = (("2024", "P17 → P1", KNOWN_ASSETS["verstappen_2024_rain_action"], theme.semantic.braking), ("2025", "PIT LANE → P3", KNOWN_ASSETS["verstappen_2025_podium"], theme.accent), ("2026", "P21 → P2", KNOWN_ASSETS["verstappen_2026_race"], theme.semantic.focus))
        y0 = int(height*.34); row_h = int(height*.18)
        for index, (year, result, photo, color) in enumerate(photos):
            y = y0 + index*row_h
            self._draw_photo_fill(image, photo, (int(width*.55), y, int(width*.894), y+int(row_h*.78)), darkness=.05, centering=(.54, .48))
            draw.rectangle((int(width*.106), y, int(width*.55), y+int(row_h*.78)), fill="#101820")
            draw.text((int(width*.14), y+int(row_h*.12)), year, font=mono, fill="#A5B2C2")
            draw.text((int(width*.14), y+int(row_h*.36)), result, font=self._font(self._ImageFont, 42*scale, family=F1_PROFILE.telemetry_family, bold=True), fill=color)
        draw.text((int(width*.106), int(height*.91)), "THE SAME CIRCUIT. THREE DIFFERENT COMEBACKS.", font=mono, fill=theme.secondary_text)

    def _draw_masterclass_conclusion(self, draw, image, theme, display, body, mono, scale, asset):
        width, height = self.manifest.dimensions
        self._draw_photo_fill(image, asset, (0, 0, width, height), darkness=.10, centering=(.48, .48))
        from PIL import Image, ImageDraw
        overlay = image.convert("RGBA")
        veil = Image.new("RGBA", (width, height), (7, 18, 29, 145))
        overlay.alpha_composite(veil); image.paste(overlay.convert("RGB"))
        draw = ImageDraw.Draw(image)
        top_panel = Image.new("RGBA", (width, int(height*.38)), (7, 18, 29, 120))
        overlay = image.convert("RGBA")
        overlay.alpha_composite(top_panel, (0, int(height*.075))); image.paste(overlay.convert("RGB"))
        draw = ImageDraw.Draw(image)
        draw.text((int(width*.106), int(height*.16)), "INTERLAGOS.", font=display, fill="#F1EFE9", stroke_width=1, stroke_fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.27)), "VERSTAPPEN'S PLAYGROUND?", font=self._font(self._ImageFont, 48*scale, family=F1_PROFILE.display_family, bold=True), fill="#F1EFE9", stroke_width=1, stroke_fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.70)), "THREE REMARKABLE COMEBACK DRIVES.", font=body, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.76)), "WHICH DRIVE WAS THE GREATEST?", font=self._font(self._ImageFont, 32*scale, family=F1_PROFILE.telemetry_family, bold=True), fill=theme.semantic.focus)
        draw.text((int(width*.106), int(height*.86)), "2024  ·  2025  ·  2026", font=mono, fill="#F1EFE9")
        draw.text((int(width*.106), int(height*.94)), "RACEXPLAINED  ·  RACING, EXPLAINED", font=mono, fill="#F1EFE9")

    def _draw_photo_fill(self, image, asset_path, box, *, darkness=0.0, centering=(0.5, 0.5)):
        if asset_path is None or not asset_path.exists():
            raise FileNotFoundError(f"photo asset is missing: {asset_path}")
        from PIL import Image, ImageOps
        x0, y0, x1, y1 = box
        target = (max(1, x1-x0), max(1, y1-y0))
        with Image.open(asset_path) as source:
            photo = ImageOps.fit(source.convert("RGB"), target, method=Image.Resampling.LANCZOS, centering=centering)
        if darkness:
            veil = Image.new("RGBA", target, (0, 0, 0, int(255 * darkness)))
            photo = Image.alpha_composite(photo.convert("RGBA"), veil).convert("RGB")
        image.paste(photo, (x0, y0))

    def _draw_track_arcs(self, draw, width, height, color, y):
        draw.arc((int(width*.05), y-int(height*.20), int(width*.90), y+int(height*.16)), 185, 350, fill=color, width=4)
        draw.arc((int(width*.18), y-int(height*.12), int(width*.82), y+int(height*.20)), 190, 340, fill=color, width=3)

    def _draw_mini_car(self, draw, x, y, color, scale):
        length, height = int(150*scale), int(48*scale)
        draw.rounded_rectangle((x-length//2, y-height//2, x+length//2, y+height//2), radius=max(5,int(14*scale)), fill=color, outline="#101820", width=max(2,int(4*scale)))
        draw.polygon(((x+length//2,y-height//2),(x+length//2+int(20*scale),y),(x+length//2,y+height//2)), fill=color, outline="#101820")
        for offset in (-int(length*.30), int(length*.30)):
            draw.ellipse((x+offset-int(13*scale),y-int(16*scale),x+offset+int(13*scale),y+int(16*scale)), fill="#101820")

    def _font(self, ImageFont, size: float, *, family: str, bold: bool):
        candidates = []
        try:
            resolved = subprocess.run(["fc-match", "-f", "%{file}", family], check=True, capture_output=True, text=True).stdout.strip()
            if resolved:
                candidates.append(resolved)
        except (OSError, subprocess.SubprocessError):
            pass
        candidates.extend(("/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        for candidate in candidates:
            if Path(candidate).exists():
                return ImageFont.truetype(candidate, max(12, int(size)))
        return ImageFont.load_default()

    def _draw_header(self, draw, slide, safe, font, theme):
        if slide.kicker:
            draw.text((safe[0], int(safe[1] * .55)), slide.kicker.upper(), font=font, fill=theme.accent)
        draw.text((safe[2] - 55, int(safe[1] * .55)), f"{slide.index:02d}", font=font, fill=theme.secondary_text, anchor="ra")

    def _draw_wrapped(self, draw, text, font, fill, box, *, max_lines, stroke_width=0):
        words, lines, line = text.upper().split(), [], ""
        max_width = box[2] - box[0]
        for word in words:
            candidate = f"{line} {word}".strip()
            if line and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
                lines.append(line); line = word
            else: line = candidate
        if line: lines.append(line)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 8
        if len(lines) > max_lines:
            raise ValueError(f"text does not fit within {max_lines} lines: {text!r}")
        if any(draw.textbbox((0, 0), item, font=font)[2] > max_width for item in lines):
            raise ValueError(f"text exceeds its layout box: {text!r}")
        for offset, item in enumerate(lines):
            draw.text((box[0], box[1] + offset * line_height), item, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=fill)

    def _draw_centered_text(self, draw, text, font, fill, center_x, top_y, max_width):
        words, lines, line = text.upper().split(), [], ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if line and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
                lines.append(line); line = word
            else: line = candidate
        if line: lines.append(line)
        line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 10
        for offset, item in enumerate(lines):
            draw.text((center_x, top_y + offset * line_height), item, font=font, fill=fill, anchor="ma")

    def _draw_car(self, draw, center, scale, color):
        x, y = center; w, h = int(250 * scale), int(520 * scale)
        draw.rounded_rectangle((x-w//2, y-h//2, x+w//2, y+h//2), radius=int(40*scale), fill=color, outline="#18232E", width=max(2, int(8*scale)))
        draw.ellipse((x-int(50*scale), y-int(95*scale), x+int(50*scale), y+int(5*scale)), fill="#18232E")
        draw.line((x, y-h//2, x, y+h//2), fill="#F1EFE9", width=max(2, int(6*scale)))

    def _draw_svg_asset(self, image, asset_path: Path, center: tuple[int, int], target_width: int) -> None:
        from PIL import ImageDraw
        try:
            import cairosvg
            from io import BytesIO
            from PIL import Image
            rendered = cairosvg.svg2png(url=str(asset_path), output_width=target_width)
            asset = Image.open(BytesIO(rendered)).convert("RGBA")
            image.paste(asset, (center[0] - asset.width // 2, center[1] - asset.height // 2), asset)
        except ImportError:
            # Keep the asset reference in the manifest, but remain renderable
            # in minimal SDK environments without an SVG rasterizer. This is
            # an explicitly stylized editorial fallback, never a claim of an
            # authentic year-specific livery render.
            draw = ImageDraw.Draw(image)
            self._draw_editorial_car(draw, center, target_width / 540)

    def _draw_editorial_car(self, draw, center, scale):
        x, y = center
        navy, blue, red, white = "#101820", "#1E3A8A", "#E73E47", "#F1EFE9"
        body_w, body_h = int(155*scale), int(430*scale)
        draw.polygon(((x, y-body_h//2), (x+body_w//3, y-body_h//4), (x+body_w//2, y+body_h//3), (x+body_w//5, y+body_h//2), (x-body_w//5, y+body_h//2), (x-body_w//2, y+body_h//3), (x-body_w//3, y-body_h//4)), fill=blue, outline=navy)
        draw.polygon(((x, y-body_h//2), (x+body_w//8, y-body_h//4), (x, y+body_h//5), (x-body_w//8, y-body_h//4)), fill=red)
        draw.rounded_rectangle((x-int(25*scale), y-int(40*scale), x+int(25*scale), y+int(80*scale)), radius=int(18*scale), fill=navy)
        draw.ellipse((x-int(17*scale), y-int(10*scale), x+int(17*scale), y+int(34*scale)), fill="#263746")
        for yy in (y-int(145*scale), y+int(115*scale)):
            draw.rounded_rectangle((x-int(105*scale), yy-int(13*scale), x-int(58*scale), yy+int(13*scale)), radius=int(8*scale), fill=navy)
            draw.rounded_rectangle((x+int(58*scale), yy-int(13*scale), x+int(105*scale), yy+int(13*scale)), radius=int(8*scale), fill=navy)
        draw.line((x, y-body_h//2, x, y+body_h//2), fill=white, width=max(2, int(3*scale)))

    def _draw_airflow(self, draw, width, y, scale, theme):
        for row in range(5):
            yy = y - int(110*scale) + row * int(55*scale)
            draw.arc((int(width*.12), yy, int(width*.88), yy+int(120*scale)), 185, 355, fill=theme.accent if row < 3 else theme.secondary_accent, width=max(2, int(8*scale)))
        self._draw_car(draw, (width//2, y), scale*.72, theme.surface)
        draw.text((int(width*.13), y+int(170*scale)), "AIRFLOW", fill=theme.secondary_text, font=self._font(self._ImageFont, 24*scale, family=F1_PROFILE.telemetry_family, bold=True))

    def _draw_comparison(self, draw, width, y, scale, theme):
        for x, label, color in ((int(width*.30), "CLEAN AIR", theme.accent), (int(width*.70), "DIRTY AIR", theme.semantic.negative_delta)):
            self._draw_car(draw, (x, y), scale*.48, color); draw.text((x, y+int(205*scale)), label, fill=theme.text, anchor="ma", font=self._font(self._ImageFont, 25*scale, family=F1_PROFILE.telemetry_family, bold=True))
        draw.line((width//2, y-int(180*scale), width//2, y+int(210*scale)), fill=theme.border, width=max(2, int(3*scale)))

    def _draw_timeline(self, draw, width, y, scale, theme):
        x0, x1 = int(width*.18), int(width*.82); draw.line((x0,y,x1,y), fill=theme.border, width=max(3,int(7*scale)))
        for i, label in enumerate(("LEAD", "WAKE", "LESS DOWNFORCE", "HARDER TO FOLLOW")):
            x = x0 + (x1-x0)*i/3; draw.ellipse((x-14,y-14,x+14,y+14), fill=theme.accent if i<2 else theme.semantic.negative_delta); draw.text((x,y+45), label, fill=theme.text, anchor="ma", font=self._font(self._ImageFont, 22*scale, family=F1_PROFILE.telemetry_family, bold=True))

    def _draw_bars(self, draw, width, y, scale, theme):
        base = y + int(160*scale)
        for i, (label, value, color) in enumerate((("CLEAN", .82, theme.accent), ("DIRTY", .42, theme.semantic.negative_delta))):
            top = base - int(240*scale*value); x = int(width*(.30 + i*.28)); draw.rounded_rectangle((x,top,x+int(120*scale),base), radius=12, fill=color); draw.text((x+int(60*scale),base+30), label, fill=theme.text, anchor="ma", font=self._font(self._ImageFont, 24*scale, family=F1_PROFILE.telemetry_family, bold=True))

    def _draw_myth_fact(self, draw, width, y, scale, theme):
        draw.rounded_rectangle((int(width*.12), y-int(150*scale), int(width*.88), y+int(150*scale)), radius=24, outline=theme.border, width=4); draw.text((width//2,y-int(100*scale)), "MYTH", fill=theme.semantic.negative_delta, anchor="ma", font=self._font(self._ImageFont, 32*scale, family=F1_PROFILE.display_family, bold=True)); draw.text((width//2,y+int(45*scale)), "FACT", fill=theme.accent, anchor="ma", font=self._font(self._ImageFont, 32*scale, family=F1_PROFILE.display_family, bold=True))

    def _draw_takeaway(self, draw, width, y, scale, theme):
        draw.ellipse((width//2-int(180*scale), y-int(180*scale), width//2+int(180*scale), y+int(180*scale)), outline=theme.accent, width=max(4,int(12*scale))); draw.line((width//2-int(110*scale),y,width//2+int(110*scale),y),fill=theme.text,width=max(3,int(8*scale)))

    def _write_preview(self, Image):
        paths = [self.output_dir / f"slide_{slide.index:02d}.png" for slide in self.manifest.slides]
        thumb_w = 270; thumb_h = int(thumb_w * self.manifest.dimensions[1] / self.manifest.dimensions[0]); cols = min(3, len(paths)); rows = (len(paths)+cols-1)//cols
        preview = Image.new("RGB", (cols*thumb_w, rows*thumb_h), "#FFFFFF")
        for offset, path in enumerate(paths):
            with Image.open(path) as slide: preview.paste(slide.resize((thumb_w,thumb_h)), ((offset%cols)*thumb_w, (offset//cols)*thumb_h))
        preview.save(self.output_dir / "preview.png", format="PNG", optimize=True)
        with Image.open(paths[0]) as first:
            first.resize((540, 720), Image.Resampling.LANCZOS).save(self.output_dir / "mobile_preview.png", format="PNG", optimize=True)

