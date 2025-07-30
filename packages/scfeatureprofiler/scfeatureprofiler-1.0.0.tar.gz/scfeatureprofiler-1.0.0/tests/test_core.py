# tests/test_core.py

import pytest
import numpy as np
import pandas as pd

from scfeatureprofiler._core import _analyze_one_feature


@pytest.fixture
def core_test_data():
    """Provides a predictable dataset for testing core calculations."""
    labels_vector = np.array(['A']*20 + ['B']*20 + ['C']*20)
    batch_vector = np.array(['b1']*10 + ['b2']*10 + ['b1']*10 + ['b2']*10 + ['b1']*10 + ['b2']*10)
    
    expr_marker_a = np.zeros(60)
    expr_marker_a[labels_vector == 'A'] = np.random.uniform(5, 10, size=20)
    
    # --- FIX: Make 'Broad' feature expressed in ALL groups ---
    expr_broad = np.zeros(60)
    expr_broad[labels_vector == 'A'] = np.random.uniform(2, 3, size=20)
    expr_broad[labels_vector == 'B'] = np.random.uniform(2, 3, size=20) # Now expressed in B
    expr_broad[labels_vector == 'C'] = np.random.uniform(2, 3, size=20)

    return {
        "labels_vector": labels_vector,
        "batch_vector": batch_vector,
        "expr_marker_a": expr_marker_a,
        "expr_broad": expr_broad
    }


def test_analyze_marker_feature(core_test_data):
    """Test analysis of a feature that is a perfect marker."""
    results = _analyze_one_feature(
        expression_vector=core_test_data['expr_marker_a'],
        labels_vector=core_test_data['labels_vector'],
        feature_name='MarkerA',
        batch_vector=core_test_data['batch_vector'],
        specificity_metric='tau'
    )
    
    assert isinstance(results, pd.DataFrame)
    assert results.shape[0] == 3
    assert not results['norm_score'].isnull().any()  # Regression test for the NaN bug

    group_a_stats = results.set_index('group').loc['A']
    assert group_a_stats['norm_score'] == pytest.approx(1.0)
    assert group_a_stats['pct_expressing'] == pytest.approx(100.0)
    assert group_a_stats['specificity_tau'] == pytest.approx(1.0)
    assert group_a_stats['p_val_presence'] < 1e-10
    assert group_a_stats['p_val_marker'] < 1e-5
    assert group_a_stats['log2fc_marker'] > 2

    group_b_stats = results.set_index('group').loc['B']
    assert group_b_stats['norm_score'] == pytest.approx(0.0)
    assert group_b_stats['pct_expressing'] == pytest.approx(0.0)


# In tests/test_core.py

def test_analyze_broadly_expressed_feature(core_test_data):
    """Test a feature expressed in multiple groups with Gini."""
    results = _analyze_one_feature(
        expression_vector=core_test_data['expr_broad'],
        labels_vector=core_test_data['labels_vector'],
        batch_vector=core_test_data['batch_vector'],
        feature_name='Broad',
        specificity_metric='gini'
    )

    assert 'specificity_gini' in results.columns
    stats = results.set_index('group')

    # --- FIX: The norm_score assertions were logically incorrect and have been removed. ---
    # We cannot assert that all groups have a high relative score.
    # The important checks for a "broad" feature are low specificity and non-significant marker p-values.

    # Specificity (Gini) should be very low (close to 0), indicating broad expression.
    assert stats.loc['A', 'specificity_gini'] < 0.2

    # All groups should be significantly present.
    assert stats.loc['A', 'p_val_presence'] < 1e-10
    assert stats.loc['B', 'p_val_presence'] < 1e-10
    assert stats.loc['C', 'p_val_presence'] < 1e-10

    # None of the groups should be a significant marker relative to the others.
    assert stats.loc['A', 'p_val_marker'] > 0.05
    assert stats.loc['B', 'p_val_marker'] > 0.05
    assert stats.loc['C', 'p_val_marker'] > 0.05

def test_edge_case_single_group():
    """Test behavior when only one group is present."""
    expression = np.array([1, 2, 3, 4, 5])
    labels = np.array(['A'] * 5)
    
    results = _analyze_one_feature(expression, labels, 'SingleGroupFeature')
    
    stats = results.iloc[0]
    assert stats['p_val_marker'] == 1.0
    assert stats['specificity_tau'] == 1.0 # This should now pass
    assert stats['norm_score'] == 0.0