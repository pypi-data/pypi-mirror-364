# tests/test_selection.py

import pytest
import numpy as np
import pandas as pd

from scfeatureprofiler._selection_marker import select_marker_candidates

@pytest.fixture
def selection_test_data():
    """
    Creates a FULLY DETERMINISTIC dataset to test the selection pipeline.
    Each feature is manually designed to test a specific filter.
    """
    n_cells, n_features = 200, 8
    feature_names = [
        "PerfectMarker", "TooRare", "TooCommon", "LowVariance",
        "NoGap", "NotHeavyTailed", "LowCV", "GoodMarker2"
    ]
    X = np.zeros((n_cells, n_features))

    # --- Manually design features with precise properties ---

    # Feature 0: PerfectMarker - Should pass everything.
    # Freq=25%, High Var/Mean, High Gap, High Tail, High CV.
    X[0:25, 0] = 2
    X[25:50, 0] = 20

    # Feature 1: TooRare - Fails frequency filter (min_freq=0.05).
    # Freq = 4/200 = 2%. Default min is 5%.
    X[0:4, 1] = 5

    # Feature 2: TooCommon - Fails frequency filter (max_freq=0.90).
    # Freq = 190/200 = 95%. Default max is 90%.
    X[0:190, 2] = 1

    # Feature 3: LowVariance - Fails var/mean > 1.5.
    # Freq=50%. Mean=0.5, Var=0.25 (Bernoulli). Var/Mean=0.5.
    X[0:100, 3] = 1

    # Feature 4: NoGap - Fails gap_stat > 1.2.
    # Freq=25%. 10th percentile of non-zeros is 0.1, which is not > 1.2.
    X[0:25, 4] = 0.1
    X[25:50, 4] = 3
    
    # Feature 5: NotHeavyTailed - Fails right_tail > 2.5.
    # Freq=25%. p90=2.9, p50=2.5. Ratio is ~1.16.
    X[0:50, 5] = np.linspace(2, 3, 50)
    
    # Feature 6: LowCV - Fails cv > 0.8.
    # Freq=25%. For non-zeros, Mean=5, Std=0.5. CV = 0.1.
    X[0:25, 6] = 4.5
    X[25:50, 6] = 5.5

    # Feature 7: GoodMarker2 - Should also pass everything.
    X[50:75, 7] = 3
    X[75:100, 7] = 30
    
    return pd.DataFrame(X, columns=feature_names)


def test_select_marker_candidates_all_filters(selection_test_data):
    """Test the full pipeline with all filters enabled."""
    data = selection_test_data
    candidates = select_marker_candidates(data, verbose=False)
    assert isinstance(candidates, list)
    assert sorted(candidates) == ["GoodMarker2", "PerfectMarker"]


def test_tier1_filters(selection_test_data):
    """Test that the Tier 1 filters (frequency and variance) work correctly."""
    data = selection_test_data
    candidates = select_marker_candidates(
        data,
        gap_stat_min=0, right_tail_min=0, cv_min=None, verbose=False
    )
    # Filters out TooRare, TooCommon, LowVariance
    expected = ["GoodMarker2", "LowCV", "NoGap", "NotHeavyTailed", "PerfectMarker"]
    assert sorted(candidates) == sorted(expected)


def test_gap_stat_filter(selection_test_data):
    """Test that the gap statistic filter correctly removes NoGap."""
    data = selection_test_data
    candidates = select_marker_candidates(
        data,
        gap_stat_min=1.2, right_tail_min=0, cv_min=None, verbose=False
    )
    assert "NoGap" not in candidates
    assert "PerfectMarker" in candidates


def test_right_tail_filter(selection_test_data):
    """Test that the right-tail filter correctly removes NotHeavyTailed."""
    data = selection_test_data
    candidates = select_marker_candidates(
        data,
        gap_stat_min=0, right_tail_min=2.5, cv_min=None, verbose=False
    )
    assert "NotHeavyTailed" not in candidates
    assert "PerfectMarker" in candidates


def test_cv_filter(selection_test_data):
    """Test the CV filter correctly removes LowCV."""
    data = selection_test_data
    candidates = select_marker_candidates(
        data,
        gap_stat_min=0, right_tail_min=0, cv_min=0.8, verbose=False
    )
    assert "LowCV" not in candidates
    assert "PerfectMarker" in candidates