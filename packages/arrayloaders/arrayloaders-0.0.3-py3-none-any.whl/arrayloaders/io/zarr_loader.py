from __future__ import annotations

import asyncio
import math
from abc import ABCMeta, abstractmethod
from collections import OrderedDict, defaultdict
from itertools import accumulate, chain, islice, pairwise
from typing import TYPE_CHECKING, Generic, NamedTuple, TypeVar, cast

import anndata as ad
import numpy as np
import zarr
import zarr.core.sync as zsync
from scipy import sparse as sp
from torch.utils.data import IterableDataset

from .utils import WorkerHandle, check_lt_1, check_var_shapes

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator
    from typing import Self


def split_given_size(a: np.ndarray, size: int) -> list[np.ndarray]:
    return np.split(a, np.arange(size, len(a), size))


OnDiskArray = TypeVar("OnDiskArray", ad.abc.CSRDataset, zarr.Array)
accepted_on_disk_types = OnDiskArray.__constraints__
InMemoryArray = TypeVar("InMemoryArray", sp.csr_matrix, np.ndarray)


def _batched(iterable, n):
    if n < 1:
        raise ValueError("n must be >= 1")
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


async def index_datasets(
    dataset_index_to_slices: OrderedDict[int, list[slice]],
    fetch_data: Callable[[list[slice], int], Awaitable[InMemoryArray]],
) -> list[InMemoryArray]:
    """Helper function meant to encapsulate asynchronous calls so that we can use the same event loop as zarr.

    Args:
        dataset_index_to_slices: A lookup of the list-placement index of a dataset to the request slices.
        fetch_data: The function to do the fetching for a given slice-dataset index pair.
    """
    tasks = []
    for dataset_idx in dataset_index_to_slices.keys():
        tasks.append(
            fetch_data(
                dataset_index_to_slices[dataset_idx],
                dataset_idx,
            )
        )
    return await asyncio.gather(*tasks)


add_dataset_docstring = """\
Append datasets to this loader.

Args:
    datasets: List of :class:`anndata.abc.CSRDataset` or :class:`zarr.Array` objects, generally from :attr:`anndata.AnnData.X`.
    obs: List of `numpy.ndarray` labels, generally from :attr:`anndata.AnnData.obs`.
"""

add_dataset_docstring = """\
Append a dataset to this loader.

Args:
    dataset: :class:`anndata.abc.CSRDataset` or :class:`zarr.Array` object, generally from :attr:`anndata.AnnData.X`.
    obs: `numpy.ndarray` labels for the dataset, generally from :attr:`anndata.AnnData.obs`.
"""


class AnnDataManager(Generic[OnDiskArray, InMemoryArray]):
    train_datasets: list[OnDiskArray] = []
    labels: list[np.ndarray] | None = None
    _return_index: bool = False
    _on_add: Callable | None = None
    _batch_size: int = 1

    def __init__(
        self,
        *,
        on_add: Callable | None = None,
        return_index: bool = False,
        batch_size: int = 1,
    ):
        self._on_add = on_add
        self._return_index = return_index
        self._batch_size = batch_size

    @property
    def dataset_type(self) -> type[OnDiskArray]:
        return type(self.train_datasets[0])

    @property
    def n_obs(self) -> int:
        return sum(ds.shape[0] for ds in self.train_datasets)

    @property
    def n_var(self) -> int:
        return self.train_datasets[0].shape[1]

    def add_anndatas(
        self,
        adatas: list[ad.AnnData],
        layer_keys: list[str | None] | str | None = None,
        obs_keys: list[str] | str | None = None,
    ) -> None:
        raise NotImplementedError("See https://github.com/scverse/anndata/issues/2021")

    def add_anndata(
        self,
        adata: ad.AnnData,
        layer_key: str | None = None,
        obs_key: str | None = None,
    ) -> None:
        raise NotImplementedError("See https://github.com/scverse/anndata/issues/2021")

    def add_datasets(
        self, datasets: list[OnDiskArray], obs: list[np.ndarray] | None = None
    ) -> None:
        if obs is None:
            obs = [None] * len(datasets)
        for ds, o in zip(datasets, obs, strict=True):
            self.add_dataset(ds, o)

    def add_dataset(self, dataset: OnDiskArray, obs: np.ndarray | None = None) -> None:
        if len(self.train_datasets) > 0:
            if self.labels is None and obs is not None:
                raise ValueError(
                    f"Cannot add a dataset with obs label {obs} when training datasets have already been added without labels"
                )
            if self.labels is not None and obs is None:
                raise ValueError(
                    "Cannot add a dataset with no obs label when training datasets have already been added without labels"
                )
        if not isinstance(dataset, accepted_types := accepted_on_disk_types):
            raise TypeError(
                f"Cannot add a dataset of type {type(dataset)}, only {accepted_types} are allowed"
            )
        if len(self.train_datasets) > 0 and not isinstance(dataset, self.dataset_type):
            raise TypeError(
                f"Cannot add a dataset whose data of type {type(dataset)} was not an instance of expected type {self.dataset_type}"
            )
        datasets = self.train_datasets + [dataset]
        check_var_shapes(datasets)
        self._var_size = datasets[0].shape[1]  # TODO: joins
        self.train_datasets = datasets
        if self.labels is not None:  # labels exist
            self.labels += [obs]
        elif (
            obs is not None
        ):  # labels dont exist yet, but are being added for the first time
            self.labels = [obs]
        if self._on_add is not None:
            self._on_add()

    def _get_relative_obs_indices(
        self, index: slice, *, use_original_space: bool = False
    ) -> list[tuple[slice, int]]:
        """Generate a slice relative to a dataset given a global slice index over all datasets.

        For a given slice indexer of axis 0, return a new slice relative to the on-disk
        data it represents given the number of total observations as well as the index of
        the underlying data on disk from the argument `sparse_datasets` to the initializer.

        For example, given slice index (10, 15), for 4 datasets each with size 5 on axis zero,
        this function returns ((0,5), 2) representing slice (0,5) along axis zero of sparse dataset 2.

        Args:
            index: The queried slice.
            use_original_space: Whether or not the slices should be reindexed against the anndata objects.

        Returns:
            A slice relative to the dataset it represents as well as the index of said dataset in `sparse_datasets`.
        """
        min_idx = index.start
        max_idx = index.stop
        curr_pos = 0
        slices = []
        for idx, array in enumerate(self.train_datasets):
            array_start = curr_pos
            n_obs = array.shape[0]
            array_end = curr_pos + n_obs

            start = max(min_idx, array_start)
            stop = min(max_idx, array_end)
            if start < stop:
                if use_original_space:
                    slices.append((slice(start, stop), idx))
                else:
                    relative_start = start - array_start
                    relative_stop = stop - array_start
                    slices.append((slice(relative_start, relative_stop), idx))
            curr_pos += n_obs
        return slices

    def _slices_to_slices_with_array_index(
        self, slices: list[slice], *, use_original_space: bool = False
    ) -> OrderedDict[int, list[slice]]:
        """Given a list of slices, give the lookup between on-disk datasets and slices relative to that dataset.

        Args:
            slices: Slices to relative to the on-disk datasets.
            use_original_space: Whether or not the slices should be reindexed against the anndata objects.

        Returns:
            A lookup between the dataset and its indexing slices, ordered by keys.
        """
        dataset_index_to_slices: defaultdict[int, list[slice]] = defaultdict(list)
        for slice in slices:
            for relative_obs_indices in self._get_relative_obs_indices(
                slice, use_original_space=use_original_space
            ):
                dataset_index_to_slices[relative_obs_indices[1]] += [
                    relative_obs_indices[0]
                ]
        keys = sorted(dataset_index_to_slices.keys())
        dataset_index_to_slices_sorted = OrderedDict()
        for k in keys:
            dataset_index_to_slices_sorted[k] = dataset_index_to_slices[k]
        return dataset_index_to_slices_sorted

    def _get_chunks(
        self, chunk_size: int, worker_handle: WorkerHandle, shuffle: bool
    ) -> np.ndarray:
        """Get a potentially shuffled list of chunk ids, accounting for the fact that this dataset might be inside a worker.

        Returns:
            A :class:`numpy.ndarray` of chunk ids.
        """
        chunks = np.array(list(range(math.ceil(self.n_obs / chunk_size))))
        if shuffle:
            worker_handle.shuffle(chunks)

        return worker_handle.get_part_for_worker(chunks)

    def iter(
        self,
        chunk_size: int,
        worker_handle: WorkerHandle,
        preload_nchunks: int,
        shuffle: bool,
        fetch_data: Callable[[list[slice], int], Awaitable[InMemoryArray]],
    ) -> Iterator[
        tuple[InMemoryArray, None | np.ndarray]
        | tuple[InMemoryArray, None | np.ndarray, np.ndarray]
    ]:
        """Iterate over the on-disk csr datasets.

        Yields:
            A one-row sparse matrix.
        """
        check_lt_1(
            [len(self.train_datasets), self.n_obs],
            ["Number of datasets", "Number of observations"],
        )
        # In order to handle data returned where (chunk_size * preload_nchunks) mod batch_size != 0
        # we must keep track of the leftover data.
        in_memory_data = None
        in_memory_labels = None
        in_memory_indices = None
        for chunk_indices in _batched(
            self._get_chunks(chunk_size, worker_handle, shuffle), preload_nchunks
        ):
            slices = [
                slice(
                    index * chunk_size,
                    min(self.n_obs, (index + 1) * chunk_size),
                )
                for index in chunk_indices
            ]
            dataset_index_to_slices = self._slices_to_slices_with_array_index(slices)
            # Fetch the data over slices
            chunks: list[InMemoryArray] = zsync.sync(
                index_datasets(dataset_index_to_slices, fetch_data)
            )
            # Accumulate labels
            labels: None | list[np.ndarray] = None
            if self.labels is not None:
                labels = []
                for dataset_idx in dataset_index_to_slices.keys():
                    labels += [
                        self.labels[dataset_idx][
                            np.concatenate(
                                [
                                    np.arange(s.start, s.stop)
                                    for s in dataset_index_to_slices[dataset_idx]
                                ]
                            )
                        ]
                    ]
            # Accumulate indices if necessary
            indices: None | list[np.ndarray] = None
            if self._return_index:
                dataset_index_to_slices = self._slices_to_slices_with_array_index(
                    slices, use_original_space=True
                )
                dataset_indices = dataset_index_to_slices.keys()
                indices = [
                    np.concatenate(
                        [
                            np.arange(
                                s.start,
                                s.stop,
                            )
                            for s in dataset_index_to_slices[index]
                        ]
                    )
                    for index in dataset_indices
                ]
            # Do batch returns, handling leftover data as necessary
            mod = sp if isinstance(chunks[0], sp.csr_matrix) else np
            in_memory_data = (
                mod.vstack(chunks)
                if in_memory_data is None
                else mod.vstack([in_memory_data, *chunks])
            )
            if self.labels is not None:
                in_memory_labels = (
                    np.concatenate(labels)
                    if in_memory_labels is None
                    else np.concatenate([in_memory_labels, *labels])
                )
            if self._return_index:
                in_memory_indices = (
                    np.concatenate(indices)
                    if in_memory_indices is None
                    else np.concatenate([in_memory_indices, *indices])
                )
            # Create random indices into in_memory_data and then index into it
            # If there is "leftover" at the end (see the modulo op),
            # save it for the next iteration.
            batch_indices = np.arange(in_memory_data.shape[0])
            if shuffle:
                np.random.default_rng().shuffle(batch_indices)
            splits = split_given_size(batch_indices, self._batch_size)
            for i, s in enumerate(splits):
                if s.shape[0] == self._batch_size:
                    res = [
                        in_memory_data[s],
                        in_memory_labels[s] if self.labels is not None else None,
                    ]
                    if self._return_index:
                        res += [in_memory_indices[s]]
                    yield tuple(res)
                if i == (
                    len(splits) - 1
                ):  # end of iteration, leftover data needs be kept
                    if (s.shape[0] % self._batch_size) != 0:
                        in_memory_data = in_memory_data[s]
                        if in_memory_labels is not None:
                            in_memory_labels = in_memory_labels[s]
                        if in_memory_indices is not None:
                            in_memory_indices = in_memory_indices[s]
                    else:
                        in_memory_data = None
                        in_memory_labels = None
                        in_memory_indices = None
        if in_memory_data is not None:  # handle any leftover data
            res = [
                in_memory_data,
                in_memory_labels if self.labels is not None else None,
            ]
            if self._return_index:
                res += [in_memory_indices[s]]
            yield tuple(res)


AnnDataManager.add_datasets.__doc__ = add_dataset_docstring
AnnDataManager.add_dataset.__doc__ = add_dataset_docstring

__init_docstring__ = """A loader for on-disk {array_type} data.

This loader batches together slice requests to the underlying {array_type} stores to acheive higher performance.
This custom code to do this task will be upstreamed into anndata at some point and no longer rely on private zarr apis.
The loader is agnostic to the on-disk chunking/sharding, but it may be advisable to align with the in-memory chunk size.

Args:
    chunk_size: The obs size (i.e., axis 0) of contiguous array data to fetch, by default 512
    preload_nchunks: The number of chunks of contiguous array data to fetch, by default 32
    shuffle: Whether or not to shuffle the data, by default True
    return_index: Whether or not to return the index on each iteration, by default False
"""


# TODO: make this part of the public zarr or zarrs-python API.
# We can do chunk coalescing in zarrs based on integer arrays, so I think
# there would make sense with ezclump or similar.
# Another "solution" would be for zarrs to support integer indexing properly, if that pipeline works,
# or make this an "experimental setting" and to use integer indexing for the zarr-python pipeline.
# See: https://github.com/zarr-developers/zarr-python/issues/3175 for why this is better than simpler alternatives.
class MultiBasicIndexer(zarr.core.indexing.Indexer):
    def __init__(self, indexers: list[zarr.core.indexing.Indexer]):
        self.shape = (sum(i.shape[0] for i in indexers), *indexers[0].shape[1:])
        self.drop_axes = indexers[0].drop_axes  # maybe?
        self.indexers = indexers

    def __iter__(self):
        total = 0
        for i in self.indexers:
            for c in i:
                out_selection = c[2]
                gap = out_selection[0].stop - out_selection[0].start
                yield type(c)(
                    c[0], c[1], (slice(total, total + gap), *out_selection[1:]), c[3]
                )
                total += gap


class AbstractIterableDataset(Generic[OnDiskArray, InMemoryArray], metaclass=ABCMeta):
    _shuffle: bool
    _preload_nchunks: int
    _worker_handle: WorkerHandle
    _chunk_size: int
    _dataset_manager: AnnDataManager[OnDiskArray, InMemoryArray]

    def __init__(
        self,
        *,
        chunk_size: int = 512,
        preload_nchunks: int = 32,
        shuffle: bool = True,
        return_index: bool = False,
        batch_size: int = 1,
    ):
        check_lt_1(
            [
                chunk_size,
                preload_nchunks,
            ],
            ["Chunk size", "Preload chunks"],
        )
        if batch_size > (chunk_size * preload_nchunks):
            raise NotImplementedError(
                "If you need batch loading that is bigger than the iterated in-memory size, please open an issue."
            )
        self._dataset_manager: AnnDataManager[ad.abc.CSRDataset, sp.csr_matrix] = (
            AnnDataManager(
                # TODO: https://github.com/scverse/anndata/issues/2021
                # on_add=self._cache_update_callback,
                return_index=return_index,
                batch_size=batch_size,
            )
        )
        self._chunk_size = chunk_size
        self._preload_nchunks = preload_nchunks
        self._shuffle = shuffle
        self._worker_handle = WorkerHandle()

    async def _cache_update_callback(self):
        pass

    @abstractmethod
    async def _fetch_data(self, slices: list[slice], dataset_idx: int) -> InMemoryArray:
        """Fetch the data for given slices and the arrays representing a dataset on-disk.

        Args:
            slices: The indexing slices to fetch.
            dataset_idx: The index of the dataset to fetch from.

        Returns:
            The in-memory array data.
        """
        ...

    def add_anndatas(
        self,
        adatas: list[ad.AnnData],
        layer_keys: list[str | None] | str | None = None,
        obs_keys: list[str] | str | None = None,
    ) -> Self:
        raise NotImplementedError("See https://github.com/scverse/anndata/issues/2021")

    def add_anndata(
        self,
        adata: ad.AnnData,
        layer_key: str | None = None,
        obs_key: str | None = None,
    ) -> Self:
        raise NotImplementedError("See https://github.com/scverse/anndata/issues/2021")

    def add_datasets(
        self, datasets: list[OnDiskArray], obs: list[np.ndarray] | None = None
    ) -> Self:
        self._dataset_manager.add_datasets(datasets, obs)
        return self

    def add_dataset(self, dataset: OnDiskArray, obs: np.ndarray | None = None) -> Self:
        self._dataset_manager.add_dataset(dataset, obs)
        return self

    def __len__(self) -> int:
        return self._dataset_manager.n_obs

    def __iter__(
        self,
    ) -> Iterator[
        tuple[InMemoryArray, None | np.ndarray]
        | tuple[InMemoryArray, None | np.ndarray, np.ndarray]
    ]:
        """Iterate over the on-disk datasets.

        Yields:
            A one-row in-memory array optionally with its label.
        """
        yield from self._dataset_manager.iter(
            self._chunk_size,
            self._worker_handle,
            self._preload_nchunks,
            self._shuffle,
            self._fetch_data,
        )


AbstractIterableDataset.add_dataset.__doc__ = add_dataset_docstring
AbstractIterableDataset.add_datasets.__doc__ = add_dataset_docstring


class ZarrDenseDataset(AbstractIterableDataset, IterableDataset):
    async def _fetch_data(self, slices: list[slice], dataset_idx: int) -> np.ndarray:
        dataset = self._dataset_manager.train_datasets[dataset_idx]
        indexer = MultiBasicIndexer(
            [
                zarr.core.indexing.BasicIndexer(
                    (s, Ellipsis),
                    shape=dataset.metadata.shape,
                    chunk_grid=dataset.metadata.chunk_grid,
                )
                for s in slices
            ]
        )
        res = cast(
            "np.ndarray",
            await dataset._async_array._get_selection(
                indexer, prototype=zarr.core.buffer.default_buffer_prototype()
            ),
        )
        return res


ZarrDenseDataset.__init__.__doc__ = __init_docstring__.format(array_type="dense")


class CSRDatasetElems(NamedTuple):
    indptr: np.ndarray
    indices: zarr.AsyncArray
    data: zarr.AsyncArray


class ZarrSparseDataset(AbstractIterableDataset, IterableDataset):
    _dataset_elem_cache: dict[int, CSRDatasetElems] = {}

    def _cache_update_callback(self):
        """Callback for when datasets are added to ensure the cache is updated."""
        return zsync.sync(self._ensure_cache())

    async def _create_sparse_elems(self, idx: int) -> CSRDatasetElems:
        """Fetch the in-memory indptr, and backed indices and data for a given dataset index.

        Args:
            idx: The index

        Returns:
            The constituent elems of the CSR dataset.
        """
        indptr = await self._dataset_manager.train_datasets[
            idx
        ].group._async_group.getitem("indptr")
        return CSRDatasetElems(
            *(
                await asyncio.gather(
                    indptr.getitem(Ellipsis),
                    self._dataset_manager.train_datasets[
                        idx
                    ].group._async_group.getitem("indices"),
                    self._dataset_manager.train_datasets[
                        idx
                    ].group._async_group.getitem("data"),
                )
            )
        )

    async def _ensure_cache(self):
        """Build up the cache of datasets i.e., in-memory indptr, and backed indices and data."""
        arr_idxs = [
            idx
            for idx in range(len(self._dataset_manager.train_datasets))
            if idx not in self._dataset_elem_cache
        ]
        all_elems = await asyncio.gather(
            *(
                self._create_sparse_elems(idx)
                for idx in range(len(self._dataset_manager.train_datasets))
                if idx not in self._dataset_elem_cache
            )
        )
        for idx, elems in zip(arr_idxs, all_elems, strict=True):
            self._dataset_elem_cache[idx] = elems

    async def _get_sparse_elems(self, dataset_idx: int) -> CSRDatasetElems:
        """Return the arrays (zarr or otherwise) needed to represent on-disk data at a given index.

        Args:
            dataset_idx: The index of the dataset whose arrays are sought.

        Returns:
            The arrays representing the sparse data.
        """
        if dataset_idx not in self._dataset_elem_cache:
            await self._ensure_cache()
        return self._dataset_elem_cache[dataset_idx]

    async def _fetch_data(
        self,
        slices: list[slice],
        dataset_idx: int,
    ) -> sp.csr_matrix:
        # See https://github.com/scverse/anndata/blob/361325fc621887bf4f381e9412b150fcff599ff7/src/anndata/_core/sparse_dataset.py#L272-L295
        # for the inspiration of this function.
        indptr, indices, data = await self._get_sparse_elems(dataset_idx)
        indptr_indices = [indptr[slice(s.start, s.stop + 1)] for s in slices]
        indptr_limits = [slice(i[0], i[-1]) for i in indptr_indices]
        indexer = MultiBasicIndexer(
            [
                zarr.core.indexing.BasicIndexer(
                    (l,), shape=data.metadata.shape, chunk_grid=data.metadata.chunk_grid
                )
                for l in indptr_limits
            ]
        )
        data_np, indices_np = await asyncio.gather(
            data._get_selection(
                indexer, prototype=zarr.core.buffer.default_buffer_prototype()
            ),
            indices._get_selection(
                indexer, prototype=zarr.core.buffer.default_buffer_prototype()
            ),
        )
        gaps = (s1.start - s0.stop for s0, s1 in pairwise(indptr_limits))
        offsets = accumulate(chain([indptr_limits[0].start], gaps))
        start_indptr = indptr_indices[0] - next(offsets)
        if len(slices) < 2:  # there is only one slice so no need to concatenate
            return sp.csr_matrix(
                (data_np, indices_np, start_indptr),
                shape=(start_indptr.shape[0] - 1, self._dataset_manager.n_var),
            )
        end_indptr = np.concatenate(
            [s[1:] - o for s, o in zip(indptr_indices[1:], offsets, strict=True)]
        )
        indptr_np = np.concatenate([start_indptr, end_indptr])
        return sp.csr_matrix(
            (data_np, indices_np, indptr_np),
            shape=(indptr_np.shape[0] - 1, self._dataset_manager.n_var),
        )


ZarrSparseDataset.__init__.__doc__ = __init_docstring__.format(array_type="sparse")
