from sluurp.job import SControlShowJobCommand


def test_slurm_scontrol_show_job_output():
    """make sure slurm output can be correctly interpret"""
    output = """
    JobId=4109679 JobName=my_script_for_slurm.sh
   UserId=payno(81067) GroupId=soft(3401) MCS_label=N/A
   Priority=400 Nice=0 Account=(null) QOS=normal
   JobState=RUNNING Reason=None Dependency=(null)
   Requeue=1 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0
   RunTime=00:00:03 TimeLimit=02:00:00 TimeMin=N/A
   SubmitTime=2022-08-17T16:44:10 EligibleTime=2022-08-17T16:44:10
   AccrueTime=2022-08-17T16:44:10
   StartTime=2022-08-17T16:44:41 EndTime=2022-08-17T18:44:41 Deadline=N/A
   SuspendTime=None SecsPreSuspend=0 LastSchedEval=2022-08-17T16:44:41 Scheduler=Backfill
   Partition=nice AllocNode:Sid=p9-04:4192388
   ReqNodeList=(null) ExcNodeList=(null)
   NodeList=hib3-3004
   BatchHost=hib3-3004
   NumNodes=1 NumCPUs=1 NumTasks=1 CPUs/Task=1 ReqB:S:C:T=0:0:*:*
   TRES=cpu=1,mem=4000M,node=1,billing=1
   Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*
   MinCPUsNode=1 MinMemoryCPU=4000M MinTmpDiskNode=0
   Features=(null) DelayBoot=00:00:00
   OverSubscribe=OK Contiguous=0 Licenses=(null) Network=(null)
   Command=/tmp/pytest-of-payno/pytest-16/test_sbatchjob_script_submissi0/test_image_key_upgrader/my_script_for_slurm.sh
   WorkDir=/home/esrf/payno/tomwer
   StdErr=/home/esrf/payno/tomwer/slurm-4109679.out
   StdIn=/dev/null
   StdOut=/home/esrf/payno/tomwer/slurm-4109679.out
   Power=
    """
    res = SControlShowJobCommand.stdout_to_dict(output)
    assert isinstance(res, dict)
    assert res["StartTime"] == "2022-08-17T16:44:41"
    assert res["JobId"] == "4109679"
    assert res["StdOut"] == "/home/esrf/payno/tomwer/slurm-4109679.out"
    assert res["Power"] == ""
