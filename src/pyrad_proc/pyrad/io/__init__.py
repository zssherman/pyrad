"""
==================================
Input and output (:mod:`pyrad.io`)
==================================

.. currentmodule:: pyrad.io

Functions to read and write data and configuration files.

Reading configuration files
===========================

.. autosummary::
    :toctree: generated/

    read_config

Reading radar data
==================

.. autosummary::
    :toctree: generated/

    get_data

Reading cosmo data
==================

.. autosummary::
    :toctree: generated/

    cosmo2radar_data
    cosmo2radar_coord
    hzt2radar_data
    hzt2radar_coord
    get_cosmo_fields
    get_iso0_field
    read_cosmo_data
    read_cosmo_coord
    read_hzt_data

Reading other data
==================

.. autosummary::
    :toctree: generated/

    read_last_state
    read_status
    read_rad4alp_cosmo
    read_rad4alp_vis
    read_colocated_gates
    read_colocated_data
    read_timeseries
    read_ts_cum
    read_monitoring_ts
    read_intercomp_scores_ts
    get_sensor_data
    read_smn
    read_smn2
    read_disdro_scattering
    read_sun_hits
    read_sun_hits_multiple_days
    read_sun_retrieval
    read_solar_flux
    read_selfconsistency
    read_antenna_pattern

Writing data
==================

.. autosummary::
    :toctree: generated/

    send_msg
    write_alarm_msg
    write_last_state
    write_smn
    write_colocated_gates
    write_colocated_data
    write_colocated_data_time_avg
    write_timeseries
    write_ts_polar_data
    write_ts_cum
    write_monitoring_ts
    write_intercomp_scores_ts
    write_sun_hits
    write_sun_retrieval
    write_cdf
    write_rhi_profile
    write_field_coverage


Auxiliary functions
===================

.. autosummary::
    :toctree: generated/

    map_hydro
    get_save_dir
    make_filename
    get_datetime
    get_datasetfields
    get_file_list
    get_datatype_fields
    get_field_unit
    get_fieldname_pyart
    get_fieldname_cosmo
    generate_field_name_str
    find_raw_cosmo_file
    find_hzt_file
    add_field
    interpol_field
    get_new_rainbow_file_name

Trajectory
==========

.. autosummary::
    :toctree: generated/

    Trajectory

TimeSeries
==========

.. autosummary::
    :toctree: generated/

    TimeSeries

"""

from .config import read_config

from .read_data_radar import get_data, add_field, interpol_field

from .read_data_cosmo import read_cosmo_data, read_cosmo_coord
from .read_data_cosmo import cosmo2radar_data, cosmo2radar_coord
from .read_data_cosmo import get_cosmo_fields

from .read_data_hzt import read_hzt_data, hzt2radar_data, hzt2radar_coord
from .read_data_hzt import get_iso0_field

from .read_data_other import read_status, read_rad4alp_cosmo, read_rad4alp_vis
from .read_data_other import read_timeseries, read_monitoring_ts, read_ts_cum
from .read_data_other import get_sensor_data, read_smn, read_disdro_scattering
from .read_data_other import read_smn2, read_intercomp_scores_ts
from .read_data_other import read_sun_hits, read_sun_hits_multiple_days
from .read_data_other import read_sun_retrieval, read_solar_flux
from .read_data_other import read_selfconsistency, read_colocated_gates
from .read_data_other import read_colocated_data, read_antenna_pattern
from .read_data_other import read_last_state

from .write_data import write_smn, write_ts_polar_data, write_ts_cum
from .write_data import write_monitoring_ts, write_intercomp_scores_ts
from .write_data import write_sun_hits, write_sun_retrieval
from .write_data import write_colocated_gates, write_colocated_data
from .write_data import write_colocated_data_time_avg, write_cdf
from .write_data import write_rhi_profile, write_field_coverage
from .write_data import write_last_state, write_alarm_msg, send_msg

from .io_aux import get_save_dir, make_filename, get_new_rainbow_file_name
from .io_aux import get_datetime, get_dataset_fields, map_hydro
from .io_aux import get_file_list, get_datatype_fields
from .io_aux import get_fieldname_pyart, get_field_unit, get_fieldname_cosmo
from .io_aux import generate_field_name_str, find_raw_cosmo_file
from .io_aux import find_hzt_file

from .trajectory import Trajectory

from .timeseries import TimeSeries

__all__ = [s for s in dir() if not s.startswith('_')]
