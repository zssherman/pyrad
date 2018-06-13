"""
pyrad.proc.process_echoclass
===============================

Functions for echo classification and filtering

.. autosummary::
    :toctree: generated/

    process_echo_id
    process_birds_id
    process_clt_to_echo_id
    process_echo_filter
    process_cdf
    process_filter_snr
    process_filter_vel_diff
    process_filter_visibility
    process_outlier_filter
    process_hydroclass
    process_melting_layer

"""

from copy import deepcopy
from warnings import warn

import numpy as np

import pyart

from ..io.io_aux import get_datatype_fields, get_fieldname_pyart


def process_echo_id(procstatus, dscfg, radar_list=None):
    """
    identifies echoes as 0: No data, 1: Noise, 2: Clutter,
    3: Precipitation

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl_field = 'reflectivity'
        if datatype == 'dBuZ':
            refl_field = 'unfiltered_reflectivity'
        if datatype == 'ZDR':
            zdr_field = 'differential_reflectivity'
        if datatype == 'ZDRu':
            zdr_field = 'unfiltered_differential_reflectivity'
        if datatype == 'RhoHV':
            rhv_field = 'cross_correlation_ratio'
        if datatype == 'uPhiDP':
            phi_field = 'uncorrected_differential_phase'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if ((refl_field not in radar.fields) or
            (zdr_field not in radar.fields) or
            (rhv_field not in radar.fields) or
            (phi_field not in radar.fields)):
        warn('Unable to create radar_echo_id dataset. Missing data')
        return None, None

    echo_id = np.zeros((radar.nrays, radar.ngates), dtype='int32')+3

    # look for clutter
    gatefilter = pyart.filters.moment_and_texture_based_gate_filter(
        radar, zdr_field=zdr_field, rhv_field=rhv_field, phi_field=phi_field,
        refl_field=refl_field, textzdr_field=None, textrhv_field=None,
        textphi_field=None, textrefl_field=None, wind_size=7,
        max_textphi=20., max_textrhv=0.3, max_textzdr=2.85,
        max_textrefl=8., min_rhv=0.6)

    is_clutter = gatefilter.gate_excluded == 1
    echo_id[is_clutter] = 2

    # look for noise
    is_noise = radar.fields[refl_field]['data'].data == (
        pyart.config.get_fillvalue())
    echo_id[is_noise] = 1

    id_field = pyart.config.get_metadata('radar_echo_id')
    id_field['data'] = echo_id

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('radar_echo_id', id_field)

    return new_dataset, ind_rad


def process_birds_id(procstatus, dscfg, radar_list=None):
    """
    identifies echoes as 0: No data, 1: Noise, 2: Clutter,
    3: Birds

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'dBZ':
            refl_field = 'reflectivity'
        if datatype == 'dBuZ':
            refl_field = 'unfiltered_reflectivity'
        if datatype == 'ZDR':
            zdr_field = 'differential_reflectivity'
        if datatype == 'ZDRu':
            zdr_field = 'unfiltered_differential_reflectivity'
        if datatype == 'RhoHV':
            rhv_field = 'cross_correlation_ratio'

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if ((refl_field not in radar.fields) or
            (zdr_field not in radar.fields) or
            (rhv_field not in radar.fields)):
        warn('Unable to create radar_echo_id dataset. Missing data')
        return None, None

    # user defined parameters
    max_zdr = dscfg.get('max_zdr', 3.)
    max_rhv = dscfg.get('max_rhv', 0.9)
    max_refl = dscfg.get('max_refl', 20.)
    rmin = dscfg.get('rmin', 2000.)
    rmax = dscfg.get('rmax', 25000.)
    elmin = dscfg.get('elmin', 1.5)
    elmax = dscfg.get('elmax', 85.)
    echo_id = np.zeros((radar.nrays, radar.ngates), dtype='int32')+3

    # look for clutter
    gatefilter = pyart.filters.birds_gate_filter(
        radar, zdr_field=zdr_field, rhv_field=rhv_field,
        refl_field=refl_field, max_zdr=max_zdr, max_rhv=max_rhv,
        max_refl=max_refl, rmin=rmin, rmax=rmax, elmin=elmin, elmax=elmax)

    is_clutter = gatefilter.gate_excluded == 1
    echo_id[is_clutter] = 2

    # look for noise
    is_noise = radar.fields[refl_field]['data'].data == (
        pyart.config.get_fillvalue())
    echo_id[is_noise] = 1

    id_field = pyart.config.get_metadata('radar_echo_id')
    id_field['data'] = echo_id

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('radar_echo_id', id_field)

    return new_dataset, ind_rad


def process_clt_to_echo_id(procstatus, dscfg, radar_list=None):
    """
    Converts clutter exit code from rad4alp into pyrad echo ID

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'CLT':
            clt_field = 'clutter_exit_code'
            break

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if clt_field not in radar.fields:
        warn('rad4alp clutter exit code not present. Unable to obtain echoID')
        return None, None

    echo_id = np.zeros((radar.nrays, radar.ngates), dtype='int32')+3
    clt = radar.fields[clt_field]['data']
    echo_id[clt == 1] = 1
    echo_id[clt >= 100] = 2

    id_field = pyart.config.get_metadata('radar_echo_id')
    id_field['data'] = echo_id

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('radar_echo_id', id_field)

    return new_dataset, ind_rad


def process_echo_filter(procstatus, dscfg, radar_list=None):
    """
    Masks all echo types that are not of the class specified in
    keyword echo_type

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        echo_type : int
            The type of echo to keep: 1 noise, 2 clutter, 3 precipitation.
            Default 3
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'echoID':
            echoid_field = get_fieldname_pyart(datatype)
            break

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if echoid_field not in radar.fields:
        warn('Unable to filter data. Missing echo ID field')
        return None, None

    echo_type = dscfg.get('echo_type', 3)
    mask = radar.fields[echoid_field]['data'] != echo_type

    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'echoID':
            continue

        field_name = get_fieldname_pyart(datatype)
        if field_name not in radar.fields:
            warn('Unable to filter '+field_name+' according to echo ID. ' +
                 'No valid input fields')
            continue
        radar_field = deepcopy(radar.fields[field_name])
        radar_field['data'] = np.ma.masked_where(
            mask, radar_field['data'])

        if field_name.startswith('corrected_'):
            new_field_name = field_name
        elif field_name.startswith('uncorrected_'):
            new_field_name = field_name.replace(
                'uncorrected_', 'corrected_', 1)
        else:
            new_field_name = 'corrected_'+field_name
        new_dataset['radar_out'].add_field(new_field_name, radar_field)

    if not new_dataset['radar_out'].fields:
        return None, None

    return new_dataset, ind_rad


def process_cdf(procstatus, dscfg, radar_list=None):
    """
    Collects the fields necessary to compute the Cumulative Distribution
    Function

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    echoid_field = None
    hydro_field = None
    vis_field = None
    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'echoID':
            echoid_field = get_fieldname_pyart(datatype)
        elif datatype == 'hydro':
            hydro_field = get_fieldname_pyart(datatype)
        elif datatype == 'VIS':
            vis_field = get_fieldname_pyart(datatype)
        else:
            field_name = get_fieldname_pyart(datatype)

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    if field_name not in radar.fields:
        warn('Unable to compute CDF. Missing field')
        return None, None

    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()

    new_dataset['radar_out'].add_field(field_name, radar.fields[field_name])
    if echoid_field is not None:
        if echoid_field not in radar.fields:
            warn('Missing echo ID field. Clutter can not be filtered')
        else:
            new_dataset['radar_out'].add_field(
                echoid_field, radar.fields[echoid_field])
    if hydro_field is not None:
        if hydro_field not in radar.fields:
            warn('Missing hydrometeor type field. ' +
                 'Filtration according to hydrometeor type not possible')
        else:
            new_dataset['radar_out'].add_field(
                hydro_field, radar.fields[hydro_field])
    if vis_field is not None:
        if vis_field not in radar.fields:
            warn('Missing visibility field. Blocked gates can not be filtered')
        else:
            new_dataset['radar_out'].add_field(
                vis_field, radar.fields[vis_field])

    return new_dataset, ind_rad


def process_filter_snr(procstatus, dscfg, radar_list=None):
    """
    filters out low SNR echoes

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        SNRmin : float. Dataset keyword
            The minimum SNR to keep the data.
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if (datatype == 'SNRh') or (datatype == 'SNRv'):
            snr_field = get_fieldname_pyart(datatype)
            break

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()

    if snr_field not in radar.fields:
        warn('Unable to filter dataset according to SNR. Missing SNR field')
        return None, None

    gatefilter = pyart.filters.snr_based_gate_filter(
        radar, snr_field=snr_field, min_snr=dscfg['SNRmin'])
    is_low_snr = gatefilter.gate_excluded == 1

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)

        if (datatype == 'SNRh') or (datatype == 'SNRv'):
            continue

        field_name = get_fieldname_pyart(datatype)
        if field_name not in radar.fields:
            warn('Unable to filter '+field_name +
                 ' according to SNR. '+'No valid input fields')
            continue

        radar_field = deepcopy(radar.fields[field_name])
        radar_field['data'] = np.ma.masked_where(
            is_low_snr, radar_field['data'])

        if field_name.startswith('corrected_'):
            new_field_name = field_name
        elif field_name.startswith('uncorrected_'):
            new_field_name = field_name.replace(
                'uncorrected_', 'corrected_', 1)
        else:
            new_field_name = 'corrected_'+field_name
        new_dataset['radar_out'].add_field(new_field_name, radar_field)


    if not new_dataset['radar_out'].fields:
        return None, None

    return new_dataset, ind_rad


def process_filter_vel_diff(procstatus, dscfg, radar_list=None):
    """
    filters out range gates that could not be used for Doppler velocity
    estimation

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        SNRmin : float. Dataset keyword
            The minimum SNR to keep the data.
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'diffV':
            vel_diff_field = get_fieldname_pyart(datatype)
            break

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()

    if vel_diff_field not in radar.fields:
        warn('Unable to filter dataset according to valid velocity. ' +
             'Missing velocity differences field')
        return None, None

    mask = np.ma.getmaskarray(radar.fields[vel_diff_field]['data'])

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)

        if datatype == 'diffV':
            continue

        field_name = get_fieldname_pyart(datatype)
        if field_name not in radar.fields:
            warn('Unable to filter '+field_name +
                 ' according to SNR. '+'No valid input fields')
            continue

        radar_field = deepcopy(radar.fields[field_name])
        radar_field['data'] = np.ma.masked_where(mask, radar_field['data'])

        if field_name.find('corrected_') != -1:
            new_field_name = field_name
        elif field_name.startswith('uncorrected_'):
            new_field_name = field_name.replace(
                'uncorrected_', 'corrected_', 1)
        else:
            new_field_name = 'corrected_'+field_name
        new_dataset['radar_out'].add_field(new_field_name, radar_field)

    if not new_dataset['radar_out'].fields:
        return None, None

    return new_dataset, ind_rad


def process_filter_visibility(procstatus, dscfg, radar_list=None):
    """
    filters out rays gates with low visibility and corrects the reflectivity

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        VISmin : float. Dataset keyword
            The minimum visibility to keep the data.
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """

    if procstatus != 1:
        return None, None

    for datatypedescr in dscfg['datatype']:
        radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
        if datatype == 'VIS':
            vis_field = get_fieldname_pyart(datatype)
            break

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()

    if vis_field not in radar.fields:
        warn('Unable to filter dataset according to visibility. ' +
             'Missing visibility field')
        return None, None

    gatefilter = pyart.filters.visibility_based_gate_filter(
        radar, vis_field=vis_field, min_vis=dscfg['VISmin'])
    is_lowVIS = gatefilter.gate_excluded == 1

    for datatypedescr in dscfg['datatype']:
        _, _, datatype, _, _ = get_datatype_fields(
            datatypedescr)

        if datatype == 'VIS':
            continue
        field_name = get_fieldname_pyart(datatype)
        if field_name not in radar.fields:
            warn('Unable to filter '+field_name +
                 ' according to visibility. No valid input fields')
            continue

        radar_aux = deepcopy(radar)
        radar_aux.fields[field_name]['data'] = np.ma.masked_where(
            is_lowVIS, radar_aux.fields[field_name]['data'])

        if ((datatype == 'dBZ') or (datatype == 'dBZc') or
                (datatype == 'dBuZ') or (datatype == 'dBZv') or
                (datatype == 'dBZvc') or (datatype == 'dBuZv')):
            radar_field = pyart.correct.correct_visibility(
                radar_aux, vis_field=vis_field, field_name=field_name)
        else:
            radar_field = radar_aux.fields[field_name]

        if field_name.startswith('corrected_'):
            new_field_name = field_name
        elif field_name.startswith('uncorrected_'):
            new_field_name = field_name.replace(
                'uncorrected_', 'corrected_', 1)
        else:
            new_field_name = 'corrected_'+field_name
        new_dataset['radar_out'].add_field(new_field_name, radar_field)

    if not new_dataset['radar_out'].fields:
        return None, None

    return new_dataset, ind_rad


def process_outlier_filter(procstatus, dscfg, radar_list=None):
    """
    filters out gates which are outliers respect to the surrounding

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        threshold : float. Dataset keyword
            The distance between the value of the examined range gate and the
            median of the surrounding gates to consider the gate an outlier
        nb : int. Dataset keyword
            The number of neighbours (to one side) to analyse. i.e. 2 would
            correspond to 24 gates
        nb_min : int. Dataset keyword
            Minimum number of neighbouring gates to consider the examined gate
            valid
        percentile_min, percentile_max : float. Dataset keyword
            gates below (above) these percentiles (computed over the sweep) are
            considered potential outliers and further examined
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """
    if procstatus != 1:
        return None, None

    radarnr, _, datatype, _, _ = get_datatype_fields(
        dscfg['datatype'][0])

    ind_rad = int(radarnr[5:8])-1
    if radar_list[ind_rad] is None:
        warn('No valid radar')
        return None, None
    radar = radar_list[ind_rad]

    field_name = get_fieldname_pyart(datatype)
    if field_name not in radar.fields:
        warn('Unable to perform outlier removal. No valid data')
        return None, None

    threshold = dscfg.get('threshold', 10.)
    nb = dscfg.get('nb', 2)
    nb_min = dscfg.get('nb_min', 3)
    percentile_min = dscfg.get('percentile_min', 5.)
    percentile_max = dscfg.get('percentile_max', 95.)

    field = radar.fields[field_name]
    field_out = deepcopy(field)
    for sweep in range(radar.nsweeps):
        # find gates suspected to be outliers
        sweep_start = radar.sweep_start_ray_index['data'][sweep]
        sweep_end = radar.sweep_end_ray_index['data'][sweep]
        nrays_sweep = radar.rays_per_sweep['data'][sweep]
        data_sweep = field['data'][sweep_start:sweep_end+1, :]

        # check if all elements in array are masked
        if np.all(np.ma.getmaskarray(data_sweep)):
            continue

        percent_vals = np.nanpercentile(
            data_sweep.filled(fill_value=np.nan),
            (percentile_min, percentile_max))
        ind_rays, ind_rngs = np.ma.where(
            np.ma.logical_or(
                data_sweep < percent_vals[0], data_sweep > percent_vals[1]))

        for i, ind_ray in enumerate(ind_rays):
            ind_rng = ind_rngs[i]
            # find neighbours of suspected outlier gate
            data_cube = []
            for ray_nb in range(-nb, nb+1):
                for rng_nb in range(-nb, nb+1):
                    if ray_nb == 0 and rng_nb == 0:
                        continue
                    if ((ind_ray+ray_nb >= 0) and
                            (ind_ray+ray_nb < nrays_sweep) and
                            (ind_rng+rng_nb >= 0) and
                            (ind_rng+rng_nb < radar.ngates)):
                        if (data_sweep[ind_ray+ray_nb, ind_rng+rng_nb] is not
                                np.ma.masked):
                            data_cube.append(
                                data_sweep[ind_ray+ray_nb, ind_rng+rng_nb])

            # remove data far from median of neighbours or with not enough
            # valid neighbours
            if len(data_cube) < nb_min:
                field_out['data'][
                    sweep_start+ind_ray, ind_rng] = np.ma.masked
            elif (abs(np.ma.median(data_cube) -
                      data_sweep[ind_ray, ind_rng]) > threshold):
                field_out['data'][sweep_start+ind_ray, ind_rng] = np.ma.masked

    if field_name.startswith('corrected_'):
        new_field_name = field_name
    elif field_name.startswith('uncorrected_'):
        new_field_name = field_name.replace(
            'uncorrected_', 'corrected_', 1)
    else:
        new_field_name = 'corrected_'+field_name

    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field(new_field_name, field_out)

    return new_dataset, ind_rad


def process_hydroclass(procstatus, dscfg, radar_list=None):
    """
    Classifies precipitation echoes

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
        HYDRO_METHOD : string. Dataset keyword
            The hydrometeor classification method. One of the following:
            SEMISUPERVISED
        RADARCENTROIDS : string. Datset keyword
            Used with HYDRO_METHOD SEMISUPERVISED. The name of the radar of
            which the derived centroids will be used. One of the following: A
            Albis, L Lema, P Plaine Morte, DX50
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """
    if procstatus != 1:
        return None, None

    if 'HYDRO_METHOD' not in dscfg:
        raise Exception(
            "ERROR: Undefined parameter 'HYDRO_METHOD' for dataset '%s'"
            % dscfg['dsname'])

    if dscfg['HYDRO_METHOD'] == 'SEMISUPERVISED':
        temp_field = None
        iso0_field = None
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'dBZ':
                refl_field = 'reflectivity'
            if datatype == 'dBZc':
                refl_field = 'corrected_reflectivity'
            if datatype == 'ZDR':
                zdr_field = 'differential_reflectivity'
            if datatype == 'ZDRc':
                zdr_field = 'corrected_differential_reflectivity'
            if datatype == 'RhoHV':
                rhv_field = 'cross_correlation_ratio'
            if datatype == 'RhoHVc':
                rhv_field = 'corrected_cross_correlation_ratio'
            if datatype == 'KDP':
                kdp_field = 'specific_differential_phase'
            if datatype == 'KDPc':
                kdp_field = 'corrected_specific_differential_phase'
            if datatype == 'TEMP':
                temp_field = 'temperature'
            if datatype == 'H_ISO0':
                iso0_field = 'height_over_iso0'

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if temp_field is None and iso0_field is None:
            warn('iso0 or temperature fields needed to create hydrometeor ' +
                 'classification field')
            return None, None

        if temp_field is not None and (temp_field not in radar.fields):
            warn('Unable to create hydrometeor classification field. ' +
                 'Missing temperature field')
            return None, None

        if iso0_field is not None and (iso0_field not in radar.fields):
            warn('Unable to create hydrometeor classification field. ' +
                 'Missing height over iso0 field')
            return None, None

        temp_ref = 'temperature'
        if iso0_field is not None:
            temp_ref = 'height_over_iso0'

        if ((refl_field not in radar.fields) or
                (zdr_field not in radar.fields) or
                (rhv_field not in radar.fields) or
                (kdp_field not in radar.fields)):
            warn('Unable to create hydrometeor classification field. ' +
                 'Missing data')
            return None, None

        mass_centers = np.zeros((9, 5))
        if dscfg['RADARCENTROIDS'] == 'A':
            #      Zh      ZDR     kdp   RhoHV   delta_Z
            mass_centers[0, :] = [
                13.5829, 0.4063, 0.0497, 0.9868, 1330.3]  # DS
            mass_centers[1, :] = [
                02.8453, 0.2457, 0.0000, 0.9798, 0653.8]  # CR
            mass_centers[2, :] = [
                07.6597, 0.2180, 0.0019, 0.9799, -1426.5]  # LR
            mass_centers[3, :] = [
                31.6815, 0.3926, 0.0828, 0.9978, 0535.3]  # GR
            mass_centers[4, :] = [
                39.4703, 1.0734, 0.4919, 0.9876, -1036.3]  # RN
            mass_centers[5, :] = [
                04.8267, -0.5690, 0.0000, 0.9691, 0869.8]  # VI
            mass_centers[6, :] = [
                30.8613, 0.9819, 0.1998, 0.9845, -0066.1]  # WS
            mass_centers[7, :] = [
                52.3969, 2.1094, 2.4675, 0.9730, -1550.2]  # MH
            mass_centers[8, :] = [
                50.6186, -0.0649, 0.0946, 0.9904, 1179.9]  # IH/HDG
        elif dscfg['RADARCENTROIDS'] == 'L':
            #       Zh      ZDR     kdp   RhoHV   delta_Z
            mass_centers[0, :] = [
                13.8231, 0.2514, 0.0644, 0.9861, 1380.6]  # DS
            mass_centers[1, :] = [
                03.0239, 0.1971, 0.0000, 0.9661, 1464.1]  # CR
            mass_centers[2, :] = [
                04.9447, 0.1142, 0.0000, 0.9787, -0974.7]  # LR
            mass_centers[3, :] = [
                34.2450, 0.5540, 0.1459, 0.9937, 0945.3]  # GR
            mass_centers[4, :] = [
                40.9432, 1.0110, 0.5141, 0.9928, -0993.5]  # RN
            mass_centers[5, :] = [
                03.5202, -0.3498, 0.0000, 0.9746, 0843.2]  # VI
            mass_centers[6, :] = [
                32.5287, 0.9751, 0.2640, 0.9804, -0055.5]  # WS
            mass_centers[7, :] = [
                52.6547, 2.7054, 2.5101, 0.9765, -1114.6]  # MH
            mass_centers[8, :] = [
                46.4998, 0.1978, 0.6431, 0.9845, 1010.1]  # IH/HDG
        elif dscfg['RADARCENTROIDS'] == 'P':
            #       Zh      ZDR     kdp   RhoHV   delta_Z
            mass_centers[0, :] = [
                13.9882, 0.2470, 0.0690, 0.9939, 1418.1]  # DS
            mass_centers[1, :] = [
                00.9834, 0.4830, 0.0043, 0.9834, 0950.6]  # CR
            mass_centers[2, :] = [
                05.3962, 0.2689, 0.0000, 0.9831, -0479.5]  # LR
            mass_centers[3, :] = [
                35.3411, 0.1502, 0.0940, 0.9974, 0920.9]  # GR
            mass_centers[4, :] = [
                35.0114, 0.9681, 0.1106, 0.9785, -0374.0]  # RN
            mass_centers[5, :] = [
                02.5897, -0.3879, 0.0282, 0.9876, 0985.5]  # VI
            mass_centers[6, :] = [
                32.2914, 0.7789, 0.1443, 0.9075, -0153.5]  # WS
            mass_centers[7, :] = [
                53.2413, 1.8723, 0.3857, 0.9454, -0470.8]  # MH
            mass_centers[8, :] = [
                44.7896, 0.0015, 0.1349, 0.9968, 1116.7]  # IH/HDG
        elif dscfg['RADARCENTROIDS'] == 'W':
            #       Zh      ZDR     kdp   RhoHV   delta_Z
            mass_centers[0, :] = [
                16.7650, 0.3754, 0.0442, 0.9866, 1409.0]  # DS
            mass_centers[1, :] = [
                01.4418, 0.3786, 0.0000, 0.9490, 1415.8]  # CR
            mass_centers[2, :] = [
                16.0987, 0.3238, 0.0000, 0.9871, -0818.7]  # LR
            mass_centers[3, :] = [
                36.5465, 0.2041, 0.0731, 0.9952, 0745.4]  # GR
            mass_centers[4, :] = [
                43.4011, 0.6658, 0.3241, 0.9894, -0778.5]  # RN
            mass_centers[5, :] = [
                00.9077, -0.4793, 0.0000, 0.9502, 1488.6]  # VI
            mass_centers[6, :] = [
                36.8091, 0.7266, 0.1284, 0.9924, -0071.1]  # WS
            mass_centers[7, :] = [
                53.8402, 0.8922, 0.5306, 0.9890, -1017.6]  # MH
            mass_centers[8, :] = [
                45.9686, 0.0845, 0.0963, 0.9940, 0867.4]  # IH/HDG
        elif dscfg['RADARCENTROIDS'] == 'DX50':
            #       Zh      ZDR     kdp   RhoHV   delta_Z
            mass_centers[0, :] = [
                19.0770, 0.4139, 0.0099, 0.9841, 1061.7]  # DS
            mass_centers[1, :] = [
                03.9877, 0.5040, 0.0000, 0.9642, 0856.6]  # CR
            mass_centers[2, :] = [
                20.7982, 0.3177, 0.0004, 0.9858, -1375.1]  # LR
            mass_centers[3, :] = [
                34.7124, -0.3748, 0.0988, 0.9828, 1224.2]  # GR
            mass_centers[4, :] = [
                33.0134, 0.6614, 0.0819, 0.9802, -1169.8]  # RN
            mass_centers[5, :] = [
                08.2610, -0.4681, 0.0000, 0.9722, 1100.7]  # VI
            mass_centers[6, :] = [
                35.1801, 1.2830, 0.1322, 0.9162, -0159.8]  # WS
            mass_centers[7, :] = [
                52.4539, 2.3714, 1.1120, 0.9382, -1618.5]  # MH
            mass_centers[8, :] = [
                44.2216, -0.3419, 0.0687, 0.9683, 1272.7]  # IH/HDG
        else:
            warn(
                ' Unknown radar. ' +
                'Default centroids will be used in classification.')
            mass_centers = None

        hydro = pyart.retrieve.hydroclass_semisupervised(
            radar, mass_centers=mass_centers,
            weights=np.array([1., 1., 1., 0.75, 0.5]), refl_field=refl_field,
            zdr_field=zdr_field, rhv_field=rhv_field, kdp_field=kdp_field,
            temp_field=temp_field, iso0_field=iso0_field, hydro_field=None,
            temp_ref=temp_ref)
    else:
        raise Exception(
            "ERROR: Unknown hydrometeor classification method " +
            dscfg['HYDRO_METHOD'])

    # prepare for exit
    new_dataset = {'radar_out': deepcopy(radar)}
    new_dataset['radar_out'].fields = dict()
    new_dataset['radar_out'].add_field('radar_echo_classification', hydro)

    return new_dataset, ind_rad


def process_melting_layer(procstatus, dscfg, radar_list=None):
    """
    Detects the melting layer

    Parameters
    ----------
    procstatus : int
        Processing status: 0 initializing, 1 processing volume,
        2 post-processing
    dscfg : dictionary of dictionaries
        data set configuration. Accepted Configuration Keywords::

        datatype : list of string. Dataset keyword
            The input data types
    radar_list : list of Radar objects
        Optional. list of radar objects

    Returns
    -------
    new_dataset : dict
        dictionary containing the output
    ind_rad : int
        radar index

    """
    if procstatus != 1:
        return None, None

    if 'ML_METHOD' not in dscfg:
        raise Exception(
            "ERROR: Undefined parameter 'ML_METHOD' for dataset '%s'"
            % dscfg['dsname'])

    if dscfg['ML_METHOD'] == 'GIANGRANDE':

        temp_ref = 'temperature'
        temp_field = None
        iso0_field = None
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'dBZ':
                refl_field = 'reflectivity'
            if datatype == 'dBZc':
                refl_field = 'corrected_reflectivity'
            if datatype == 'ZDR':
                zdr_field = 'differential_reflectivity'
            if datatype == 'ZDRc':
                zdr_field = 'corrected_differential_reflectivity'
            if datatype == 'RhoHV':
                rhv_field = 'cross_correlation_ratio'
            if datatype == 'RhoHVc':
                rhv_field = 'corrected_cross_correlation_ratio'
            if datatype == 'TEMP':
                temp_field = 'temperature'
            if datatype == 'H_ISO0':
                iso0_field = 'height_over_iso0'

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if temp_field is None and iso0_field is None:
            warn('iso0 or temperature fields needed to detect melting layer')
            return None, None

        if temp_field is not None and (temp_field not in radar.fields):
            warn('Unable to detect melting layer. Missing temperature field')
            return None, None

        if iso0_field is not None and (iso0_field not in radar.fields):
            warn('Unable to detect melting layer. ' +
                 'Missing height over iso0 field')
            return None, None

        if iso0_field is not None:
            temp_ref = 'height_over_iso0'

        if ((refl_field not in radar.fields) or
                (zdr_field not in radar.fields) or
                (rhv_field not in radar.fields)):
            warn('Unable to detect melting layer. Missing data')
            return None, None

        # User defined variables
        # (more parameters are currently hard coded into the detection
        # algorithm)
        # min rhohv to consider pixel potential melting layer pixel
        rhomin = dscfg.get('rhomin', 0.75)
        # max rhohv to consider pixel potential melting layer pixel
        rhomax = dscfg.get('rhomax', 0.94)
        # minimum number of melting layer points to consider valid melting
        # layer detection
        nml_points_min = dscfg.get('nml_points_min', 1500)
        # percentile of ml points above which is considered that the bottom of
        # the melting layer starts
        percentile_bottom = dscfg.get('percentile_bottom', 0.3)

        if not dscfg['initialized']:
            # initialize dataset
            new_dataset = pyart.retrieve.melting_layer_giangrande(
                radar, rhomin=rhomin, rhomax=rhomax,
                nml_points_min=nml_points_min,
                percentile_bottom=percentile_bottom, refl_field=refl_field,
                zdr_field=zdr_field, rhv_field=rhv_field,
                temp_field=temp_field, iso0_field=iso0_field, ml_field=None,
                temp_ref=temp_ref, get_iso0=True, new_dataset=None)
            dscfg['initialized'] = True
        else:
            # use previous detection
            new_dataset = pyart.retrieve.melting_layer_giangrande(
                radar, rhomin=rhomin, rhomax=rhomax,
                nml_points_min=nml_points_min,
                percentile_bottom=percentile_bottom, refl_field=refl_field,
                zdr_field=zdr_field, rhv_field=rhv_field,
                temp_field=temp_field, iso0_field=iso0_field, ml_field=None,
                temp_ref=temp_ref, get_iso0=True,
                new_dataset=dscfg['ml_globdata'])

        # update global stack
        dscfg['ml_globdata'] = new_dataset

    elif dscfg['ML_METHOD'] == 'WOLFENSBERGER':
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'dBZ':
                refl_field = 'reflectivity'
            if datatype == 'dBZc':
                refl_field = 'corrected_reflectivity'
            if datatype == 'RhoHV':
                rhohv_field = 'cross_correlation_ratio'
            if datatype == 'RhoHVc':
                rhohv_field = 'corrected_cross_correlation_ratio'

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if ((refl_field not in radar.fields) or
                (rhohv_field not in radar.fields)):
            warn('Unable to detect melting layer. Missing data')
            return None, None

        # User defined parameters
        max_range = dscfg.get('max_range', 20000.)
        detect_threshold = dscfg.get('detect_threshold', 0.02)
        interp_holes = dscfg.get('interp_holes', False)
        max_length_holes = dscfg.get('max_length_holes', 250)
        check_min_length = dscfg.get('check_min_length', True)

        ml_list = pyart.retrieve.detect_ml(
            radar, refl_field=refl_field, rhohv_field=rhohv_field,
            max_range=max_range, detect_threshold=detect_threshold,
            interp_holes=interp_holes, max_length_holes=max_length_holes,
            check_min_length=check_min_length)

        ml_data = np.ma.empty((radar.nrays, radar.ngates), dtype=int)
        ml_data[:] = np.ma.masked

        ml_top = np.ma.empty(radar.nrays, dtype=float)
        ml_top[:] = np.ma.masked
        ml_bottom = np.ma.empty(radar.nrays, dtype=float)
        ml_bottom[:] = np.ma.masked
        for ind_sweep, ml_dict in enumerate(ml_list):
            ind_start = radar.sweep_start_ray_index['data'][ind_sweep]
            ind_end = radar.sweep_end_ray_index['data'][ind_sweep]
            ml_data[ind_start:ind_end+1, :] = ml_dict['ml_pol']['data']+2
            ml_top[ind_start:ind_end+1] = ml_dict['ml_pol']['top_ml']
            ml_bottom[ind_start:ind_end+1] = ml_dict['ml_pol']['bottom_ml']

        mask = np.logical_or(
            np.ma.getmaskarray(radar.fields[refl_field]['data']),
            np.ma.getmaskarray(radar.fields[rhohv_field]['data']))
        ml_data = np.ma.masked_where(mask, ml_data)
        ml = pyart.config.get_metadata('melting_layer')
        ml['data'] = ml_data

        ml_top = np.ma.masked_invalid(ml_top)
        ml_bottom = np.ma.masked_invalid(ml_bottom)

    elif dscfg['ML_METHOD'] == 'FROM_HYDROCLASS':
        for datatypedescr in dscfg['datatype']:
            radarnr, _, datatype, _, _ = get_datatype_fields(datatypedescr)
            if datatype == 'hydro':
                hydro_field = get_fieldname_pyart(datatype)

        ind_rad = int(radarnr[5:8])-1
        if radar_list[ind_rad] is None:
            warn('No valid radar')
            return None, None
        radar = radar_list[ind_rad]

        if hydro_field not in radar.fields:
            warn('Unable to detect melting layer. Missing data')
            return None, None

        ml_data = np.ma.empty((radar.nrays, radar.ngates), dtype=int)
        ml_data[:] = np.ma.masked
        hydro_data = radar.fields[hydro_field]['data']

        # get the location of each hydrometeor class
        is_ds = hydro_data == 1
        is_cr = hydro_data == 2
        is_lr = hydro_data == 3
        is_gr = hydro_data == 4
        is_rn = hydro_data == 5
        is_vi = hydro_data == 6
        is_ws = hydro_data == 7
        # is_mh = hydro_data == 8
        is_ih = hydro_data == 9

        ml_data[is_ds] = 5
        ml_data[is_cr] = 5
        ml_data[is_lr] = 1
        ml_data[is_gr] = 5
        ml_data[is_rn] = 1
        ml_data[is_vi] = 5
        ml_data[is_ws] = 3
        ml_data[is_ih] = 5

        mask = deepcopy(np.ma.getmaskarray(ml_data))

        # User defined parameters
        force_continuity = dscfg.get('force_continuity', True)
        dist_max = dscfg.get('dist_max', 350.)

        ml_top = np.ma.empty(radar.nrays, dtype=float)
        ml_top[:] = np.ma.masked
        ml_bottom = np.ma.empty(radar.nrays, dtype=float)
        ml_bottom[:] = np.ma.masked
        for ind_ray in range(radar.nrays):
            inds_rng_ml = np.ma.where(ml_data[ind_ray, :] == 3)[0]

            # No melting layer identified. Do nothing
            if inds_rng_ml.size == 0:
                if force_continuity:
                    ml_data[ind_ray, :] = np.ma.masked
                continue

            # Remove holes in melting layer
            if force_continuity:
                # There is just one gate. Do nothing
                if inds_rng_ml.size == 1:
                    continue

                # identify continuos regions
                rng_ml = radar.range['data'][inds_rng_ml]
                dist_ml = np.append(
                    rng_ml[1:]-rng_ml[0:-1], rng_ml[-1]-rng_ml[-2])
                ind_valid = np.where(dist_ml < dist_max)[0]
                inds_rng_ml = inds_rng_ml[ind_valid]

                # melting layer discontinuous. Remove ray
                if inds_rng_ml.size == 0:
                    ml_data[ind_ray, :] = np.ma.masked
                    continue

                # Fill in gaps
                ml_data[ind_ray, :] = 3
                if inds_rng_ml[0] > 0:
                    ml_data[ind_ray, 0:inds_rng_ml[0]] = 1
                if inds_rng_ml[-1] < radar.ngates-1:
                    ml_data[ind_ray, inds_rng_ml[-1]+1:] = 5

            # get top and bottom
            ml_bottom[ind_ray] = (
                radar.gate_altitude['data'][ind_ray, inds_rng_ml[0]])
            ml_top[ind_ray] = (
                radar.gate_altitude['data'][ind_ray, inds_rng_ml[-1]])

        if force_continuity:
            ml_data = np.ma.masked_where(mask, ml_data)

        ml = pyart.config.get_metadata('melting_layer')
        ml['data'] = ml_data

        get_iso0 = dscfg.get('get_iso0', False)

        # Create melting layer object containing top and bottom and metadata
        ml_obj = deepcopy(radar)

        # modify original metadata
        ml_obj.range['data'] = np.array([0, 1], dtype='float64')
        ml_obj.ngates = 2

        ml_obj.gate_x = np.zeros((ml_obj.nrays, ml_obj.ngates), dtype=float)
        ml_obj.gate_y = np.zeros((ml_obj.nrays, ml_obj.ngates), dtype=float)
        ml_obj.gate_z = np.zeros((ml_obj.nrays, ml_obj.ngates), dtype=float)

        ml_obj.gate_longitude = np.zeros(
            (ml_obj.nrays, ml_obj.ngates), dtype=float)
        ml_obj.gate_latitude = np.zeros(
            (ml_obj.nrays, ml_obj.ngates), dtype=float)
        ml_obj.gate_altitude = np.zeros(
            (ml_obj.nrays, ml_obj.ngates), dtype=float)

        # input field
        ml_pos = pyart.config.get_metadata('melting_layer_height')
        ml_aux = np.ma.empty((ml_obj.nrays, ml_obj.ngates), dtype='float64')
        ml_aux[:, 0] = ml_bottom
        ml_aux[:, 1] = ml_top
        ml_pos['data'] = ml_aux

        ml_obj.fields = dict()
        ml_obj.add_field('melting_layer_height', ml_pos)

        # prepare for exit
        new_dataset = {
            'radar_out': deepcopy(radar),
            'ml_obj': ml_obj}
        new_dataset['radar_out'].fields = dict()
        new_dataset['radar_out'].add_field('melting_layer', ml)

        if get_iso0:
            iso0_data = np.ma.empty((radar.nrays, radar.ngates), dtype=float)
            iso0_data[:] = np.ma.masked
            for ind_ray in range(radar.nrays):
                iso0_data[ind_ray, :] = radar.gate_altitude['data'][ind_ray, :]-ml_top[ind_ray]
            iso0_dict = pyart.config.get_metadata('height_over_iso0')
            iso0_dict['data'] = iso0_data
            new_dataset['radar_out'].add_field('height_over_iso0', iso0_dict)

    else:
        raise Exception(
            "ERROR: Unknown melting layer retrieval method " +
            dscfg['ML_METHOD'])

    return new_dataset, ind_rad
