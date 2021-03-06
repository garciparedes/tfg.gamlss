import unittest
from typing import List

import jinete as jit

from tests.utils import (
    generate_vehicles,
    generate_trips,
    generate_one_vehicle,
    generate_one_position,
)


class TestOneShiftLocalSearchStrategy(unittest.TestCase):
    vehicle: jit.Vehicle
    position: jit.Position
    stops: List[jit.Stop]

    def setUp(self) -> None:
        self.vehicle = generate_one_vehicle()
        self.position = generate_one_position()
        stop0 = jit.Stop(self.vehicle, self.position, None)

        stop1 = jit.Stop(self.vehicle, generate_one_position(), stop0)
        stop0.following = stop1

        stop2 = jit.Stop(self.vehicle, generate_one_position(), stop1)
        stop1.following = stop2

        stop3 = jit.Stop(self.vehicle, generate_one_position(), stop2)
        stop2.following = stop3

        stop4 = jit.Stop(self.vehicle, generate_one_position(), stop3)
        stop3.following = stop4

        stops = [stop0, stop1, stop2, stop3, stop4]
        self.stops = stops

        self.route = jit.Route(self.vehicle, self.stops)
        self.planning = jit.Planning({self.route})

        self.job = jit.Job(generate_trips(10), objective_cls=jit.DialARideObjective)
        self.fleet = jit.Fleet(generate_vehicles(10))
        self.algorithm = jit.NaiveAlgorithm(self.fleet, self.job)
        self.result = jit.Result(self.algorithm, self.planning, computation_time=float(0.0))

    def test_creation(self):
        strategy = jit.OneShiftLocalSearchStrategy(self.result)

        self.assertNotEqual(self.planning, strategy._planning)
        self.assertEqual(1, len(strategy._routes))
        self.assertEqual(tuple(self.route.positions), tuple(next(iter(strategy._routes)).positions))

    def test_improve(self):
        strategy = jit.OneShiftLocalSearchStrategy(self.result)
        result = strategy.improve()
        self.assertIsInstance(result, jit.Result)
        # TODO: Improve test validations.

    def test_one_shift(self):
        strategy = jit.OneShiftLocalSearchStrategy(self.result)
        stops = self.route.stops

        strategy._flip(self.route, stops[1], stops[2], stops[3])

        self.assertEqual(stops[0].position, self.stops[0].position)
        self.assertEqual(stops[1].position, self.stops[2].position)
        self.assertEqual(stops[2].position, self.stops[1].position)
        self.assertEqual(stops[3].position, self.stops[3].position)

        for first, second in zip(stops[:-1], stops[1:]):
            self.assertEqual(second.previous, first)


if __name__ == "__main__":
    unittest.main()
