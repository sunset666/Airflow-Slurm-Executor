[![PyPI](https://img.shields.io/pypi/v/airflow-slurm-executor)](https://pypi.org/project/airflow-slurm-executor/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/airflow-slurm-executor)](https://pypi.org/project/airflow-slurm-executor/)

# Slurm Executor

The Slurm executor is based on work done by Hanno Holties in https://git.astron.nl/eosc/slurmexecutorplugin, this one 
extends the use of parameters to be passed to the Slurm cluster so one can control the partition, the account, and other
details about the jobs submission.

It was changed from **srun** to **sbatch** as a default command to interact with the cluster, so multiple jobs can be 
submitted at a time.


To use the plugin after installing the package change
the AIRFLOW configuration file as such:
```
# The executor class that airflow should use. Choices include
# SequentialExecutor, LocalExecutor, CeleryExecutor, DaskExecutor, KubernetesExecutor
executor = airflow_slurm_executor.SlurmExecutor
```

## Custom Use

One can pass the **executor_config** parameter in the default_args attribute to any DAG to customize some aspects of the
job.
```
with DAG(
    dag_id="my_dag",
    start_date=pendulum.datetime(2016, 1, 1),
    schedule="@daily",
    default_args={"executor_config": {"SlurmExecutor: {"attribute": "value"}}},
):
```
The attributes implemented so far are:

* **cpu_nodes**: Gives one control on which nodes to run this DAG, used as **nodelist** in slurm.
* **gpu_config**: Gives one control on which gpu parameters can be used. The current supported schema is: 
```{'gres': GPU_REQUIRED, 'queue': SPECIAL_GPU_PARTITION}``` If the queue/partition where the DAG task will be 
executed matches the parameter sent here, **cpu_nodes** will be ignored in favor of the **gres** node selecton.
* **output_path**: Gives one control over where the slurm output log will be generated, remember the slurm nodes should
have access to this location.
* **account**: Gives one control over which account the jobs are going to be linked to.