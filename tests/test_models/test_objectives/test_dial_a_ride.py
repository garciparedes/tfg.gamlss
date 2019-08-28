import unittest

import jinete as jit


class TestDialARideObjective(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        surface = jit.GeometricSurface(jit.DistanceMetric.MANHATTAN)
        vehicle = jit.Vehicle(
            identifier='TEST',
            initial=surface.get_or_create_position([0, 0]),
        )
        fleet = jit.Fleet({vehicle})
        route = jit.Route(vehicle)

        trips = [
            jit.Trip(
                identifier='TEST_1',
                origin=surface.get_or_create_position([0, 0]),
                destination=surface.get_or_create_position([1, 1]),
                earliest=0.0,
                timeout=10.0,
            ), jit.Trip(
                identifier='TEST_1',
                origin=surface.get_or_create_position([1, 1]),
                destination=surface.get_or_create_position([10, 10]),
                earliest=0.0,
                timeout=20.0,
            ),
        ]
        job = jit.Job(set(trips), jit.DialARideObjective)

        cls.planned_trip = route.conjecture_trip(trips[0])
        cls.stop = route.stops[0]
        route.append_planned_trip(cls.planned_trip)
        route.append_planned_trip(route.conjecture_trip(trips[1]))

        cls.route = route
        cls.planning = jit.Planning({route})
        cls.result = jit.Result(fleet, job, jit.NaiveAlgorithm, cls.planning, 0.0)

    def test_creation(self):
        objective = jit.DialARideObjective()
        self.assertEqual(jit.OptimizationDirection.MINIMIZATION, objective.direction)
        self.assertEqual('Dial-a-Ride', objective.name)

    def test_result(self):
        objective = jit.DialARideObjective()

        self.assertEqual(
            20.0,
            objective.optimization_function(self.result),
        )

    def test_planning(self):
        objective = jit.DialARideObjective()

        self.assertEqual(
            20.0,
            objective.optimization_function(self.planning),
        )

    def test_route(self):
        objective = jit.DialARideObjective()

        self.assertEqual(
            20.0,
            objective.optimization_function(self.route),
        )

    def test_stop(self):
        objective = jit.DialARideObjective()

        self.assertEqual(
            2.0,
            objective.optimization_function(self.stop),
        )

    def test_planning_trip(self):
        objective = jit.DialARideObjective()

        self.assertEqual(
            2.0,
            objective.optimization_function(self.planned_trip),
        )

    def test_best(self):
        objective = jit.DialARideObjective()

        self.assertEqual(
            next(self.route.planned_trips),
            objective.best(*self.route.planned_trips),
        )


if __name__ == '__main__':
    unittest.main()