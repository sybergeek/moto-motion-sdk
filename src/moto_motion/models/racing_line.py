"""Deterministic, illustrative racing-line time simulation.

This is intentionally a teaching model rather than vehicle telemetry.  It
constrains speed by lateral acceleration (v² / r) and longitudinal acceleration
limits, then compares whole-path elapsed time.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import atan2, cos, hypot, pi, sin, sqrt


Point = tuple[float, float]


def _distance(left: Point, right: Point) -> float:
    return hypot(right[0] - left[0], right[1] - left[1])


@dataclass(frozen=True)
class RacingLineRoute:
    name: str
    color: str
    points: tuple[Point, ...]
    curvature_radius: float

    @property
    def length(self) -> float:
        return sum(_distance(left, right) for left, right in zip(self.points, self.points[1:]))


@dataclass(frozen=True)
class RouteResult:
    route: RacingLineRoute
    speed_samples: tuple[float, ...]
    time_samples: tuple[float, ...]
    distance_samples: tuple[float, ...]
    corner_speed_limit: float

    @property
    def elapsed_seconds(self) -> float:
        return self.time_samples[-1]

    @property
    def corner_exit_speed(self) -> float:
        """Speed at the end of the turn, before the following straight.

        The final sample is intentionally not used here: the tighter line has
        more straight remaining and can regain speed later.  This is the
        meaningful value for the illustrated exit-speed comparison.
        """
        apex_exit = (self.route.curvature_radius, 0.0)
        index = min(
            range(len(self.route.points)),
            key=lambda candidate: _distance(self.route.points[candidate], apex_exit),
        )
        return self.speed_samples[index]

    def pose_at(self, time_seconds: float) -> tuple[Point, float]:
        time_seconds = min(max(0.0, time_seconds), self.elapsed_seconds)
        for index in range(1, len(self.time_samples)):
            if self.time_samples[index] >= time_seconds:
                before, after = self.time_samples[index - 1], self.time_samples[index]
                fraction = 0.0 if after == before else (time_seconds - before) / (after - before)
                start, end = self.route.points[index - 1], self.route.points[index]
                point = (start[0] + (end[0] - start[0]) * fraction, start[1] + (end[1] - start[1]) * fraction)
                return point, atan2(end[1] - start[1], end[0] - start[0])
        end, previous = self.route.points[-1], self.route.points[-2]
        return end, atan2(end[1] - previous[1], end[0] - previous[0])


@dataclass(frozen=True)
class RacingLineSimulation:
    """Two routes sharing a start; red travels farther but wins on elapsed time."""

    lateral_acceleration_limit: float = 8.0
    # Deliberately modest illustrative acceleration makes the exit-speed
    # advantage persist onto the next straight instead of disappearing at the
    # finish marker.
    acceleration_limit: float = 1.0
    braking_limit: float = 6.0
    entry_speed: float = 5.5
    terminal_speed_limit: float = 6.4
    blue: RouteResult | None = None
    red: RouteResult | None = None

    @classmethod
    def build(cls) -> "RacingLineSimulation":
        base = cls()
        blue_route = RacingLineRoute("BLUE · shorter inside", "#2E8BFF", _route_points(radius=1.55), 1.55)
        red_route = RacingLineRoute("RED · wider exit line", "#F04444", _route_points(radius=2.55), 2.55)
        blue = _solve(base, blue_route)
        red = _solve(base, red_route)
        if red.route.length <= blue.route.length:
            raise AssertionError("wide route must cover more distance")
        if red.elapsed_seconds >= blue.elapsed_seconds:
            raise AssertionError("configured illustrative model must demonstrate the stated comparison")
        return cls(**{**asdict(base), "blue": blue, "red": red})

    def report(self) -> dict[str, object]:
        assert self.blue and self.red
        return {
            "schema": "moto-motion.racing-line-simulation.v1",
            "status": "illustrative simulation; not rider telemetry",
            "equation": "lateral_acceleration = speed^2 / turn_radius",
            "assumptions": {
                "lateral_acceleration_limit": self.lateral_acceleration_limit,
                "acceleration_limit": self.acceleration_limit,
                "braking_limit": self.braking_limit,
                "entry_speed": self.entry_speed,
                "terminal_speed_limit": self.terminal_speed_limit,
            },
            "blue": _route_report(self.blue),
            "red": _route_report(self.red),
            "comparison": {
                "red_extra_distance": self.red.route.length - self.blue.route.length,
                "red_time_advantage_seconds": self.blue.elapsed_seconds - self.red.elapsed_seconds,
                "winner": "red",
            },
        }


def _route_points(radius: float, *, steps: int = 90) -> tuple[Point, ...]:
    """Common start, gentle setup, quarter-circle apex, then exit straight."""
    # Keep the complete teaching diagram inside the 9:16 portrait safe frame.
    start = (-3.6, -2.0)
    setup = (0.0, -radius)
    points: list[Point] = []
    for index in range(24):
        t = index / 23
        # smooth lateral set-up from the shared start to the arc entry
        ease = t * t * (3 - 2 * t)
        points.append((start[0] + (setup[0] - start[0]) * t, start[1] + (setup[1] - start[1]) * ease))
    for index in range(1, steps + 1):
        theta = -pi / 2 + (pi / 2) * index / steps
        points.append((radius * cos(theta), radius * sin(theta)))
    # The arc leaves pointing upward, so the following straight must continue
    # upward as well.  Keeping it tangent avoids manufacturing an impossible
    # ninety-degree kink (and a fake zero-speed "exit").
    exit_start = (radius, 0.0)
    for index in range(1, 38):
        t = index / 37
        points.append((exit_start[0], exit_start[1] + 5.2 * t))
    return tuple(points)


def _solve(simulation: RacingLineSimulation, route: RacingLineRoute) -> RouteResult:
    points = route.points
    distances = [0.0]
    for left, right in zip(points, points[1:]):
        distances.append(distances[-1] + _distance(left, right))
    curvatures = [0.0] * len(points)
    for index in range(1, len(points) - 1):
        a, b, c = points[index - 1], points[index], points[index + 1]
        ab, bc, ac = _distance(a, b), _distance(b, c), _distance(a, c)
        area_twice = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        curvatures[index] = 0.0 if area_twice < 1e-9 else 2 * area_twice / max(1e-9, ab * bc * ac)
    caps = [simulation.terminal_speed_limit if curvature < 1e-6 else min(simulation.terminal_speed_limit, sqrt(simulation.lateral_acceleration_limit / curvature)) for curvature in curvatures]
    speeds = caps[:]
    speeds[0] = min(speeds[0], simulation.entry_speed)
    for index in range(1, len(speeds)):
        segment = distances[index] - distances[index - 1]
        speeds[index] = min(speeds[index], sqrt(speeds[index - 1] ** 2 + 2 * simulation.acceleration_limit * segment))
    for index in range(len(speeds) - 2, -1, -1):
        segment = distances[index + 1] - distances[index]
        speeds[index] = min(speeds[index], sqrt(speeds[index + 1] ** 2 + 2 * simulation.braking_limit * segment))
    times = [0.0]
    for index in range(1, len(points)):
        segment = distances[index] - distances[index - 1]
        times.append(times[-1] + segment / max(0.05, (speeds[index - 1] + speeds[index]) / 2))
    return RouteResult(route, tuple(speeds), tuple(times), tuple(distances), sqrt(simulation.lateral_acceleration_limit * route.curvature_radius))


def _route_report(result: RouteResult) -> dict[str, float | str]:
    return {
        "path_length": result.route.length,
        "turn_radius": result.route.curvature_radius,
        "corner_speed_limit": result.corner_speed_limit,
        "corner_exit_speed": result.corner_exit_speed,
        "elapsed_seconds": result.elapsed_seconds,
    }
