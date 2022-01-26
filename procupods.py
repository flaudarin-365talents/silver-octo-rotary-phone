import re

import click
import matplotlib.pyplot as plt
import pandas as pd

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


def load_data(data_file_path) -> pd.DataFrame:
    # Loads data from CSV file
    data: pd.DataFrame = pd.read_csv(data_file_path, sep=';')

    # Sets column names
    data.columns = ['name', 'time', 'load']

    # Converts column name to category
    data['name'] = data['name'].astype('category')

    return data


def sec_to_min(seconds: int):
    r"""
    >>> sec_to_min(88)
    '1\' 28"'
    >>> sec_to_min(-88)
    '-1\' 28"'

    :param seconds:
    :return:
    """
    if seconds >= 0:
        minutes = seconds // 60
        rem_seconds = seconds % 60
        minus = False
    else:
        minutes = -seconds // 60
        rem_seconds = -seconds % 60
        minus = True

    return f"{'-' if minus else ''}{minutes}' {rem_seconds}\""


@click.command(name='plot')
@click.argument("data_file_path", type=click.STRING)
@click.option('--pod-indices', "pod_indices", type=click.STRING, help="List of indices, e.g.: 2,3,6")
def plot(data_file_path: str, pod_indices: str):
    """
    Plot CPU load time history

    :param data_file_path: path to the data file
    :param pod_indices: string with comma-separated indices
    """
    data = load_data(data_file_path)

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

    plt.ylabel("Load (milli CPU)")

    plt.legend(loc='lower right')

    plt.grid(True)
    plt.show()
    plt.close()
    # data.plot()
    # plt.legend(loc='best')


@click.command(name='list_pods')
@click.argument("data_file_path", type=click.STRING)
def list_pods(data_file_path: str):
    data = load_data(data_file_path)

    # List of pod names
    pod_names = data['name'].cat.categories
    print(f"File '{data_file_path}' contains data on pods:")
    for name in pod_names:
        print(f"  * {name}")


@click.command(name='start_times')
@click.argument("data_file_path", type=click.STRING)
@click.option('--offset', "offset", type=click.INT, default=0, help="Apply an offset to start times")
def start_times(data_file_path: str, offset: int):
    data = load_data(data_file_path)

    # Sorts data by ascending time
    data.sort_index(axis=0, ascending=True, inplace=True, kind='quicksort', na_position='last')

    # List of pod names
    pod_names = sorted(data['name'].cat.categories)

    print("Times when pods were created:")

    for name in pod_names:
        # noinspection PyTypeChecker
        pod_mask: pd.Series = data['name'] == name
        start_time_value = pod_mask[pod_mask].index[0] + offset

        print(f"  * {name}: {sec_to_min(start_time_value)}")


cli.add_command(plot)
cli.add_command(list_pods)
cli.add_command(start_times)

if __name__ == '__main__':
    cli()
