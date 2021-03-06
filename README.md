# Scripts for analyzing the activity in a K8s cluster

![The silver octo rotary phone](https://drive.google.com/uc?export=view&id=1ZNc0teUqKH0lHIP4J_JBeI712Q3nGVM0)

## Move it you lazy pod!
This script records CPU load time series from command `kubectl top pod`.

Example:
```
perl move-it-lazy-pods.perl 'fix-k8s-hpa-analyzer-worker' 1 > ~/Development/fix-k8s-hpa-analyzer-worker.cpu.load.22-01-25.log
```

## Procupods
Analyze the CPU time series of a group of pods. Needs an active virtual environment with dependencies in file `requirements.txt`.

Examples:
```
python procupods.py plot /path/to/data_file
python procupods.py start_times /path/to/data_file
```
