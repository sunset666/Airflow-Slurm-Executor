from airflow.plugins_manager import AirflowPlugin
from slurm_executor import SlurmExecutor


class SlurmExecutorPlugin(AirflowPlugin):
    name = "slurm_executor_plugin"
    executors = [SlurmExecutor]
