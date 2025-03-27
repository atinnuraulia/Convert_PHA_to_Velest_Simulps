# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 12:32:17 2025

@author: Atin
"""

# Input and output file paths
input_file = "example_data.pha"  # Replace with actual file
stations_file = "example_station.txt"  # File containing station names
output_file_cnv = "inputVelest.cnv"  # Output file in CNV format for Velest

# Set minimum P and S values for filtering
MIN_P = 3  # Minimum required P values per event
MIN_S = 1  # Minimum required S values per event

# Load station names into a set
station_names = set()
with open(stations_file, "r") as sfile:
    for line in sfile:
        parts = line.split()
        if parts:  # Ensure the line is not empty
            station = parts[0]  # Extract first column (station name)
            station_names.add(station)

        station_names.add(station)

# Initialize storage
header = None
event_id = None
p_data = {}
s_data = {}
event_info_dict = {}

with open(input_file, "r") as infile:
    for line in infile:
        line = line.strip()
        if line.startswith("#"):  # New event header
            if event_id is not None:
                p_count = len(p_data.get(event_id, {}))
                s_count = len(s_data.get(event_id, {}))
                if p_count >= MIN_P and s_count >= MIN_S:
                    event_info_dict[event_id] = header  # Store event metadata

            # Reset for new event
            parts = line[1:].split()
            header = parts[:14]  # Extract event metadata
            event_id = parts[13]  # Event number (event_id)
            p_data[event_id] = {}
            s_data[event_id] = {}

        elif header and line:  # Process travel time data
            parts = line.split()
            station_name = parts[0].strip()  # Station name

            if station_name in station_names:  # Filter based on station list
                travel_time = float(parts[1])  # Travel time
                phase_type = parts[-1]  # Phase type (P or S)

                if phase_type == "P":
                    p_data[event_id][station_name] = travel_time
                elif phase_type == "S":
                    s_data[event_id][station_name] = travel_time

# Process last event
if event_id is not None:
    p_count = len(p_data.get(event_id, {}))
    s_count = len(s_data.get(event_id, {}))
    if p_count >= MIN_P and s_count >= MIN_S:
        event_info_dict[event_id] = header  # Store last event metadata

# Function to write earthquake data to data.cnv (using original S values)
def write_data_cnv(fidC, event_id, header, p_data, s_data):
    """Writes formatted earthquake event data to data.cnv (CNV format)."""
    year, month, date, hour, minute, origin_time, lat, lon, depth, mag, *_ = header
    latitude = float(lat)
    longitude = float(lon)
    depth = float(depth)
    magnitude = float(mag)

    lat_abs = abs(latitude)
    lat_dir = "N" if latitude >= 0 else "S"
    lon_dir = "E"  # Longitude always uses 'E'

    # Write event header
    fidC.write(f"{year[-2:]}{month}{date} {hour}{minute} {float(origin_time):5.2f} "
               f"{lat_abs:7.2f}{lat_dir}{abs(longitude):9.2f}{lon_dir} "
               f"  {depth:5.2f}   {magnitude:5.2f}   0\n")

    # Prepare travel time data
    travel_time_list = []
    for station in sorted(p_data[event_id].keys()):
        ttp = p_data[event_id][station]
        tts = s_data.get(event_id, {}).get(station, 99.99)  # Default S to 99.99

        station_name = station.rjust(4)  # Left align station name
        if ttp != 99.99:
            travel_time_list.append(f"{station_name}P1{ttp:6.2f}")
        if tts != 99.99:
            travel_time_list.append(f"{station_name}S1{tts:6.2f}")  # Original S value

    for j in range(0, len(travel_time_list), 6):
        fidC.write("".join(travel_time_list[j:j+6]) + "\n")

    fidC.write("\n")  # Blank line as event separator


# Write both output files
with open(output_file_cnv, "w") as fidC:
    for event_id, header in event_info_dict.items():
        write_data_cnv(fidC, event_id, header, p_data, s_data)


