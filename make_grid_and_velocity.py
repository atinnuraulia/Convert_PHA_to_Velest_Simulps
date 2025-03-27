# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:01:20 2025

@author: Atin
"""

import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj, Transformer

# ===== Define Coordinate Projections =====
wgs_proj = Proj(proj="latlong", datum="WGS84")  # WGS84 Lat/Lon
utm_proj = Proj(proj="utm", zone=51, datum="WGS84", south=True)  # Adjust UTM zone/south if needed

# Transformers
transformer_to_utm = Transformer.from_proj(wgs_proj, utm_proj)
transformer_to_latlon = Transformer.from_proj(utm_proj, wgs_proj)

# ===== Reference Point (Longitude, Latitude) =====
lon_ref = 121.6425  # Change as needed
lat_ref = -3.9063   # Change as needed

# Convert to UTM
X_ref, Y_ref = transformer_to_utm.transform(lon_ref, lat_ref)

# ===== Grid Definitions (Same as Velocity File) =====
xn = np.array([-400.0, -300.0, -200.0, -100.0, -50.0, -25.0, 0.0, 25.0, 50.0, 100.0, 200.0, 300.0, 400.0])
yn = np.array([-400.0, -300.0, -200.0, -100.0, -50.0, -25.0, 0.0, 25.0, 50.0, 100.0, 200.0, 300.0, 400.0])
zn = np.array([-10.0, 0.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0, 150.0, 200.0])  # Depth positive down

nx, ny, nz = len(xn), len(yn), len(zn)
nzz = nz + nz  # For velocity array

vel = [3.00, 5.40, 6.156, 6.157, 6.377, 7.816, 7.929, 8.102, 8.123, 8.217,  # P-wave velocity
       1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75, 1.75]  # S-wave velocity

# ===== Generate Grid and Save to File =====
grid_data = []
itung = 0
with open('grid_data.txt', 'w') as out:
    for k in range(nz):
        for i in range(nx):
            for j in range(ny):
                itung += 1
                x = X_ref + (xn[j] * 1000)
                y = Y_ref + (yn[i] * 1000)
                z = zn[k]  # Depth positive down

                lon, lat = transformer_to_latlon.transform(x, y)
                grid_data.append([itung, lon, lat, z, 0])
                out.write(f'{itung:4d} {lon:20.7f} {lat:20.7f} {z:5.1f} {0}\n')

# Convert grid data to NumPy array
mdat12 = np.array(grid_data)
lon1, lat1, zz1 = mdat12[:, 1], mdat12[:, 2], mdat12[:, 3]

# ===== Read Earthquake Data from data.pha =====
earthquake_lons, earthquake_lats, earthquake_depths = [], [], []

with open("example_data.pha", "r") as pha_file:
    for line in pha_file:
        parts = line.split()
        if line.startswith("#") and len(parts) >= 10:
            lat = float(parts[7])
            lon = float(parts[8])
            depth = float(parts[9])
            earthquake_lats.append(lat)
            earthquake_lons.append(lon)
            earthquake_depths.append(depth)

# ===== Write Velocity File =====
with open('velocity.dat', 'wt') as out:
    out.write(f' 1{nx:3d}{ny:3d}{nz:3d}\n')
    out.write("".join(f"{val:6.1f}" for val in xn) + "\n")  # X grid values
    out.write("".join(f"{val:6.1f}" for val in yn) + "\n")  # Y grid values
    out.write("".join(f"{val:6.1f}" for val in zn) + "\n")  # Z grid values
    out.write(' 0  0  0\n')

    for i in range(nzz):
        for j in range(ny):
            for k in range(nx):
                out.write(f'{vel[i]:5.2f}')
            out.write('\n')
# ===== User-defined perturbation =====
perturbation_percent = 0.05  # Example: 5% perturbation
increase_factor = 1 + perturbation_percent  # 1.05 for 5% increase
decrease_factor = 1 - perturbation_percent  # 0.95 for 5% decrease

# ===== Write Velocity File for Checkerboard Model =====
with open('velocityforcheckerboard.dat', 'wt') as out:
    out.write(f' 1{nx:3d}{ny:3d}{nz:3d}\n')
    out.write("".join(f"{val:6.1f}" for val in xn) + "\n")  # X grid values
    out.write("".join(f"{val:6.1f}" for val in yn) + "\n")  # Y grid values
    out.write("".join(f"{val:6.1f}" for val in zn) + "\n")  # Z grid values
    out.write(' 0  0  0\n')

    for i in range(nzz):
        for j in range(ny):
            for k in range(nx):
                perturbation = increase_factor if (i + j + k) % 2 == 0 else decrease_factor  # Checkerboard pattern
                out.write(f'{vel[i] * perturbation:5.2f}')
            out.write('\n')

# ===== PLOTTING =====

# Horizontal Grid (Longitude vs Latitude)
plt.figure(1)
plt.title('Horizontal Grid')

plt.plot(lon1, lat1, '+', color='red', label='Grid Points')
plt.plot(earthquake_lons, earthquake_lats, 'bo', markersize=2, label='Earthquakes')
plt.plot(lon_ref, lat_ref, 'og', markerfacecolor='g', markersize=8, label='Reference Point')

plt.xlabel('Longitude (°)')
plt.ylabel('Latitude (°)')
plt.legend()
plt.grid(True)
plt.savefig('Horizontal_Grid_LonLat.jpg')

# East-West Vertical Grid (Longitude vs Depth)
plt.figure(2)
plt.title('East-West Grid')
plt.plot(lon1, zz1, '+', color='red', label='Grid Points')
plt.plot(earthquake_lons, earthquake_depths, 'bo', markersize=2, label='Earthquakes')

plt.xlabel('Longitude (°)')
plt.ylabel('Depth (km)')
plt.gca().invert_yaxis()  # Invert Y-axis so depth increases downward
plt.legend()
plt.grid(True)
plt.savefig('Vertical_Grid_EW.jpg')

# North-South Vertical Grid (Latitude vs Depth)
plt.figure(3)
plt.title('North-South Grid')
plt.plot(lat1, zz1, '+', color='red', label='Grid Points')
plt.plot(earthquake_lats, earthquake_depths, 'bo', markersize=2, label='Earthquakes')

plt.xlabel('Latitude (°)')
plt.ylabel('Depth (km)')
plt.gca().invert_yaxis()  # Invert Y-axis so depth increases downward
plt.legend()
plt.grid(True)
plt.savefig('Vertical_Grid_NS.jpg')

plt.show()
