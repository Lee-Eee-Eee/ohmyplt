"""Numerical checks for the runnable residual-model example (NumPy only)."""
import importlib.util
import math
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "residual_model", ROOT / "examples" / "residual_model.py"
)
MODEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)


def zero_weights():
    return {
        "wi": np.zeros((96, 27)),
        "wh": np.zeros((96, 32)),
        "W1": np.zeros((32, 32)),
        "b1": np.zeros(32),
        "W2": np.zeros((8, 32)),
        "b2": np.zeros(8),
        "WR": np.zeros((8, 243)),
        "bR": np.zeros(8),
    }


class ResidualModelTests(unittest.TestCase):
    def test_nine_step_gru_matches_closed_form(self):
        # With n=1/2 and z=3/4 at every step, h_9=(1/2)(1-(3/4)^9).
        features = np.zeros((9, 27))
        features[:, 0] = 1
        weights = zero_weights()
        weights["wi"][32, 0] = math.log(3)
        weights["wi"][64, 0] = math.atanh(0.5)
        weights["W1"][0, 0] = 1
        weights["W2"][0, 0] = 1

        hidden = 0.5 * (1 - 0.75**9)
        expected = 0.5 * hidden * (1 + math.erf(hidden / math.sqrt(2)))
        fixed, correction, prediction = MODEL.predict(features, weights)
        np.testing.assert_array_equal(fixed, np.zeros(8))
        np.testing.assert_allclose(correction, [expected, 0, 0, 0, 0, 0, 0, 0],
                                   rtol=1e-13, atol=1e-14)
        np.testing.assert_array_equal(prediction, correction)

    def test_reset_gate_scales_only_recurrent_candidate_term(self):
        # The first seven zero inputs keep h=0. At step eight, r=3/4,
        # z=2/3, n=3/5, so h=1/5. At step nine (input 2), r=9/10,
        # z=4/5 and n=tanh(log(4)+9/100). This distinguishes r/z/n order
        # and PyTorch's reset placement from resetting the whole candidate.
        features = np.zeros((9, 27))
        features[-2:, 0] = [1, 2]
        weights = zero_weights()
        weights["wi"][0, 0] = math.log(3)
        weights["wi"][32, 0] = math.log(2)
        weights["wi"][64, 0] = math.atanh(0.6)
        weights["wh"][64, 0] = 0.5
        weights["W1"][0, 0] = 1
        weights["W2"][0, 0] = 1

        exponential = 16 * math.exp(0.18)
        candidate = (exponential - 1) / (exponential + 1)
        hidden = 0.16 + 0.2 * candidate
        expected = hidden * (1 + math.erf(hidden / math.sqrt(2))) / 2
        _, correction, _ = MODEL.predict(features, weights)
        np.testing.assert_allclose(correction, [expected, 0, 0, 0, 0, 0, 0, 0],
                                   rtol=1e-13, atol=1e-14)

    def test_exact_gelu_and_row_major_affine_residual(self):
        features = np.zeros((9, 27))
        features[0, 1], features[1, 0], features[8, 26] = 2, 3, 5
        weights = zero_weights()
        weights["b1"][:3] = [-math.sqrt(2), 0, math.sqrt(2)]
        coefficients = np.column_stack((np.arange(1, 9), np.ones(8), -np.ones(8)))
        weights["W2"][:, :3] = coefficients
        weights["b2"][:] = 0.25
        weights["WR"][:, [1, 27, 242]] = [0.5, -2, 3]
        weights["bR"][:] = np.arange(8) - 4

        # GELU(+-sqrt(2)) uses erf(+-1), with no tanh approximation.
        negative = -math.sqrt(2) * (1 - math.erf(1)) / 2
        positive = math.sqrt(2) * (1 + math.erf(1)) / 2
        expected_correction = np.arange(1, 9) * negative - positive + 0.25
        # vec(X)[1]=2, vec(X)[27]=3, vec(X)[242]=5: .5*2-2*3+3*5=10.
        expected_fixed = 10 + np.arange(8) - 4
        fixed, correction, prediction = MODEL.predict(features, weights)
        self.assertEqual(fixed.shape, (8,))
        self.assertEqual(correction.shape, (8,))
        self.assertEqual(prediction.shape, (8,))
        np.testing.assert_array_equal(fixed, expected_fixed)
        np.testing.assert_allclose(correction, expected_correction, rtol=1e-13, atol=1e-14)
        np.testing.assert_allclose(prediction, expected_fixed + expected_correction,
                                   rtol=1e-13, atol=1e-14)

    def test_feature_shape_is_checked(self):
        for shape in [(8, 27), (9, 26), (243,), (1, 9, 27)]:
            with self.subTest(shape=shape):
                with self.assertRaisesRegex(ValueError, "features.*shape"):
                    MODEL.predict(np.zeros(shape), zero_weights())

    def test_each_weight_shape_is_checked(self):
        for name, original in zero_weights().items():
            weights = zero_weights()
            weights[name] = np.zeros((original.shape[0] + 1, *original.shape[1:]))
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, name + ".*shape"):
                    MODEL.predict(np.zeros((9, 27)), weights)

    def test_nonfinite_features_are_rejected(self):
        for value in [np.nan, np.inf, -np.inf]:
            features = np.zeros((9, 27))
            features[4, 7] = value
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "features.*finite"):
                    MODEL.predict(features, zero_weights())

    def test_nonfinite_values_in_each_weight_are_rejected(self):
        for name in zero_weights():
            for value in [np.nan, np.inf, -np.inf]:
                weights = zero_weights()
                weights[name].flat[0] = value
                with self.subTest(name=name, value=value):
                    with self.assertRaisesRegex(ValueError, name + ".*finite"):
                        MODEL.predict(np.zeros((9, 27)), weights)

    def test_missing_weight_is_rejected(self):
        weights = zero_weights()
        del weights["bR"]
        with self.assertRaisesRegex(ValueError, "Missing weight arrays: bR"):
            MODEL.predict(np.zeros((9, 27)), weights)


if __name__ == "__main__":
    unittest.main()
