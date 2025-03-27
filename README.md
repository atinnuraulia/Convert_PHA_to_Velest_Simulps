# PHA_to_Velest_Simulps
This script base on python language to convert data from *.pha (BMKG catatalog)  in to Velest and Simulps12 format.
Velest and Simulps12 are programs in Fortran 77 language which are very sensitive to errors in input writing format, so this script was created to avoid errors in input writing.

# Pha_to_Simulps
This script is used to convert catalog data from BKMG with *.pha extension to make inputVelest.cnv as a Velest format input.
In this script you can add minimum criteria of P phase and S phase on each earthquake event that will be processed using Velest.
This script can also do filtering where the travel time used is only the travel time recorded by the station in the station list.

# Pha_to_Simulps
This script is used to convert catalog data from BKMG with *.pha extension to make earthq.dat as a simulps12 format input.
In this script you can add minimum criteria of P phase and S phase on each earthquake event that will be processed using SIMULPS12.
This script can also do filtering where the travel time used is only the travel time recorded by the station in the station list.

# make_grid_and_velocity.py
This script is used to make velocity model and checkerboard velocity model.
In addition to the velocity model, this script is also used to provide a 3-D grid plot and the distribution of earthquake hypocenters based on *.pha catalog data.

# System Requirements
* Python 3.8 or higher
* numpy
* matplotlib
* pyproj

# Example Output


Horizontal Grid
![Horizontal_Grid_LonLat](https://github.com/user-attachments/assets/93f53546-3a81-47bc-a7dd-b89c5f4891f0)


Vertical Grid
![Vertical_Grid_EW](https://github.com/user-attachments/assets/4e61294e-98bd-41db-bb09-182c4dfbdb38)
![Vertical_Grid_NS](https://github.com/user-attachments/assets/5ff9fb97-dd3b-4b74-89b4-8973c4662f40)

