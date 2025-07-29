from __future__ import annotations

import subprocess
import platform as _platform_mod
from shutil import which


def has_sbatch_available(platform="Linux"):
    return which("sbatch") is not None


def has_scancel_available():
    return which("scancel") is not None


def has_scontrol_available():
    return which("scontrol") is not None


def get_partitions() -> tuple:
    """
    return a list of existing partition
    """
    # sinfo -O partition
    process = SubProcessCommand(command="sinfo -O partition")
    try:
        res = process.run()
    except Exception:
        pass
    else:
        return filter(
            lambda x: x not in ("", "PARTITION"),
            [
                str(line).replace(" ", "").rstrip("*") for line in res.split("\n")
            ],  # * symbol should be removed to get the list of partitions (* means it is the default partition)
        )


def get_partition_gpus(partition: str) -> tuple:
    """
    return the available gpus of a partition.
    Please keep in mind that the GRES synthax might evolve. So this function is
    not expected to always work.
    """
    process = SubProcessCommand(command=f"sinfo --partition={partition} -o '%G'")
    try:
        res = process.run()
    except Exception:
        res = ()

    gpus = filter(
        lambda x: x.startswith("gpu:"),
        res.split("\n"),
    )
    try:
        return tuple([gpu.split(":")[1] for gpu in gpus])
    except Exception:
        return tuple()


def get_partition_walltime(partition: str) -> dict[str, str]:
    """
    Return for the given partition:
    * time: walltime limit as HH:MM:SS
    * default_time: default walltime as HH:MM:SS
    """
    process = SubProcessCommand(
        command=f"sinfo --partition={partition} -O DefaultTime,Time"
    )
    try:
        res = process.run()
    except Exception:
        return None, None

    # treat output string
    res = res.split("\n")
    if len(res) < 1:
        return None, None
    else:
        times = filter(lambda a: a, res[1].split(" "))
        default_time, time = times
        return {
            "default_time": default_time,
            "time": time,
        }


def get_partition_nodes(partition: str) -> tuple:
    """
    For a given partition return the available nodes
    """
    process = SubProcessCommand(command=f"sinfo --partition={partition} --Node")
    try:
        res = process.run()
    except Exception:
        return None, None

    # treat output string
    res = res.split("\n")
    if len(res) < 1:
        return tuple()
    else:
        # pop first list (HEADER)
        res = res[1:]
        return tuple(
            filter(None, [line.split(" ")[0] for line in res])  # filter empty strings
        )


class SubProcessCommand:
    def __init__(self, command, platform="Linux"):
        if platform != _platform_mod.system():
            raise ValueError
        self._command = command
        self.raw_stdout = None
        self.raw_stderr = None

    def run(self):
        stdout, stderr = self.launch_command()
        self.raw_stdout = stdout.decode("utf-8")
        self.raw_stderr = stderr.decode("utf-8")
        return self.interpret_result(self.raw_stdout, self.raw_stderr)

    def interpret_result(self, stdout, stderr):
        return stdout

    def launch_command(self):
        process = subprocess.Popen(
            self._command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return process.communicate()

    __call__ = run
