import dataclasses
import json
import datetime

import pytest
from dataclass_dict_convert import UnknownFieldError

from dataclass_dict_convert import datetime_now, dump_rfc3339, parse_rfc3339

from imecilabt.gpulab.model.slave_info2 import ResourceInfo, SlaveInfo2, WatchdogStatistic, GpuModel, \
    STORAGE_PATH_LIMITED_CLUSTER_PROJECTS

TEST_SLAVEINFO_ACTIVE_JOB_UUID_A = "0ae7f528-ac52-4362-8d2f-ab6756977a1c"
TEST_SLAVEINFO_ACTIVE_JOB_UUID_B = "0a49e527-8e86-4803-9162-ed6509206baf"
TEST_SLAVEINFO_ACTIVE_JOB_UUID_C = "0ae7f61f-c617-46a9-bbb0-060041ab537c"

_test_time = datetime_now()
_test_time_rfc3339 = dump_rfc3339(_test_time)
TEST_SLAVEINFO_A = SlaveInfo2(
    deployment_environment="testing",
    name="slaveA",
    host="a.example.com",
    aliases=["A", "nickA"],
    instance_id="slaveAinst1",
    pid=45,
    cluster_id=10,
    gpu_model=[GpuModel(vendor="nvidia", name="gpumodel", memory_mb=8000)],
    cpu_model=["cpumodel1", "cpumodel2"],
    worker=ResourceInfo(system_total=10, acquired=10, used=5, available=5),
    cpu_memory_mb=ResourceInfo(system_total=1024, acquired=512, used=256, available=256),
    gpu=ResourceInfo(system_total=10, acquired=8, used=2, available=6),
    cpu=ResourceInfo(system_total=20, acquired=16, used=4, available=12),
    active_job_uuids=[TEST_SLAVEINFO_ACTIVE_JOB_UUID_A, TEST_SLAVEINFO_ACTIVE_JOB_UUID_B],
    cuda_version_full="10.1.2",
    last_update=_test_time,
    comment="a comment",
    shutting_down=True,
    docker_disk_used_percent=90.0,
    accepting_jobs=True,
)


def test_resource_info_from_json1():
    json_in = '{"systemTotal": 5, "acquired": 4, "used": 3, "available": 1}'
    actual = ResourceInfo.from_json(json_in)
    assert actual.system_total == 5
    assert actual.acquired == 4
    assert actual.used == 3
    assert actual.available == 1


def test_resource_info_from_json3():
    json_in = '{"systemTotal": 5, "acquired": 4, "used": 3, "extrajunk": 2, "available": 1}'
    with pytest.raises(UnknownFieldError, match='.*extrajunk.*'):
        actual = ResourceInfo.from_json(json_in)


def test_resource_info_from_json2a():
    json_in = '{"systemTotal": "five", "acquired": 4, "used": 3, "available": 1}'
    with pytest.raises(TypeError, match='ResourceInfo.system_total must be int, not str'):
        actual = ResourceInfo.from_json(json_in)


def test_resource_info_from_json2b():
    json_in = '{"systemTotal": "5", "acquired": 4, "used": 3, "available": 1}'
    with pytest.raises(TypeError, match='.*system_total.*'):
        actual = ResourceInfo.from_json(json_in)


def test_resource_info_from_json3a():
    json_in = '{"systemTotal": 5, "acquired": 4, "used": 3}'
    # with pytest.raises(KeyError, match='.*available.*'):
    with pytest.raises(TypeError, match='.*available.*'):
        actual = ResourceInfo.from_json(json_in)


def test_resource_info_from_json3b():
    json_in = '{"systemTotal": 5, "acquired": 4, "used": 3, "available": 77}'
    with pytest.raises(Exception, match='.*available.*'):
        actual = ResourceInfo.from_json(json_in)


def test_slave_info2_to_json1():
    slave_info2_in = TEST_SLAVEINFO_A
    actual = slave_info2_in.to_json()
    assert '{' in actual
    assert '}' in actual
    assert 'instanceId' in actual
    assert 'nickA' in actual
    assert 'a.example.com' in actual
    assert 'systemTotal' in actual
    assert 'cudaVersionFull' in actual
    assert 'cudaVersionMajor' in actual
    assert 'dockerDiskUsedPercent' in actual
    assert 'acceptingJobs' in actual
    assert _test_time_rfc3339 in actual
    assert TEST_SLAVEINFO_ACTIVE_JOB_UUID_A in actual


def test_slave_info2_from_json1a():
    # without cudaVersionMajor
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "host": "a.example.com",
  "aliases": ["A", "nickA"],
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "cpuMemoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true,
  "dockerDiskUsedPercent": 90.0,
  "acceptingJobs": true
}"""

    actual = SlaveInfo2.from_json(json_in)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'a.example.com'
    assert actual.aliases == ['A', 'nickA']
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == 45
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)]
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=1024, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=10,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=20,acquired=16,used=4,available=12)
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True
    assert actual.docker_disk_used_percent == 90.0
    assert actual.accepting_jobs is True


def test_slave_info2_from_json1b():
    # with correct cudaVersionMajor
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "host": "a.example.com",
  "aliases": ["A", "nickA"],
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "cpuMemoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionMajor": 10,
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true,
  "dockerDiskUsedPercent": 95.0,
  "acceptingJobs": false
}"""

    actual = SlaveInfo2.from_json(json_in)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'a.example.com'
    assert actual.aliases == ['A', 'nickA']
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == 45
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)]
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=1024, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=10,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=20,acquired=16,used=4,available=12)
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True
    assert actual.docker_disk_used_percent == 95.0
    assert actual.accepting_jobs is False


def test_slave_info2_from_json1c():
    # with wrong cudaVersionMajor
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "host": "a.example.com",
  "aliases": ["A", "nickA"],
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "cpuMemoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionMajor": 11,
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true
}"""

    with pytest.raises(Exception, match='.*major.*'):
        actual = SlaveInfo2.from_json(json_in)


def test_slave_info2_from_json1d():
    # without host and aliases
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "cpuMemoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionMajor": 10,
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true,
  "dockerDiskUsedPercent": 95.0,
  "acceptingJobs": false
}"""

    actual = SlaveInfo2.from_json(json_in)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == None
    assert actual.aliases == []
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == 45
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)]
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=1024, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=10,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=20,acquired=16,used=4,available=12)
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True
    assert actual.docker_disk_used_percent == 95.0
    assert actual.accepting_jobs is False


def test_slave_info2_from_json1d():
    # with wrong type in cpu model list
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "host": "a.example.com",
  "aliases": ["A", "nickA"],
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    1, 2
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "cpuMemoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionMajor": 10,
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true
}"""

    with pytest.raises(Exception, match='.*cpu_?[mM]odel.*'):
        actual = SlaveInfo2.from_json(json_in)


def test_slave_info2_convert():
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)

    slave_info2_in = SlaveInfo2(
        deployment_environment='testing',
        name='slaveA',
        host='a.example.com',
        aliases=['A', 'nickA'],
        instance_id='slaveAinst1',
        pid=45,
        cluster_id=10,
        gpu_model=[GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)],
        cpu_model=['cpumodel1', 'cpumodel2'],
        worker=ResourceInfo(system_total=10,acquired=10,used=5,available=5),
        cpu_memory_mb=ResourceInfo(system_total=1024, acquired=512, used=256, available=256),
        gpu=ResourceInfo(system_total=10, acquired=8, used=2, available=6),
        cpu=ResourceInfo(system_total=20, acquired=16, used=4, available=12),
        active_job_uuids=[TEST_SLAVEINFO_ACTIVE_JOB_UUID_C],
        cuda_version_full='10.1.2',
        last_update=test_time,
        comment='a comment',
        shutting_down=True,
        docker_disk_used_percent=90.0,
        accepting_jobs=False)
    slave_info1_out = slave_info2_in.to_slave_info_1()
    print(json.dumps(slave_info1_out.to_dict()))
    actual = SlaveInfo2.from_slave_info_1(slave_info1_out)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'slaveA' # 'a.example.com' # Data loss because SlaveInfo does not support host
    assert actual.aliases == [] # ['A', 'nickA'] # Data loss because SlaveInfo does not support aliases
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == -1  # Data loss because SlaveInfo does not support pid
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=0)]  # memory_mb information lost due to convert
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    # Data loss because SlaveInfo does not support system_total
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=512, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=8,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=16,acquired=16,used=4,available=12)
    assert actual.active_job_uuids is None
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True

    assert actual.docker_disk_used_percent == -1.0  # information lost due to convert
    assert actual.accepting_jobs is True  # information lost due to convert


def test_slave_info2_convert_no_last_update():
    test_time = None
    test_time_expected = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    test_time_expected2 = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc)
    assert test_time_expected.tzinfo is not None
    assert test_time_expected2.tzinfo is not None
    assert test_time_expected2 == test_time_expected
    test_time_rfc3339 = dump_rfc3339(test_time_expected2)
    assert '1970' in test_time_rfc3339
    assert test_time_rfc3339.endswith('Z')

    slave_info2_in = SlaveInfo2(
        deployment_environment='testing',
        name='slaveA',
        host='a.example.com',
        aliases=['A', 'nickA'],
        instance_id='slaveAinst1',
        pid=45,
        cluster_id=10,
        gpu_model=[GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)],
        cpu_model=['cpumodel1', 'cpumodel2'],
        worker=ResourceInfo(system_total=10,acquired=10,used=5,available=5),
        cpu_memory_mb=ResourceInfo(system_total=1024, acquired=512, used=256, available=256),
        gpu=ResourceInfo(system_total=10, acquired=8, used=2, available=6),
        cpu=ResourceInfo(system_total=20, acquired=16, used=4, available=12),
        active_job_uuids=[TEST_SLAVEINFO_ACTIVE_JOB_UUID_A, TEST_SLAVEINFO_ACTIVE_JOB_UUID_B],
        cuda_version_full='10.1.2',
        last_update=test_time_expected,
        comment='a comment',
        shutting_down=True,
        docker_disk_used_percent=90.0,
        accepting_jobs=False)
    slave_info1_out = slave_info2_in.to_slave_info_1()
    slave_info1_out.last_update = None
    print(json.dumps(slave_info1_out.to_dict()))
    actual = SlaveInfo2.from_slave_info_1(slave_info1_out)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'slaveA' # 'a.example.com' # Data loss because SlaveInfo does not support host
    assert actual.aliases == [] # ['A', 'nickA'] # Data loss because SlaveInfo does not support aliases
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == -1  # Data loss because SlaveInfo does not support pid
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=0)]  # memory_mb information lost due to convert
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    # Data loss because SlaveInfo does not support system_total
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=512, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=8,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=16,acquired=16,used=4,available=12)
    assert actual.active_job_uuids is None
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time_expected
    assert (actual.last_update - test_time_expected).total_seconds() == 0
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True

    assert actual.docker_disk_used_percent == -1.0  # information lost due to convert
    assert actual.accepting_jobs is True  # information lost due to convert


def test_slave_info2_from_any_json1():
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "host": "a.example.com",
  "aliases": ["A", "nickA"],
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "cpuMemoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionMajor": 10,
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true
}"""

    actual = SlaveInfo2.from_any_json(json_in)
    assert isinstance(actual, SlaveInfo2), 'did not return SlaveInfo2 but {}'.format(type(actual).__name__)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'a.example.com'
    assert actual.aliases == ['A', 'nickA']
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == 45
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)]
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=1024, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=10,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=20,acquired=16,used=4,available=12)
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True


def test_slave_info2_from_any_json1b():
    # memoryMb instead of cpuMemoryMb
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "host": "a.example.com",
  "aliases": ["A", "nickA"],
  "instanceId": "slaveAinst1",
  "pid": 45,
  "clusterId": 10,
  "gpuModel": [
    { "vendor": "nvidia", "name": "gpumodel", "memoryMb": 8000 }
  ],
  "cpuModel": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker": {
    "systemTotal": 10,
    "acquired": 10,
    "used": 5,
    "available": 5
  },
  "memoryMb": {
    "systemTotal": 1024,
    "acquired": 512,
    "used": 256,
    "available": 256
  },
  "gpu": {
    "systemTotal": 10,
    "acquired": 8,
    "used": 2,
    "available": 6
  },
  "cpu": {
    "systemTotal": 20,
    "acquired": 16,
    "used": 4,
    "available": 12
  },
  "cudaVersionMajor": 10,
  "cudaVersionFull": "10.1.2",
  "lastUpdate": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shuttingDown": true
}"""

    actual = SlaveInfo2.from_any_json(json_in)
    assert isinstance(actual, SlaveInfo2), 'did not return SlaveInfo2 but {}'.format(type(actual).__name__)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'a.example.com'
    assert actual.aliases == ['A', 'nickA']
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == 45
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)]
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=1024, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=10,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=20,acquired=16,used=4,available=12)
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True
    assert actual.accepting_jobs is True
    assert actual.docker_disk_used_percent == -1.0


def test_slave_info2_from_any_json1c():
    # check actual old SlaveInfo2 format
    test_time_rfc3339 = '2020-07-08T07:02:36Z'
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
        "deploymentEnvironment": "production", 
        "hostname": "n053-02", 
        "instanceId": "inst10", 
        "pid": 14648, 
        "clusterId": 4, 
        "gpuModel": ["GeForce GTX 1080 Ti"], 
        "cpuModel": ["Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz"],
         "worker": {"systemTotal": 64, "acquired": 64, "used": 8, "available": 56}, 
        "memoryMb": {"systemTotal": 254576, "acquired": 254576, "used": 254576, "available": 0}, 
        "gpu": {"systemTotal": 7, "acquired": 7, "used": 7, "available": 0}, 
        "cpu": {"systemTotal": 28, "acquired": 28, "used": 28, "available": 0}, 
        "lastUpdate": "2020-07-08T07:02:36Z", 
        "comment": "todo", 
        "shuttingDown": true,
        "cudaVersionFull": "10.2.89", 
        "cudaVersionMajor": 10,
        "dockerDiskUsedPercent": 7.7, 
        "acceptingJobs": false
        }"""

    actual = SlaveInfo2.from_any_json(json_in)
    assert isinstance(actual, SlaveInfo2), 'did not return SlaveInfo2 but {}'.format(type(actual).__name__)
    assert actual.deployment_environment == 'production'
    assert actual.name == 'n053-02'
    assert actual.host == 'n053-02'
    assert actual.aliases == []
    assert actual.instance_id == 'inst10'
    assert actual.pid == 14648
    assert actual.cluster_id == 4
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='GeForce GTX 1080 Ti', memory_mb=-1)]
    assert actual.cpu_model == ['Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz']
    assert actual.worker == ResourceInfo(system_total=64,acquired=64,used=8,available=56)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=254576, acquired=254576, used=254576, available=0)
    assert actual.gpu == ResourceInfo(system_total=7,acquired=7,used=7,available=0)
    assert actual.cpu == ResourceInfo(system_total=28,acquired=28,used=28,available=0)
    assert actual.cuda_version_full == '10.2.89'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'todo'
    assert actual.shutting_down is True
    assert actual.accepting_jobs is False
    assert actual.docker_disk_used_percent == 7.7


def test_slave_info2_from_any_json2():
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    json_in = """{
  "version": "testing",
  "slave_hostname": "slaveA",
  "slave_instance_id": "slaveAinst1",
  "cluster_id": 10,
  "gpu_models": ["gpumodel"],
  "cpu_models": [
    "cpumodel1",
    "cpumodel2"
  ],
  "worker_count": 10,
  "system_memory_mb": 512,
  "gpu_count": 8,
  "cpu_count": 16,
  "worker_inuse": 5,
  "system_memory_inuse_mb": 256,
  "gpu_inuse": 2,
  "cpu_inuse": 4,
  "cuda_version_major": 10,
  "cuda_version_full": "10.1.2",
  "last_update": """+'"'+test_time_rfc3339+'"'+""",
  "comment": "a comment",
  "shutting_down": true
}"""

    actual = SlaveInfo2.from_any_json(json_in)
    assert isinstance(actual, SlaveInfo2), 'did not return SlaveInfo2 but {}'.format(type(actual).__name__)
    assert actual.deployment_environment == 'testing'
    assert actual.name == 'slaveA'
    assert actual.host == 'slaveA'
    assert actual.aliases == []
    assert actual.instance_id == 'slaveAinst1'
    assert actual.pid == -1  # conversion data loss
    assert actual.cluster_id == 10
    assert actual.gpu_model == [GpuModel(vendor='nvidia', name='gpumodel', memory_mb=0)]  # memory_mb information lost due to convert
    assert actual.cpu_model == ['cpumodel1', 'cpumodel2']
    # conversion data loss in system_total
    assert actual.worker == ResourceInfo(system_total=10,acquired=10,used=5,available=5)
    assert actual.cpu_memory_mb == ResourceInfo(system_total=512, acquired=512, used=256, available=256)
    assert actual.gpu == ResourceInfo(system_total=8,acquired=8,used=2,available=6)
    assert actual.cpu == ResourceInfo(system_total=16,acquired=16,used=4,available=12)
    assert actual.cuda_version_full == '10.1.2'
    assert actual.cuda_version_major == 10
    assert actual.last_update == test_time
    assert actual.comment == 'a comment'
    assert actual.shutting_down is True


def test_slave_info2_from_any_json3():
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)

    json_in = """{
  "deploymentEnvironment": "testing",
  "name": "slaveA",
  "gpu_models": ["foo"],
  "gpuModel": [{ "vendor": "acme", "name": "bar", "memoryMb": 4000 }]
}"""

    with pytest.raises(ValueError):
        actual = SlaveInfo2.from_any_json(json_in)


def test_slave_info2_dict_datetime_convert():
    test_time = None
    test_time_expected = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    test_time_expected2 = datetime.datetime.fromtimestamp(0).astimezone(datetime.timezone.utc)
    assert test_time_expected.tzinfo is not None
    assert test_time_expected2.tzinfo is not None
    assert test_time_expected2 == test_time_expected
    test_time_rfc3339 = dump_rfc3339(test_time_expected2)
    assert '1970' in test_time_rfc3339
    assert test_time_rfc3339.endswith('Z')

    slave_info2_in = SlaveInfo2(
        deployment_environment='testing',
        name='slaveA',
        host='a.example.com',
        aliases=['A', 'nickA'],
        instance_id='slaveAinst1',
        pid=45,
        cluster_id=10,
        gpu_model=[GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)],
        cpu_model=['cpumodel1', 'cpumodel2'],
        worker=ResourceInfo(system_total=10,acquired=10,used=5,available=5),
        cpu_memory_mb=ResourceInfo(system_total=1024, acquired=512, used=256, available=256),
        gpu=ResourceInfo(system_total=10, acquired=8, used=2, available=6),
        cpu=ResourceInfo(system_total=20, acquired=16, used=4, available=12),
        active_job_uuids=[TEST_SLAVEINFO_ACTIVE_JOB_UUID_B],
        cuda_version_full='10.1.2',
        last_update=test_time_expected,
        comment='a comment',
        shutting_down=True,
        docker_disk_used_percent=90.0,
        accepting_jobs=False)

    dict_out = slave_info2_in.to_dict()
    print('dict_out.lastUpdate={}'.format(dict_out['lastUpdate']))
    assert isinstance(dict_out['lastUpdate'], str)
    assert dict_out['lastUpdate'] == test_time_rfc3339


def test_watchdog_statistics_to_json():
    test_time = datetime_now()
    test_time_rfc3339 = dump_rfc3339(test_time)
    test_time = parse_rfc3339(test_time_rfc3339)

    obj_in = WatchdogStatistic(
        alive_now=True,
        last_alive_date=test_time,
        alarm_counts={'tst': 5},
        alarm_last_dates={'tst': test_time_rfc3339},
        emails_sent=10
    )

    dict_out = obj_in.to_dict()
    print('dict_out={}'.format(dict_out))
    assert dict_out['aliveNow'] is True
    assert 'lastAliveDate' in dict_out
    assert isinstance(dict_out['lastAliveDate'], str), 'did not convert datetime to str: {}'.format(type(dict_out['lastAliveDate']).__name__)
    assert dict_out['lastAliveDate'] == test_time_rfc3339
    assert 'alarmLastDates' in dict_out
    assert 'tst' in dict_out['alarmLastDates']
    assert isinstance(dict_out['alarmLastDates']['tst'], str), 'did not convert datetime to str: {}'.format(type(dict_out['alarmLastDates']['tst']).__name__)
    assert dict_out['alarmLastDates']['tst'] == test_time_rfc3339

    json_out = obj_in.to_json()
    assert test_time_rfc3339 in json_out
    print('json_out={}'.format(json_out))

    dict_out_in = json.loads(json_out)
    print('dict_out_in={}'.format(dict_out_in))
    assert dict_out_in['aliveNow'] is True
    assert 'lastAliveDate' in dict_out_in
    assert isinstance(dict_out_in['lastAliveDate'], str), 'did not convert datetime to str: {}'.format(type(dict_out_in['lastAliveDate']).__name__)
    assert dict_out_in['lastAliveDate'] == test_time_rfc3339
    assert 'alarmLastDates' in dict_out_in
    assert 'tst' in dict_out_in['alarmLastDates']
    assert isinstance(dict_out_in['alarmLastDates']['tst'], str), 'did not convert datetime to str: {}'.format(type(dict_out_in['alarmLastDates']['tst']).__name__)
    assert dict_out_in['alarmLastDates']['tst'] == test_time_rfc3339

    actual = WatchdogStatistic.from_json(json_out)
    assert isinstance(actual, WatchdogStatistic), 'did not return WatchdogStatistic but {}'.format(type(actual).__name__)
    assert actual.alive_now is True
    assert actual.emails_sent == 10
    assert actual.alarm_counts == {'tst': 5}
    assert actual.last_alive_date == test_time
    assert actual.alarm_last_dates == {'tst': test_time_rfc3339}

    copy = obj_in.make_copy()
    assert isinstance(copy, WatchdogStatistic), 'did not return WatchdogStatistic but {}'.format(type(copy).__name__)
    assert copy.alive_now is True
    assert copy.emails_sent == 10
    assert copy.alarm_counts == {'tst': 5}
    assert copy.last_alive_date == test_time
    assert copy.alarm_last_dates == {'tst': test_time_rfc3339}


def test_name_matches():
    slave_info2 = SlaveInfo2(
        deployment_environment='testing',
        name='slaveA1',
        host='a.example.com',
        aliases=['A1', 'nick A1'],
        instance_id='slaveA1inst1',
        pid=45,
        cluster_id=10,
        gpu_model=[GpuModel(vendor='nvidia', name='gpumodel', memory_mb=8000)],
        cpu_model=['cpumodel1', 'cpumodel2'],
        worker=ResourceInfo(system_total=10,acquired=10,used=5,available=5),
        cpu_memory_mb=ResourceInfo(system_total=1024, acquired=512, used=256, available=256),
        gpu=ResourceInfo(system_total=10, acquired=8, used=2, available=6),
        cpu=ResourceInfo(system_total=20, acquired=16, used=4, available=12),
        active_job_uuids=[TEST_SLAVEINFO_ACTIVE_JOB_UUID_A],
        cuda_version_full='10.1.2',
        last_update=datetime_now(),
        comment='a comment',
        shutting_down=True,
        docker_disk_used_percent=90.0,
        accepting_jobs=True)

    assert slave_info2.matches_name('A1')
    assert slave_info2.matches_name('a1')
    assert slave_info2.matches_name('A 1')
    assert slave_info2.matches_name('_A_1_')
    assert slave_info2.matches_name('nick A1')
    assert slave_info2.matches_name('NICKA1')
    assert slave_info2.matches_name('nick_A1')
    assert slave_info2.matches_name('slaveA1')
    assert slave_info2.matches_name('SLAVEa1')
    assert slave_info2.matches_name('SLAVE A1')
    assert slave_info2.matches_name(' S__L A V$$$$E  &^  A 1   *')

    assert not slave_info2.matches_name('SLAVEA')
    assert not slave_info2.matches_name('a')
    assert not slave_info2.matches_name('a2')
    assert not slave_info2.matches_name('nick A')
    assert not slave_info2.matches_name('A1nick')
    assert not slave_info2.matches_name('slave')
    assert not slave_info2.matches_name('nick')


_TEST_PROJ_URN1a = 'urn:publicid:IDN+example.com+project+project1'
_TEST_PROJ_URN1b = 'urn:publicid:IDN+example.com+project+Project1'
_TEST_PROJ_URN2a = 'urn:publicid:IDN+example.com+project+Project2'
_TEST_PROJ_URN2b = 'urn:publicid:IDN+example.com+project+PROJECT2'
_TEST_PROJ_URN3 = 'urn:publicid:IDN+example.com+project+p3'


def test_has_storage_1():
    slave_info2 = dataclasses.replace(TEST_SLAVEINFO_A,
        storage_paths_available=['/project', '/project_scratch/'],
        storage_aliases_available={
            '/project_alias1': '/project',
            '/project_alias2/': '/project',
            '/project_alias3/': '/project/',
            '/project_alias4': '/project/',
            '/project_scratch_alias1': '/project_scratch',
            '/project_scratch_alias2/': '/project_scratch',
            '/project_scratch_alias3/': '/project_scratch/',
            '/project_scratch_alias4': '/project_scratch/',
        },
        storage_paths_available_project_limited={
            '/project/': [_TEST_PROJ_URN1a, _TEST_PROJ_URN2a],
            '/project_scratch/': [_TEST_PROJ_URN1b, _TEST_PROJ_URN2b],
        }
    )

    assert slave_info2.has_storage('/project')
    assert slave_info2.has_storage('/project/')
    assert slave_info2.has_storage('/project/foo/')
    assert slave_info2.has_storage('/project/foo/bar')
    assert not slave_info2.has_storage('project')
    assert not slave_info2.has_storage('/PROJECT')

    assert not slave_info2.has_storage('/project_alias')
    assert not slave_info2.has_storage('/project_alias/')

    assert slave_info2.has_storage('/project_alias1')
    assert slave_info2.has_storage('/project_alias1/')
    assert slave_info2.has_storage('/project_alias1/foo/')
    assert slave_info2.has_storage('/project_alias1/foo/bar')

    assert slave_info2.has_storage('/project_alias2')
    assert slave_info2.has_storage('/project_alias2/')
    assert slave_info2.has_storage('/project_alias2/foo/')
    assert slave_info2.has_storage('/project_alias2/foo/bar')

    assert slave_info2.has_storage('/project_alias3')
    assert slave_info2.has_storage('/project_alias3/')
    assert slave_info2.has_storage('/project_alias3/foo/')
    assert slave_info2.has_storage('/project_alias3/foo/bar')

    assert slave_info2.has_storage('/project_alias4')
    assert slave_info2.has_storage('/project_alias4/')
    assert slave_info2.has_storage('/project_alias4/foo/')
    assert slave_info2.has_storage('/project_alias4/foo/bar')


def test_allows_storage_1():
    slave_info2 = dataclasses.replace(TEST_SLAVEINFO_A,
        storage_paths_available=['/project', '/project_scratch/'],
        storage_aliases_available={
            '/project_alias1': '/project',
            '/project_alias2/': '/project',
            '/project_alias3/': '/project/',
            '/project_alias4': '/project/',
            '/project_scratch_alias1': '/project_scratch',
            '/project_scratch_alias2/': '/project_scratch',
            '/project_scratch_alias3/': '/project_scratch/',
            '/project_scratch_alias4': '/project_scratch/',
        },
        storage_paths_available_project_limited={
            '/project/': [_TEST_PROJ_URN1a, _TEST_PROJ_URN2a],
            '/project_scratch/': [_TEST_PROJ_URN1b, _TEST_PROJ_URN2b],
        }
    )

    for proj_urn in (_TEST_PROJ_URN1a, _TEST_PROJ_URN1b, _TEST_PROJ_URN2a, _TEST_PROJ_URN2b):
        assert slave_info2.allows_storage('/project', proj_urn), f'Failed allow_storage for proj_urn={proj_urn}'
        assert slave_info2.allows_storage('/project/', proj_urn)
        assert slave_info2.allows_storage('/project/foo/', proj_urn)
        assert slave_info2.allows_storage('/project/foo/bar', proj_urn)
        assert not slave_info2.allows_storage('project', proj_urn)
        assert not slave_info2.allows_storage('/PROJECT', proj_urn)

        assert not slave_info2.allows_storage('/project_alias', proj_urn)
        assert not slave_info2.allows_storage('/project_alias/', proj_urn)

        assert slave_info2.allows_storage('/project_alias1', proj_urn)
        assert slave_info2.allows_storage('/project_alias1/', proj_urn)
        assert slave_info2.allows_storage('/project_alias1/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_alias1/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_alias2', proj_urn)
        assert slave_info2.allows_storage('/project_alias2/', proj_urn)
        assert slave_info2.allows_storage('/project_alias2/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_alias2/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_alias3', proj_urn)
        assert slave_info2.allows_storage('/project_alias3/', proj_urn)
        assert slave_info2.allows_storage('/project_alias3/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_alias3/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_alias4', proj_urn)
        assert slave_info2.allows_storage('/project_alias4/', proj_urn)
        assert slave_info2.allows_storage('/project_alias4/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_alias4/foo/bar', proj_urn)

    proj_urn = _TEST_PROJ_URN3
    assert not slave_info2.allows_storage('/project', proj_urn)
    assert not slave_info2.allows_storage('/project/', proj_urn)
    assert not slave_info2.allows_storage('/project/foo/', proj_urn)
    assert not slave_info2.allows_storage('/project/foo/bar', proj_urn)
    assert not slave_info2.allows_storage('project', proj_urn)
    assert not slave_info2.allows_storage('/PROJECT', proj_urn)

    assert not slave_info2.allows_storage('/project_alias', proj_urn)
    assert not slave_info2.allows_storage('/project_alias/', proj_urn)

    assert not slave_info2.allows_storage('/project_alias1', proj_urn)
    assert not slave_info2.allows_storage('/project_alias1/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias1/foo/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias1/foo/bar', proj_urn)

    assert not slave_info2.allows_storage('/project_alias2', proj_urn)
    assert not slave_info2.allows_storage('/project_alias2/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias2/foo/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias2/foo/bar', proj_urn)

    assert not slave_info2.allows_storage('/project_alias3', proj_urn)
    assert not slave_info2.allows_storage('/project_alias3/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias3/foo/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias3/foo/bar', proj_urn)

    assert not slave_info2.allows_storage('/project_alias4', proj_urn)
    assert not slave_info2.allows_storage('/project_alias4/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias4/foo/', proj_urn)
    assert not slave_info2.allows_storage('/project_alias4/foo/bar', proj_urn)


def test_allows_storage_2():
    slave_info2 = dataclasses.replace(TEST_SLAVEINFO_A,
        storage_paths_available=['/project', '/project_scratch/'],
        storage_aliases_available={
            '/project_alias1': '/project',
            '/project_alias2/': '/project',
            '/project_alias3/': '/project/',
            '/project_alias4': '/project/',
            '/project_scratch_alias1': '/project_scratch',
            '/project_scratch_alias2/': '/project_scratch',
            '/project_scratch_alias3/': '/project_scratch/',
            '/project_scratch_alias4': '/project_scratch/',
        },
        storage_paths_available_project_limited={
            '/project/': []
        }
    )

    for proj_urn in (_TEST_PROJ_URN1a, _TEST_PROJ_URN1b, _TEST_PROJ_URN2a, _TEST_PROJ_URN2b, _TEST_PROJ_URN3):
        assert not slave_info2.allows_storage('/project', proj_urn), f'Failed allow_storage for proj_urn={proj_urn}'
        assert not slave_info2.allows_storage('/project/', proj_urn)
        assert not slave_info2.allows_storage('/project/foo/', proj_urn)
        assert not slave_info2.allows_storage('/project/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_scratch', proj_urn)
        assert slave_info2.allows_storage('/project_scratch/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch/foo/bar', proj_urn)

        assert not slave_info2.allows_storage('project', proj_urn)
        assert not slave_info2.allows_storage('/PROJECT', proj_urn)

        assert not slave_info2.allows_storage('/project_alias', proj_urn)
        assert not slave_info2.allows_storage('/project_alias/', proj_urn)

        assert not slave_info2.allows_storage('/project_alias1', proj_urn)
        assert not slave_info2.allows_storage('/project_alias1/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias1/foo/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias1/foo/bar', proj_urn)

        assert not slave_info2.allows_storage('/project_alias2', proj_urn)
        assert not slave_info2.allows_storage('/project_alias2/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias2/foo/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias2/foo/bar', proj_urn)

        assert not slave_info2.allows_storage('/project_alias3', proj_urn)
        assert not slave_info2.allows_storage('/project_alias3/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias3/foo/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias3/foo/bar', proj_urn)

        assert not slave_info2.allows_storage('/project_alias4', proj_urn)
        assert not slave_info2.allows_storage('/project_alias4/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias4/foo/', proj_urn)
        assert not slave_info2.allows_storage('/project_alias4/foo/bar', proj_urn)

        assert not slave_info2.allows_storage('/project_scratch_alias', proj_urn)
        assert not slave_info2.allows_storage('/project_scratch_alias/', proj_urn)

        assert slave_info2.allows_storage('/project_scratch_alias1', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias1/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias1/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias1/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_scratch_alias2', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias2/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias2/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias2/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_scratch_alias3', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias3/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias3/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias3/foo/bar', proj_urn)

        assert slave_info2.allows_storage('/project_scratch_alias4', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias4/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias4/foo/', proj_urn)
        assert slave_info2.allows_storage('/project_scratch_alias4/foo/bar', proj_urn)


def test_allows_storage_3():
    slave_info2 = dataclasses.replace(TEST_SLAVEINFO_A,
        storage_paths_available=['/project', '/project_scratch/'],
        storage_aliases_available={
            '/project_alias1': '/project',
            '/project_alias2/': '/project',
            '/project_alias3/': '/project/',
            '/project_alias4': '/project/',
            '/project_scratch_alias1': '/project_scratch',
            '/project_scratch_alias2/': '/project_scratch',
            '/project_scratch_alias3/': '/project_scratch/',
            '/project_scratch_alias4': '/project_scratch/',
        },
        storage_paths_available_project_limited={
            '/project/': [STORAGE_PATH_LIMITED_CLUSTER_PROJECTS],
            '/project_scratch/': [_TEST_PROJ_URN1b, _TEST_PROJ_URN2b],
        }
    )

    cluster_projects_allowed = [_TEST_PROJ_URN1a, _TEST_PROJ_URN2a]

    for proj_urn in (_TEST_PROJ_URN1a, _TEST_PROJ_URN1b, _TEST_PROJ_URN2a, _TEST_PROJ_URN2b):
        assert slave_info2.allows_storage('/project', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert not slave_info2.allows_storage('project', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert not slave_info2.allows_storage('/PROJECT', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

        assert not slave_info2.allows_storage('/project_alias', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert not slave_info2.allows_storage('/project_alias/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

        assert slave_info2.allows_storage('/project_alias1', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias1/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias1/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias1/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

        assert slave_info2.allows_storage('/project_alias2', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias2/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias2/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias2/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

        assert slave_info2.allows_storage('/project_alias3', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias3/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias3/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias3/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

        assert slave_info2.allows_storage('/project_alias4', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias4/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias4/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
        assert slave_info2.allows_storage('/project_alias4/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

    proj_urn = _TEST_PROJ_URN3
    assert not slave_info2.allows_storage('/project', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('project', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/PROJECT', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

    assert not slave_info2.allows_storage('/project_alias', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

    assert not slave_info2.allows_storage('/project_alias1', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias1/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias1/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias1/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

    assert not slave_info2.allows_storage('/project_alias2', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias2/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias2/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias2/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

    assert not slave_info2.allows_storage('/project_alias3', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias3/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias3/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias3/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)

    assert not slave_info2.allows_storage('/project_alias4', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias4/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias4/foo/', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
    assert not slave_info2.allows_storage('/project_alias4/foo/bar', proj_urn, cluster_projects_allowed=cluster_projects_allowed)
