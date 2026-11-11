"""Vehicle models shared by renderers."""

from dataclasses import dataclass, field

from ..core.constants import CYAN, RED


@dataclass
class VehicleStyle:
    primary: str = CYAN
    secondary: str = RED


@dataclass
class F1CarModel:
    position: tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0
    scale: float = 1.0
    style: VehicleStyle = field(default_factory=VehicleStyle)

    def transform(self, position=None, rotation=None, scale=None) -> "F1CarModel":
        return F1CarModel(position or self.position, self.rotation if rotation is None else rotation, self.scale if scale is None else scale, self.style)
