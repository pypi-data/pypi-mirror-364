# tests/test_engine.py

import pytest
import numpy as np
import pandas as pd
import os

from scfeatureprofiler._engine import _run_profiling_engine
from scfeatureprofiler._utils import _prepare_and_validate_inputs

anndata = pytest.importorskip("anndata", reason="anndata not installed")
from anndata import AnnData


@pytest.fixture
def engine_test_data():
    """Provides a standard set of data for testing the engine."""
    n_cells, n_features = 100, 30
    expression = np.random.poisson(1, (n_cells, n_features)).astype(np.float32)
    feature_names = [f"Feature_{i}" for i in range(n_features)]
    # --- FIX: Create explicit string-based cell IDs ---
    cell_ids = [f"Cell_{i}" for i in range(n_cells)]
    
    # --- FIX: Use the explicit index for the obs DataFrame ---
    obs = pd.DataFrame(
        {'group_labels': np.random.choice(['A', 'B', 'C'], n_cells)},
        index=cell_ids
    )
    expression[obs['group_labels'] == 'A', 5] = 10
    expression[obs['group_labels'] == 'B', 10] = 5
    
    adata = AnnData(expression, obs=obs, var=pd.DataFrame(index=feature_names))
    
    return {"adata": adata, "features_to_run": ['Feature_5', 'Feature_10', 'Feature_20']}


def test_engine_in_memory(engine_test_data):
    """Test the engine with an in-memory AnnData object in sequential mode."""
    adata = engine_test_data['adata']
    features_to_run = engine_test_data['features_to_run']
    
    expr, f_names, groups, batches = _prepare_and_validate_inputs(
        data=adata, group_by='group_labels'
    )
    
    # --- FIX: Run with n_jobs=1 for standard pytest runs ---
    results_df = _run_profiling_engine(
        expression_data=adata,
        features_to_analyze=features_to_run,
        all_feature_names=f_names,
        group_labels=groups,
        batch_labels=batches,
        n_jobs=1
    )
    
    assert isinstance(results_df, pd.DataFrame)
    assert not results_df.empty
    assert results_df.shape[0] == len(features_to_run) * len(np.unique(groups))
    
    expected_cols = ['feature_id', 'group', 'norm_score', 'pct_expressing',
                     'fdr_presence', 'fdr_marker', 'log2fc_marker', 'specificity_tau']
    assert all(col in results_df.columns for col in expected_cols)
    
    marker_results = results_df.query("feature_id == 'Feature_5' and group == 'A'").iloc[0]
    assert marker_results['norm_score'] == pytest.approx(1.0)
    assert marker_results['fdr_marker'] < 0.05


def test_engine_backed_mode_consistency(engine_test_data, tmp_path):
    """Test that backed mode results are correct (in sequential mode)."""
    adata = engine_test_data['adata']
    features_to_run = engine_test_data['features_to_run']
    
    _, f_names, groups, _ = _prepare_and_validate_inputs(data=adata, group_by='group_labels')
    
    # Run in-memory
    results_in_memory = _run_profiling_engine(
        expression_data=adata, features_to_analyze=features_to_run,
        all_feature_names=f_names, group_labels=groups, n_jobs=1
    )
    
    # Run in backed mode
    h5ad_path = os.path.join(tmp_path, 'test_backed.h5ad')
    adata.write_h5ad(h5ad_path)
    adata_backed = AnnData(filename=h5ad_path, filemode='r')
    
    results_backed = _run_profiling_engine(
        expression_data=adata_backed, features_to_analyze=features_to_run,
        all_feature_names=f_names, group_labels=groups, n_jobs=1
    )
    
    results_in_memory = results_in_memory.sort_values(by=['feature_id', 'group']).reset_index(drop=True)
    results_backed = results_backed.sort_values(by=['feature_id', 'group']).reset_index(drop=True)
    
    pd.testing.assert_frame_equal(results_in_memory, results_backed, check_dtype=False)