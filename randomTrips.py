# -*- coding: utf-8 -*-
import os, sys
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
from utils import SUMO_outputs_process, simulate, gen_sumo_cfg


def exec_randomTrips(folders, fname, ini_time, veh_number, repetitions):
    # SUMO Tool randomtrips
    sumo_tool = os.path.join(folders.SUMO_exec, '..', 'tools', 'randomTrips.py')
    net_file = os.path.join(folders.parents_dir, 'templates', 'osm.net.xml')
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


def trips_for_traffic(folders, end_hour, repetitions):
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


def update_vehicle_ID(folders):
    trips = os.listdir(folders.trips)
    veh_id = 0
    print('Update vehicle IDs......\n')
    for f in tqdm(trips): veh_id = change_veh_ID(f, veh_id, folders)
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


def rt(config, k, repetitions, gui):
    """
    Parameters
    ----------
    config : TYPE
        DESCRIPTION.
    k : TYPE
        DESCRIPTION.
    repetitions : TYPE
        DESCRIPTION.
    end_hour : TYPE
        DESCRIPTION.
    processors : TYPE
        DESCRIPTION.
    routing : TYPE
        DESCRIPTION.
    gui : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # trips per hour
    trips_for_traffic(config, config.simtime, repetitions)
    # via route Travessera
    # custom_routes(config)


    # update bundle of trips
    update_vehicle_ID(config)

    # read trips
    read_trips = os.listdir(config.trips)
    trips = ','.join([f'{os.path.join(config.trips, elem)}' for elem in read_trips])


    # generate sumo cfg file
    gen_sumo_cfg(config.tool, trips, k, config, config.reroute_probability)
    # execute simulations

    simulate(config, config.processors, gui)
    """
    # detectors
    # singlexml2csv('detector.xml')

    # process sumo outputs
    SUMO_outputs_process(config)
    """
