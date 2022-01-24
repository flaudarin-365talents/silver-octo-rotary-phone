import re
from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd

data_file_path = Path('/home/flaudarin/Development/fix-k8s-hpa-analyzer-worker.cpu.load.log')
deployment_name = 'fix-k8s-hpa-analyzer-worker'
replica_number = 10


@click.command()
@click.option("--no-fig/--fig", "no_figure", default=False, help="Do no plot time series")
@click.option("--list/--no-list", "list_pod_names", default=False, help="Do no plot time series")
@click.option('--pod-indices', "pod_indices", type=click.STRING, help="List of indices, e.g.: 2,3,6")
# @click.argument("redis_export_port", type=click.INT)
# @click.argument("redis_import_port", type=click.INT)
# @click.option("--client", "-c", "clients", type=click.STRING, multiple=True, help="Migrate feedbacks for a specific client")
# @click.option("--redis_import_password", type=click.STRING, required=False, help="Password for connecting to the importing Redis server")
def main(no_figure: bool, list_pod_names: bool, pod_indices: str):
    # Loads data from CSV file
    data: pd.DataFrame = pd.read_csv(data_file_path, sep=';')

    # Sets column names
    data.columns = ['name', 'time', 'load']

    # Converts column name to category
    data['name'] = data['name'].astype('category')

    time_series = {}

    # List of pod names
    pod_names = data['name'].cat.categories

    if list_pod_names:
        print(f"File '{data_file_path}' contains data on pods:")
        for name in time_series.keys():
            print(f"  * {name}")

    if pod_indices:
        indices = {int(item) for item in pod_indices.split(',')}

        def index_in_selection(value: str):
            match = re.search(r'(\d+)$', value)
            if match:
                index = int(match.group(1))
                if index in indices:
                    return True
            return False

        pod_names = [name for name in pod_names if index_in_selection(name)]

    for name in pod_names:
        filter_mask = data['name'] == name
        # time_series[pod_name] = data[filter_mask].drop(columns=['name'])
        df = data[filter_mask]
        time_series[name] = df['load']

        # Converts time to minutes
        time_series[name].index = df['time'] / 60

    if not no_figure:
        plt.figure()
        for name in pod_names:
            time_series[name].plot(label=name)

        plt.legend(loc='lower right')

        plt.grid(True)
        plt.show()
        plt.close()
        # data.plot()
        # plt.legend(loc='best')


if __name__ == '__main__':
    main()
