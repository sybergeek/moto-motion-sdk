from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..geometry import Trajectory


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def endpoint_speed_profile(start_slope: float = 1.0, end_slope: float = 1.0) -> Callable[[float], float]:
    """Return a monotonic cubic profile with explicit boundary velocities.

    ``smoothstep`` is appropriate when an object should stop at both ends. It
    is not appropriate for adjacent path clips because its zero endpoint
    derivatives create a visible stop/restart at every edit. The slopes here
    are normalized progress derivatives; ``1, 1`` is linear motion.
    """
    if start_slope < 0 or end_slope < 0:
        raise ValueError("endpoint slopes must be non-negative")
    if start_slope + end_slope > 3.0 + 1e-9:
        raise ValueError("endpoint slopes are too large for a monotonic cubic profile")

    def profile(value: float) -> float:
        t = max(0.0, min(1.0, value))
        t2 = t * t
        t3 = t2 * t
        return (t3 - 2 * t2 + t) * start_slope + (-2 * t3 + 3 * t2) + (t3 - t2) * end_slope

    return profile


def trajectory_speed_profile(
    trajectory: Trajectory,
    duration: float,
    *,
    start_speed: float,
    end_speed: float,
) -> Callable[[float], float]:
    """Build a path profile whose endpoint speeds are in world units/second."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    if trajectory.length <= 1e-9:
        raise ValueError("trajectory must have non-zero length")
    scale = duration / trajectory.length
    return endpoint_speed_profile(start_speed * scale, end_speed * scale)


@dataclass(frozen=True)
class VehicleMotion:
    trajectory: Trajectory
    duration: float = 6.0
    speed_profile: Callable[[float], float] | None = None
    follow_rotation: bool = True

    def state_at(self, elapsed: float) -> tuple[tuple[float, float], float]:
        normalized = max(0.0, min(1.0, elapsed / self.duration)) if self.duration else 1.0
        progress = self.speed_profile(normalized) if self.speed_profile else smoothstep(normalized)
        return self.trajectory.point_at_distance(progress), self.trajectory.heading(self.trajectory.distance_to_parameter(progress * self.trajectory.length))
