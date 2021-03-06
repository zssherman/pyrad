"""
pyrad.graph.plots_aux
=====================

Auxiliary plotting functions

.. autosummary::
    :toctree: generated/

    get_colobar_label
    get_field_name
    get_norm

"""

import matplotlib as mpl
mpl.use('Agg')

# Increase a bit font size
mpl.rcParams.update({'font.size': 16})
mpl.rcParams.update({'font.family':  "sans-serif"})

import pyart


def get_colobar_label(field_dict, field_name):
    """
    creates the colorbar label using field metadata

    Parameters
    ----------
    field_dict : dict
        dictionary containing field metadata
    field_name : str
        name of the field

    Returns
    -------
    label : str
        colorbar label

    """
    if 'standard_name' in field_dict:
        standard_name = field_dict['standard_name']
    elif 'long_name' in field_dict:
        standard_name = field_dict['long_name']
    else:
        standard_name = field_name

    if 'units' in field_dict:
        units = field_dict['units']
    else:
        units = '?'

    return pyart.graph.common.generate_colorbar_label(standard_name, units)


def get_field_name(field_dict, field):
    """
    Return a nice field name for a particular field

    Parameters
    ----------
    field_dict : dict
        dictionary containing field metadata
    field : str
        name of the field

    Returns
    -------
    field_name : str
        the field name

    """
    if 'standard_name' in field_dict:
        field_name = field_dict['standard_name']
    elif 'long_name' in field_dict:
        field_name = field_dict['long_name']
    else:
        field_name = str(field)
    field_name = field_name.replace('_', ' ')
    field_name = field_name[0].upper() + field_name[1:]

    return field_name


def get_norm(field_name):
    """
    Computes the normalization of the colormap, and gets the ticks and labels
    of the colorbar from the metadata of the field. Returns None if the
    required parameters are not present in the metadata

    Parameters
    ----------
    field_name : str
        name of the field

    Returns
    -------
    norm : list
        the colormap index
    ticks : list
        the list of ticks in the colorbar
    labels : list
        the list of labels corresponding to each tick

    """
    norm = None
    ticks = None
    ticklabs = None

    field_dict = pyart.config.get_metadata(field_name)
    cmap = mpl.cm.get_cmap(pyart.config.get_field_colormap(field_name))

    if 'boundaries' in field_dict:
        norm = mpl.colors.BoundaryNorm(
            boundaries=field_dict['boundaries'], ncolors=cmap.N)

    if 'ticks' in field_dict:
        ticks = field_dict['ticks']
        if 'labels' in field_dict:
            ticklabs = field_dict['labels']

    return norm, ticks, ticklabs
