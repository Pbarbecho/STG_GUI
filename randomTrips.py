# -*- coding: utf-8 -*-
import os, sys
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
from utils import SUMO_outputs_process, simulate, gen_sumo_cfg
import random

def exec_randomTrips(folders, fname, ini_time, veh_number, repetitions):
    # SUMO Tool randomtrips
    sumo_tool = os.path.join(folders.SUMO_exec, '..', 'tools', 'randomTrips.py')
    net_file = folders.network
    add_file = os.path.join(folders.parents_dir, 'templates', 'vtype.xml')

    # output directory
    output = os.path.join(folders.trips, f'{fname}.xml')

    vtype = "car"
    # iter_seed = seed + 1
    begin = ini_time
    end = begin + 15 * 60  # 15 minutes

    # vehicles arrival
    period = (end - begin) / veh_number
    # Execute random trips
    cmd = f"python {sumo_tool} -v \
    --weights-prefix='RT'\
    -n {net_file} \
    -a {add_file}  \
    --edge-permission passenger  \
    -b {begin} -e {end} -p {period} \
    --trip-attributes 'type=\"{vtype}\" departSpeed=\"0\"' \
    -s {repetitions}  \
    -o {output} \
    --validate"
    # exec each randomtrip file
    os.system(cmd)


# --validate \
# --edge-permission {vtype}  \


def custom_routes(folders):
    randomtrips = os.listdir(folders.random_dir)

    for trip in randomtrips:
        # file locations
        trip_loc = os.path.join(folders.random_dir, trip)

        # Open original file
        tree = ET.parse(trip_loc)
        root = tree.getroot()

        # Update via route in xml
        for i, child in enumerate(root):
            if i != 0:
                child.set('via', route_0)

        # Write xml
        cfg_name = os.path.join(folders.random_dir, trip)
        tree.write(cfg_name)


def trips_for_traffic(folders):
    # general configurations
    end_hour = folders.simtime
    repetitions = folders.repetitions
    # read real traffic file
    traffic_df = pd.read_csv(folders.realtraffic)
    # generate randomtrips file each 15 min
    col = list(traffic_df)
    col = col[1:-1]
    # cpu script
    # subprocess.Popen(['/root/cpu_mem_check.sh', f'{folders.cpu}'])

    print(f'\nGenerating {len(col) * end_hour} randomTrips ......')
    for hour in tqdm(range(end_hour)):  # hora
        for minute in col:  # minute
            vehicles = traffic_df[minute][hour]

            if folders.factor !=0:scaling_factor = folders.factor
            else: scaling_factor = 1
            vehicles = vehicles * scaling_factor

            name = f'{hour}_{minute}_randomTrips'
            # convert to sec
            ini_time = hour * 3600 + (int(minute)) * 60
            exec_randomTrips(folders, name, ini_time, vehicles, repetitions)

    # kill_cpu_pid()
    # verify generated trip files
    if len(os.listdir(folders.trips)) == len(col) * end_hour:
        print('OK')
    else:
        sys.exit(f'Missing randomTrips files in {folders.random_dir}')


def change_veh_ID(trip_file, veh_id_number, folders):
    # full path
    file = os.path.join(folders.trips, trip_file)
    # Open original file
    tree = ET.parse(file)
    root = tree.getroot()

    # Update via route in xml
    veh_id = veh_id_number
    for child in root:
        veh_id += 1
        child.set('id', str(veh_id))
    # Write xml
    tree.write(file)
    return veh_id

def count_vehicles(trip_file, folders):
    # full path
    file = os.path.join(folders.trips, trip_file)
    # Open original file
    tree = ET.parse(file)
    root = tree.getroot()
    counter = 0
    for child in root:
        counter += 1
    return counter

def erase_first_line_trips(trip_file, folders):
    # full path
    file = os.path.join(folders.trips, trip_file)
    # Open original file
    tree = ET.parse(file)
    root = tree.getroot()
    veh_id=0
    # Update via route in xml
    for child in root:
        veh_id += 1
        if child == 'vType':
            child.remove()
    # Write xml
    tree.write(file)
    return veh_id

def update_vehicle_ID(folders):
    trips = os.listdir(folders.trips)
    veh_id = 0
    print('Update vehicle IDs......\n')
    # erase first line vtype
    for f in tqdm(trips): veh_id = erase_first_line_trips(f, folders)
    # update veh id
    for f in tqdm(trips): veh_id = change_veh_ID(f, veh_id, folders)

    # count number of vehicles
    total_veh = 0
    for f in trips:
        total_veh += count_vehicles(f, folders)
    print('\nTotal number of vehicles: ',total_veh)

    # change vehicle type
    ev_penetration = float(folders.ev_penetration)
    number_of_evs = int(ev_penetration * total_veh)
    number_of_gas = total_veh - number_of_evs
    #number_of_trip_files = len(trips)
    #evs_per_trip_file = int(number_of_evs/number_of_trip_files)
    print('\nEVs number: ', number_of_evs)
    print('\nGAS number: ', number_of_gas)
    iter = True
    counter = 0
    counter_gas = 0
    counter_ev = 0

    for f in trips:
        file = os.path.join(folders.trips, f)
        tree = ET.parse(file)
        root = tree.getroot()

        for child in root:
            counter += 1
            if iter and number_of_gas > 0:
                child.set('type', 'gas')
                number_of_gas -= 1
                if counter_ev == number_of_evs:
                    iter = True
                else:
                    iter = False
                counter_gas+=1
            elif counter_ev < number_of_evs:
                child.set('type', 'ev')
                counter_ev += 1
                iter = True

        tree.write(file)
    print('generated evs:',counter_ev, 'generated gas:',counter_gas)
    print('Update vehicle IDs End......\n')

def singlexml2csv(f):
    # output directory
    output = os.path.join(folders.detector, f'{f.strip(".xml")}.csv')
    # SUMO tool xml into csv
    sumo_tool = os.path.join(tools, 'xml', 'xml2csv.py')
    # Run sumo tool with sumo output file as input

    print('\nConvert to csv detector ! \nExecute outside...........\n')
    cmd = 'python {} {} -s , -o {}'.format(sumo_tool, os.path.join(folders.detector, f), output)
    print(cmd)
    # os.system(cmd)


def rt(config, k):
    # GENERATE TRIPS  per hour
    trips_for_traffic(config)
    # via route Travessera
    # custom_routes(config)
    # update bundle of trips
    update_vehicle_ID(config) # change vehicle type
    # read trips
    read_trips = os.listdir(config.trips)
    trips = ','.join([f'{os.path.join(config.trips, elem)}' for elem in read_trips])
    # generate sumo cfg file
    gen_sumo_cfg(trips, k, config)
    # execute simulations

    #simulate(config, config.processors, gui) # add in utils
    """
    # detectors
    # singlexml2csv('detector.xml')

    # process sumo outputs
    SUMO_outputs_process(config)
    """

