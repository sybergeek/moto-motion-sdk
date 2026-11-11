"""World-space environment model with explicit z-ordering."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from .geometry import Trajectory


class Layer(IntEnum):
    BACKGROUND = 0
    TRACK = 10
    RACING_LINE = 20
    VEHICLE = 30
    ANNOTATION = 40
    FOREGROUND = 50
    UI = 100


@dataclass
class Environment:
    track: Any | None = None
    vehicles: list[Any] = field(default_factory=list)
    racing_lines: list[Trajectory] = field(default_factory=list)
    apex_markers: list[tuple[float, float]] = field(default_factory=list)
    braking_zones: list[tuple[tuple[float, float], tuple[float, float]]] = field(default_factory=list)
    background: list[Any] = field(default_factory=list)
    foreground: list[Any] = field(default_factory=list)

    def add_vehicle(self, vehicle: Any) -> None:
        self.vehicles.append(vehicle)

    def add_racing_line(self, trajectory: Trajectory) -> None:
        self.racing_lines.append(trajectory)

    def ordered(self) -> list[tuple[Layer, Any]]:
        items: list[tuple[Layer, Any]] = [(Layer.BACKGROUND, item) for item in self.background]
        if self.track is not None:
            items.append((Layer.TRACK, self.track))
        items.extend((Layer.RACING_LINE, item) for item in self.racing_lines)
        items.extend((Layer.VEHICLE, item) for item in self.vehicles)
        items.extend((Layer.FOREGROUND, item) for item in self.foreground)
        return sorted(items, key=lambda item: item[0])
