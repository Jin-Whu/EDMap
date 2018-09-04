# EDMap
Plot ionosphere electron density profile.

# Requirements
1. python2.7
2. python packages: numpy, scipy, matplotlib, Basemap, netCDF4

# Usage
## Options:
- -i, --input: edmap filepath
- -o, --output: output directory
- -p, --parameter: parameter
- -t, --type: {ied, tec, lon, lat}

## Examples:
- Plot IED:  
`python edmap.py -i ionMap.nc -o . -t ied -p 200`
  > p is altitude, unit is km.

- Plot Tec:  
`python edmap.py -i ionMap.nc -o . -t tec`

- Plot lon/lat IED Profile:
  1. `python edmap.py -i ionMap.nc -o . -t lon -p 80`
    > p is longitude, unit is degree.

  2. `python edmap.py -i ionMap.nc -o . -t lat -p 30`
    > p is latitude, unit is degree.
