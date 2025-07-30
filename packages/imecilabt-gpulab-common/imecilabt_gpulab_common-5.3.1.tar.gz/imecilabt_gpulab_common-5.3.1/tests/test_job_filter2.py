import pytest
from imecilabt.gpulab.model.job2 import JobStatus

from imecilabt.gpulab.model.job_filter2 import JobFilter2


def test_jobstatus_decoder_a():
    assert JobStatus.__members__.get('ONHOLD') == JobStatus.ONHOLD


def test_jobfilter_from_dict_a():
    actual = JobFilter2.from_dict(
        {'allowedStates': ['ONHOLD', 'QUEUED', 'FINISHED', 'FAILED', 'CANCELLED', 'RUNNING', 'STARTING'],
         'deploymentEnvironment': 'testing',
         'clusterId': 2,
         'userUrn': 'urn:publicid:IDN+example.com+user+test1',
         'userName': 'foo',
         'projectUrn': 'urn:publicid:IDN+example.com+project+bar',
         'projectName': 'projectX',
         'assignedSlaveName': 'host.example.com',
         'assignedSlaveInstanceId': 'instA',
         }
    )
    assert actual == JobFilter2(
        allowed_states=[JobStatus.ONHOLD, JobStatus.QUEUED, JobStatus.FINISHED, JobStatus.FAILED, JobStatus.CANCELLED,
                        JobStatus.RUNNING, JobStatus.STARTING],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )


def test_jobfilter_from_dict_a_from_param():
    actual = JobFilter2.from_params(
        {'allowed_states': 'ONHOLD,QUEUED,FINISHED',
         'deployment_environment': 'testing',
         'cluster_id': 2,
         'user_urn': 'urn:publicid:IDN+example.com+user+test1',
         'user_name': 'foo',
         'project_urn': 'urn:publicid:IDN+example.com+project+bar',
         'project_name': 'projectX',
         'assigned_slave_name': 'host.example.com',
         'assigned_slave_instance_id': 'instA',
         }
    )
    assert actual == JobFilter2(
        allowed_states=[JobStatus.ONHOLD, JobStatus.QUEUED, JobStatus.FINISHED],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )


def test_jobfilter_from_dict_a_from_param_backwardcompat():
    actual = JobFilter2.from_params(
        {'allowed_states': 'ONHOLD , QUEUED , FINISHED',
         'version': 'testing',
         'cluster_id': 2,
         'userurn': 'urn:publicid:IDN+example.com+user+test1',
         'username': 'foo',
         'projecturn': 'urn:publicid:IDN+example.com+project+bar',
         'projectname': 'projectX',
         'assigned_slave_name': 'host.example.com',
         'assigned_slave_instance_id': 'instA',
         'max_hours': 5,
         'max_seconds': 6,
         'max_count': 7,
         'empty_cluster_id': True,
         'cpu_sharing_jobs': False,
         'max_system_memory_mb': 5000,
         'max_gpu_count': 10,
         'max_cpu_count': 1024,
         'other_user_running': True,
         'max_duration_s': 1000000,
         'slave_cuda_version': '1800',
         'slave_gpu_models': 'blah'
         }
    )
    assert actual == JobFilter2(
        allowed_states=[JobStatus.ONHOLD, JobStatus.QUEUED, JobStatus.FINISHED],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )


def test_jobfilter_from_dict_a_from_param_pending_filter():
    actual = JobFilter2.from_params(
        {'pending': True,
         'version': 'testing',
         'cluster_id': 2,
         'userurn': 'urn:publicid:IDN+example.com+user+test1',
         'username': 'foo',
         'projecturn': 'urn:publicid:IDN+example.com+project+bar',
         'projectname': 'projectX',
         'assigned_slave_name': 'host.example.com',
         'assigned_slave_instance_id': 'instA',
         'max_hours': 5,
         'max_seconds': 6,
         'max_count': 7,
         'empty_cluster_id': True,
         'cpu_sharing_jobs': False,
         'max_system_memory_mb': 5000,
         'max_gpu_count': 10,
         'max_cpu_count': 1024,
         'other_user_running': True,
         'max_duration_s': 1000000,
         'slave_cuda_version': '1800',
         'slave_gpu_models': 'blah'
         }
    )
    assert actual == JobFilter2(
        allowed_states=[JobStatus.ONHOLD, JobStatus.QUEUED],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )


def test_jobfilter_from_dict_a_from_param_running_filter():
    actual = JobFilter2.from_params(
        {'running': True,
         'version': 'testing',
         'cluster_id': 2,
         'userurn': 'urn:publicid:IDN+example.com+user+test1',
         'username': 'foo',
         'projecturn': 'urn:publicid:IDN+example.com+project+bar',
         'projectname': 'projectX',
         'assigned_slave_name': 'host.example.com',
         'assigned_slave_instance_id': 'instA',
         'max_hours': 5,
         'max_seconds': 6,
         'max_count': 7,
         'empty_cluster_id': True,
         'cpu_sharing_jobs': False,
         'max_system_memory_mb': 5000,
         'max_gpu_count': 10,
         'max_cpu_count': 1024,
         'other_user_running': True,
         'max_duration_s': 1000000,
         'slave_cuda_version': '1800',
         'slave_gpu_models': 'blah'
         }
    )
    assert actual == JobFilter2(
        allowed_states=[JobStatus.RUNNING, JobStatus.STARTING, JobStatus.MUSTHALT, JobStatus.HALTING],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )


def test_jobfilter_from_dict_a_from_param_finished_filter():
    actual = JobFilter2.from_params(
        {'finished': True,
         'version': 'testing',
         'cluster_id': 2,
         'userurn': 'urn:publicid:IDN+example.com+user+test1',
         'username': 'foo',
         'projecturn': 'urn:publicid:IDN+example.com+project+bar',
         'projectname': 'projectX',
         'assigned_slave_name': 'host.example.com',
         'assigned_slave_instance_id': 'instA',
         'max_hours': 5,
         'max_seconds': 6,
         'max_count': 7,
         'empty_cluster_id': True,
         'cpu_sharing_jobs': False,
         'max_system_memory_mb': 5000,
         'max_gpu_count': 10,
         'max_cpu_count': 1024,
         'other_user_running': True,
         'max_duration_s': 1000000,
         'slave_cuda_version': '1800',
         'slave_gpu_models': 'blah'
         }
    )
    assert actual == JobFilter2(
        allowed_states=[JobStatus.FINISHED, JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.HALTED],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )


def test_jobfilter_to_from_dict_a():
    orig = JobFilter2(
        allowed_states=[JobStatus.ONHOLD, JobStatus.QUEUED, JobStatus.FINISHED, JobStatus.FAILED, JobStatus.CANCELLED,
                        JobStatus.RUNNING, JobStatus.STARTING],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )
    d = orig.to_dict()
    actual = JobFilter2.from_dict(d)
    assert orig == actual


def test_jobfilter_to_from_param_a():
    orig = JobFilter2(
        allowed_states=[JobStatus.ONHOLD, JobStatus.QUEUED, JobStatus.FINISHED, JobStatus.FAILED, JobStatus.CANCELLED,
                        JobStatus.RUNNING, JobStatus.STARTING],
        deployment_environment='testing',
        cluster_id=2,
        user_urn='urn:publicid:IDN+example.com+user+test1',
        user_name='foo',
        project_urn='urn:publicid:IDN+example.com+project+bar',
        project_name='projectX',
        assigned_slave_name='host.example.com',
        assigned_slave_instance_id='instA',
    )
    p = orig.to_params()
    actual = JobFilter2.from_params(p)
    assert orig == actual
