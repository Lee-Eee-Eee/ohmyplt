"""Run the initialized NumPy model represented by the network gallery figure.

    python examples/residual_model.py
    python examples/residual_model.py --weights output/network-demo.npz --out output/prediction.json

The archive supplies a nine-step history and initialized demonstration weights.
This example performs inference; it does not train or evaluate predictive accuracy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = ROOT / "assets/gallery/network-demo.npz"
SHAPES = {
    "wi": (96, 27),
    "wh": (96, 32),
    "W1": (32, 32),
    "b1": (32,),
    "W2": (8, 32),
    "b2": (8,),
    "WR": (8, 243),
    "bR": (8,),
}


def _array(value, name, shape):
    array = np.asarray(value)
    if not np.issubdtype(array.dtype, np.number) or np.iscomplexobj(array):
        raise ValueError(f"{name} must contain real numeric values.")
    if array.shape != shape:
        raise ValueError(f"{name} has shape {array.shape}; expected {shape}.")
    array = array.astype(np.float64, copy=False)
    if not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite values.")
    return array


def _sigmoid(value):
    # Separate the two signs to avoid overflowing exp for large finite inputs.
    result = np.empty_like(value)
    positive = value >= 0
    result[positive] = 1.0 / (1.0 + np.exp(-value[positive]))
    exponential = np.exp(value[~positive])
    result[~positive] = exponential / (1.0 + exponential)
    return result


def predict(features, weights: Mapping[str, np.ndarray]):
    """Return ``(fixed, correction, prediction)`` as three length-eight arrays.

    History rows are chronological. ``wi`` and ``wh`` use PyTorch's ``r, z, n``
    gate order, without GRU biases, and the initial hidden state is zero.
    The fixed affine map uses row-major ``features.reshape(-1)``.
    """
    features = _array(features, "features", (9, 27))
    missing = [name for name in SHAPES if name not in weights]
    if missing:
        raise ValueError("Missing weight arrays: " + ", ".join(missing))
    parameters = {
        name: _array(weights[name], name, shape) for name, shape in SHAPES.items()
    }
    wi, wh = parameters["wi"], parameters["wh"]
    hidden = np.zeros(32, dtype=np.float64)
    with np.errstate(over="raise", invalid="raise"):
        for step in features:
            input_r, input_z, input_n = np.split(wi @ step, 3)
            hidden_r, hidden_z, hidden_n = np.split(wh @ hidden, 3)
            reset = _sigmoid(input_r + hidden_r)
            update = _sigmoid(input_z + hidden_z)
            candidate = np.tanh(input_n + reset * hidden_n)
            hidden = (1.0 - update) * candidate + update * hidden

        dense = parameters["W1"] @ hidden + parameters["b1"]
        activated = np.array(
            [0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0))) for x in dense]
        )
        correction = parameters["W2"] @ activated + parameters["b2"]
        fixed = parameters["WR"] @ features.reshape(-1) + parameters["bR"]
        prediction = fixed + correction
    for name, value in (
        ("fixed", fixed), ("correction", correction), ("prediction", prediction)
    ):
        _array(value, name, (8,))
    return fixed, correction, prediction


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--weights", type=Path, default=DEFAULT_WEIGHTS
    )
    parser.add_argument("--out", type=Path, default=Path("output/residual-model.json"))
    args = parser.parse_args()

    try:
        with np.load(args.weights, allow_pickle=False) as archive:
            if "features" not in archive:
                raise ValueError("The NPZ archive must contain features.")
            features = archive["features"]
            weights = {name: archive[name] for name in SHAPES if name in archive}
            if "t" in archive:
                time = _array(archive["t"], "t", (9,))
                if not np.all(np.diff(time) > 0):
                    raise ValueError("t must be strictly increasing.")
        fixed, correction, prediction = predict(features, weights)
    except (OSError, ValueError, FloatingPointError) as exc:
        parser.error(str(exc))

    summary = {
        "weights_kind": (
            "initialized demonstration weights"
            if args.weights.resolve() == DEFAULT_WEIGHTS.resolve()
            else "supplied NPZ weights"
        ),
        "weights_file": str(args.weights),
        "weights_sha256": hashlib.sha256(args.weights.read_bytes()).hexdigest(),
        "features_shape": list(features.shape),
        "hidden_size": 32,
        "gru_gate_order": ["r", "z", "n"],
        "gru_bias": False,
        "initial_hidden_state": "zeros",
        "activation": "exact GELU (math.erf)",
        "fixed_flatten_order": "C (row-major)",
        "output_shape": list(prediction.shape),
        "fixed": fixed.tolist(),
        "correction": correction.tolist(),
        "prediction": prediction.tolist(),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf8",
    )
    print(args.out)


if __name__ == "__main__":
    main()
