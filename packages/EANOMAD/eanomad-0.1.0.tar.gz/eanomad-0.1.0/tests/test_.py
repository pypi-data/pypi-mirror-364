# -*- coding: utf-8 -*-
"""Unit tests for *EANOMAD*.
Run with ``pytest -q``.

The tests are lightweight smoke checks that ensure:
* both optimiser types ("pure" and "hybrid") run without error,
* invalid arguments raise `ValueError`,
* seeding makes the run deterministic.
"""
from __future__ import annotations

import numpy as np
import pytest

from EANOMAD import EANOMAD

# ---------------------------------------------------------------------------
# Test helper – simple objective
# ---------------------------------------------------------------------------

def sphere(x: np.ndarray) -> float:
    """Negative sphere – global maximum at 0 with fitness 0."""
    return -np.sum(x ** 2)


# ---------------------------------------------------------------------------
# Smoke tests for both optimiser types
# ---------------------------------------------------------------------------

def _run_smoke(optim_type: str):
    opt = EANOMAD(
        optim_type,
        population_size=8,
        dimension=4,
        objective_fn=sphere,
        subset_size=2,
        bounds=0.1,
        max_bb_eval=20,
        n_elites=2,
        n_mutate_coords=1,
        seed=42,
        use_ray=False,
    )
    best_x, best_fit = opt.run(generations=3)
    assert best_x.shape == (4,)
    assert isinstance(best_fit, float)
    assert best_fit <= 0  # sphere is <= 0


def test_pure_smoke():
    _run_smoke("pure")


def test_hybrid_smoke():
    _run_smoke("hybrid")


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("crossover_type", ["foo", "", None])
def test_invalid_crossover_type_raises(crossover_type):
    with pytest.raises(ValueError):
        EANOMAD(
            "pure",
            population_size=4,
            dimension=2,
            objective_fn=sphere,
            crossover_type=crossover_type,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("crossover_rate", [-0.1, -10, 1.5])
def test_invalid_crossover_rate_raises(crossover_rate):
    with pytest.raises(ValueError):
        EANOMAD(
            "pure",
            population_size=4,
            dimension=2,
            objective_fn=sphere,
            crossover_rate=crossover_rate,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Determinism with seed
# ---------------------------------------------------------------------------

def test_seed_reproducibility():
    """Global RNG seeding should make two runs identical."""
    opt1 = EANOMAD(
        "hybrid",
        population_size=6,
        dimension=3,
        objective_fn=sphere,
        subset_size=2,
        seed=7,
        use_ray=False,
    )
    best_x1, best_fit1 = opt1.run(generations=3)

   
    opt2 = EANOMAD(
        "hybrid",
        population_size=6,
        dimension=3,
        objective_fn=sphere,
        subset_size=2,
        seed=7,
        use_ray=False,
    )
    best_x2, best_fit2 = opt2.run(generations=3)

    assert np.allclose(best_x1, best_x2)
    assert best_fit1 == best_fit2
