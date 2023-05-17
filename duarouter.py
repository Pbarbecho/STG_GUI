import os, sys, glob
import xml.etree.ElementTree as ET
import random

from joblib import Parallel, delayed, parallel_backend
from utils import SUMO_outputs_process, simulate, gen_sumo_cfg, exec_od2trips, gen_od2trips, create_O_file, parallel_batch_size, gen_DUArouter, gen_MArouter

#route_0 = "24406397#1"

def clean_folder(folder):
    files = glob.glob(os.path.join(folder,'*'))
    [os.remove(f) for f in files]
    #print(f'Cleanned: {folder}')
    

def gen_routes(O, k, O_files, folders):
     """
     Generate configuration files for dua / ma router
     """
     routing = folders.tool

     # Generate od2trips cfg
     cfg_name, output_name = gen_od2trips(O,k,folders)

     # Execute od2trips
     output_name = exec_od2trips(cfg_name, output_name, folders)

     if routing == 'dua':
        # Generate DUArouter cfg

        cfg_name, output_name = gen_DUArouter(output_name, k, folders)
                          
     elif routing == 'ma':
        # Generate MArouter cfg
        cfg_name, output_name = gen_MArouter(O, k, O_files, folders)
  
     else:
        SystemExit('Routing name not found')

     folders.rou_dir = output_name
     # Generate sumo cfg
     gen_sumo_cfg(output_name, k, folders) # last element reroute probability

     return cfg_name, output_name



def gen_route_files(folders, k):
    """
    Generate O files given the real traffic in csv format. 
    Args:
    folder: (path class) .
    max_processors: (int) The max number of cpus to use. By default, all cpus are used.
    repetitios: number of repetitions
    end hour: The simulation time is the end time of the simulations 
    """
    repetitions = folders.repetitions
    end_hour = folders.simtime
    routing = folders.tool



    # without TAZ
# generate cfg files
    for h in [folders.O_district]:
        for sd in [folders.D_district]:
            print(f'\n Generating cfg files for TAZ  From:{h} -> To:{sd}')
            # build O file
            O_name = os.path.join(folders.O, f'{h}_{sd}')
            create_O_file(folders, O_name, h, sd, end_hour, folders.factor) # factor = 1

            # Generate cfg files
            for k in range(repetitions):
                # backup O files
                O_files = os.listdir(folders.O)
                # Gen DUArouter/MArouter
                print(O_files)
                cfg_name,output_name = gen_routes(O_name, k, O_files,folders)

    return cfg_name,output_name
"""
    # with TAZ
    # generate cfg files
    for h in [folders.O_district]:
        for sd in [folders.D_district]:
            print(f'\n Generating cfg files for TAZ  From:{h} -> To:{sd}')
            # build O file    
            O_name = os.path.join(folders.O, f'{h}_{sd}')
            create_O_file(folders, O_name, h, sd, end_hour, folders.factor) # factor = 1

            # Generate cfg files 
            for k in range(repetitions):
                # backup O files
                O_files = os.listdir(folders.O)
                # Gen DUArouter/MArouter
                print(O_files)
                gen_routes(O_name, k, O_files,folders)
"""

def exec_duarouter_cmd(fname):
    print('\Generating DUArouter.......')
    cmd = f'duarouter -c {fname}'
    os.system(cmd)    

def exec_marouter_cmd(fname):
    print('\Generating MArouter.......')
    cmd = f'marouter -c {fname}'
    os.system(cmd) 

def count_vehicles(trip_file):
    # full path
    file = trip_file
    # Open original file
    tree = ET.parse(file)
    root = tree.getroot()
    counter = 0
    for child in root:
        counter += 1
    return counter

def change_vtype(routes_file, folders):
    total_veh = count_vehicles(routes_file)
    ev_penetration = float(folders.ev_penetration)
    number_of_evs = int(ev_penetration * total_veh)
    number_of_gas = total_veh - number_of_evs
    print('\nEVs number: ', number_of_evs)
    print('\nGAS number: ', number_of_gas)

    counter_gas = 0
    counter_ev = 0

    #routes_file
    tree = ET.parse(routes_file)
    root = tree.getroot()

    for child in root:
        child.set('type', 'gas')

    while(counter_ev<=number_of_evs):
        random_num = random.randint(1, total_veh)
        print(f"{random_num}")
        for enum,child in enumerate(root):
            if (random_num == enum):
                counter_ev += 1
                child.set('type', 'ev')
                break
    tree.write(routes_file)
    print('generated evs:', counter_ev, 'generated gas:', counter_gas)

def exec_DUArouter(folders):
    cfg_files = os.listdir(folders.O)
    # Get dua.cfg files list
    dua_cfg_list = []
    [dua_cfg_list.append(cf) for cf in cfg_files if 'duarouter' in cf.split('_')]

    if dua_cfg_list:
        batch = parallel_batch_size(dua_cfg_list)
        # Generate dua routes
        print(f'\nGenerating duaroutes ({len(dua_cfg_list)} files) ...........\n')
        with parallel_backend("loky"):
            Parallel(n_jobs=folders.processors, verbose=0, batch_size=batch)(delayed(exec_duarouter_cmd)(
                     os.path.join(folders.O, cfg)) for cfg in dua_cfg_list)
    else:
       sys.exit('No dua.cfg files}')
    
 
def exec_MArouter(folders):
    cfg_files = os.listdir(folders.O)
  
    # Get ma.cfg files list
    ma_cfg_list = []
    [ma_cfg_list.append(cf) for cf in cfg_files if 'marouter' in cf.split('_')]
    
    if ma_cfg_list:
        batch = parallel_batch_size(ma_cfg_list)
        
        # Generate dua routes
        print(f'\nGenerating MAroutes ({len(ma_cfg_list)} files) ...........\n')
        with parallel_backend("loky"):
            Parallel(n_jobs=folders.processors, verbose=0, batch_size=batch)(delayed(exec_marouter_cmd)(
                     os.path.join(folders.O, cfg)) for cfg in ma_cfg_list)
    else:
       sys.exit('No ma.cfg files}')
                                   

def dua_ma(config, k):
    # Generate cfg files
    cfg_name, output_name = gen_route_files(config, k)

    if config.tool == 'dua':
        # Execute DUArouter 
        exec_DUArouter(config)
        change_vtype(output_name, config)
    elif config.tool == 'ma':
        # Execute MArouter 
        exec_MArouter(config)


    """
    simulate(config, processors, gui)
    # Outputs preprocess
    SUMO_outputs_process(config)
    """
 




