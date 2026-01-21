# from typing import List, Dict, Any
# import numpy as np
# import xarray as xr

# from gnssvodpy.signal_frequency_mapping.signal_mapping import SignalIDMapper
# from gnssvodpy.signal_frequency_mapping.gnss_systems import (GLONASS, GPS,
#                                                              GALILEO, BEIDOU,
#                                                              IRNSS, SBAS, QZSS)
# from gnssvodpy.globals import AGGREGATE_GLONASS_FDMA

# class IcechunkPreprocessor:
#     """
#     Handles preprocessing of RINEX-converted datasets before writing to Icechunk:
#     - pad `sid` dimension
#     - normalize `sid` dtype to object
#     - add future data_vars placeholder (from metadata)
#     - strip conflicting fillvalue attrs
#     """

#     @staticmethod
#     def pad_to_global_sid(ds: xr.Dataset) -> xr.Dataset:
#         '''
#         Pad the dataset to include all SIDs from the global sid list. This is necessary\
#             because different RINEX files may contain different sets of satellites, \
#             and we want to ensure consistency across datasets. It is also a prerequisite\
#             for appending to an Icechunk repository, which requires consistent dimensions.

#         Parameters
#         ----------
#         ds : xr.Dataset
#             The input dataset to be padded.

#         Returns
#         -------
#         xr.Dataset
#             The padded dataset with all SIDs from the global sid list.
#         '''
#         mapper = SignalIDMapper()
#         systems = {
#             "G": GPS(),
#             "E": GALILEO(),
#             "R": GLONASS(aggregate_fdma=AGGREGATE_GLONASS_FDMA),
#             "C": BEIDOU(),
#             "I": IRNSS(),
#             "S": SBAS(),
#             "J": QZSS(),
#         }
#         sids = [
#             f"{sv}|{band}|{code}"
#             for sys_letter, bands in mapper.SYSTEM_BANDS.items()
#             for _, band in bands.items() for sv in systems[sys_letter].svs
#             for code in systems[sys_letter].BAND_CODES.get(band, ["X"])
#         ]
#         sids += [f"{sv}|X1|X" for sys in systems.values() for sv in sys.svs]
#         sids = sorted(sids)

#         return ds.reindex({"sid": sids}, fill_value=np.nan)

#     # @staticmethod
#     # def normalize_sid_dtype(ds: xr.Dataset) -> xr.Dataset:
#     #     """
#     #     NOTE: might be unnecessary if `pad_to_global_sid` is adapated accordingly.
#     #     Ensure `sid` coordinate uses object dtype (avoids <U... warnings in Zarr).

#     #     Parameters
#     #     ----------
#     #     ds : xr.Dataset
#     #         The dataset with `sid` coordinate.

#     #     Returns
#     #     -------
#     #     xr.Dataset
#     #         Dataset with `sid` normalized to object dtype.
#     #     """
#     #     if "sid" in ds.coords and ds.sid.dtype == 'object':
#     #         # Convert object back to string dtype
#     #         clean_values = [
#     #             str(val) if val is not None else '' for val in ds.sid.values
#     #         ]
#     #         max_len = max(len(s) for s in clean_values) if clean_values else 1
#     #         string_dtype = f'U{max(max_len, 1)}'
#     #         ds = ds.assign_coords({
#     #             'sid':
#     #             (ds.sid.dims, np.array(clean_values,
#     #                                    dtype=string_dtype), ds.sid.attrs)
#     #         })
#     #     return ds

#     @staticmethod
#     def normalize_sid_dtype(ds: xr.Dataset) -> xr.Dataset:
#         """Ensure sid uses object dtype (avoids issues with Icechunk dtypes)."""
#         if "sid" in ds.coords and ds.sid.dtype.kind == "U":
#             new_sid = ds.sid.values.astype(object)
#             ds = ds.assign_coords(
#                 sid=xr.Variable("sid", new_sid, ds.sid.attrs))
#         return ds

#     @staticmethod
#     def strip_fillvalue(ds: xr.Dataset) -> xr.Dataset:
#         '''
#         Remove any _FillValue attributes from the dataset variables to avoid conflicts\
#             when writing to Icechunk.

#         Parameters
#         ----------
#         ds : xr.Dataset
#             The input dataset from which to strip _FillValue attributes.

#         Returns
#         -------
#         xr.Dataset
#             The dataset with _FillValue attributes removed.
#         '''

#         for v in ds.data_vars:
#             ds[v].attrs.pop("_FillValue", None)
#             ds[v].encoding.pop("_FillValue", None)
#         return ds

#     @staticmethod
#     def add_future_datavars(
#         ds: xr.Dataset,
#         var_config: Dict[str, Dict[str, Any]],
#     ) -> xr.Dataset:
#         '''
#         Add additional data variables to the dataset based on the provided configuration.

#         Parameters
#         ----------
#         ds : xr.Dataset
#             The input dataset to which new variables will be added.
#         var_config : Dict[str, Dict[str, Any]]
#             A dictionary where keys are variable names and values are dictionaries \
#                 containing 'fill_value', 'dtype', and 'attrs' for each variable.\
#                 Examples: `gnssvodpy.rinexreader.metadata.DATAVARS_TO_BE_FILLED`.

#         Returns
#         -------
#         xr.Dataset
#             The dataset with new variables added.
#         '''

#         n_epochs, n_sids = ds.sizes["epoch"], ds.sizes["sid"]
#         for name, cfg in var_config.items():
#             if name not in ds:
#                 arr = np.full(
#                     (n_epochs, n_sids),
#                     cfg["fill_value"],
#                     dtype=cfg["dtype"],
#                 )
#                 ds[name] = (("epoch", "sid"), arr, cfg["attrs"])
#         return ds

from typing import Any, Dict, List

import numpy as np
import xarray as xr

from gnssvodpy.globals import AGGREGATE_GLONASS_FDMA
from gnssvodpy.signal_frequency_mapping.gnss_systems import (
    BEIDOU,
    GALILEO,
    GLONASS,
    GPS,
    IRNSS,
    QZSS,
    SBAS,
)
from gnssvodpy.signal_frequency_mapping.signal_mapping import SignalIDMapper


class IcechunkPreprocessor:
    """
    Handles preprocessing of RINEX-converted datasets before writing to Icechunk.
    Provides helpers to:
    - Pad datasets to a global sid list
    - Normalize sid dtypes
    - Add placeholder variables
    - Strip conflicting _FillValue attributes
    - Map auxiliary datasets from sv → sid
    """

    @staticmethod
    def create_sv_to_sid_mapping(svs: list[str]) -> dict[str, list[str]]:
        """
        Build mapping from each sv to its possible SIDs.
        Adds `X1|X` placeholder SIDs as well.

        Parameters
        ----------
        svs : List[str]
            List of space vehicles (e.g., ["G01", "E02"])

        Returns
        -------
        Dict[str, List[str]]
            Mapping from sv → list of SIDs
        """
        mapper = SignalIDMapper()
        systems = {
            "G": GPS(),
            "E": GALILEO(),
            "R": GLONASS(aggregate_fdma=AGGREGATE_GLONASS_FDMA),
            "C": BEIDOU(),
            "I": IRNSS(),
            "S": SBAS(),
            "J": QZSS(),
        }

        sv_to_sids: dict[str, list[str]] = {}
        for sv in svs:
            sys_letter = sv[0]
            if sys_letter not in systems:
                continue

            system = systems[sys_letter]
            sids = []
            if sys_letter in mapper.SYSTEM_BANDS:
                for _, band in mapper.SYSTEM_BANDS[sys_letter].items():
                    codes = system.BAND_CODES.get(band, ["X"])
                    sids.extend(f"{sv}|{band}|{code}" for code in codes)
            sids.append(f"{sv}|X1|X")  # aux observation

            sv_to_sids[sv] = sorted(sids)

        return sv_to_sids

    @staticmethod
    def map_aux_sv_to_sid(aux_ds: xr.Dataset,
                          fill_value: float = np.nan) -> xr.Dataset:
        """
        Transform auxiliary dataset from sv → sid dimension.

        Each sv in the dataset is expanded to all its possible SIDs.
        Values are replicated across SIDs for the same satellite.

        Parameters
        ----------
        aux_ds : xr.Dataset
            Dataset with 'sv' dimension
        fill_value : float, default np.nan
            Fill value for missing entries

        Returns
        -------
        xr.Dataset
            Dataset with 'sid' dimension replacing 'sv'
        """
        svs = aux_ds["sv"].values.tolist()
        sv_to_sids = IcechunkPreprocessor.create_sv_to_sid_mapping(svs)
        all_sids = sorted(
            {sid
             for sv in svs
             for sid in sv_to_sids.get(sv, [])})

        new_data_vars = {}
        for name, arr in aux_ds.data_vars.items():
            if "sv" in arr.dims:
                sv_dim = arr.dims.index("sv")
                new_shape = list(arr.shape)
                new_shape[sv_dim] = len(all_sids)
                expanded = np.full(new_shape, fill_value, dtype=arr.dtype)

                for sv_idx, sv in enumerate(svs):
                    for sid in sv_to_sids.get(sv, []):
                        sid_idx = all_sids.index(sid)
                        if sv_dim == 0:
                            expanded[sid_idx, ...] = arr.values[sv_idx, ...]
                        elif sv_dim == 1:
                            expanded[..., sid_idx] = arr.values[..., sv_idx]
                        else:
                            slices_new = [slice(None)] * len(new_shape)
                            slices_old = [slice(None)] * len(arr.shape)
                            slices_new[sv_dim] = sid_idx
                            slices_old[sv_dim] = sv_idx
                            expanded[tuple(slices_new)] = arr.values[tuple(
                                slices_old)]

                new_dims = list(arr.dims)
                new_dims[sv_dim] = "sid"
                new_data_vars[name] = (tuple(new_dims), expanded, arr.attrs)
            else:
                new_data_vars[name] = arr

        # Coordinates
        new_coords = {
            **{
                k: v
                for k, v in aux_ds.coords.items() if k != "sv"
            },
            "sid": ("sid", all_sids),
        }

        new_ds = xr.Dataset(new_data_vars,
                            coords=new_coords,
                            attrs=aux_ds.attrs.copy())

        # Coordinates
        new_coords = {
            **{
                k: v
                for k, v in aux_ds.coords.items() if k != "sv"
            },
            "sid": ("sid", all_sids),
        }

        return new_ds

    @staticmethod
    def pad_to_global_sid(ds: xr.Dataset) -> xr.Dataset:
        """
        Pad dataset so it has all possible SIDs across all constellations.
        Ensures consistent sid dimension for appending to Icechunk.
        """
        from gnssvodpy.globals import KEEP_SIDS

        mapper = SignalIDMapper()
        systems = {
            "G": GPS(),
            "E": GALILEO(),
            "R": GLONASS(aggregate_fdma=AGGREGATE_GLONASS_FDMA),
            "C": BEIDOU(),
            "I": IRNSS(),
            "S": SBAS(),
            "J": QZSS(),
        }
        sids = [
            f"{sv}|{band}|{code}"
            for sys_letter, bands in mapper.SYSTEM_BANDS.items()
            for _, band in bands.items() for sv in systems[sys_letter].svs
            for code in systems[sys_letter].BAND_CODES.get(band, ["X"])
        ]
        sids = sorted(sids)

        if KEEP_SIDS is not None and len(KEEP_SIDS) > 0:
            sids = sorted(set(sids).intersection(set(KEEP_SIDS)))

        return ds.reindex({"sid": sids}, fill_value=np.nan)

    @staticmethod
    def normalize_sid_dtype(ds: xr.Dataset) -> xr.Dataset:
        """Ensure sid coordinate uses object dtype."""
        if ds is None:
            return ds
        if "sid" in ds.coords and ds.sid.dtype.kind == "U":
            ds = ds.assign_coords(sid=xr.Variable(
                "sid", ds.sid.values.astype(object), ds.sid.attrs))
        return ds

    @staticmethod
    def strip_fillvalue(ds: xr.Dataset) -> xr.Dataset:
        """Remove _FillValue attrs/encodings (avoids Icechunk conflicts)."""
        if ds is None:
            return ds
        for v in ds.data_vars:
            ds[v].attrs.pop("_FillValue", None)
            ds[v].encoding.pop("_FillValue", None)
        return ds

    @staticmethod
    def add_future_datavars(
            ds: xr.Dataset, var_config: dict[str, dict[str,
                                                       Any]]) -> xr.Dataset:
        """Add placeholder data variables from a configuration dictionary."""
        n_epochs, n_sids = ds.sizes["epoch"], ds.sizes["sid"]
        for name, cfg in var_config.items():
            if name not in ds:
                arr = np.full((n_epochs, n_sids),
                              cfg["fill_value"],
                              dtype=cfg["dtype"])
                ds[name] = (("epoch", "sid"), arr, cfg["attrs"])
        return ds

    @staticmethod
    def prep_aux_ds(aux_ds: xr.Dataset,
                    fill_value: float = np.nan) -> xr.Dataset:
        """
        Preprocess auxiliary dataset before writing to Icechunk:
        - Convert sv → sid dimension
        - Normalize sid dtype
        - Strip _FillValue attrsprep_aux_ds

        Parameters
        ----------
        aux_ds : xr.Dataset
            Dataset with 'sv' dimension
        fill_value : float, default np.nan
            Fill value for missing entries

        Returns
        -------
        xr.Dataset
            Cleaned dataset ready for Icechunk
        """
        ds = IcechunkPreprocessor.map_aux_sv_to_sid(aux_ds, fill_value)
        ds = IcechunkPreprocessor.pad_to_global_sid(ds)
        ds = IcechunkPreprocessor.normalize_sid_dtype(ds)
        ds = IcechunkPreprocessor.strip_fillvalue(ds)
        return ds
