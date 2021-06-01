import pandas as pd
import os
import sumolib  # noqa


def statistics_route_file(file, metric):
    print("Reading '%s'..." % file)
    # vehicles  firts level in .rou.xml structure
    vehicles_rou_file = sumolib.output.parse_sax__asList(file, "vehicle", metric)
    print(vehicles_rou_file)
    return vehicles_rou_file



if __name__ == "__main__":
    # Read files
    sumo_files_location = '/root/Documents/SUMO_SEM/CATALUNYA/sim_files/'
    routes_file = os.path.join(sumo_files_location, 'dua.rou.xml')

    # Define measured attributes
    measure = ['id', 'fromTaz', 'toTaz']
    summary = statistics_route_file(routes_file, measure)

    # process summary
    results = pd.DataFrame(summary)
    results = results.groupby(['fromTaz', 'toTaz']).count()
    print(results)