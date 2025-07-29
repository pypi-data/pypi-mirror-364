# pylint: disable=unused-import
"""
=========
netcdf-convert.py
=========

Functions related to converting a NetCDF file to other formats.
"""

import os
import pathlib
from logging import Logger
from os.path import join as path_join, basename
from tempfile import TemporaryDirectory
from typing import List

import rasterio
import rioxarray  # noqa
import xarray as xr
from rasterio import CRS
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from rioxarray.exceptions import DimensionError, InvalidDimensionOrder
from pyproj.crs import CRS as pyCRS
from pyproj.exceptions import CRSError
from net2cog.utilities import (
    resolve_relative_path,
    Net2CogError,
    reorder_dimensions,
    is_valid_shape,
    is_valid_dtype,
    is_valid_spatial_dimensions,
)

EXCLUDE_VARS = ['lon', 'lat', 'longitude', 'latitude', 'time']


def _rioxr_swapdims(netcdf_xarray):
    netcdf_xarray.coords['y'] = ('lat', netcdf_xarray.lat)
    netcdf_xarray.coords['x'] = ('lon', netcdf_xarray.lon)

    return netcdf_xarray.swap_dims({'lat': 'y', 'lon': 'x'})


# pylint: disable=R0914
def _write_cogtiff(
    output_directory: str,
    nc_xarray: xr.DataTree,
    variable_path: str,
    logger: Logger,
) -> str | None:
    """
    This function converts a variable inside a NetCDF file into a
    cloud optimized geotiff.

    Parameters
    ----------
    output_directory : str
        Path to temporary directory where output GeoTIFFs will be stored before
        being staged in S3.
        example :/home/dockeruser/converter/podaac/netcdf_converter/temp/
            netcdf_converter/
            RSS_smap_SSS_L3_8day_running_2020_037_FNL_v04.0_test
    nc_xarray : xarray.DataTree
        xarray DataTree loaded from NetCDF file. This represents the whole
        file.
    variable_path: str
        Full of the variable within the file to convert.
    logger : logging.Logger
        Python Logger object for emitting log messages.

    Notes
    -----
    - Assumption that 0 is always on the prime meridian/equator.
    - The output name for converted GeoTIFFs is `<variable path>.tif`, with any
      slashes replaced with underscores.
    """

    logger.debug("NetCDF Var: %s", variable_path)

    if variable_path in EXCLUDE_VARS:
        logger.debug(f"Variable {variable_path} is excluded. Will not produce COG")
        return None

    output_basename = f'{variable_path}.tif'.lstrip('/').replace('/', '_')
    output_file_name = path_join(output_directory, output_basename)

    with TemporaryDirectory() as tempdir:
        temp_file_name = path_join(tempdir, output_basename)

        try:
            if not is_valid_spatial_dimensions(
                nc_xarray[variable_path],
                variable_path,
                logger
            ):
                # The variable being processed does not have spatial dimensions:
                raise Net2CogError(
                    variable_path,
                    f'{variable_path} does not have spatial dimensions such as '
                    'lat / lon or x / y',
                )
            nc_xarray[variable_path].rio.to_raster(temp_file_name)
        except KeyError as error:
            # Occurs when trying to locate a variable that is not in the DataTree
            raise Net2CogError(
                variable_path,
                f"No variable named '{variable_path}'."
            ) from error
        except (LookupError, TypeError) as err:
            logger.info("Variable %s cannot be converted to tif: %s", variable_path, err)
            raise Net2CogError(variable_path, err) from err
        except InvalidDimensionOrder as dmerr:
            try:
                logger.info("%s: reorder dimensions...", dmerr)
                nc_xarray_tmp = reorder_dimensions(nc_xarray, variable_path)
                nc_xarray_tmp[variable_path].rio.to_raster(temp_file_name)
            except (RuntimeError, Exception, Net2CogError) as runerr:
                logger.info("Variable %s cannot be converted to tif: %s", variable_path, runerr)
                raise Net2CogError(variable_path, runerr) from runerr
        except DimensionError as dmerr:
            try:
                logger.info("%s: No x or y xarray dimensions, adding them...", dmerr)
                nc_xarray_tmp = _rioxr_swapdims(nc_xarray)
                nc_xarray_tmp[variable_path].rio.to_raster(temp_file_name)
            except RuntimeError as runerr:
                logger.info("Variable %s cannot be converted to tif: %s", variable_path, runerr)
                raise Net2CogError(variable_path, runerr) from runerr
            except Exception as aerr:  # pylint: disable=broad-except
                logger.info("Variable %s cannot be converted to tif: %s", variable_path, aerr)
                raise Net2CogError(variable_path, aerr) from aerr

        # Option to add additional GDAL config settings
        # config = dict(GDAL_NUM_THREADS="ALL_CPUS", GDAL_TIFF_OVR_BLOCKSIZE="128")
        # with rasterio.Env(**config):

        logger.info("Starting conversion... %s", output_file_name)

        # default CRS setting
        # crs = rasterio.crs.CRS({"init": "epsg:3857"})

        with rasterio.open(temp_file_name, mode='r+') as src_dataset:
            # if src_dst.crs is None:
            #     src_dst.crs = crs
            src_dataset.crs = get_crs_from_grid_mapping(
                nc_xarray, variable_path, logger
            )
            dst_profile = cog_profiles.get("deflate")
            cog_translate(
                src_dataset,
                output_file_name,
                dst_profile,
                use_cog_driver=True
            )

    logger.info("Finished conversion, writing variable: %s", output_file_name)
    logger.info("NetCDF conversion complete. Returning COG generated.")
    return output_file_name


def get_all_data_variables(
    root_datatree: xr.DataTree,
    logger: Logger,
) -> list[str]:
    """Traverse tree and retrieve all data variables in all groups.

    Parameters
    ----------
    root_datatree : xarray.DataTree
        DataTree object representing the root group of the NetCDF-4 file.

    Returns
    -------
    list[str]
        A list of paths to all variables in the `data_vars` property of any
        node in the DataTree. These variables are filtered to remove any
        variables that are 1-D, attribute-only (e.g., CRS definitions),
        dtype = string(S1/S2), or variable without dimensions.

    """
    data_variables = []
    for group_path, group in root_datatree.to_dict().items():
        data_variables.extend([
            '/'.join([group_path.rstrip('/'), str(data_var)])
            for data_var in group.data_vars
        ])

    return [
        data_variable
        for data_variable in data_variables
        if is_valid_shape(root_datatree[data_variable], data_variable, logger)
        and is_valid_dtype(root_datatree[data_variable], data_variable, logger)
        and is_valid_spatial_dimensions(
            root_datatree[data_variable], data_variable, logger
        )
    ]


def get_crs_from_grid_mapping(
    nc_xarray: xr.DataTree,
    variable_path: str,
    logger: Logger,
) -> CRS:
    """Check the metadata attributes for the variable to find the associated
    grid mapping variable.  If the grid mapping variable, as referred to in the
    grid_mapping CF-Convention metadata attribute, does not exist then
    default to "+proj=latlong".

    Parameters
    ----------
    nc_xarray : xarray.DataTree
        xarray DataTree loaded from NetCDF file. This represents the whole
        file.
    variable_path: str
        Full of the variable within the file to convert.
    logger : logging.Logger
        Python Logger object for emitting log messages.

    Returns
    -------
    csr
        Returns a `CRS` object corresponding to a grid mapping variable.

    """
    # Default CRS EPSG:4326
    crs = CRS.from_epsg(4326)

    grid_mapping_attribute = nc_xarray[variable_path].attrs.get("grid_mapping")

    if grid_mapping_attribute is not None:
        cf_reference_attribute = resolve_relative_path(
            nc_xarray, variable_path, grid_mapping_attribute
        )

        try:
            if cf_reference_attribute is not None:
                cf_parameters = nc_xarray[cf_reference_attribute].attrs
                crs = pyCRS.from_cf(cf_parameters)
                logger.info("CRS: %s", crs)
        except CRSError as error:
            raise Net2CogError(
                variable_path, f"An unsupported target CRS. Use default CRS '{crs}'."
            ) from error

    return crs


def netcdf_converter(
    input_nc_file: pathlib.Path,
    output_directory: pathlib.Path,
    var_list: list[str],
    logger: Logger,
) -> List[str]:
    """Primary function for beginning NetCDF conversion using rasterio,
    rioxarray and xarray

    Parameters
    ----------
    input_nc_file : pathlib.Path
        Path to  NetCDF file to process
    output_directory : pathlib.Path
        Path to temporary directory into which results will be placed before
        staging in S3.
    var_list : list[str]
        List of variable names to be converted to various single band cogs,
        ex: ['gland', 'fland', 'sss_smap']. For hierarchical granules, these
        names will be full paths to the variable location in the file, omitting
        the leading slash, e.g.: 'Grid/precipitationCal'. If this list is
        empty, it is assumed that all data variables have been requested.
    logger : logging.Logger
        Python Logger object for emitting log messages.

    Notes
    -----
    Currently uses local file paths, no s3 paths
    """
    logger.info("Input file name: %s", input_nc_file)

    netcdf_file = os.path.abspath(input_nc_file)
    logger.debug('NetCDF Path: %s', netcdf_file)

    if netcdf_file.endswith(('.nc', '.nc4', 'h5')):
        logger.info("Reading %s", basename(netcdf_file))

        input_datatree = xr.open_datatree(netcdf_file)

        if not var_list:
            # Empty list means "all" variables, so get all variables in
            # the `xarray.DataTree`.
            var_list = get_all_data_variables(input_datatree, logger)

        raw_output_files = [
            _write_cogtiff(output_directory, input_datatree, variable_name, logger)
            for variable_name in var_list
        ]
        # Remove None returns, e.g., for excluded variables
        output_files = [
            output_file
            for output_file in raw_output_files
            if output_file is not None
        ]

    else:
        logger.info("Not a NetCDF file; Skipped file: %s", netcdf_file)
        output_files = []

    return output_files
