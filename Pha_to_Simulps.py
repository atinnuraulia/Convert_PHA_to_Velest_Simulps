# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 12:32:17 2025

@author: Atin
"""

# Input and output file paths
input_file = "example_data.pha"  # Replace with actual file
stations_file = "example_station.txt"  # File containing station names
output_file_simulps = "earthq.dat"  # Output file for SimulPS

# Set minimum P and S values for filtering
MIN_P = 5  # Minimum required P values per event
MIN_S = 2  # Minimum required S values per event

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

 
# Function to write earthquake data to earthq.dat (using S-P values)
def write_earthq_dat(fidP, event_id, header, p_data, s_data):
    """Writes formatted earthquake event data to earthq.dat (SimulPS format)."""
    year, month, date, hour, minute, origin_time, lat, lon, depth, mag, *_ = header
    latitude = float(lat)
    longitude = float(lon)
    depth = float(depth)
    magnitude = float(mag)

    # Convert to required format
    yymmdd = f"{year[-2:]}{month.zfill(2)}{date.zfill(2)}"
    hhmm = f"{hour.zfill(2)}{minute.zfill(2)}"
    ss = float(origin_time)

    latdeg = abs(int(latitude))
    latmin = (abs(latitude) - latdeg) * 60

    longdeg = int(longitude)
    longmin = (abs(longitude) - longdeg) * 60

    # Write event header
    fidP.write(f"{yymmdd} {hhmm:4}{ss:6.2f}"
               f"{latdeg:3}{latmin:6.2f} "
               f"{longdeg:3}{longmin:6.2f}{depth:7.2f}   "
               f"{magnitude:4.1f} {int(event_id):4d}\n")

    # Prepare travel time data
    travel_time_list = []
    for station in sorted(p_data[event_id].keys()):
        ttp = p_data[event_id][station]
        tts = s_data.get(event_id, {}).get(station, 99.99)  # Default S to 99.99
        sp_value = 99.99 if tts == 99.99 else round(tts - ttp, 2)  # Calculate S-P

        station_name = station.rjust(4)
        if ttp != 99.99:
            travel_time_list.append(f"{station_name} P 0{ttp:6.2f}")
        if sp_value != 99.99:
            travel_time_list.append(f"{station_name} S 0{sp_value:6.2f}")  # S-P value

    for j in range(0, len(travel_time_list), 6):
        fidP.write("".join(travel_time_list[j:j+6]) + "\n")

    fidP.write("0\n")  # End of event marker

# Write both output files
with open(output_file_simulps, "w") as fidP:
    for event_id, header in event_info_dict.items():
        write_earthq_dat(fidP, event_id, header, p_data, s_data)


