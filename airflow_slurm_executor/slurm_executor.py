from airflow.plugins_manager import AirflowPlugin
from airflow.executors.base_executor import BaseExecutor
from airflow.utils.state import State
from airflow_slurm_executor.slurm_control import get_jobs_status, run_job
import logging
import uuid
import sys


logger = logging.getLogger(__name__)


def reindex_job_status_by_job_name(job_list):
    return {job_status.job_name: job_status for job_status in job_list.values()}


class SlurmExecutor(BaseExecutor):
    def __init__(self):
        super().__init__()
        self.commands_to_check = {}
        self.tasks_to_run = []
        self.running_tasks = []

    def start(self):
        logging.info('Starting Slurm executor')

    def execute_async(self, key, command, queue=None, executor_config=None):
        logging.info("execute async called")
        unique_id = str(key[0]) + str(uuid.uuid1())
        queue = queue if queue != 'default' else None
        logging.debug('submitting job %s on queue %s', key, queue)
        run_job(cmd=command, queue=queue, task_name=unique_id, executor_config=executor_config)
        self.commands_to_check[unique_id] = key

    def check_state(self):
        ids = list(self.commands_to_check.keys())
        statuses = reindex_job_status_by_job_name(get_jobs_status(job_name=ids))
        logger.debug('statuses found are %s', statuses)
        logger.debug('commands to check are %s', self.commands_to_check)

        completed_jobs = []
        for unique_id, key in self.commands_to_check.items():
            status = statuses[unique_id]
            if status.status_code == 'CD':
                self.change_state(key, State.SUCCESS)
                completed_jobs.append(unique_id)
            elif status.status_code == 'F':
                self.change_state(key, State.FAILED)
                completed_jobs.append(unique_id)
            elif status.status_code in ('CG', 'R'):
                self.change_state(key, State.RUNNING)
            elif status.status_code == 'PD':
                self.change_state(key, State.SCHEDULED)

        for unique_id in completed_jobs:
            if unique_id in self.commands_to_check:
                self.commands_to_check.pop(unique_id)
            else:
                logger.error('id %s missing in %s', unique_id, self.commands_to_check)

    def trigger_tasks(self, open_slots):
        self.check_state()
        super().trigger_tasks(open_slots)

    def sync(self):
        pass

    def end(self):
        self.heartbeat()


# Defining the plugin class
class SlurmExecutorPlugin(AirflowPlugin):
    name = "slurm"
    executors = [SlurmExecutor]


if __name__ == '__main__':
    print('output', get_jobs_status())
    print('output', get_jobs_status(sys.argv[1:]))
