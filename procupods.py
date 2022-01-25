import re
from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd

data_file_path = Path('/home/flaudarin/Development/fix-k8s-hpa-analyzer-worker.cpu.load.log')
deployment_name = 'fix-k8s-hpa-analyzer-worker'
replica_number = 10


@click.group()
def cli():
    """
    Examples:

        python procupods.py list_pods\n
        python procupods.py plot --pod-indices '0,3,4'
    """
    pass


def load_data() -> pd.DataFrame:
    # Loads data from CSV file
    data: pd.DataFrame = pd.read_csv(data_file_path, sep=';')

    # Sets column names
    data.columns = ['name', 'time', 'load']

    # Converts column name to category
    data['name'] = data['name'].astype('category')

    return data


def sec_to_min(seconds: int):
    minutes = seconds // 60
    rem_seconds = seconds % 60

    return f"{minutes}' {rem_seconds}\""


@click.command(name='plot')
@click.option('--pod-indices', "pod_indices", type=click.STRING, help="List of indices, e.g.: 2,3,6")
def plot(pod_indices: str):
    """
    Plot CPU load time history

    :param pod_indices: string with comma-separated indices
    """
    data = load_data()

    time_series = {}

    # List of pod names
    pod_names = data['name'].cat.categories

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

    plt.figure()
    for name in pod_names:
        time_series[name].plot(label=name)

    plt.legend(loc='lower right')

    plt.grid(True)
    plt.show()
    plt.close()
    # data.plot()
    # plt.legend(loc='best')


@click.command(name='list_pods')
def list_pods():
    data = load_data()

    # List of pod names
    pod_names = data['name'].cat.categories
    print(f"File '{data_file_path}' contains data on pods:")
    for name in pod_names:
        print(f"  * {name}")


@click.command(name='start_times')
def start_times():
    data = load_data()

    # Sorts data by ascending time
    data.sort_index(axis=0, ascending=True, inplace=True, kind='quicksort', na_position='last')

    # List of pod names
    pod_names = sorted(data['name'].cat.categories)

    print("Times when pods were created:")

    for name in pod_names:
        # noinspection PyTypeChecker
        pod_mask: pd.Series = data['name'] == name
        start_time_value = pod_mask[pod_mask].index[0]

        print(f"  * {name}: {sec_to_min(start_time_value)}")


cli.add_command(plot)
cli.add_command(list_pods)
cli.add_command(start_times)

if __name__ == '__main__':
    cli()