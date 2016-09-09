"""
pyrad.graph.plots
=================

Functions to plot Pyrad datasets

.. autosummary::
    :toctree: generated/

    plot_ppi
    plot_rhi
    plot_timeseries
    plot_timeseries_comp

"""

import matplotlib.pyplot as plt
import numpy as np

import pyart


def plot_ppi(radar, field_name, ind_el, prdcfg, fname):
    """
    plots a PPI

    Parameters
    ----------
    radar : Radar object
        object containing the radar data to plot

    field_name : str
        name of the radar field to plot

    ind_el : int
        sweep index to plot

    prdcfg : dict
        dictionary containing the product configuration

    fname : str
        name of the file where to store the plot

    Returns
    -------
    no return

    """
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=[prdcfg['ppiImageConfig']['xsize'],
                              prdcfg['ppiImageConfig']['ysize']],
                     dpi=72)
    ax = fig.add_subplot(111)
    display.plot_ppi(field_name, sweep=ind_el)
    display.set_limits(
        ylim=[prdcfg['ppiImageConfig']['ymin'],
              prdcfg['ppiImageConfig']['ymax']],
        xlim=[prdcfg['ppiImageConfig']['xmin'],
              prdcfg['ppiImageConfig']['xmax']])
    display.plot_range_rings([10, 20, 30, 40])
    display.plot_cross_hair(5.)

    fig.savefig(fname)

    plt.close()


def plot_rhi(radar, field_name, ind_az, prdcfg, fname):
    """
    plots an RHI

    Parameters
    ----------
    radar : Radar object
        object containing the radar data to plot

    field_name : str
        name of the radar field to plot

    ind_az : int
        sweep index to plot

    prdcfg : dict
        dictionary containing the product configuration

    fname : str
        name of the file where to store the plot

    Returns
    -------
    no return

    """
    display = pyart.graph.RadarDisplay(radar)
    fig = plt.figure(figsize=[prdcfg['rhiImageConfig']['xsize'],
                              prdcfg['rhiImageConfig']['ysize']],
                     dpi=72)
    ax = fig.add_subplot(111)
    display.plot_rhi(field_name, sweep=ind_az, reverse_xaxis=False)
    display.set_limits(
        ylim=[prdcfg['rhiImageConfig']['ymin'],
              prdcfg['rhiImageConfig']['ymax']],
        xlim=[prdcfg['rhiImageConfig']['xmin'],
              prdcfg['rhiImageConfig']['xmax']])
    display.plot_cross_hair(5.)

    fig.savefig(fname)
    plt.close()


def plot_timeseries(date, value, fname, labelx='Time [UTC]', labely='Value',
                    titl='Time Series', period=0):
    """
    plots a time series

    Parameters
    ----------
    date : datetime object
        time of the time series

    value : float array
        values of the time series

    fname : str
        name of the file where to store the plot

    labelx : str
        The label of the X axis

    labely : str
        The label of the Y axis

    titl : str
        The figure title

    period : float
        measurement period in seconds used to compute accumulation. If 0 no
        accumulation is computed

    Returns
    -------
    no return

    """
    if period > 0:
        value *= (period/3600.)
        value = np.ma.cumsum(value)

    fig = plt.figure(figsize=[10, 6])
    plt.plot(date, value)
    plt.xlabel(labelx)
    plt.ylabel(labely)
    plt.title(titl)

    fig.savefig(fname)
    plt.close()


def plot_timeseries_comp(date1, value1, date2, value2, fname,
                         labelx='Time [UTC]', labely='Value',
                         label1='Sensor 1', label2='Sensor 2',
                         titl='Time Series Comparison', period1=0, period2=0):
    """
    plots 2 time series in the same graph

    Parameters
    ----------
    date1 : datetime object
        time of the first time series

    value1 : float array
        values of the first time series

    date2 : datetime object
        time of the second time series

    value2 : float array
        values of the second time series

    fname : str
        name of the file where to store the plot

    labelx : str
        The label of the X axis

    labely : str
        The label of the Y axis

    label1, label2 : str
        legend label for each time series

    titl : str
        The figure title

     period1, period2 : float
        measurement period in seconds used to compute accumulation. If 0 no
        accumulation is computed

    Returns
    -------
    no return

    """
    if (period1 > 0) and (period2 > 0):
        value1 *= (period1/3600.)
        value1 = np.ma.cumsum(value1)

        value2 *= (period2/3600.)
        value2 = np.ma.cumsum(value2)

    fig = plt.figure(figsize=[10, 6])
    plt.plot(date1, value1, 'b', label=label1)
    plt.plot(date2, value2, 'r', label=label2)
    plt.legend(loc='best')
    plt.xlabel(labelx)
    plt.ylabel(labely)
    plt.title(titl)

    fig.savefig(fname)
    plt.close()