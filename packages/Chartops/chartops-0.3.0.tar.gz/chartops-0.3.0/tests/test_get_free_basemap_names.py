#!/usr/bin/env python
import unittest
from chartops import common


class TestGetFreeBasemapNames(unittest.TestCase):

    def test_returns_list_of_strings(self):
        names = common.get_free_basemap_names()
        self.assertIsInstance(names, list)
        self.assertTrue(
            all(isinstance(name, str) for name in names),
            "Not all basemap names are strings",
        )

    def test_non_empty_result(self):
        names = common.get_free_basemap_names()
        self.assertTrue(len(names) > 0, "Expected non-empty list of basemap names")

    def test_known_basemap_exists(self):
        expected = {"OpenStreetMap.Mapnik", "Esri.WorldImagery", "CartoDB.Positron"}
        actual = set(common.get_free_basemap_names())
        found = expected.intersection(actual)

        self.assertTrue(
            found, f"Expected at least one of {expected} in the returned basemap names"
        )
