from __future__ import annotations

from pathlib import Path

import anndata as ad
import dask.array as da
import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp
import zarr

from arrayloaders.io.store_creation import _write_sharded


@pytest.fixture(autouse=True)
def anndata_settings():
    ad.settings.zarr_write_format = 3  # Needed to support sharding in Zarr


@pytest.fixture(params=[False, True], ids=["zarr-python", "zarrs"])
def use_zarrs(request):
    return request.param


@pytest.fixture(scope="session")
def mock_store(tmpdir_factory, n_shards: int = 3):
    """Create a mock Zarr store for testing."""
    feature_dim = 100
    n_cells_per_shard = 200
    tmp_path = Path(tmpdir_factory.mktemp("stores"))
    for shard in range(n_shards):
        adata = ad.AnnData(
            X=da.random.random(
                (n_cells_per_shard, feature_dim), chunks=(10, -1)
            ).astype("f4"),
            obs=pd.DataFrame(
                {
                    "label": np.random.default_rng().integers(
                        0, 5, size=n_cells_per_shard
                    )
                },
                index=np.arange(n_cells_per_shard).astype(str),
            ),
            layers={
                "sparse": sp.random(
                    n_cells_per_shard,
                    feature_dim,
                    format="csr",
                    rng=np.random.default_rng(),
                )
            },
        )

        f = zarr.open(tmp_path / f"chunk_{shard}.zarr", mode="w", zarr_format=3)
        _write_sharded(
            f,
            adata,
            chunk_size=10,
            shard_size=20,
        )
    yield tmp_path
