import zarr
import mrcfile
import os
from typing import Tuple
from dask.array.core import slices_from_chunks, normalize_chunks
from dask.distributed import Client, wait
from toolz import partition_all
import time
from zarrify.utils.volume import Volume
from abc import ABCMeta
from numcodecs import Zstd
import logging
import copy

class Mrc3D(Volume):

    def __init__(
        self,
        src_path: str,
        axes: list[str],
        scale: list[float],
        translation: list[float],
        units: list[str],
    ):
        """Construct all the necessary attributes for the proper conversion of tiff to OME-NGFF Zarr.

        Args:
            input_filepath (str): path to source tiff file.
        """
        super().__init__(src_path, axes, scale, translation, units)

        self.memmap = mrcfile.mmap(self.src_path, mode="r")
        self.ndim = self.memmap.data.ndim
        self.shape = self.memmap.data.shape
        self.dtype = self.memmap.data.dtype


    def write_to_zarr(
        self,
        dest: str,
        client: Client,
        zarr_chunks : list[int],
        comp : ABCMeta = Zstd(level=6),
    ):
        """Use mrcfile memmap to access small parts of the mrc file and write them into zarr chunks.

        Args:
            dest_path (str): path to the zarr group where the output dataset is stored.
            client (Client): instance of a dask client
        """
        
        logging.basicConfig(level=logging.INFO, 
                         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        src_path = copy.copy(self.src_path)
        z_arr = self.get_output_array(dest, zarr_chunks, comp)
        
        out_slices = slices_from_chunks(
            normalize_chunks(z_arr.chunks, shape=z_arr.shape)
        )
        out_slices_partitioned = tuple(partition_all(100000, out_slices))

        for idx, part in enumerate(out_slices_partitioned):

            logging.info(f"{idx + 1} / {len(out_slices_partitioned)}")
            start = time.time()
            fut = client.map(lambda v: save_chunk(src_path, z_arr, v), part)
            logging.info(
                f"Submitted {len(part)} tasks to the scheduler in {time.time()- start}s"
            )
            # wait for all the futures to complete
            result = wait(fut)
            logging.info(f"Completed {len(part)} tasks in {time.time() - start}s")

def save_chunk(src_path, z_arr: zarr.Array, chunk_slice: Tuple[slice, ...]):
    """Copies data from a particular part of the input mrc array into a specific chunk of the output zarr array.

    Args:
        z_arr (zarr.core.Array): output zarr array object
        chunk_slice (Tuple[slice, ...]): slice of the mrc array to copy.
    """
    mrc_file = mrcfile.mmap(src_path, mode="r")

    if not (mrc_file.data[chunk_slice] == 0).all():
        z_arr[chunk_slice] = mrc_file.data[chunk_slice]