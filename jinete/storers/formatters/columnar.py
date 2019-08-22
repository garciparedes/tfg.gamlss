import itertools as it
from typing import List

from .abc import StorerFormatter

from ...models import (
    Route,
    Vehicle,
    PlannedTrip,
)


class ColumnarStorerFormatter(StorerFormatter):

    def __init__(self, tab_character: str = '  ', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_character = tab_character

    def vehicle_to_str(self, vehicle: Vehicle) -> List[str]:
        return [
            f'ID: "{vehicle.uuid}"',
            f'Initial:  {vehicle.initial}',
            f'Final:    {vehicle.final}',
            f'Earliest: {vehicle.earliest:7.2f}',
            f'Latest:   {vehicle.latest:7.2f}',
            f'Capacity: {vehicle.capacity:7.2f}',
        ]

    def planned_trip_to_str(self, planned_trip: PlannedTrip) -> List[str]:
        return [
            self.tab_character.join((
                f'ID: {planned_trip.trip.identifier:5}',
                f'P: {planned_trip.origin} to {planned_trip.destination}',
                f'TW: {planned_trip.trip.earliest:6.01f} to {planned_trip.trip.latest:6.01f}',
                f'WT: {planned_trip.pickup_stop.waiting_time:5.01f}',
                f'NT: {planned_trip.pickup_stop.navigation_time:5.01f}',
                f'LT: {planned_trip.trip.load_time:4.01f}',
                f'TT: {planned_trip.duration:6.01f}',
                f'T: {planned_trip.pickup_time:6.01f} to {planned_trip.delivery_time:6.01f}',
                f'L: {planned_trip.capacity}',
                f'S: {self.objective.planned_trip_scoring(planned_trip):7.02f}'
            )),
        ]

    def route_to_str(self, route: Route) -> List[str]:
        rows = it.chain.from_iterable(self.planned_trip_to_str(planned_trip) for planned_trip in route.planned_trips)
        return [
            f'Vehicle: ',
            *(f'{self.tab_character}{row}' for row in self.vehicle_to_str(route.vehicle)),
            f'Planned Trips: "{sum(1 for _ in route.planned_trips)}"',
            *(f'{self.tab_character}{row}' for row in rows)
        ]

    def format(self) -> str:
        rows = it.chain.from_iterable(self.route_to_str(route) for route in self.planning.routes)
        return '\n'.join((
            f'Planning UUID: "{self.planning.uuid}"',
            f'Routes count: "{len(self.planning.routes)}"',
            f'Routes: ',
            '\n'.join(f'{self.tab_character}{row}' for row in rows),
            f'Computation time: "{self.result.computation_time:0.4f}" seconds',
            f'Coverage Rate: "{self.result.coverage_rate}"',
            f'Scoring: "{self.result.scoring}"',
            f'Direction: "{self.result.direction}"',
        ))
