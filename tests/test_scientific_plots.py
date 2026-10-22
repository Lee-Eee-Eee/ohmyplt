"""Check the numerical definitions used by the scientific plotting examples."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "scientific_plots", ROOT / "examples" / "scientific_plots.py"
)
PLOTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLOTS)


class WeightedFitTests(unittest.TestCase):
    def test_weighted_fit_matches_hand_calculation(self):
        # Weights 1, 1, 1/4 give intercept 7/9 and slope 2/3. The
        # covariance is (X.T @ diag(1/sigma**2) @ X)^-1, without rescaling.
        x = np.array([0.0, 1.0, 2.0])
        y = np.array([1.0, 1.0, 3.0])
        sigma = np.array([1.0, 1.0, 2.0])
        coefficients, covariance, residual, chi_square = PLOTS.weighted_linear_fit(
            x, y, sigma
        )
        np.testing.assert_allclose(coefficients, [7 / 9, 2 / 3], atol=1e-13)
        np.testing.assert_allclose(
            covariance, [[8 / 9, -2 / 3], [-2 / 3, 1]], atol=1e-13
        )
        np.testing.assert_allclose(residual, [2 / 9, -4 / 9, 8 / 9], atol=1e-13)
        self.assertAlmostEqual(chi_square, 4 / 9, places=13)
        self.assertAlmostEqual(chi_square, float(np.sum((residual / sigma) ** 2)))

    def test_exact_line_with_unequal_uncertainties(self):
        x = np.array([-1.0, 0.0, 2.0, 4.0])
        sigma = np.array([0.1, 0.2, 0.5, 1.0])
        coefficients, covariance, residual, chi_square = PLOTS.weighted_linear_fit(
            x, 3 + 2 * x, sigma
        )
        np.testing.assert_allclose(coefficients, [3, 2], atol=1e-12)
        np.testing.assert_allclose(residual, np.zeros(4), atol=1e-12)
        self.assertLess(chi_square, 1e-20)
        # Known observation errors still imply nonzero coefficient uncertainty
        # when the observed points happen to lie exactly on a line.
        self.assertTrue(np.all(np.linalg.eigvalsh(covariance) > 0))

    def test_uncertainties_must_be_finite_and_positive(self):
        for value in [0, -1, np.nan, np.inf, -np.inf]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                PLOTS.weighted_linear_fit([0, 1, 2], [1, 2, 3], [1, value, 1])

    def test_fit_rejects_incompatible_shapes(self):
        cases = [
            ([0, 1], [1, 2, 3], [1, 1, 1]),
            ([0, 1, 2], [1, 2, 3], [1, 1]),
            ([[0], [1], [2]], [1, 2, 3], [1, 1, 1]),
            ([0, 1, 2], [1, 2, 3], [[1], [1], [1]]),
        ]
        for x, y, sigma in cases:
            with self.subTest(x=x, sigma=sigma), self.assertRaises(ValueError):
                PLOTS.weighted_linear_fit(x, y, sigma)


class SyntheticDataTests(unittest.TestCase):
    def test_spectrum_bin_geometry_and_poisson_error(self):
        data = PLOTS.spectrum_data()
        edges = data["edges"]
        counts = data["counts"]
        self.assertGreater(counts.size, 1)
        self.assertEqual(edges.shape, (counts.size + 1,))
        self.assertTrue(np.all(np.diff(edges) > 0))
        np.testing.assert_allclose(data["centers"], (edges[:-1] + edges[1:]) / 2)
        self.assertTrue(np.all(counts >= 0))
        np.testing.assert_array_equal(counts, np.floor(counts))
        np.testing.assert_allclose(data["count_sigma"], np.sqrt(counts))
        self.assertEqual(data["expected_counts"].shape, counts.shape)
        self.assertTrue(np.all(np.isfinite(data["expected_counts"])))
        self.assertTrue(np.all(data["expected_counts"] >= 0))

    def test_spatial_error_and_grid_geometry(self):
        data = PLOTS.heatmap_data()
        reference, prediction, error = (
            data["reference"], data["prediction"], data["error"]
        )
        self.assertEqual(reference.ndim, 2)
        self.assertEqual(reference.shape, prediction.shape)
        self.assertEqual(reference.shape, error.shape)
        self.assertEqual(len(data["x_edges"]), reference.shape[1] + 1)
        self.assertEqual(len(data["y_edges"]), reference.shape[0] + 1)
        self.assertTrue(np.all(np.diff(data["x_edges"]) > 0))
        self.assertTrue(np.all(np.diff(data["y_edges"]) > 0))
        np.testing.assert_allclose(error, prediction - reference, atol=1e-14)
        self.assertTrue(np.isfinite(reference).all())
        self.assertTrue(np.isfinite(prediction).all())

    def test_distribution_arrays_represent_individual_cases(self):
        data = PLOTS.distribution_data()
        cases, group_a, group_b = data["case_id"], data["group_a"], data["group_b"]
        self.assertEqual(cases.ndim, 1)
        self.assertGreater(len(cases), 1)
        self.assertEqual(group_a.shape, cases.shape)
        self.assertEqual(group_b.shape, cases.shape)
        self.assertEqual(len(np.unique(cases)), len(cases))
        self.assertTrue(np.isfinite(group_a).all())
        self.assertTrue(np.isfinite(group_b).all())

    def test_seeded_generators_are_reproducible(self):
        for name in ["spectrum_data", "heatmap_data", "distribution_data"]:
            generator = getattr(PLOTS, name)
            with self.subTest(generator=name):
                first, repeated, other = generator(seed=37), generator(seed=37), generator(seed=38)
                self.assertEqual(set(first), set(repeated))
                for key in first:
                    np.testing.assert_array_equal(first[key], repeated[key])
                self.assertTrue(any(not np.array_equal(first[key], other[key]) for key in first))


if __name__ == "__main__":
    unittest.main()
