from typing import List, Tuple, Union, Dict
from subprocess import run as __run_process
import logging

from dataclasses import dataclass


__SQUEUE_PATH = "squeue"
__SBATCH_PATH = "sbatch"


logger = logging.getLogger(__name__)


@dataclass
class SlurmJobStatus:
    job_id: str
    job_name: str
    status_code: str
    status: str
    reason: str


def __execute_on_shell(cmd, args):
    logger.info(f"Status {cmd}, {args}")
    process_status = __run_process([cmd] + args, capture_output=True)
    if process_status.returncode > 0:
        logger.info(f"Status {process_status}")
        raise SlurmCallError()
    output = process_status.stdout.decode()
    return output


class EmptyListException(Exception):
    pass


class SlurmCallError(Exception):
    pass


def __list_contains_valid_ids(ids_list):
    if ids_list:
        for item in ids_list:
            if not isinstance(item, int) and not item.is_digit():
                return False
        return True
    else:
        raise EmptyListException()


def __compose_get_processes_status_cmd(
    job_ids: Union[List, Tuple] = (), job_name: Union[List, Tuple] = ()
):
    cmd = ["--states=all", "-h"]
    fmt = "%i;%j;%t;%T;%r"
    cmd += ["--format=%s" % fmt]

    if job_ids:
        cmd += [",".join(job_ids)]
    else:
        cmd += ["-a"]

    if job_name:
        cmd += ["-n", ",".join(job_name)]

    return cmd


def __execute_squeue(args):
    return __execute_on_shell(__SQUEUE_PATH, args)


def __parse_squeue_output(squeue_output) -> List[SlurmJobStatus]:
    """
    Parses the output of squeue
    e.g.
    123;test_job;CD;COMPLETED;None
    :param squeue_output:
    :return:
    """
    jobs_found = []
    if squeue_output:
        for line in squeue_output.split("\n"):
            if not line:
                continue
            job_id, job_name, status_code, status, reason = line.split(";")
            jobs_found.append(
                SlurmJobStatus(
                    job_id=job_id,
                    job_name=job_name,
                    status_code=status_code,
                    status=status,
                    reason=reason,
                )
            )

    return jobs_found


def __map_job_status_per_jobid(
    job_status_list: List[SlurmJobStatus],
) -> Dict[str, SlurmJobStatus]:
    return {job_status.job_id: job_status for job_status in job_status_list}


def get_jobs_status(
    job_ids: Union[List, Tuple] = (), job_name: Union[List, Tuple] = ()
) -> Dict[str, SlurmJobStatus]:
    args = __compose_get_processes_status_cmd(job_ids, job_name)
    output = __execute_squeue(args)
    parsed_output = __parse_squeue_output(output)
    return __map_job_status_per_jobid(parsed_output)


def __execute_srun(args):
    return __execute_on_shell(__SBATCH_PATH, args)


def __compose_run_job_arguments(cmd, queue=None, executor_config=None, job_name=None):
    gpu_config = None
    output_path = None
    cpu_node = None
    account = None
    if executor_config:
        try:
            gpu_config = executor_config.get("SlurmExecutor").get("gpu_config")
        except:
            pass
        try:
            output_path = (
                executor_config.get("SlurmExecutor").get("slurm_output_path") + "slurm-%j.out"
            )
        except:
            pass
        try:
            cpu_node = executor_config.get("SlurmExecutor").get("cpu_nodes")
        except:
            pass
        try:
            account = executor_config.get("SlurmExecutor").get("account")
        except:
            pass

    args = []
    if queue:
        args += ["--partition", queue]
    if gpu_config:
        args += ["--gres", gpu_config]
    if cpu_node:
        args += ["--nodelist", cpu_node]
    if account:
        args += ["--account", account]
    if output_path:
        args += ["--output", output_path]
    args += ["--job-name", job_name] if job_name else ["--job-name", cmd]
    args += cmd.split(" ") if isinstance(cmd, str) else cmd
    return args


# TODO collect output
def run_job(cmd, queue=None, executor_config=None, task_name=None):
    args = __compose_run_job_arguments(cmd, queue, executor_config, task_name)

    _ = __execute_srun(args)
