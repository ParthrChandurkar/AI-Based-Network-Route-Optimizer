import unittest

import networkx as nx

from routing import route_ai, route_traditional
from simulation import apply_random_failures, restore, snapshot


class RoutingFailureTests(unittest.TestCase):
    def test_all_failed_links_are_not_usable_routes(self):
        graph = nx.Graph()
        graph.add_edge(
            "A",
            "B",
            distance=5,
            failure_prob=0.9,
            risk_label="High",
            failed=True,
        )

        traditional = route_traditional(graph, "A", "B")
        ai_route = route_ai(graph, "A", "B")

        self.assertFalse(traditional["found"])
        self.assertFalse(ai_route["found"])
        self.assertEqual(traditional["path_str"], "No path found")
        self.assertEqual(ai_route["path_str"], "No path found")


class SimulationTests(unittest.TestCase):
    def test_random_failures_only_choose_active_links(self):
        graph = nx.Graph()
        graph.add_edge("A", "B", failed=True)
        graph.add_edge("B", "C", failed=False)
        graph.add_edge("C", "D", failed=False)

        failed_edges = apply_random_failures(graph, n_fail=5, seed=7)

        self.assertEqual(len(failed_edges), 2)
        self.assertEqual(
            {frozenset(edge) for edge in failed_edges},
            {frozenset(("B", "C")), frozenset(("C", "D"))},
        )
        self.assertTrue(graph["A"]["B"]["failed"])
        self.assertTrue(graph["B"]["C"]["failed"])
        self.assertTrue(graph["C"]["D"]["failed"])

    def test_restore_replaces_stale_edge_attributes(self):
        graph = nx.Graph()
        graph.add_edge("A", "B", latency=10, failed=False)
        saved = snapshot(graph)

        graph["A"]["B"]["latency"] = 250
        graph["A"]["B"]["failed"] = True
        graph["A"]["B"]["temporary_metric"] = 99

        restore(graph, saved)

        self.assertEqual(graph["A"]["B"]["latency"], 10)
        self.assertFalse(graph["A"]["B"]["failed"])
        self.assertNotIn("temporary_metric", graph["A"]["B"])


if __name__ == "__main__":
    unittest.main()
