import pytest
import logging
from sluurp.job import SBatchScriptJob, ScriptJob, submit_sbatch_job
import os
import platform as _platform_mod
from concurrent import futures
from sluurp.utils import (
    SubProcessCommand,
    has_sbatch_available,
    has_scontrol_available,
)


def run_async(job):
    job.run()
    return job.result


@pytest.mark.skipif(
    _platform_mod.system() != "Linux", reason="job script only works on linux platform"
)
def test_job_script(tmp_path):
    test_dir = tmp_path / "test_image_key_upgrader"
    script_path = test_dir / "my_script.sh"

    with pytest.raises(TypeError):
        SBatchScriptJob(script="echo test", script_path=script_path, clean_script=False)

    script_job = SBatchScriptJob(
        script=("echo test",), script_path=script_path, clean_script=False
    )
    script_job.dry_run = True
    assert not os.path.exists(script_path)
    script_job.run()
    assert os.path.exists(script_path)
    assert len(os.listdir(test_dir)) == 1


@pytest.mark.asyncio
@pytest.mark.skipif(
    _platform_mod.system() != "Linux", reason="job script only works on linux platform"
)
async def test_job_script_submission(tmp_path):
    test_dir = tmp_path / "test_image_key_upgrader"
    script_path = test_dir / "my_script.sh"

    sleep_time = 4
    assert isinstance(sleep_time, int)

    class MyBashScriptJob(ScriptJob):
        def run(self):
            script_path = self._save_script()
            if not os.path.exists(script_path):
                raise OSError(
                    f"{script_path} doesn't exists. Unable to write script file. Can be write rights error."
                )
            self._result = SubProcessCommand(command=f"bash {script_path}").run()
            if self.clean_script:
                self._do_script_cleaning()

    script_job = MyBashScriptJob(
        script=(f"sleep {sleep_time}s", "echo 'succeed'"),
        script_path=script_path,
        clean_script=False,
    )

    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_async, script_job)
        result = future.result(timeout=10)
        assert result == "succeed\n"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not (has_sbatch_available() and has_scontrol_available()),
    reason="slurm command not available",
)
@pytest.mark.skipif(
    _platform_mod.system() != "Linux", reason="job script only works on linux platform"
)
async def test_sbatchjob_script_submission(tmp_path):
    test_dir = tmp_path / "test_image_key_upgrader"
    script_path = test_dir / "my_script_for_slurm.sh"

    sleep_time = 20
    assert isinstance(sleep_time, int)
    script_job = SBatchScriptJob(
        script=(f"sleep {sleep_time}s", "echo 'succeed'"),
        script_path=script_path,
        clean_script=False,
    )

    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(submit_sbatch_job, script_job)
        future.result(timeout=10)


@pytest.mark.asyncio
@pytest.mark.skipif(
    not (has_sbatch_available() and has_scontrol_available()),
    reason="slurm command not available",
)
async def test_sbatchjob_script_submission_with_slurm_config(tmp_path):
    """
    test sbatch job submission in dry_mode
    """
    test_dir = tmp_path / "test_image_key_upgrader"
    script_path = test_dir / "my_script_for_slurm.sh"

    sleep_time = 20
    assert isinstance(sleep_time, int)
    script_job = SBatchScriptJob(
        script=(f"sleep {sleep_time}s", "echo 'succeed'"),
        script_path=script_path,
        clean_script=False,
        slurm_config={
            "memory": "15GB",
            "partition": "my_partition",
            "n_gpus": 2,
            "python_venv": "path/to/my/python/venv",
        },
    )
    script_job.dry_run = True

    with futures.ThreadPoolExecutor() as executor:
        future = executor.submit(submit_sbatch_job, script_job)
        future.result(timeout=10)

    lines = []
    with open(script_path, mode="r") as file_object:
        [lines.append(line) for line in file_object]

    assert lines == [
        "#!/bin/bash -l\n",
        "#SBATCH --mem=15GB\n",
        "#SBATCH -p my_partition\n",
        "#SBATCH --gres=gpu:2\n",
        "source path/to/my/python/venv\n",
        f"sleep {sleep_time}s\n",
        "echo 'succeed'\n",
    ]


def test_interpret_slurm_config(caplog):
    """
    insure interpretation done by 'interpret_slurm_config' works
    """
    caplog.set_level(logging.INFO)
    SBatchScriptJob.interpret_slurm_config({"new_key": "test"})
    assert "Unknow slurm configuration key: new_key" in caplog.text

    assert SBatchScriptJob.interpret_slurm_config(
        {"cpu-per-task": 2, "n_tasks": 1, "memory": None}
    ) == (
        (
            "#SBATCH --cpus-per-task=2",
            "#SBATCH --ntasks=1",
        ),
        (),
    )

    assert SBatchScriptJob.interpret_slurm_config(
        {
            "python_venv": "my_python",
            "walltime": None,
            "memory": "10",
            "job_name": "my_project",
        }
    ) == (
        (
            "#SBATCH --mem=10GB",
            "#SBATCH -J 'my_project'",
        ),
        ("source my_python",),
    )

    assert SBatchScriptJob.interpret_slurm_config(
        {"n_gpus": "3", "partition": "my_partition"}
    ) == (
        (
            "#SBATCH --gres=gpu:3",
            "#SBATCH -p my_partition",
        ),
        (),
    )

    assert SBatchScriptJob.interpret_slurm_config(
        {
            "walltime": None,
            "memory": "10",
            "modules": (
                "tomotools",
                "pycharm/11.7.1",
            ),
        },
        sbatch_extra_params={
            "gpu_card": "a40"
        },  # just to make sure this doesn't add gpu options of no gpu requested
    ) == (
        ("#SBATCH --mem=10GB",),
        ("module load tomotools", "module load pycharm/11.7.1"),
    )

    assert SBatchScriptJob.interpret_slurm_config(
        slurm_config={"n_gpus": "3", "partition": "my_partition"},
        sbatch_extra_params={"gpu_card": "a40"},
    ) == (
        (
            "#SBATCH --gres=gpu:3 -C a40",
            "#SBATCH -p my_partition",
        ),
        (),
    )


def test_strip_gpu_card_name():
    """test `strip_gpu_card_name` function"""
    assert SBatchScriptJob.strip_gpu_card_name("a40") == "a40"
    assert SBatchScriptJob.strip_gpu_card_name("nvidia_a40") == "a40"
    assert SBatchScriptJob.strip_gpu_card_name("tesla_56") == "56"
    assert SBatchScriptJob.strip_gpu_card_name("tesla_v100-pcie-32gb") == "v100"
