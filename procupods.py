from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

data_file_path = Path('/home/flaudarin/Development/fix-k8s-hpa-analyzer-worker.cpu.load.log')
deployment_name = 'fix-k8s-hpa-analyzer-worker'
replica_number = 10

if __name__ == '__main__':
    data: pd.DataFrame = pd.read_csv(data_file_path, sep=';')
    data.columns = ['name', 'time', 'load']
    data['name'] = data['name'].astype('category')

    time_series = {}

    pod_names = data['name'].cat.categories

    for name in pod_names:
        filter_mask = data['name'] == name
        # time_series[pod_name] = data[filter_mask].drop(columns=['name'])
        df = data[filter_mask]
        time_series[name] = df['load']
        time_series[name].index = df['time'] / 60

    print(time_series.keys())
    plt.figure()
    for name in pod_names:
        time_series[name].plot(label=name)

    plt.legend(loc='lower right')

    plt.grid(True)
    plt.show()
    # data.plot()
    # plt.legend(loc='best')