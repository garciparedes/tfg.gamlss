from __future__ import annotations

import logging
from enum import (
    Enum,
)
from typing import (
    TYPE_CHECKING,
    Optional,
)
from .abc import (
    Model,
)

if TYPE_CHECKING:
    from uuid import (
        UUID,
    )
    from typing import (
        Dict,
        Any,
    )
    from .positions import (
        Position,
    )
    from .planned_trips import (
        PlannedTrip
    )
    from .routes import (
        Route,
    )
    from .vehicles import (
        Vehicle,
    )

logger = logging.getLogger(__name__)


class StopKind(Enum):
    PICKUP = 1
    DELIVERY = 2

    def __str__(self):
        return self.name


class StopCause(Model):
    planned_trip: PlannedTrip
    kind: StopKind
    stop: Stop

    def __init__(self, planned_trip: PlannedTrip, kind: StopKind, stop: Stop = None):
        self.planned_trip = planned_trip
        self.kind = kind
        self.stop = stop

    @property
    def trip(self):
        return self.planned_trip.trip

    @property
    def trip_uuid(self):
        return self.trip.uuid

    @property
    def position(self):
        return self.stop.position

    @property
    def earliest(self) -> float:
        return self.planned_trip.trip.earliest

    @property
    def down_time(self) -> float:
        return self.planned_trip.down_time

    @property
    def load_time(self) -> float:
        return self.planned_trip.trip.load_time

    def as_dict(self) -> Dict[str, Any]:
        return {
            'position': self.position,
            'trip_uuid': self.trip_uuid,
            'kind': self.kind
        }


class Stop(Model):
    route: Route
    position: Position

    def __init__(self, route: Route, position: Position, previous: Optional[Stop], with_caching: bool = True):

        self.route = route
        self.position = position
        self.causes = set()

        self.previous = previous

        self.with_caching = with_caching

        self._previous_time = None
        self._navigation_time = None
        self._waiting_time = None
        self._arrival_time = None
        self._earliest = None
        self._load_time = None
        self._latest = None

    def append_stop_cause(self, stop_cause: StopCause) -> None:
        stop_cause.stop = self
        self.causes.add(stop_cause)

    def as_dict(self) -> Dict[str, Any]:
        return {
            'vehicle_uuid': self.vehicle_uuid,
            'position': self.position,
        }

    @property
    def vehicle(self) -> Vehicle:
        return self.route.vehicle

    @property
    def vehicle_uuid(self) -> UUID:
        return self.vehicle.uuid

    @property
    def previous_time(self) -> float:
        if self.previous is None:
            return self.vehicle.earliest
        if self._previous_time is None:
            self._previous_time = self.previous.latest
        return self._previous_time

    @property
    def previous_position(self) -> Position:
        if self.previous is None:
            return self.vehicle.initial
        return self.previous.position

    @property
    def navigation_time(self):
        if self._navigation_time is None:
            self._navigation_time = self.previous_position.time_to(self.position, None)
        return self._navigation_time

    @property
    def waiting_time(self):
        if self._waiting_time is None:
            earliest = max((cause.earliest for cause in self.causes), default=0.0)
            self._waiting_time = max(self.arrival_time, earliest) - self.arrival_time
        return self._waiting_time

    @property
    def arrival_time(self):
        if self._arrival_time is None:
            before_earliest = self.previous_time
            before_earliest += max((cause.down_time for cause in self.causes), default=0.0)
            before_earliest += self.navigation_time
            self._arrival_time = before_earliest
        return self._arrival_time

    @property
    def earliest(self):
        if self._earliest is None:
            earliest = max((cause.earliest for cause in self.causes), default=0.0)
            self._earliest = max(self.arrival_time, earliest)
        return self._earliest

    @property
    def load_time(self) -> float:
        if self._load_time is None:
            self._load_time = max((cause.load_time for cause in self.causes), default=0.0)
        return self._load_time

    @property
    def latest(self) -> float:
        if self._latest is None:
            self._latest = self.earliest + self.load_time
        return self._latest

    @property
    def departure_time(self) -> float:
        return self.latest
