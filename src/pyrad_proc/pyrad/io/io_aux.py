"""
pyrad.io.io_aux
===============

Auxiliary functions for reading/writing files

.. autosummary::
    :toctree: generated/

    map_hydro
    map_Doppler
    get_save_dir
    make_filename
    generate_field_name_str
    get_datatype_metranet
    get_datatype_odim
    get_fieldname_pyart
    get_fieldname_cosmo
    get_field_unit
    get_field_name
    get_file_list
    get_trtfile_list
    get_scan_list
    get_new_rainbow_file_name
    get_datatype_fields
    get_dataset_fields
    get_datetime
    find_raw_cosmo_file
    find_cosmo_file
    find_hzt_file
    find_rad4alpcosmo_file
    _get_datetime

"""

import os
import glob
import re
import datetime

from warnings import warn
from copy import deepcopy
import numpy as np

from pyart.config import get_metadata

def map_hydro(hydro_data_op):
    """
    maps the operational hydrometeor classification identifiers to the ones
    used by Py-ART

    Parameters
    ----------
    hydro_data_op : numpy array
        The operational hydrometeor classification data

    Returns
    -------
    hydro_data_py : numpy array
        The pyart hydrometeor classification data

    """
    hydro_data_py = deepcopy(hydro_data_op)
    hydro_data_py[hydro_data_op == 25] = 2  # crystals
    hydro_data_py[hydro_data_op == 50] = 1  # aggregate
    hydro_data_py[hydro_data_op == 75] = 3  # light rain
    hydro_data_py[hydro_data_op == 100] = 5  # rain
    hydro_data_py[hydro_data_op == 125] = 4  # graupel
    hydro_data_py[hydro_data_op == 150] = 7  # wet snow
    hydro_data_py[hydro_data_op == 175] = 9  # ice hail
    hydro_data_py[hydro_data_op == 200] = 8  # melting hail

    return hydro_data_py


def map_Doppler(Doppler_data_bin, Nyquist_vel):
    """
    maps the binary METRANET Doppler data to actual Doppler velocity

    Parameters
    ----------
    Doppler_data_bin : numpy array
        The binary METRANET data

    Returns
    -------
    Doppler_data : numpy array
        The Doppler veloctiy in [m/s]

    """
    Doppler_data = (Doppler_data_bin-128.)/127.*Nyquist_vel

    return Doppler_data


def get_save_dir(basepath, procname, dsname, prdname, timeinfo=None,
                 timeformat='%Y-%m-%d', create_dir=True):
    """
    obtains the path to a product directory and eventually creates it

    Parameters
    ----------
    basepath : str
        product base path
    procname : str
        name of processing space
    dsname : str
        data set name
    prdname : str
        product name
    timeinfo : datetime
        time info to generate the date directory. If None there is no time
        format in the path
    timeformat : str
        Optional. The time format.
    create_dir : boolean
        If True creates the directory

    Returns
    -------
    savedir : str
        path to product

    """
    if timeinfo is None:
        savedir = basepath+procname+'/'+dsname+'/'+prdname+'/'
    else:
        daydir = timeinfo.strftime(timeformat)
        savedir = basepath+procname+'/'+daydir+'/'+dsname+'/'+prdname+'/'

    if create_dir is False:
        return savedir

    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    return savedir


def make_filename(prdtype, dstype, dsname, ext_list, prdcfginfo=None,
                  timeinfo=None, timeformat='%Y%m%d%H%M%S',
                  runinfo=None):
    """
    creates a product file name

    Parameters
    ----------
    timeinfo : datetime
        time info to generate the date directory
    prdtype : str
        product type, i.e. 'ppi', etc.
    dstype : str
        data set type, i.e. 'raw', etc.
    dsname : str
        data set name
    ext_list : list of str
        file name extensions, i.e. 'png'
    prdcfginfo : str
        Optional. string to add product configuration information, i.e. 'el0.4'
    timeformat : str
        Optional. The time format
    runinfo : str
        Optional. Additional information about the test (e.g. 'RUN01', 'TS011')

    Returns
    -------
    fname_list : list of str
        list of file names (as many as extensions)

    """
    if timeinfo is None:
        timeinfostr = ''
    else:
        timeinfostr = timeinfo.strftime(timeformat)+'_'

    if prdcfginfo is None:
        cfgstr = ''
    else:
        cfgstr = '_' + prdcfginfo

    if runinfo is None or runinfo == '':
        runstr = ''
    else:
        runstr = runinfo + '_'

    fname_list = list()
    for ext in ext_list:
        fname_list.append(timeinfostr + runstr + prdtype + '_' +
                          dstype + '_' + dsname + cfgstr + '.' + ext)

    return fname_list


def generate_field_name_str(datatype):
    """
    Generates a field name in a nice to read format.

    Parameters
    ----------
    datatype : str
        The data type

    Returns
    -------
    field_str : str
        The field name

    """
    field_name = get_fieldname_pyart(datatype)
    field_dic = get_metadata(field_name)
    field_str = field_dic['standard_name'].replace('_', ' ')
    field_str = field_str[0].upper() + field_str[1:]
    field_str += ' ('+field_dic['units']+')'

    return field_str


def get_field_name(datatype):
    """
    Return long name of datatype.

    Parameters
    ----------
    datatype : str
        The data type

    Returns
    -------
    name : str
        The name

    """
    field_name = get_fieldname_pyart(datatype)
    field_dic = get_metadata(field_name)
    name = field_dic['long_name'].replace('_', ' ')
    name = name[0].upper() + name[1:]

    return name


def get_field_unit(datatype):
    """
    Return unit of datatype.

    Parameters
    ----------
    datatype : str
        The data type

    Returns
    -------
    unit : str
        The unit

    """
    field_name = get_fieldname_pyart(datatype)
    field_dic = get_metadata(field_name)

    return field_dic['units']


def get_datatype_metranet(datatype):
    """
    maps de config file radar data type name into the corresponding metranet
    data type  name and Py-ART field name

    Parameters
    ----------
    datatype : str
        config file radar data type name

    Returns
    -------
    metranet type : dict
        dictionary containing the metranet data type name and its
        corresponding Py-ART field name

    """
    if datatype == 'dBZ':
        datatype_metranet = 'ZH'
        field_name = 'reflectivity'
    elif datatype == 'dBZv':
        datatype_metranet = 'ZV'
        field_name = 'reflectivity_vv'
    elif datatype == 'ZDR':
        datatype_metranet = 'ZDR'
        field_name = 'differential_reflectivity'
    elif datatype == 'uRhoHV':
        datatype_metranet = 'RHO'
        field_name = 'uncorrected_cross_correlation_ratio'
    elif datatype == 'uPhiDP':
        datatype_metranet = 'PHI'
        field_name = 'uncorrected_differential_phase'
    elif datatype == 'V':
        datatype_metranet = 'VEL'
        field_name = 'velocity'
    elif datatype == 'W':
        datatype_metranet = 'WID'
        field_name = 'spectrum_width'
    elif datatype == 'CLT':
        datatype_metranet = 'CLT'
        field_name = 'clutter_exit_code'
    else:
        raise ValueError(
            'ERROR: Metranet fields do not contain datatype '+datatype)

    return {datatype_metranet: field_name}


def get_datatype_odim(datatype):
    """
    maps the config file radar data type name into the corresponding odim
    data type name and Py-ART field name

    Parameters
    ----------
    datatype : str
        config file radar data type name

    Returns
    -------
    metranet type : dict
        dictionary containing the odim data type name and its
        corresponding Py-ART field name

    """
    if datatype == 'udBZ':
        datatype_odim = 'TH'
        field_name = 'uncorrected_reflectivity'
    elif datatype == 'udBZv':
        datatype_odim = 'TV'
        field_name = 'uncorrected_reflectivity_vv'
    elif datatype == 'dBZ':
        datatype_odim = 'DBZH'
        field_name = 'reflectivity'
    elif datatype == 'dBZv':
        datatype_odim = 'DBZV'
        field_name = 'reflectivity_vv'
    elif datatype == 'dBZc':
        datatype_odim = 'DBZH'
        field_name = 'corrected_reflectivity'
    elif datatype == 'dBZvc':
        datatype_odim = 'DBZV'
        field_name = 'corrected_reflectivity_vv'
    elif datatype == 'ZDR':
        datatype_odim = 'ZDR'
        field_name = 'differential_reflectivity'
    elif datatype == 'RhoHV':
        datatype_odim = 'RHOHV'
        field_name = 'cross_correlation_ratio'
    elif datatype == 'LDR':
        datatype_odim = 'LDR'
        field_name = 'linear_polarization_ratio'
    elif datatype == 'PhiDP':
        datatype_odim = 'PHIDP'
        field_name = 'differential_phase'
    elif datatype == 'KDP':
        datatype_odim = 'KDP'
        field_name = 'specific_differential_phase'
    elif datatype == 'SQI':
        datatype_odim = 'SQI'
        field_name = 'normalized_coherent_power'
    elif datatype == 'SNR':
        datatype_odim = 'SNR'
        field_name = 'signal_to_noise_ratio'
    elif datatype == 'V':
        datatype_odim = 'VRAD'
        field_name = 'velocity'
    elif datatype == 'Vh':
        datatype_odim = 'VRADH'
        field_name = 'velocity'
    elif datatype == 'Vv':
        datatype_odim = 'VRADV'
        field_name = 'velocity_vv'
    elif datatype == 'W':
        datatype_odim = 'WRAD'
        field_name = 'spectrum_width'
    elif datatype == 'QIND':
        datatype_odim = 'QIND'
        field_name = 'signal_quality_index'
    else:
        raise ValueError(
            'ERROR: ODIM fields do not contain datatype '+datatype)

    return {datatype_odim: field_name}


def get_fieldname_pyart(datatype):
    """
    maps the config file radar data type name into the corresponding rainbow
    Py-ART field name

    Parameters
    ----------
    datatype : str
        config file radar data type name

    Returns
    -------
    field_name : str
        Py-ART field name

    """
    if datatype == 'dBZ':
        field_name = 'reflectivity'
    elif datatype == 'dBuZ':
        field_name = 'unfiltered_reflectivity'
    elif datatype == 'dBZc':
        field_name = 'corrected_reflectivity'
    elif datatype == 'dBuZc':
        field_name = 'corrected_unfiltered_reflectivity'
    elif datatype == 'dBZv':
        field_name = 'reflectivity_vv'
    elif datatype == 'dBZvc':
        field_name = 'corrected_reflectivity_vv'
    elif datatype == 'dBuZv':
        field_name = 'unfiltered_reflectivity_vv'
    elif datatype == 'dBuZvc':
        field_name = 'corrected_unfiltered_reflectivity_vv'
    elif datatype == 'dBZ_bias':
        field_name = 'reflectivity_bias'
    elif datatype == 'eta_h':
        field_name = 'volumetric_reflectivity'
    elif datatype == 'eta_v':
        field_name = 'volumetric_reflectivity_vv'
    elif datatype == 'rcs_h':
        field_name = 'radar_cross_section_hh'
    elif datatype == 'rcs_v':
        field_name = 'radar_cross_section_vv'

    elif datatype == 'ZDR':
        field_name = 'differential_reflectivity'
    elif datatype == 'ZDRu':
        field_name = 'unfiltered_differential_reflectivity'
    elif datatype == 'ZDRc':
        field_name = 'corrected_differential_reflectivity'
    elif datatype == 'ZDRuc':
        field_name = 'corrected_unfiltered_differential_reflectivity'
    elif datatype == 'ZDR_prec':
        field_name = 'differential_reflectivity_in_precipitation'
    elif datatype == 'ZDR_snow':
        field_name = 'differential_reflectivity_in_snow'
    elif datatype == 'ZDR_col':
        field_name = 'differential_reflectivity_column_height'

    elif datatype == 'dBm':
        field_name = 'signal_power_hh'
    elif datatype == 'dBmv':
        field_name = 'signal_power_vv'
    elif datatype == 'Nh':
        field_name = 'noisedBZ_hh'
    elif datatype == 'Nv':
        field_name = 'noisedBZ_vv'
    elif datatype == 'SNRh':
        field_name = 'signal_to_noise_ratio_hh'
    elif datatype == 'SNRv':
        field_name = 'signal_to_noise_ratio_vv'

    elif datatype == 'dBm_sun_hit':
        field_name = 'sun_hit_power_h'
    elif datatype == 'dBmv_sun_hit':
        field_name = 'sun_hit_power_v'
    elif datatype == 'ZDR_sun_hit':
        field_name = 'sun_hit_differential_reflectivity'
    elif datatype == 'dBm_sun_est':
        field_name = 'sun_est_power_h'
    elif datatype == 'dBmv_sun_est':
        field_name = 'sun_est_power_v'
    elif datatype == 'ZDR_sun_est':
        field_name = 'sun_est_differential_reflectivity'
    elif datatype == 'sun_pos_h':
        field_name = 'sun_hit_h'
    elif datatype == 'sun_pos_v':
        field_name = 'sun_hit_v'
    elif datatype == 'sun_pos_zdr':
        field_name = 'sun_hit_zdr'

    elif datatype == 'RhoHV':
        field_name = 'cross_correlation_ratio'
    elif datatype == 'uRhoHV':
        field_name = 'uncorrected_cross_correlation_ratio'
    elif datatype == 'RhoHVc':
        field_name = 'corrected_cross_correlation_ratio'
    elif datatype == 'RhoHV_rain':
        field_name = 'cross_correlation_ratio_in_rain'
    elif datatype == 'L':
        field_name = 'logarithmic_cross_correlation_ratio'
    elif datatype == 'CDR':
        field_name = 'circular_depolarization_ratio'

    elif datatype == 'PhiDP':
        field_name = 'differential_phase'
    elif datatype == 'uPhiDP':
        field_name = 'uncorrected_differential_phase'
    elif datatype == 'PhiDPc':
        field_name = 'corrected_differential_phase'
    elif datatype == 'PhiDP0':
        field_name = 'system_differential_phase'
    elif datatype == 'PhiDP0_bin':
        field_name = 'first_gate_differential_phase'
    elif datatype == 'KDP':
        field_name = 'specific_differential_phase'
    elif datatype == 'KDPc':
        field_name = 'corrected_specific_differential_phase'

    elif datatype == 'V':
        field_name = 'velocity'
    elif datatype == 'dealV':
        field_name = 'dealiased_velocity'
    elif datatype == 'Vc':
        field_name = 'corrected_velocity'
    elif datatype == 'dealVc':
        field_name = 'dealiased_corrected_velocity'
    elif datatype == 'estV':
        field_name = 'retrieved_velocity'
    elif datatype == 'stdV':
        field_name = 'retrieved_velocity_std'
    elif datatype == 'diffV':
        field_name = 'velocity_difference'
    elif datatype == 'W':
        field_name = 'spectrum_width'
    elif datatype == 'Wc':
        field_name = 'corrected_spectrum_width'
    elif datatype == 'wind_vel_h_az':
        field_name = 'azimuthal_horizontal_wind_component'
    elif datatype == 'wind_vel_v':
        field_name = 'vertical_wind_component'
    elif datatype == 'wind_vel_h_u':
        field_name = 'eastward_wind_component'
    elif datatype == 'wind_vel_h_v':
        field_name = 'northward_wind_component'
    elif datatype == 'windshear_v':
        field_name = 'vertical_wind_shear'
    elif datatype == 'WIND_SPEED':
        field_name = 'wind_speed'
    elif datatype == 'WIND_DIRECTION':
        field_name = 'wind_direction'

    elif datatype == 'Ah':
        field_name = 'specific_attenuation'
    elif datatype == 'Ahc':
        field_name = 'corrected_specific_attenuation'
    elif datatype == 'PIA':
        field_name = 'path_integrated_attenuation'
    elif datatype == 'PIAc':
        field_name = 'corrected_path_integrated_attenuation'
    elif datatype == 'Adp':
        field_name = 'specific_differential_attenuation'
    elif datatype == 'Adpc':
        field_name = 'corrected_specific_differential_attenuation'
    elif datatype == 'PIDA':
        field_name = 'path_integrated_differential_attenuation'
    elif datatype == 'PIDAc':
        field_name = 'corrected_path_integrated_differential_attenuation'

    elif datatype == 'TEMP':
        field_name = 'temperature'
    elif datatype == 'ISO0':
        field_name = 'iso0'
    elif datatype == 'H_ISO0':
        field_name = 'height_over_iso0'
    elif datatype == 'cosmo_index':
        field_name = 'cosmo_index'
    elif datatype == 'hzt_index':
        field_name = 'hzt_index'
    elif datatype == 'ml':
        field_name = 'melting_layer'

    elif datatype == 'VIS':
        field_name = 'visibility'

    elif datatype == 'echoID':
        field_name = 'radar_echo_id'
    elif datatype == 'CLT':
        field_name = 'clutter_exit_code'
    elif datatype == 'occurrence':
        field_name = 'occurrence'
    elif datatype == 'freq_occu':
        field_name = 'frequency_of_occurrence'
    elif datatype == 'RR':
        field_name = 'radar_estimated_rain_rate'

    elif datatype == 'hydro':
        field_name = 'radar_echo_classification'
    elif datatype == 'entropy':
        field_name = 'hydroclass_entropy'
    elif datatype == 'propAG':
        field_name = 'proportion_AG'
    elif datatype == 'propCR':
        field_name = 'proportion_CR'
    elif datatype == 'propLR':
        field_name = 'proportion_LR'
    elif datatype == 'propRP':
        field_name = 'proportion_RP'
    elif datatype == 'propRN':
        field_name = 'proportion_RN'
    elif datatype == 'propVI':
        field_name = 'proportion_VI'
    elif datatype == 'propWS':
        field_name = 'proportion_WS'
    elif datatype == 'propMH':
        field_name = 'proportion_MH'
    elif datatype == 'propIH':
        field_name = 'proportion_IH'

    elif datatype == 'time_avg_flag':
        field_name = 'time_avg_flag'
    elif datatype == 'colocated_gates':
        field_name = 'colocated_gates'
    elif datatype == 'nsamples':
        field_name = 'number_of_samples'
    elif datatype == 'bird_density':
        field_name = 'bird_density'

    # vol2bird field names
    elif datatype == 'ff':
        field_name = 'wind_speed'
    elif datatype == 'dd':
        field_name = 'wind_direction'
    elif datatype == 'u':
        field_name = 'eastward_wind_component'
    elif datatype == 'v':
        field_name = 'northward_wind_component'
    elif datatype == 'w':
        field_name = 'vertical_wind_component'
    elif datatype == 'width':
        field_name = 'height_resolution'
    elif datatype == 'gap':
        field_name = 'gap'
    elif datatype == 'dbz':
        field_name = 'bird_reflectivity'
    elif datatype == 'eta':
        field_name = 'volumetric_reflectivity'
    elif datatype == 'dens':
        field_name = 'bird_density'
    elif datatype == 'n':
        field_name = 'number_of_samples_velocity'
    elif datatype == 'n_dbz':
        field_name = 'number_of_samples_reflectivity'
    elif datatype == 'sd_vvp':
        field_name = 'retrieved_velocity_std'
    elif datatype == 'DBZH':
        field_name = 'reflectivity'
    elif datatype == 'n_all':
        field_name = 'number_of_samples_velocity_all'
    elif datatype == 'n_dbz_all':
        field_name = 'number_of_samples_reflectivity_all'
    else:
        raise ValueError('ERROR: Unknown data type '+datatype)

    return field_name


def get_fieldname_cosmo(field_name):
    """
    maps the Py-ART field name into the corresponding COSMO variable name

    Parameters
    ----------
    field_name : str
        Py-ART field name

    Returns
    -------
    cosmo_name : str
        Py-ART variable name

    """
    if field_name == 'temperature':
        cosmo_name = 'T'
    elif field_name == 'wind_speed':
        cosmo_name = 'FF'
    elif field_name == 'wind_direction':
        cosmo_name = 'DD'
    elif field_name == 'vertical_wind_shear':
        cosmo_name = 'WSHEAR'
    else:
        raise ValueError('ERROR: Unknown field name '+field_name)

    return cosmo_name


def get_file_list(datadescriptor, starttime, endtime, cfg, scan=None):
    """
    gets the list of files with a time period

    Parameters
    ----------
    datadescriptor : str
        radar field type. Format : [radar file type]:[datatype]
    startime : datetime object
        start of time period
    endtime : datetime object
        end of time period
    cfg: dictionary of dictionaries
        configuration info to figure out where the data is
    scan : str
        scan name

    Returns
    -------
    filelist : list of strings
        list of files within the time period

    """
    startdate = starttime.replace(hour=0, minute=0, second=0, microsecond=0)
    enddate = endtime.replace(hour=0, minute=0, second=0, microsecond=0)
    ndays = int((enddate-startdate).days)+1

    radarnr, datagroup, datatype, dataset, product = get_datatype_fields(
        datadescriptor)
    ind_rad = int(radarnr[5:8])-1

    if (datatype == 'Nh') or (datatype == 'Nv'):
        datatype = 'dBZ'

    t_filelist = []
    for i in range(ndays):
        if datagroup == 'RAINBOW':
            if scan is None:
                warn('Unknown scan name')
                return None
            daydir = (
                starttime+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            dayinfo = (starttime+datetime.timedelta(days=i)).strftime('%Y%m%d')
            datapath = cfg['datapath'][ind_rad] + scan + daydir + '/'
            if not os.path.isdir(datapath):
                # warn("WARNING: Unknown datapath '%s'" % datapath)
                continue
            dayfilelist = glob.glob(datapath+dayinfo+'*00'+datatype+'.*')
            for filename in dayfilelist:
                t_filelist.append(filename)
        elif datagroup == 'RAD4ALP':
            if scan is None:
                warn('Unknown scan name')
                return None
            dayinfo = (starttime+datetime.timedelta(days=i)).strftime('%y%j')
            basename = ('M'+cfg['RadarRes'][ind_rad] +
                        cfg['RadarName'][ind_rad]+dayinfo)
            if cfg['path_convention'] == 'LTE':
                yy = dayinfo[0:2]
                dy = dayinfo[2:]
                subf = ('M' + cfg['RadarRes'][ind_rad] +
                        cfg['RadarName'][ind_rad] + yy + 'hdf' + dy)
                datapath = cfg['datapath'][ind_rad] + subf + '/'

                # check that M files exist. if not search P files
                dayfilelist = glob.glob(datapath+basename+'*.'+scan+'*')
                if not dayfilelist:
                    subf = ('P' + cfg['RadarRes'][ind_rad] +
                            cfg['RadarName'][ind_rad] + yy + 'hdf' + dy)
                    datapath = cfg['datapath'][ind_rad] + subf + '/'
                    basename = ('P'+cfg['RadarRes'][ind_rad] +
                                cfg['RadarName'][ind_rad]+dayinfo)
            elif cfg['path_convention'] == 'MCH':
                datapath = cfg['datapath'][ind_rad]+dayinfo+'/'+basename+'/'

                # check that M files exist. if not search P files
                dayfilelist = glob.glob(datapath+basename+'*.'+scan+'*')
                if not dayfilelist:
                    basename = ('P'+cfg['RadarRes'][ind_rad] +
                                cfg['RadarName'][ind_rad]+dayinfo)
                    datapath = (cfg['datapath'][ind_rad]+dayinfo+'/' +
                                basename+'/')
            else:
                datapath = (
                    cfg['datapath'][ind_rad]+'M'+cfg['RadarRes'][ind_rad] +
                    cfg['RadarName'][ind_rad]+'/')

                # check that M files exist. if not search P files
                dayfilelist = glob.glob(datapath+basename+'*.'+scan+'*')
                if not dayfilelist:
                    basename = ('P'+cfg['RadarRes'][ind_rad] +
                                cfg['RadarName'][ind_rad]+dayinfo)
                    datapath = (
                        cfg['datapath'][ind_rad]+'P'+cfg['RadarRes'][ind_rad] +
                        cfg['RadarName'][ind_rad]+'/')

            if not os.path.isdir(datapath):
                warn("WARNING: Unknown datapath '%s'" % datapath)
                continue
            dayfilelist = glob.glob(datapath+basename+'*.'+scan+'*')
            for filename in dayfilelist:
                t_filelist.append(filename)
        elif datagroup == 'ODIM':
            if scan is None:
                warn('Unknown scan name')
                return None
            if cfg['path_convention'] == 'MCH':
                dayinfo = (starttime+datetime.timedelta(days=i)).strftime('%y%j')
                basename = ('M'+cfg['RadarRes'][ind_rad] +
                            cfg['RadarName'][ind_rad]+dayinfo)
                datapath = cfg['datapath'][ind_rad]+dayinfo+'/'+basename+'/'

                # check that M files exist. if not search P files
                dayfilelist = glob.glob(datapath+basename+'*'+scan+'*')
                if not dayfilelist:
                    basename = ('P'+cfg['RadarRes'][ind_rad] +
                                cfg['RadarName'][ind_rad]+dayinfo)
                    datapath = (cfg['datapath'][ind_rad]+dayinfo+'/' +
                                basename+'/')
            elif cfg['path_convention'] == 'ODIM':
                try:
                    fpath_strf = dataset[dataset.find("D")+2:dataset.find("F")-2]
                except AttributeError:
                    warn('Unknown ODIM directory and/or date convention, check product config file')
                daydir = (
                    starttime+datetime.timedelta(days=i)).strftime(
                        fpath_strf)
                datapath = (cfg['datapath'][ind_rad] + daydir+'/')
                dayfilelist = glob.glob(datapath+'*'+scan)
            else:
                dayinfo = (starttime+datetime.timedelta(days=i)).strftime('%y%j')
                basename = ('M'+cfg['RadarRes'][ind_rad] +
                            cfg['RadarName'][ind_rad]+dayinfo)
                datapath = (
                    cfg['datapath'][ind_rad]+'M'+cfg['RadarRes'][ind_rad] +
                    cfg['RadarName'][ind_rad]+'/')

                # check that M files exist. if not search P files
                dayfilelist = glob.glob(datapath+basename+'*'+scan+'*')
                if not dayfilelist:
                    basename = ('P'+cfg['RadarRes'][ind_rad] +
                                cfg['RadarName'][ind_rad]+dayinfo)
                    datapath = (
                        cfg['datapath'][ind_rad]+'P'+cfg['RadarRes'][ind_rad] +
                        cfg['RadarName'][ind_rad]+'/')

            if not os.path.isdir(datapath):
                warn("WARNING: Unknown datapath '%s'" % datapath)
                continue
            for filename in dayfilelist:
                t_filelist.append(filename)
        elif datagroup == 'CFRADIAL':
            daydir = (
                starttime+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            dayinfo = (starttime+datetime.timedelta(days=i)).strftime('%Y%m%d')
            datapath = (
                cfg['loadbasepath'][ind_rad]+cfg['loadname'][ind_rad]+'/' +
                daydir+'/'+dataset+'/'+product+'/')
            if not os.path.isdir(datapath):
                warn("WARNING: Unknown datapath '%s'" % datapath)
                continue
            dayfilelist = glob.glob(datapath+dayinfo+'*'+datatype+'.nc')
            for filename in dayfilelist:
                t_filelist.append(filename)
        elif datagroup == 'MXPOL':
            if scan is None:
                warn('Unknown scan name')
                return None
            if cfg['path_convention'] == 'LTE':
                sub1 = str(starttime.year)
                sub2 = starttime.strftime('%m')
                sub3 = starttime.strftime('%d')
                datapath = (cfg['datapath'][ind_rad]+'/'+sub1+'/'+sub2+'/' +
                            sub3+'/')
                basename = ('MXPol-polar-'+starttime.strftime('%Y%m%d')+'-*-' +
                            scan+'*')
                dayfilelist = glob.glob(datapath+basename)
            else:
                daydir = (
                    starttime+datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                dayinfo = (
                    starttime+datetime.timedelta(days=i)).strftime('%Y%m%d')
                datapath = cfg['datapath'][ind_rad]+scan+'/'+daydir+'/'
                if not os.path.isdir(datapath):
                    warn("WARNING: Unknown datapath '%s'" % datapath)
                    continue
                dayfilelist = glob.glob(
                    datapath+'MXPol-polar-'+dayinfo+'-*-'+scan+'.nc')
            for filename in dayfilelist:
                t_filelist.append(filename)
    filelist = []
    for filename in t_filelist:
        filenamestr = str(filename)
        fdatetime = get_datetime(filenamestr, datadescriptor)
        if (fdatetime >= starttime) and (fdatetime <= endtime):
            filelist.append(filenamestr)

    return sorted(filelist)


def get_trtfile_list(datapath, starttime, endtime):
    """
    gets the list of TRT files with a time period

    Parameters
    ----------
    datapath : str
        directory where to look for data
    startime : datetime object
        start of time period
    endtime : datetime object
        end of time period

    Returns
    -------
    filelist : list of strings
        list of files within the time period

    """
    dayfilelist = glob.glob(datapath+'CZC*0T.trt')
    if not dayfilelist:
        warn('No TRT files in '+datapath)
        return None

    filelist = []
    for filename in dayfilelist:
        bfile = os.path.basename(filename)
        datetimestr = bfile[3:12]
        fdatetime = datetime.datetime.strptime(datetimestr, '%y%j%H%M')
        if (fdatetime >= starttime) and (fdatetime <= endtime):
            pass
            # filelist.append(filename)
        filelist.append(filename)

    return sorted(filelist)


def get_scan_list(scandescriptor_list):
    """
    determine which is the scan list for each radar

    Parameters
    ----------
    scandescriptor : list of string
        the list of all scans for all radars

    Returns
    -------
    scan_list : list of lists
        the list of scans corresponding to each radar

    """
    descrfields = scandescriptor_list[0].split(':')
    if len(descrfields) == 1:
        # one radar
        return [scandescriptor_list]

    # one or more radars
    # check how many radars are there
    radar_list = set()
    for scandescriptor in scandescriptor_list:
        radar_list.add(scandescriptor.split(':')[0])
    nradar = len(radar_list)

    # create the list of lists
    scan_list = [[] for i in range(nradar)]
    for scandescriptor in scandescriptor_list:
        descrfields = scandescriptor.split(':')
        ind_rad = int(descrfields[0][5:8])-1
        scan_list[ind_rad].append(descrfields[1])

    return scan_list


def get_new_rainbow_file_name(master_fname, master_datadescriptor, datatype):
    """
    get the rainbow file name containing datatype from a master file name
    and data type

    Parameters
    ----------
    master_fname : str
        the master file name
    master_datadescriptor : str
        the master data type descriptor
    datatype : str
        the data type of the new file name to be created

    Returns
    -------
    new_fname : str
        the new file name

    """
    _, _, master_datatype, _, _ = get_datatype_fields(master_datadescriptor)
    datapath = os.path.dirname(master_fname)
    voltime = get_datetime(master_fname, master_datatype)
    voltype = os.path.basename(master_fname).split('.')[1]

    return (datapath+'/'+voltime.strftime('%Y%m%d%H%M%S')+'00'+datatype+'.' +
            voltype)


def get_datatype_fields(datadescriptor):
    """
    splits the data type descriptor and provides each individual member

    Parameters
    ----------
    datadescriptor : str
        radar field type. Format : [radar file type]:[datatype]

    Returns
    -------
    radarnr : str
        radar number, i.e. RADAR1, RADAR2, ...
    datagroup : str
        data type group, i.e. RAINBOW, RAD4ALP, ODIM, CFRADIAL, COSMO, MXPOL ...
    datatype : str
        data type, i.e. dBZ, ZDR, ISO0, ...
    dataset : str
        dataset type (for saved data only)
    product : str
        product type (for saved data only)

    """
    descrfields = datadescriptor.split(':')
    if len(descrfields) == 1:
        radarnr = 'RADAR001'
        datagroup = 'RAINBOW'
        datatype = descrfields[0]
        dataset = None
        product = None
    elif descrfields[0].startswith('RADAR'):
        radarnr = descrfields[0]
        if len(descrfields) == 2:
            radarnr = descrfields[0]
            datagroup = 'RAINBOW'
            datatype = descrfields[1]
            dataset = None
            product = None
        else:
            datagroup = descrfields[1]
            if datagroup == 'CFRADIAL':
                descrfields2 = descrfields[2].split(',')
                datatype = descrfields2[0]
                dataset = descrfields2[1]
                product = descrfields2[2]
            elif datagroup == 'MXPOL':
                datatype = descrfields[2]
                dataset = None
                product = None
            elif datagroup == 'ODIM':
                descrfields2 = descrfields[2].split(',')
                datatype = descrfields2[0]
                product = None
                dataset = None
                if np.size(descrfields2) == 2:
                    dataset = descrfields2[1]
            else:
                datatype = descrfields[2]
                dataset = None
                product = None
    else:
        radarnr = 'RADAR001'
        datagroup = descrfields[0]
        if datagroup == 'CFRADIAL':
            descrfields2 = descrfields[1].split(',')
            datatype = descrfields2[0]
            dataset = descrfields2[1]
            product = descrfields2[2]
        elif datagroup == 'MXPOL':
            datatype = descrfields[1]
            dataset = None
            product = None
        elif datagroup == 'ODIM':
            descrfields2 = descrfields[1].split(',')
            #warn(" descrfields2:  '%s'" % descrfields2[1])
            if len(descrfields2) == 2:
                datatype = descrfields2[0]
                dataset = descrfields2[1]
                product = None
                #warn(" dataset:  '%s'" % dataset)
            else:
                datatype = descrfields[1]
                dataset = None
                product = None
        else:
            datatype = descrfields[1]
            dataset = None
            product = None
    #warn(" dataset:  '%s'" % dataset)
    return radarnr, datagroup, datatype, dataset, product


def get_dataset_fields(datasetdescr):
    """
    splits the dataset type descriptor and provides each individual member

    Parameters
    ----------
    datasetdescr : str
        dataset type. Format : [processing level]:[dataset type]

    Returns
    -------
    proclevel : str
        dataset processing level

    dataset : str
        dataset type, i.e. dBZ, ZDR, ISO0, ...

    """
    descrfields = datasetdescr.split(':')
    if len(descrfields) == 1:
        proclevel = 'l00'
        dataset = descrfields[0]
    else:
        proclevel = descrfields[0]
        dataset = descrfields[1]
        if len(proclevel) == 2:
            proclevel = proclevel[0]+'0'+proclevel[1]

    return proclevel, dataset


def get_datetime(fname, datadescriptor):
    """
    Given a data descriptor gets date and time from file name

    Parameters
    ----------
    fname : str
        file name
    datadescriptor : str
        radar field type. Format : [radar file type]:[datatype]

    Returns
    -------
    fdatetime : datetime object
        date and time in file name

    """
    _, datagroup, _, dataset, _ = get_datatype_fields(datadescriptor)

    return _get_datetime(fname, datagroup, ftime_format=dataset)


def find_cosmo_file(voltime, datatype, cfg, scanid, ind_rad=0):
    """
    Search a COSMO file in Rainbow format

    Parameters
    ----------
    voltime : datetime object
        volume scan time
    datatype : str
        type of COSMO data to look for
    cfg : dictionary of dictionaries
        configuration info to figure out where the data is
    scanid : str
        name of the scan
    ind_rad : int
        radar index

    Returns
    -------
    fname : str
        Name of COSMO file if it exists. None otherwise

    """
    # hour rounded date-time
    fdatetime = voltime.strftime('%Y%m%d%H')+'000000'

    # initial run time to look for
    hvol = int(voltime.strftime('%H'))
    runhour0 = int(hvol/cfg['CosmoRunFreq'])*cfg['CosmoRunFreq']
    runtime0 = voltime.replace(hour=runhour0, minute=0, second=0)

    # look for cosmo file
    found = False
    nruns_to_check = int((cfg['CosmoForecasted']-1)/cfg['CosmoRunFreq'])
    for i in range(nruns_to_check):
        runtime = runtime0-datetime.timedelta(hours=i * cfg['CosmoRunFreq'])
        runtimestr = runtime.strftime('%Y%m%d%H')+'000000'

        daydir = runtime.strftime('%Y-%m-%d')
        datapath = cfg['cosmopath'][ind_rad]+datatype+'/'+scanid+daydir+'/'

        search_name = (
            datapath+datatype+'_RUN'+runtimestr+'_DX50'+fdatetime+'.*')
        print('Looking for file: '+search_name)
        fname = glob.glob(search_name)
        if fname:
            found = True
            break

    if not found:
        warn('WARNING: Unable to get COSMO '+datatype+' information')
        return None

    return fname[0]


def find_raw_cosmo_file(voltime, datatype, cfg, ind_rad=0):
    """
    Search a COSMO file in netcdf format

    Parameters
    ----------
    voltime : datetime object
        volume scan time
    datatype : str
        type of COSMO data to look for
    cfg : dictionary of dictionaries
        configuration info to figure out where the data is
    ind_rad : int
        radar index

    Returns
    -------
    fname : str
        Name of COSMO file if it exists. None otherwise

    """
    # initial run time to look for
    runhour0 = int(voltime.hour/cfg['CosmoRunFreq'])*cfg['CosmoRunFreq']
    runtime0 = voltime.replace(hour=runhour0, minute=0, second=0)

    # look for cosmo file
    found = False
    nruns_to_check = int((cfg['CosmoForecasted']-1)/cfg['CosmoRunFreq'])
    for i in range(nruns_to_check):
        runtime = runtime0-datetime.timedelta(hours=i * cfg['CosmoRunFreq'])
        runtimestr = runtime.strftime('%Y%m%d%H')

        daydir = runtime.strftime('%Y-%m-%d')
        datapath = cfg['cosmopath'][ind_rad]+datatype+'/raw1/'+daydir+'/'
        if datatype == 'TEMP':
            search_name = (datapath+'cosmo-1_MDR_3D_'+runtimestr+'.nc')
        elif datatype == 'WIND':
            search_name = (datapath+'cosmo-1_MDR_3DWIND_'+runtimestr+'.nc')
        else:
            warn('Unable to get COSMO '+datatype+'. Unknown variable')
        print('Looking for file: '+search_name)
        fname = glob.glob(search_name)
        if fname:
            found = True
            break

    if not found:
        warn('WARNING: Unable to get COSMO '+datatype+' information')
        return None

    return fname[0]


def find_hzt_file(voltime, cfg, ind_rad=0):
    """
    Search an ISO-0 degree file in HZT format

    Parameters
    ----------
    voltime : datetime object
        volume scan time
    cfg : dictionary of dictionaries
        configuration info to figure out where the data is
    ind_rad : int
        radar index

    Returns
    -------
    fname : str
        Name of HZT file if it exists. None otherwise

    """
    # initial run time to look for
    runhour0 = int(voltime.hour/cfg['CosmoRunFreq'])*cfg['CosmoRunFreq']
    runtime0 = voltime.replace(hour=runhour0, minute=0, second=0)

    # look for cosmo file
    found = False
    nruns_to_check = int((cfg['CosmoForecasted']-1)/cfg['CosmoRunFreq'])
    for i in range(nruns_to_check):
        runtime = runtime0-datetime.timedelta(hours=i * cfg['CosmoRunFreq'])
        target_hour = int((voltime - runtime).total_seconds() / 3600.)
        runtimestr = runtime.strftime('%y%j%H00')

        daydir = runtime.strftime('%y%j')
        if cfg['path_convention'] == 'RT':
            datapath = cfg['cosmopath'][ind_rad]+'HZT/'
        else:
            datapath = cfg['cosmopath'][ind_rad]+'HZT/'+daydir+'/'
        search_name = datapath+'HZT'+runtimestr+'0L.8'+'{:02d}'.format(
            target_hour)

        print('Looking for file: '+search_name)
        fname = glob.glob(search_name)
        if fname:
            found = True
            break

    if not found:
        warn('WARNING: Unable to find HZT file')
        return None

    return fname[0]


def find_rad4alpcosmo_file(voltime, datatype, cfg, scanid, ind_rad=0):
    """
    Search a COSMO file

    Parameters
    ----------
    voltime : datetime object
        volume scan time
    datatype : str
        type of COSMO data to look for
    cfg: dictionary of dictionaries
        configuration info to figure out where the data is
    ind_rad: int
        radar index

    Returns
    -------
    fname : str
        Name of COSMO file if it exists. None otherwise

    scanid: str
        name of the scan

    """
    # hour rounded date-time
    fdatetime = voltime.strftime('%y%j%H')+'00'

    # initial run time to look for
    hvol = int(voltime.strftime('%H'))
    runhour0 = int(hvol/cfg['CosmoRunFreq'])*cfg['CosmoRunFreq']
    runtime0 = voltime.replace(hour=runhour0, minute=0, second=0)

    # look for cosmo file
    found = False
    nruns_to_check = int((cfg['CosmoForecasted']-1)/cfg['CosmoRunFreq'])
    rad_id = 'P'+cfg['RadarRes'][ind_rad]+cfg['RadarName'][ind_rad]
    for i in range(nruns_to_check):
        runtime = runtime0-datetime.timedelta(hours=i * cfg['CosmoRunFreq'])
        runtimestr = runtime.strftime('%y%j%H')+'00'

        daydir = runtime.strftime('%y%j')
        datapath = (
            cfg['cosmopath'][ind_rad]+datatype+'/'+rad_id+'/'+daydir+'/')

        search_name = (
            datapath+datatype+'_RUN'+runtimestr+'_'+rad_id+fdatetime+'.' +
            scanid+'.bin')
        print('Looking for file: '+search_name)
        fname = glob.glob(search_name)
        if fname:
            found = True
            break

    if not found:
        warn('WARNING: Unable to get COSMO '+datatype+' information')
        return None

    return fname[0]


def _get_datetime(fname, datagroup, ftime_format=None):
    """
    Given a data group gets date and time from file name

    Parameters
    ----------
    fname : str
        file name
    datadescriptor : str
        radar field type. Format : [radar file type]:[datatype]
    ftime_format : str or None
        if the file is of type ODIM this contain the file time format

    Returns
    -------
    fdatetime : datetime object
        date and time in file name

    """
    bfile = os.path.basename(fname)
    if datagroup == 'RAINBOW' or datagroup == 'CFRADIAL':
        datetimestr = bfile[0:14]
        fdatetime = datetime.datetime.strptime(datetimestr, '%Y%m%d%H%M%S')
    elif datagroup == 'RAD4ALP':
        datetimestr = bfile[3:12]
        fdatetime = datetime.datetime.strptime(datetimestr, '%y%j%H%M')
    elif datagroup == 'ODIM':
        if ftime_format is None:
            # we assume is rad4alp format
            datetimestr = bfile[3:12]
            fdatetime = datetime.datetime.strptime(datetimestr, '%y%j%H%M')
        else:
            fdate_strf = ftime_format[ftime_format.find("F")+2:-1]
            today = datetime.datetime.now()
            len_datestr = len(today.strftime(fdate_strf))
            count = 0
            while True:
                try:
                    fdatetime = datetime.datetime.strptime(
                        os.path.basename(bfile)[count:count+len_datestr], fdate_strf)
                except ValueError:
                    count = count + 1
                else:
                    # No error, stop the loop
                    break
    elif datagroup == 'MXPOL':
        datetimestr = re.findall(r"([0-9]{8}-[0-9]{6})", bfile)[0]
        fdatetime = datetime.datetime.strptime(datetimestr, '%Y%m%d-%H%M%S')
    else:
        warn('unknown data group')
        return None

    return fdatetime
