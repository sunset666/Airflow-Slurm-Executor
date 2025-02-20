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
    default_args={"executor_config": {"SlurmExecutor: {"attribute": "value"}},
                  "queue": "QUEUE"},
):
```

The **QUEUE** parameter defined as default argument will be translated as the partition to be used by slurm.