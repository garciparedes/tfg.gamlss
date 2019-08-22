from __future__ import annotations
import logging
from abc import (
    ABC,
    abstractmethod)
from collections import defaultdict

from typing import (
    TYPE_CHECKING,
)

from uuid import (
    uuid4,
)

from .abc import (
    Model,
)
from .constants import (
    DistanceMetric,
)
from .positions import (
    GeometricPosition,
)

if TYPE_CHECKING:
    from typing import (
        Set,
        Any,
        Dict,
    )
    from uuid import (
        UUID,
    )
    from .positions import (
        Position,
    )

logger = logging.getLogger(__name__)


class Surface(Model, ABC):
    uuid: UUID

    def __init__(self, positions: Set[Position] = None, uuid: UUID = None, *args, **kwargs):
        if uuid is None:
            uuid = uuid4()
        if positions is None:
            positions = set()
        self.uuid = uuid
        self.positions = positions

    def get_or_create_position(self, *args, **kwargs) -> Position:
        position = self._build_position(*args, **kwargs)
        if not position in self.positions:
            self.positions.add(position)
        return position

    @abstractmethod
    def _build_position(self, *args, **kwargs):
        pass

    @abstractmethod
    def distance(self, position_a: Position, position_b: Position) -> float:
        pass

    @abstractmethod
    def time(self, position_a: Position, position_b: Position, now: float) -> float:
        pass

    def as_dict(self) -> Dict[str, Any]:
        positions_str = ', '.join(str(position) for position in self.positions)
        dict_values = {
            'positions': f'{{{positions_str}}}'
        }
        return dict_values


class GeometricSurface(Surface):
    positions: Set[GeometricPosition]
    cached_distance: Dict[Position, Dict[Position, float]]

    def __init__(self, metric: DistanceMetric, with_caching: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric = metric

        self.cached_distance = defaultdict(dict)
        self.with_caching = with_caching

    def _build_position(self, *args, **kwargs):
        return GeometricPosition(surface=self, *args, **kwargs)

    def is_cached(self, position_a: GeometricPosition, position_b: GeometricPosition) -> bool:
        return position_a in self.cached_distance and position_b in self.cached_distance[position_a]

    def distance(self, position_a: GeometricPosition, position_b: GeometricPosition) -> float:
        if self.with_caching and not self.is_cached(position_a, position_b):
            self.cached_distance[position_a][position_b] = self.metric(position_a, position_b)
        return self.cached_distance[position_a][position_b]

    def time(self, position_a: GeometricPosition, position_b: GeometricPosition, now: float) -> float:
        return self.distance(position_a, position_b)
