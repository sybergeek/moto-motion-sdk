"""Renderer-neutral MotoGP vehicle model.

The same trajectories, circuits, portrait scenes, and motion profiles can be
used for both categories; only the vehicle model and asset adapter change.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..core.constants import CYAN, GOLD


@dataclass
class MotoGPBikeStyle:
    primary: str = GOLD
    secondary: str = CYAN


@dataclass
class MotoGPBikeModel:
    position: tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    scale: float = 1.0
    style: MotoGPBikeStyle = field(default_factory=MotoGPBikeStyle)
