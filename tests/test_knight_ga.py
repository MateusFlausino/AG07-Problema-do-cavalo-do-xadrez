import random
import unittest

from knight_ga import (
    ALL_SQUARES,
    TOTAL_SQUARES,
    apply_mutation,
    evaluate_route,
    ordered_crossover,
    run_genetic_algorithm,
    warnsdorff_route,
)


class KnightGATest(unittest.TestCase):
    def assert_valid_permutation(self, route):
        self.assertEqual(len(route), TOTAL_SQUARES)
        self.assertEqual(set(route), set(ALL_SQUARES))

    def test_ordered_crossover_preserves_permutation(self):
        rng = random.Random(10)
        parent_a = list(ALL_SQUARES)
        parent_b = list(reversed(ALL_SQUARES))
        child = ordered_crossover(parent_a, parent_b, rng)
        self.assert_valid_permutation(child)

    def test_mutations_preserve_permutation(self):
        rng = random.Random(20)
        route = list(ALL_SQUARES)
        for operator in ["swap", "insert", "inversion", "shuffle", "mixed"]:
            with self.subTest(operator=operator):
                mutated = apply_mutation(route, operator, rng)
                self.assert_valid_permutation(mutated)

    def test_warnsdorff_route_respects_no_repetition(self):
        rng = random.Random(30)
        route = warnsdorff_route(rng)
        self.assert_valid_permutation(route)
        self.assertGreaterEqual(evaluate_route(route).valid_moves, 50)

    def test_ga_emits_progress_payload(self):
        payload = next(
            run_genetic_algorithm(
                config=__import__("knight_ga").GAConfig(
                    population_size=30,
                    generations=2,
                    seed=42,
                    report_every=1,
                )
            )
        )
        self.assertIn("route", payload)
        self.assertEqual(len(payload["route"]), TOTAL_SQUARES)


if __name__ == "__main__":
    unittest.main()
