# tests/test_utils.py

import pytest
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from scfeatureprofiler._utils import (
    _prepare_and_validate_inputs,
    get_active_features,
)

anndata = pytest.importorskip("anndata", reason="anndata not installed")

@pytest.fixture
def test_data():
    """Provides a standard set of data for testing."""
    n_cells, n_features = 50, 20
    expression_dense = np.random.poisson(1, (n_cells, n_features))
    expression_sparse = csr_matrix(expression_dense)
    
    feature_names = [f"Feature_{i}" for i in range(n_features)]
    cell_ids = [f"Cell_{i}" for i in range(n_cells)]
    
    obs = pd.DataFrame({
        'group_labels': np.random.choice(['A', 'B'], n_cells),
        'donor_labels': np.random.choice(['d1', 'd2'], n_cells)
    }, index=cell_ids)
    
    adata = anndata.AnnData(expression_dense, obs=obs, var=pd.DataFrame(index=feature_names))
    df = pd.DataFrame(expression_dense, columns=feature_names, index=cell_ids)
    
    return {
        "adata": adata,
        "dataframe": df,
        "numpy_array": expression_dense,
        "sparse_matrix": expression_sparse,
        "feature_names": feature_names,
        "group_labels": obs['group_labels'].values,
        "donor_labels": obs['donor_labels'].values,
        "n_cells": n_cells,
        "n_features": n_features
    }

def test_validator_with_anndata(test_data):
    adata = test_data["adata"]
    expr, f_names, groups, batches = _prepare_and_validate_inputs(
        data=adata, group_by='group_labels', batch_by='donor_labels'
    )
    assert expr is adata.X
    assert f_names == test_data["feature_names"]
    np.testing.assert_array_equal(groups, test_data["group_labels"])
    np.testing.assert_array_equal(batches, test_data["donor_labels"])

def test_validator_with_dataframe(test_data):
    df = test_data["dataframe"]
    expr, f_names, groups, batches = _prepare_and_validate_inputs(
        data=df, group_by=test_data["group_labels"], batch_by=test_data["donor_labels"]
    )
    np.testing.assert_array_equal(expr, test_data["numpy_array"])
    assert f_names == test_data["feature_names"]
    np.testing.assert_array_equal(groups, test_data["group_labels"])
    np.testing.assert_array_equal(batches, test_data["donor_labels"])

def test_validator_with_numpy(test_data):
    arr = test_data["numpy_array"]
    expr, f_names, groups, _ = _prepare_and_validate_inputs(
        data=arr, group_by=test_data["group_labels"], feature_names=test_data["feature_names"]
    )
    assert expr is arr
    assert f_names == test_data["feature_names"]
    np.testing.assert_array_equal(groups, test_data["group_labels"])

def test_validator_with_sparse(test_data):
    sparse = test_data["sparse_matrix"]
    expr, f_names, groups, _ = _prepare_and_validate_inputs(
        data=sparse, group_by=test_data["group_labels"], feature_names=test_data["feature_names"]
    )
    assert expr is sparse
    assert f_names == test_data["feature_names"]
    np.testing.assert_array_equal(groups, test_data["group_labels"])

def test_validator_raises_on_mismatched_labels(test_data):
    with pytest.raises(ValueError, match="Length of `group_by`"):
        _prepare_and_validate_inputs(
            data=test_data["dataframe"], group_by=['A'] * (test_data["n_cells"] - 1)
        )

def test_validator_raises_on_missing_feature_names(test_data):
    with pytest.raises(ValueError, match="`feature_names` must be provided"):
        _prepare_and_validate_inputs(
            data=test_data["numpy_array"], group_by=test_data["group_labels"]
        )

def test_validator_raises_on_extra_feature_names(test_data):
    with pytest.raises(ValueError, match="Do not provide `feature_names`"):
        _prepare_and_validate_inputs(
            data=test_data["dataframe"], group_by=test_data["group_labels"], feature_names=test_data["feature_names"]
        )

def test_validator_raises_on_extra_feature_names_anndata(test_data):
    with pytest.raises(ValueError, match="Do not provide `feature_names`"):
        _prepare_and_validate_inputs(
            data=test_data["adata"], group_by="group_labels", feature_names=test_data["feature_names"]
        )

def test_validator_raises_on_nan_in_labels(test_data):
    bad_labels = test_data["group_labels"].copy().astype(object)
    bad_labels[0] = np.nan
    with pytest.raises(ValueError, match="contains NaN"):
        _prepare_and_validate_inputs(
            data=test_data["dataframe"], group_by=bad_labels
        )
        
def test_validator_raises_on_bad_anndata_key(test_data):
    with pytest.raises(ValueError, match="not found in `adata.obs`"):
        _prepare_and_validate_inputs(
            data=test_data["adata"], group_by="non_existent_key"
        )

def test_get_active_features_logic(test_data):
    n_cells, n_features = test_data["n_cells"], test_data["n_features"]
    arr = np.zeros((n_cells, n_features))
    arr[:15, 0] = 1
    arr[:5, 1] = 1
    
    active_10 = get_active_features(arr, feature_names=test_data["feature_names"], min_cells=10)
    assert active_10 == ["Feature_0"]

    active_5 = get_active_features(arr, feature_names=test_data["feature_names"], min_cells=5)
    assert sorted(active_5) == ["Feature_0", "Feature_1"]

def test_get_active_features_with_anndata(test_data):
    adata = test_data["adata"].copy()
    adata.X = np.zeros_like(adata.X)
    
    adata.X[:15, 0] = 1
    adata.X[:5, 1] = 1
    
    active_features = get_active_features(adata, min_cells=5)
    assert sorted(active_features) == ["Feature_0", "Feature_1"]

def test_get_active_features_with_min_expression(test_data):
    n_cells, n_features = test_data["n_cells"], test_data["n_features"]
    arr = np.zeros((n_cells, n_features))
    arr[:12, 5] = 5
    arr[:15, 8] = 0.5
    
    active = get_active_features(
        arr, feature_names=test_data["feature_names"], min_cells=10, min_expression=1
    )
    assert active == ["Feature_5"]