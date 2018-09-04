#!/usr/bin/env python
# coding:utf-8


import argparse
from datetime import datetime
from netCDF4 import Dataset
import numpy as np
from numpy import meshgrid
from scipy.interpolate import interp2d
from scipy.ndimage import zoom
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


class EdMap(Dataset):
    def __init__(self, filepath):
        super(EdMap, self).__init__(filepath)

    @property
    def msl_alt(self):
        return self.variables['MSL_alt'][:]

    @property
    def geo_lon(self):
        return self.variables['GEO_lon'][:]

    @property
    def geo_lat(self):
        return self.variables['GEO_lat'][:]

    @property
    def elec_dens(self):
        return self.variables['ELEC_dens'][:]

    @property
    def time(self):
        return datetime(self.year, self.month, self.day,
                        self.hour, self.minute, int(self.second))


def plot_ied(filepath, output, altitude=250):
    try:
        edmap = EdMap(filepath)
    except IOError:
        return
    lat = edmap.geo_lat
    lon = edmap.geo_lon
    alt = edmap.msl_alt
    elec_dens = edmap.elec_dens
    map = Basemap(llcrnrlon=lon[0], urcrnrlon=lon[-1],
                  llcrnrlat=lat[0], urcrnrlat=lat[-1])
    ind = min(range(len(alt)), key=lambda i: abs(alt[i] - altitude))
    f = interp2d(lon, lat, elec_dens[ind])
    x = np.arange(lon[0], lon[-1] + 0.5, 0.5)
    y = np.arange(lat[0], lat[-1] + 0.5, 0.5)
    xx, yy = meshgrid(x, y)
    data = f(x, y) / 1E6
    map.pcolormesh(xx, yy, data, shading='gouraud', vmin=0, vmax=1)
    map.colorbar()
    plt.title('IED %s (%s)' % (edmap.time, alt[ind]), size=25)
    plt.show()


def plot_contour(filepath, output, value, flag):
    try:
        edmap = EdMap(filepath)
    except IOError:
        return
    elec_dens = edmap.elec_dens
    alt = edmap.msl_alt
    lat = edmap.geo_lat
    lon = edmap.geo_lon
    nalt = elec_dens.shape[0]
    nlat = elec_dens.shape[1]
    nlon = elec_dens.shape[2]
    ind = 0
    elec_line = None

    if flag == 0:
        ind = min(range(nlon), key=lambda i: abs(lon[i] - value))
        elec_line = elec_dens[:, :, ind] / (10 ** 6)
        plt.contourf(lat, alt, elec_line)
    elif flag == 1:
        ind = min(range(nlat), key=lambda i: abs(lat[i] - value))
        elec_line = elec_dens[:, ind, :]
        plt.contourf(lon, alt, elec_line)
    plt.colorbar()
    plt.show()
    plt.clf()
    plt.close()


def plot_vtec(filepath, output):
    try:
        edmap = EdMap(filepath)
    except IOError:
        return
    elec_dens = edmap.elec_dens
    lat = edmap.geo_lat
    lon = edmap.geo_lon
    nalt = elec_dens.shape[0]
    nlat = elec_dens.shape[1]
    nlon = elec_dens.shape[2]
    vtec_map = np.zeros((nlat, nlon))
    for i in range(nlat):
        for j in range(nlon):
            for k in range(nalt):
                vtec_map[i, j] += elec_dens[k, i, j] * 1E6 * 50 * 1E3 / 1E16
    map = Basemap(llcrnrlon=lon[0], urcrnrlon=lon[-1],
                  llcrnrlat=lat[0], urcrnrlat=lat[-1])
    map.drawparallels(lat[0:nlat:int(nlat / 5)],
                      linewidth=0., labels=[1, 0, 0, 0])
    map.drawmeridians(lon[0:nlon:int(nlon / 6)],
                      linewidth=0., labels=[0, 0, 0, 1])
    map.drawcoastlines()
    f = interp2d(lon, lat, vtec_map)
    x = np.arange(lon[0], lon[-1] + 0.5, 0.5)
    y = np.arange(lat[0], lat[-1] + 0.5, 0.5)
    xx, yy = meshgrid(x, y)
    data = f(x, y)
    map.pcolormesh(xx, yy, data, shading='gouraud')
    map.colorbar()
    plt.title('TEC %s' % edmap.time, size=25)
    plt.show()


def process(filepath, output, parameter, t):
    if t == 'ied':
        plot_ied(filepath, output, parameter)
    elif t == 'tec':
        plot_vtec(filepath, output)
    elif t == 'lon':
        plot_contour(filepath, output, parameter, 0)
    elif t == 'lat':
        plot_contour(filepath, output, parameter, 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('edmap')
    parser.add_argument('-i', '--input', type=str,
                        help='edmap filepath', required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='output dir', required=True)
    parser.add_argument('-p', '--parameter', type=float, default=250)
    parser.add_argument('-t', '--type', type=str,
                        choices=['ied', 'tec', 'lon', 'lat'], default='ied')
    args = parser.parse_args()
    process(args.input, args.output, args.parameter, args.type)
