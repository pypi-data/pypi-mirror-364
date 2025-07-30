import json
import uuid
from datetime import timedelta
from pstats import SortKey

import pytest
from dataclass_dict_convert.convert import TypeConvertorError
from imecilabt_utils.urn_util import UrnError

from tests.test_usage_statistics import TEST_GPU_OVERVIEW_OBJ, \
    TEST_GPU_OVERVIEW_JSON, TEST_GPULAB_USAGE_STATISTICS_JSON, TEST_GPULAB_USAGE_STATISTICS_OBJ

from imecilabt.gpulab.model.job2 import *

from dataclass_dict_convert import parse_rfc3339


def _parse_date(date: str) -> datetime.datetime:
    return parse_rfc3339(date)



def ignore_unknown_fields(field_name: str):
    print(f'ignoring unknown field for test: {field_name!r}')



TEST_JOB2_REQUEST_RESOURCES_JSON = """{
  "cpus": 4,
  "gpus": 2,
  "cpuMemoryGb": 8,

  "minCudaVersion": 10,
  "clusterId": 7,
  "gpuModel": ["1080", "v100"],
  "slaveName": "slave4B",
  "slaveInstanceId": "inst10",
  "features": ["SHARED_PROJECT_STORAGE", "FAST_SCRATCH_PROJECT_STORAGE", 
               "PUBLIC_IPV4", "PUBLIC_IPV6", "UNFIREWALLED_PORTS", "SSH_ACCESS"],
    "someOtherRequestResourceField": "foobar"
}"""
TEST_JOB2_REQUEST_SCHEDULING_JSON = """{
  "interactive": false,
  "minDuration": "5 hour",
  "restartable": false,
  "reservationId": "123456-789a-bcde-f012-34567890",

  "maxDuration": "5 hour",
  "maxSimultaneousJobs": {
    "bucketName": "my-3jobs-demo",
    "bucketMax": 3
  },
  "notBefore": "2020-03-17T05:00:13Z",
  "notAfter": "2020-03-17T18:00:13Z",
  "someOtherRequestSchedulingField": "foobar"
}"""
TEST_JOB2_REQUEST_DOCKER_JSON = """{
    "image": "gitlab.ilabt.imec.be:4567/ilabt/gpu-docker-stacks/tensorflow-notebook:83755206e3198b4914852bd640c102cb757fc02e",
    "command": [ "/project/start-demo.sh", "demo" ],
    "environment": {
      "MYDEMOENVVAR": "demo"
    },
    "storage": [
      {
        "containerPath": "/proj",
        "hostPath": "/project",
        "sizeGb": 5
      },
      {
        "hostPath": "/project_scratch",
        "someOther": "foobar"
      },
      {
        "containerPath": "/project_scratch2"
      },
      {
        "containerPath": "/foobar",
        "hostPath": "tmpfs",
        "sizeGb": 5
      }
    ],
    "portMappings": [
      {
        "containerPort": 8888,
        "hostPort": 80
      }
    ],

    "projectGidVariableName": "NB_GID",
    "user": "root",
    "groupAdd": ["demogroup"],
    "workingDir": "/root/",
    "someOtherRequestDockerOption": ["a", 2]
}"""
TEST_JOB2_REQUEST_EXTRA_JSON = """{
   "sshPubKeys": ["ssh-rsa test1"],
   "emailOnEnd": ["end@example.com"],
   "emailOnQueue": ["queue1@example.com", "queue2@example.com"],
   "emailOnRun": ["run@example.com"],
   "emailOnHalt": ["halted@example.com"],
   "emailOnRestart": ["restart@example.com"],
   "someOtherEmailReason": ["other@example.com"]
}"""

TEST_JOB2_REQUEST_JSON = """{
    "resources": """+TEST_JOB2_REQUEST_RESOURCES_JSON+""",
    "scheduling": """+TEST_JOB2_REQUEST_SCHEDULING_JSON+""",
    "docker": """+TEST_JOB2_REQUEST_DOCKER_JSON+""",
    "extra": """+TEST_JOB2_REQUEST_EXTRA_JSON+""",
    "someOtherRequestField": "foobar"
}"""

TEST_JOB2_REQUEST_RESOURCES_OBJ_A = JobRequestResources(
    cpus=4,
    gpus=2,
    cpu_memory_gb=8,
    gpu_memory_gb=None,
    min_cuda_version=10,
    cluster_id=7,
    gpu_model=["1080", "v100"],
    slave_name="slave4B",
    slave_instance_id="inst10",
    features=["SHARED_PROJECT_STORAGE", "FAST_SCRATCH_PROJECT_STORAGE",
              "PUBLIC_IPV4", "PUBLIC_IPV6", "UNFIREWALLED_PORTS", "SSH_ACCESS"],
)
TEST_JOB2_REQUEST_RESOURCES_OBJ_B = JobRequestResources(
    cpus=1,
    gpus=0,
    cpu_memory_gb=4,
    gpu_memory_gb=4,
)

TEST_JOB2_REQUEST_SCHEDULING_OBJ_A = JobRequestScheduling(
    interactive=False,
    min_duration="5 hour",
    restartable=False,
    reservation_ids=["123456-789a-bcde-f012-34567890"],
    max_duration="5 hour",
    max_simultaneous_jobs=MaxSimultaneousJobs(bucket_max=3, bucket_name="my-3jobs-demo"),
    not_before=_parse_date("2020-03-17T05:00:13Z"),
    not_after=_parse_date("2020-03-17T18:00:13Z"),
)

TEST_JOB2_REQUEST_DOCKER_OBJ_A = JobRequestDocker(
    image="gitlab.ilabt.imec.be:4567/ilabt/gpu-docker-stacks/tensorflow-notebook:83755206e3198b4914852bd640c102cb757fc02e",
    command=["/project/start-demo.sh", "demo"],
    environment={"MYDEMOENVVAR": "demo"},
    project_gid_variable_name="NB_GID",
    user="root",
    group_add=["demogroup"],
    working_dir="/root/",
    storage=[
        JobStorage(container_path="/proj", host_path="/project", size_gb=5),
        JobStorage(container_path="/project_scratch", host_path="/project_scratch", size_gb=None),
        JobStorage(container_path="/project_scratch2", host_path="/project_scratch2", size_gb=None),
        JobStorage(container_path="/foobar", host_path="tmpfs", size_gb=5),
    ],
    port_mappings=[
        JobPortMapping(container_port=8888, host_port=80)
    ],
)
TEST_JOB2_REQUEST_DOCKER_OBJ_B = JobRequestDocker(
    image="debian:stable"
)

TEST_JOB2_REQUEST_EXTRA_OBJ_A = JobRequestExtra(
    ssh_pub_keys=['ssh-rsa test1'],
    email_on_end=['end@example.com'],
    email_on_queue=['queue1@example.com', 'queue2@example.com'],
    email_on_run=['run@example.com'],
    email_on_halt=['halted@example.com'],
    email_on_restart=['restart@example.com'],
)

TEST_JOB2_REQUEST_OBJ_A = JobRequest(
    resources=TEST_JOB2_REQUEST_RESOURCES_OBJ_A,
    scheduling=TEST_JOB2_REQUEST_SCHEDULING_OBJ_A,
    docker=TEST_JOB2_REQUEST_DOCKER_OBJ_A,
    extra=TEST_JOB2_REQUEST_EXTRA_OBJ_A,
)
TEST_JOB2_REQUEST_OBJ_B = JobRequest(
    resources=TEST_JOB2_REQUEST_RESOURCES_OBJ_B,
    docker=TEST_JOB2_REQUEST_DOCKER_OBJ_B,
)


def test_job2_request_from_json():
    out_job2_request: JobRequest = JobRequest.from_json(TEST_JOB2_REQUEST_JSON,
                                                        on_unknown_field_override=ignore_unknown_fields)
    assert out_job2_request == TEST_JOB2_REQUEST_OBJ_A


def test_job2_request_from_dict():
    out_job2_request: JobRequest = JobRequest.from_dict(json.loads(TEST_JOB2_REQUEST_JSON),
                                                        on_unknown_field_override=ignore_unknown_fields)
    assert out_job2_request == TEST_JOB2_REQUEST_OBJ_A


def test_job2_request_docker_from_json1():
    in_json = """{
            "image": "dummy",
            "command": "test direct string",
            "groupAdd": "demogroup",
            "someOtherReqDockerField": "foobar"
        }
    """
    out_job2_request_docker: JobRequestDocker = \
        JobRequestDocker.from_json(in_json, on_unknown_field_override=ignore_unknown_fields)

    assert out_job2_request_docker == JobRequestDocker(
        image="dummy",
        command="test direct string",
        environment={},
        project_gid_variable_name=None,
        user=None,
        group_add=["demogroup"],
        working_dir=None,
        storage=[],
        port_mappings=[],
    )


def test_job2_request_docker_from_json2():
    in_json = """{
            "image": "dummy",
            "someOther": "foobar",
            "storage": [
              "/project_scratch",
              {
                "containerPath": "/proj",
                "hostPath": "/project",
                "sizeGb": 5
              },
              "/project_scratch2",
              {
                "containerPath": "/baz",
                "hostPath": "tmpfs",
                "sizeGb": 4,
                "someOtherStorageField": "foobar"
              }
            ],
            "portMappings": [
              77,
              {
                "containerPort": 8888,
                "hostPort": 80,
                "someOtherStorageField": "foobar"
              }
            ]
        }
    """
    out_job2_request_docker: JobRequestDocker = \
        JobRequestDocker.from_json(in_json, on_unknown_field_override=ignore_unknown_fields)

    assert out_job2_request_docker == JobRequestDocker(
        image="dummy",
        command=[],
        environment={},
        project_gid_variable_name=None,
        user=None,
        group_add=[],
        working_dir=None,
        storage=[
            JobStorage(container_path="/project_scratch", host_path="/project_scratch", size_gb=None),
            JobStorage(container_path="/proj", host_path="/project", size_gb=5),
            JobStorage(container_path="/project_scratch2", host_path="/project_scratch2", size_gb=None),
            JobStorage(container_path="/baz", host_path="tmpfs", size_gb=4),
        ],
        port_mappings=[
            JobPortMapping(container_port=77, host_port=None),
            JobPortMapping(container_port=8888, host_port=80),
        ],
    )


TEST_JOB2_STATE_RESOURCES_JSON="""{
   "clusterId": 7,
   "cpuIds": [4, 5],
   "gpuIds": [1],
   "cpuMemoryGb": 8,
   "gpuMemoryGb": 4,
 
   "slaveHost": "hostname.example.com",
   "slaveName": "hostname",
   "slaveInstanceId": "inst8",
   "slaveInstancePid": 5097,
   "workerId": 11,
 
   "sshHost": "host.example.com",
   "sshPort": 22,
   "sshUsername": "ABCDEF",
   "sshProxyHost": "bastion.example.com",
   "sshProxyPort": 2222,
   "sshProxyUsername": "fffdemo",
   
    "someOtherStateResourcesField": "foobar",
 
   "gpuDetails": """+TEST_GPU_OVERVIEW_JSON+""",
   "portMappings": [
     {
       "containerPort": 8888,
       "hostIp": "0.0.0.0",
       "hostPort": 32935,
        "someOtherPortMappingField": "foobar"
     }
   ]
 }"""

TEST_JOB2_STATE_EVENTTIMES_JSON="""{
   "created": "2020-03-17T09:59:19Z",
   "statusUpdated": "2020-03-17T10:00:13Z",

   "QUEUED": "2020-03-17T09:59:20Z",
   "ASSIGNED": "2020-03-17T08:59:24Z",
   "STARTING": "2020-03-17T09:59:21Z",
   "RUNNING": "2020-03-17T09:59:22Z",
   "FINISHED": "2020-03-17T09:59:23Z",
   "FAILED": "2020-03-17T09:59:24Z",
   "CANCELLED": "2020-03-17T09:59:25Z",
   "DELETED": "2020-03-17T09:59:26Z",
   "longRunNotify": "2020-03-18T09:59:21Z",
    "someOtherStateEventTimeField": "foobar",
    "MUSTHALT": "2020-03-17T09:59:27Z",
    "HALTING": "2020-03-17T09:59:28Z",
    "HALTED": "2020-03-17T09:59:29Z"
 }"""

TEST_JOB2_STATE_SCHEDULING_JSON="""{
   "assignedClusterId": 7,
   "assignedInstanceId": "inst8",
   "assignedSlaveName": "dgx2-idlab",
   "queuedExplanations": [],
   "withinMaxSimultaneousJobs": true,
   "tallyIncrement": 123.4,
    "someOtherStateSchedulingField": "foobar"
}"""

TEST_JOB2_STATE_JSON = """{
     "status": "RUNNING",
     "resources": """+TEST_JOB2_STATE_RESOURCES_JSON+""",
     "eventTimes": """+TEST_JOB2_STATE_EVENTTIMES_JSON+""",
     "scheduling": """+TEST_JOB2_STATE_SCHEDULING_JSON+""",
     "finalUsageStatistics": """+TEST_GPULAB_USAGE_STATISTICS_JSON+""",
    "someOtherStateField": "foobar"
}"""

TEST_JOB2_STATE_RESOURCES_OBJ_A = JobStateResources(
    cluster_id=7,
    cpu_ids=[4, 5],
    gpu_ids=[1],
    cpu_memory_gb=8,
    gpu_memory_gb=4,
    slave_host="hostname.example.com",
    slave_name="hostname",
    slave_instance_id="inst8",
    slave_instance_pid=5097,
    worker_id=11,
    ssh_host="host.example.com",
    ssh_port=22,
    ssh_username="ABCDEF",
    ssh_proxy_host="bastion.example.com",
    ssh_proxy_port=2222,
    ssh_proxy_username="fffdemo",
    port_mappings=[
        JobPortMapping(container_port=8888, host_ip="0.0.0.0", host_port=32935)
    ],
    gpu_details=TEST_GPU_OVERVIEW_OBJ,
    tmpfs_mem_gb=0,
)

TEST_JOB2_STATE_SCHEDULING_OBJ_A = JobStateScheduling(
    assigned_cluster_id=7,
    assigned_instance_id="inst8",
    assigned_slave_name="dgx2-idlab",
    queued_explanations=[],
    within_max_simultaneous_jobs=True,
    tally_increment=123.4,
)
TEST_JOB2_STATE_SCHEDULING_OBJ_B = JobStateScheduling(
    queued_explanations=["Not enough free resources too run this Job"]
)

TEST_JOB2_STATE_EVENTTIMES_OBJ_A = JobEventTimes(
    created=_parse_date("2020-03-17T09:59:19Z"),
    status_updated=_parse_date("2020-03-17T10:00:13Z"),
    QUEUED=_parse_date("2020-03-17T09:59:20Z"),
    ASSIGNED=_parse_date("2020-03-17T08:59:24Z"),
    STARTING=_parse_date("2020-03-17T09:59:21Z"),
    RUNNING=_parse_date("2020-03-17T09:59:22Z"),
    FINISHED=_parse_date("2020-03-17T09:59:23Z"),
    FAILED=_parse_date("2020-03-17T09:59:24Z"),
    CANCELLED=_parse_date("2020-03-17T09:59:25Z"),
    DELETED=_parse_date("2020-03-17T09:59:26Z"),
    MUSTHALT=_parse_date("2020-03-17T09:59:27Z"),
    HALTING=_parse_date("2020-03-17T09:59:28Z"),
    HALTED=_parse_date("2020-03-17T09:59:29Z"),
    long_run_notify=_parse_date("2020-03-18T09:59:21Z")
)
TEST_JOB2_STATE_EVENTTIMES_OBJ_B = JobEventTimes(
    created=_parse_date("2020-04-15T09:59:19Z"),
    status_updated=_parse_date("2020-04-15T12:34:56Z"),
    QUEUED=_parse_date("2020-04-15T09:59:20Z"),
)
TEST_JOB2_STATE_OBJ_A = JobState(
    status=JobStatus.RUNNING,
    resources=TEST_JOB2_STATE_RESOURCES_OBJ_A,
    scheduling=TEST_JOB2_STATE_SCHEDULING_OBJ_A,
    event_times=TEST_JOB2_STATE_EVENTTIMES_OBJ_A,
    final_usage_statistics=TEST_GPULAB_USAGE_STATISTICS_OBJ,
)

TEST_JOB2_STATE_OBJ_B = JobState(
    status=JobStatus.QUEUED,
    resources=None,
    scheduling=TEST_JOB2_STATE_SCHEDULING_OBJ_B,
    event_times=TEST_JOB2_STATE_EVENTTIMES_OBJ_B,
    final_usage_statistics=None,
)


def test_job2_state_from_json():
    out_job2_state: JobState = JobState.from_json(TEST_JOB2_STATE_JSON, on_unknown_field_override=ignore_unknown_fields)
    assert out_job2_state == TEST_JOB2_STATE_OBJ_A


TEST_JOB2_OWNER_JSON = """{
    "userUrn": "urn:publicid:IDN+example.com+user+tester",
    "userEmail": "tester@example.com",
    "projectUrn": "urn:publicid:IDN+example.com+project+testproj",
    "someOtherOwnerField": "foobar"
}"""

TEST_JOB2_OWNER_OBJ_A = JobOwner(
    user_urn="urn:publicid:IDN+example.com+user+tester",
    user_email="tester@example.com",
    project_urn="urn:publicid:IDN+example.com+project+testproj",
)

TEST_JOB2_OWNER_OBJ_B = JobOwner(
    user_urn="urn:publicid:IDN+example.com+user+testerB",
    user_email="testerB@example.com",
    project_urn="urn:publicid:IDN+example.com+project+testprojB",
)


def test_job_owner1():
    expected = TEST_JOB2_OWNER_OBJ_A
    actual = JobOwner.from_json(TEST_JOB2_OWNER_JSON, on_unknown_field_override=ignore_unknown_fields)
    assert expected == actual

TEST_JOB2_UUID_A   = str(uuid.uuid4())
TEST_JOB2_UUID_B   = '0ae7f528-ac52-4362-8d2f-ab6756977a1c'
TEST_JOB2_UUID_NEW = str(uuid.uuid4())
TEST_JOB2_UUID_B_2 = '0a49e527-8e86-4803-9162-ed6509206baf'
TEST_JOB2_UUID_B_5 = '0ae7f61f-c617-46a9-bbb0-060041ab537c'


TEST_JOB2_JSON = """{
    "uuid": """+'"'+TEST_JOB2_UUID_A+'"'+""",
    "name": "testJobA",
    "deploymentEnvironment": "testing",
    "request": """+TEST_JOB2_REQUEST_JSON+""",
    "description": "Test Job A",
    "owner": """+TEST_JOB2_OWNER_JSON+""",
    "state": """+TEST_JOB2_STATE_JSON+""",
    "someOtherJobField": "foobar"
}"""

TEST_JOB2_OBJ_A = Job(
    uuid=TEST_JOB2_UUID_A,
    name="testJobA",
    deployment_environment="testing",
    request=TEST_JOB2_REQUEST_OBJ_A,
    description="Test Job A",
    owner=TEST_JOB2_OWNER_OBJ_A,
    state=TEST_JOB2_STATE_OBJ_A,
)


TEST_JOB2_OBJ_B = Job(
    uuid=TEST_JOB2_UUID_B,
    name="TestJobB",
    deployment_environment="testing",
    request=TEST_JOB2_REQUEST_OBJ_B,
    description="Test Job B",
    owner=TEST_JOB2_OWNER_OBJ_B,
    state=TEST_JOB2_STATE_OBJ_B,
)

TEST_JOB2_JSON_B = TEST_JOB2_OBJ_B.to_json()


def test_job_a():
    expected = TEST_JOB2_OBJ_A
    actual = Job.from_json(TEST_JOB2_JSON, on_unknown_field_override=ignore_unknown_fields)
    assert expected == actual


def test_job_a_to_from_json():
    expected = TEST_JOB2_OBJ_A
    actual = Job.from_json(TEST_JOB2_OBJ_A.to_json(), on_unknown_field_override=ignore_unknown_fields)
    assert expected == actual


def test_job_a_to_from_dict():
    expected = TEST_JOB2_OBJ_A
    actual = Job.from_dict(TEST_JOB2_OBJ_A.to_dict(), on_unknown_field_override=ignore_unknown_fields)
    assert expected == actual


def test_jobs_from_dict_1():
    input = []
    expected = []
    actual: List[Job] = Job.from_dict_list(input, on_unknown_field_override=ignore_unknown_fields)
    assert expected == actual


def test_jobs_from_dict_2():
    input = [TEST_JOB2_OBJ_A.to_dict()]
    expected = [TEST_JOB2_OBJ_A]
    # should work, but fails de decode RFC3339 date correctly:
    # actual: List[Job] = Job.schema().load(input, many=True)
    actual: List[Job] = Job.from_dict_list(input, on_unknown_field_override=ignore_unknown_fields)
    assert expected == actual


def test_job_from_json_no_uuid():
    in_json = '''{
       "name":"NVIDIA SMI",
       "description":"Writes the output of the command 'nvidia-smi' to the log and exits",
       "request": {
          "docker": {
             "command":"nvidia-smi",
             "image":"nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04",
             "storage":[],
             "portMappings":[],
             "groupAdd":[],
    "someOther": "foobar"
          },
          "resources": {
             "clusterId":1,"cpus":1,"gpus":1,"cpuMemoryGb":2,"gpuMemoryGb":4,"minCudaVersion":10,"features":[],"gpuModel":[],
    "someOther": "foobar"
          },
          "scheduling": {
             "interactive":false,"restartable":false,
    "someOther": "foobar"
          },
          "extra": {
             "sshPubKeys":[],"emailOnQueue":[],"emailOnRun":[],"emailOnEnd":[],"emailOnHalt":[],"emailOnRestart":[],
    "someOther": "foobar"
          },
    "someOther": "foobar"
       },
       "owner": {
          "projectUrn": "urn:publicid:IDN+example.com+project+good",
          "userUrn": "urn:publicid:IDN+example.com+user+good",
          "userEmail": "good@example.com"
       },
       "deploymentEnvironment": "staging",
    "someOther": "foobar"
    }'''
    actual = Job.from_json(in_json, on_unknown_field_override=ignore_unknown_fields)
    assert actual.uuid is None
    assert actual.name == "NVIDIA SMI"


def test_resource_request_gpu_model_dict2b():
    dict_in = TEST_JOB2_OBJ_A.to_dict()
    dict_in['request']['resources']['gpuModel'] = 'TITAN'
    job = Job.from_dict(dict_in, on_unknown_field_override=ignore_unknown_fields)
    assert job.request.resources.gpu_model == ['TITAN']
    assert job.request.resources == dataclasses.replace(TEST_JOB2_OBJ_A.request.resources, gpu_model=['TITAN'])


def test_resource_request_gpu_model_dict2c():
    dict_in = TEST_JOB2_OBJ_A.request.to_dict()
    dict_in['resources']['gpuModel'] = 'TITAN'
    job_request = JobRequest.from_dict(dict_in, on_unknown_field_override=ignore_unknown_fields)
    assert job_request.resources.gpu_model == ['TITAN']
    assert job_request.resources == dataclasses.replace(TEST_JOB2_OBJ_A.request.resources, gpu_model=['TITAN'])


def test_job_state_resource_tmpfs_zero_1():
    obj_in = TEST_JOB2_STATE_RESOURCES_OBJ_A
    assert obj_in.tmpfs_mem_gb == 0

    dict_expected = json.loads(TEST_JOB2_STATE_RESOURCES_JSON)
    del dict_expected['someOtherStateResourcesField']
    del dict_expected['portMappings'][0]['someOtherPortMappingField']
    assert 'tmpfsMemGb' not in dict_expected

    dict_actual = obj_in.to_dict(remove_none=True)

    assert dict_actual == dict_expected


def test_job_state_resource_tmpfs_zero_2():
    obj_in = TEST_JOB2_STATE_RESOURCES_OBJ_A
    obj_in = dataclasses.replace(obj_in, tmpfs_mem_gb=1)
    assert obj_in.tmpfs_mem_gb == 1

    dict_expected = json.loads(TEST_JOB2_STATE_RESOURCES_JSON)
    del dict_expected['someOtherStateResourcesField']
    del dict_expected['portMappings'][0]['someOtherPortMappingField']
    dict_expected['tmpfsMemGb'] = 1
    assert 'tmpfsMemGb' in dict_expected
    assert dict_expected['tmpfsMemGb'] == 1

    dict_actual = obj_in.to_dict(remove_none=True)

    assert dict_actual == dict_expected


def test_job_state_resource_tmpfs_zero_3():
    obj_in = TEST_JOB2_STATE_RESOURCES_OBJ_A
    obj_in = dataclasses.replace(obj_in, tmpfs_mem_gb=None)
    assert obj_in.tmpfs_mem_gb is None

    dict_expected = json.loads(TEST_JOB2_STATE_RESOURCES_JSON)
    del dict_expected['someOtherStateResourcesField']
    del dict_expected['portMappings'][0]['someOtherPortMappingField']
    assert 'tmpfsMemGb' not in dict_expected

    dict_actual = obj_in.to_dict(remove_none=True)

    assert dict_actual == dict_expected
