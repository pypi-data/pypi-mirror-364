import datetime
import logging
import os
import sys

from itertools import product

import ecmwfapi
import pandas as pd
import xarray as xr

from download_toolbox.cli import CDSDownloadArgParser, DownloadArgParser
from download_toolbox.dataset import DatasetConfig
from download_toolbox.download import ThreadedDownloader, DownloaderError
from download_toolbox.location import Location
from download_toolbox.time import Frequency
"""

"""

class ECMWFDatasetConfig(DatasetConfig):
    CDI_MAP = {
        'tas': '2m_temperature',
        'ta': 'temperature',  # 500
        'tos': 'sea_surface_temperature',
        'ps': 'surface_pressure',
        'zg': 'geopotential',  # 250 and 500
        'hus': 'specific_humidity',  # 1000
        'rlds': 'surface_thermal_radiation_downwards',
        'rsds': 'surface_solar_radiation_downwards',
        'uas': '10m_u_component_of_wind',
        'vas': '10m_v_component_of_wind',
        'ua': 'u_component_of_wind',
        'va': 'v_component_of_wind',
        'sic': 'sea_ice_cover',
        'psl': 'mean_sea_level_pressure',
    }

    def __init__(self,
                 identifier: str = None,
                 cdi_map: object = None,
                 **kwargs):
        super().__init__(identifier="cds"
                         if identifier is None else identifier,
                         **kwargs)

        self._cdi_map = CDSDatasetConfig.CDI_MAP
        if cdi_map is not None:
            self._cdi_map.update(cdi_map)

        for var_config in self.variables:
            if var_config.prefix not in self._cdi_map:
                raise RuntimeError("{} requested but we don't have a map to CDS API naming, "
                                   "please select one of: {}".format(var_config.prefix, self._cdi_map))

    @property
    def cdi_map(self):
        return self._cdi_map


class SEAS5DatasetConfig(ECMWFDatasetConfig):
    """
    ECMWF seasonal forecasts (SEAS5)
    https://www.ecmwf.int/en/newsletter/154/meteorology/ecmwfs-new-long-range-forecasting-system-seas5
    """
    def __init__(self,
                 identifier: str = None,
                 cdi_map: object = None,
                 **kwargs):
        super().__init__(identifier="seas5"
                         if identifier is None else identifier,
                         cdi_map=cdi_map,
                         **kwargs)

class HRESDatasetConfig(ECMWFDatasetConfig):
    """
    ECMWF Atmospheric Model high resolution 15-day forecast (Set I - HRES)
    https://www.ecmwf.int/en/forecasts/datasets/set-i
    """
    def __init__(self,
                 identifier: str = None,
                 cdi_map: object = None,
                 **kwargs):
        super().__init__(identifier="seas5"
                         if identifier is None else identifier,
                         cdi_map=cdi_map,
                         **kwargs)


class HRESDownloader(ClimateDownloader):
    """Climate downloader to provide CMIP6 reanalysis data from ESGF APIs

    :param identifier: how to identify this dataset

    """

    PARAM_TABLE = 128

    # Background on the use of forecast and observational data
    # https://confluence.ecmwf.int/pages/viewpage.action?pageId=85402030
    # https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Dateandtimespecification
    HRES_PARAMS = {
        "siconca": (31, "siconc"),  # sea_ice_area_fraction
        "tos": (34, "sst"),  # sea surface temperature (actually
        # sst?)
        "zg": (129, "z"),  # geopotential
        "ta": (130, "t"),  # air_temperature (t)
        "hus": (133, "q"),  # specific_humidity
        "psl": (134, "sp"),  # surface_pressure
        "uas": (165, "u10"),  # 10m_u_component_of_wind
        "vas": (166, "v10"),  # 10m_v_component_of_wind
        "tas": (167, "t2m"),  # 2m_temperature (t2m)
        # https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Meanrates/fluxesandaccumulations
        # https://apps.ecmwf.int/codes/grib/param-db/?id=175
        # https://confluence.ecmwf.int/pages/viewpage.action?pageId=197702790
        #
        # Mean rate/flux parameters in ERA5 (e.g. Table 4 for surface and
        # single levels) provide similar information to accumulations (e.g.
        # Table 3 for surface and single levels), except they are expressed as
        # temporal means, over the same processing periods, and so have units
        # of "per second".
        "rlds": (175, "strd"),
        "rsds": (169, "ssrd"),

        # plev  129.128 / 130.128 / 133.128
        # sfc   31.128 / 34.128 / 134.128 /
        #       165.128 / 166.128 / 167.128 / 169.128 / 177.128

        # ORAS5 variables in param-db (need to consider depth)
        # "thetao":       (151129, "thetao"),
        # "so":           (151130, "so"),
        # Better matches than equivalent X / Y parameters in param-db
        # "uo":           (151131, "uo"),
        # "vo":           (151132, "vo"),
    }

    # https://confluence.ecmwf.int/display/UDOC/Keywords+in+MARS+and+Dissemination+requests
    MARS_TEMPLATE = """
retrieve,
  class=od,
  date={date},
  expver=1,
  levtype={levtype},
  {levlist}param={params},
  step={step},
  stream=oper,
  time=12:00:00,
  type=fc,
  area={area},
  grid=0.25/0.25,
  target="{target}",
  format=netcdf
    """

    def __init__(self, *args, identifier: str = "mars.hres", **kwargs):
        super().__init__(*args, identifier=identifier, **kwargs)

        self._server = ecmwfapi.ECMWFService("mars")

    def _single_download(self, var_names: object, pressures: object,
                         req_dates: object):
        """

        :param var_names:
        :param pressures:
        :param req_dates:
        :return:
        """

        for dt in req_dates:
            assert dt.year == req_dates[0].year

        downloads = []
        levtype = "plev" if pressures else "sfc"

        for req_batch in batch_requested_dates(req_dates, attribute="month"):
            req_batch = sorted(req_batch)
            request_month = req_batch[0].strftime("%Y%m")

            logging.info("Downloading month file {}".format(request_month))

            if req_batch[-1] - datetime.datetime.utcnow().date() == \
                    datetime.timedelta(days=-1):
                logging.warning("Not allowing partial requests at present, "
                                "removing {}".format(req_batch[-1]))
                req_batch = req_batch[:-1]

            request_target = os.path.join(
                self.base_path, self.hemisphere_str[0],
                "{}.{}.nc".format(levtype, request_month))

            os.makedirs(os.path.dirname(request_target), exist_ok=True)

            request = self.mars_template.format(
                area="/".join([str(s) for s in self.hemisphere_loc]),
                date="/".join([el.strftime("%Y%m%d") for el in req_batch]),
                levtype=levtype,
                levlist="levelist={},\n  ".format(pressures)
                if pressures else "",
                params="/".join([
                    "{}.{}".format(self.params[v][0], self.param_table)
                    for v in var_names
                ]),
                target=request_target,
                # We are only allowed date prior to -24 hours ago, dynamically
                # retrieve if date is today
                # TODO: too big - step="/".join([str(i) for i in range(24)]),
                step=0,
            )

            if not os.path.exists(request_target):
                logging.debug("MARS REQUEST: \n{}\n".format(request))

                try:
                    self._server.execute(request, request_target)
                except ecmwfapi.api.APIException:
                    logging.exception("Could not complete ECMWF request: {}")
                else:
                    downloads.append(request_target)
            else:
                logging.debug("Already have {}".format(request_target))
                downloads.append(request_target)

        logging.debug("Files downloaded: {}".format(downloads))

        ds = xr.open_mfdataset(downloads)
        ds = ds.resample(time='1D', keep_attrs=True).mean(keep_attrs=True)

        for var_name, pressure in product(
                var_names,
                pressures.split('/') if pressures else [None]):
            var = var_name if not pressure else \
                "{}{}".format(var_name, pressure)

            da = getattr(ds, self.params[var_name][1])

            if pressure:
                da = da.sel(level=int(pressure))

            self.save_temporal_files(var, da)

        ds.close()

        if self.delete:
            for downloaded_file in downloads:
                if os.path.exists(downloaded_file):
                    logging.info("Removing {}".format(downloaded_file))
                    os.unlink(downloaded_file)

    def download(self):
        """

        """
        logging.info("Building request(s), downloading and daily averaging "
                     "from {} API".format(self.identifier.upper()))

        sfc_vars = [
            var for idx, var in enumerate(self.var_names)
            if not self.levels[idx]
        ]
        level_vars = [
            var for idx, var in enumerate(self.var_names) if self.levels[idx]
        ]
        levels = "/".join([
            str(s)
            for s in sorted(set([p for ps in self.levels if ps for p in ps]))
        ])

        # req_dates = self.filter_dates_on_data()

        dates_per_request = \
            batch_requested_dates(self._dates,
                                  attribute=self.group_dates_by)

        for req_batch in dates_per_request:
            if len(sfc_vars) > 0:
                self._single_download(sfc_vars, None, req_batch)

            if len(level_vars) > 0:
                self._single_download(level_vars, levels, req_batch)

        logging.info("{} daily files downloaded".format(
            len(self._files_downloaded)))

    @property
    def mars_template(self):
        return getattr(self, "MARS_TEMPLATE")

    @property
    def params(self):
        return getattr(self, "HRES_PARAMS")

    @property
    def param_table(self):
        return getattr(self, "PARAM_TABLE")

class SEASDownloader(HRESDownloader):
    MARS_TEMPLATE = """
retrieve,
    class=od,
    date={date},
    expver=1,
    levtype={levtype},
    method=1,
    number=0/1/2/3/4/5/6/7/8/9/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24,
    origin=ecmf,
    {levlist}param={params},
    step=0/to/2232/by/24,
    stream=mmsf,
    system=5,
    time=00:00:00,
    type=fc,
    target="{target}",
    format=netcdf,
    grid=0.25/0.25,
    area={area}"""

    def _single_download(self, var_names: object, pressures: object,
                         req_dates: object):
        """

        :param var_names:
        :param pressures:
        :param req_dates:
        :return:
        """

        for dt in req_dates:
            assert dt.year == req_dates[0].year

        downloads = []
        levtype = "plev" if pressures else "sfc"

        for req_date in req_dates:
            request_day = req_date.strftime("%Y%m%d")

            logging.info("Downloading daily file {}".format(request_day))

            request_target = os.path.join(
                self.base_path, self.hemisphere_str[0],
                "{}.{}.nc".format(levtype, request_day))
            os.makedirs(os.path.dirname(request_target), exist_ok=True)

            request = self.mars_template.format(
                area="/".join([str(s) for s in self.hemisphere_loc]),
                date=req_date.strftime("%Y-%m-%d"),
                levtype=levtype,
                levlist="levelist={},\n  ".format(pressures)
                if pressures else "",
                params="/".join([
                    "{}.{}".format(self.params[v][0], self.param_table)
                    for v in var_names
                ]),
                target=request_target,
            )

            if not os.path.exists(request_target):
                logging.debug("MARS REQUEST: \n{}\n".format(request))

                try:
                    self._server.execute(request, request_target)
                except ecmwfapi.api.APIException:
                    logging.exception("Could not complete ECMWF request: {}")
                else:
                    downloads.append(request_target)
            else:
                logging.debug("Already have {}".format(request_target))
                downloads.append(request_target)

        logging.debug("Files downloaded: {}".format(downloads))

        for download_filename in downloads:
            logging.info("Processing {}".format(download_filename))
            ds = xr.open_dataset(download_filename)
            ds = ds.mean("number")

            for var_name, pressure in product(
                    var_names,
                    pressures.split('/') if pressures else [None]):
                var = var_name if not pressure else \
                    "{}{}".format(var_name, pressure)

                da = getattr(ds, self.params[var_name][1])

                if pressure:
                    da = da.sel(level=int(pressure))

                self.save_temporal_files(var, da, date_format="%Y%m%d")

            ds.close()

        if self.delete:
            for downloaded_file in downloads:
                if os.path.exists(downloaded_file):
                    logging.info("Removing {}".format(downloaded_file))
                    os.unlink(downloaded_file)

    def save_temporal_files(self, var, da, date_format=None, freq=None):
        """

        :param var:
        :param da:
        :param date_format:
        :param freq:
        """
        var_folder = self.get_data_var_folder(var)

        req_date = pd.to_datetime(da.time.values[0])
        latlon_path, regridded_name = \
            self.get_req_filenames(var_folder,
                                   req_date,
                                   date_format=date_format)

        logging.info("Retrieving and saving {}".format(latlon_path))
        da.compute()
        da.to_netcdf(latlon_path)

        if not os.path.exists(regridded_name):
            self._files_downloaded.append(latlon_path)


def main(identifier, extra_kwargs=None):
    args = download_args()

    logging.info("ECMWF {} Data Downloading".format(identifier))
    cls = getattr(sys.modules[__name__], "{}Downloader".format(identifier))

    if extra_kwargs is None:
        extra_kwargs = dict()

    instance = cls(
        identifier="mars.{}".format(identifier.lower()),
        var_names=args.vars,
        dates=[
            pd.to_datetime(date).date()
            for date in pd.date_range(args.start_date, args.end_date, freq="D")
        ],
        delete_tempfiles=args.delete,
        levels=args.levels,
        north=args.hemisphere == "north",
        south=args.hemisphere == "south",
        **extra_kwargs)
    instance.download()
    instance.regrid()


def seas_main():
    main("SEAS", dict(group_dates_by="day",))


def hres_main():
    main("HRES")