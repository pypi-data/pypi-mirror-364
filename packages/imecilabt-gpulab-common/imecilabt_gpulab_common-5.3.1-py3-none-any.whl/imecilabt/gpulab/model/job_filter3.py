from dataclasses import dataclass, field
from typing import List, Optional, TypeVar, Union

from dataclass_dict_convert import (dataclass_auto_type_check,
                                    dataclass_copy_method,
                                    dataclass_dict_convert)
from imecilabt.gpulab.model.job2 import JobStatus
from imecilabt.gpulab.model.slave_info2 import SlaveInfo2
from stringcase import camelcase, snakecase

##
## Version 3 of JobFilter: JobFilter3
##
## Changes:
##   - allow multiple values of each filter
##


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class JobFilter3:
    cluster_id: List[int] = field(
        default_factory=list
    )  # requested OR assigned cluster ID
    allowed_states: List[JobStatus] = field(
        default_factory=list
    )  # [] means: don't filter
    user_urn: List[str] = field(default_factory=list)
    user_name: List[str] = field(default_factory=list)
    project_urn: List[str] = field(default_factory=list)
    project_name: List[str] = field(default_factory=list)
    assigned_slave_name: List[str] = field(default_factory=list)
    assigned_slave_instance_id: List[str] = field(default_factory=list)
    interactive: Optional[bool] = None
    waste: Optional[bool] = None
    reservation_id: Optional[str] = None

    @classmethod
    def for_pending(cls) -> "JobFilter3":
        """typical JobFilter used to find all Pending Jobs"""
        return cls(
            allowed_states=[JobStatus.QUEUED],
        )

    @classmethod
    def no_filter(cls) -> "JobFilter3":
        return cls(allowed_states=[])

    def fix_assigned_slave_name(self, slave_infos: List[SlaveInfo2]) -> "JobFilter3":
        """
        :param slave_infos: list of current slaves
        :return: A copy of this JobFilter3, with the assigned_slave_name replaced by the slave name,
                 if it matches the slave. That means that if it matches an alias,
                 it will now match the slave name instead. As the slave name can be matched against, this is handy.
        """
        if not slave_infos:
            slave_infos = []
        fixed_assigned_slave_name = []
        
        for asn in self.assigned_slave_name:
            for slave_info in slave_infos:
                if slave_info.match_name(asn):
                    fixed_assigned_slave_name.append(slave_info.name)

        if not fixed_assigned_slave_name:
            # If there are no matching slave info's at all, do not fix anything. This will cause an empty result.
            fixed_assigned_slave_name = self.assigned_slave_name
            # return self

        return JobFilter3(
            cluster_id=self.cluster_id,
            allowed_states=self.allowed_states,
            user_urn=self.user_urn,
            user_name=self.user_name,
            project_urn=self.project_urn,
            project_name=self.project_name,
            assigned_slave_name=fixed_assigned_slave_name,
            assigned_slave_instance_id=self.assigned_slave_instance_id,
            interactive=self.interactive,
            waste=self.waste,
        )

    def to_params(self) -> dict:
        base = self.to_dict()
        res = {}
        for key, val in base.items():
            res[snakecase(key)] = val
        if self.allowed_states:
            res["allowed_states"] = ",".join(
                list(map(lambda state: state.name, self.allowed_states))
            )
        return res

    @classmethod
    def from_params(
        cls, params: dict
    ) -> "JobFilter3":
        def _process_bool_arg(
            args: dict, key, default: Optional[bool] = None
        ) -> Optional[bool]:
            value = args.pop(key, None)  # Note: this changes args!
            if value is None:
                return default
            if value == "":
                return True
            if str(value).lower() in ["true", "t", "1", "yes"]:
                return True
            if str(value).lower() in ["false", "f", "0", "no"]:
                return False
            return default

        params = dict(params)  # Shallow copy. (This might be an ImmutableMultiDict.)

        # Remove old params no longer supported
        for ignored_key in (
            "max_hours",
            "max_seconds",
            "page",
            "page_size",
            "sort",
            "max_count",
            "empty_cluster_id",
            "cpu_sharing_jobs",
            "max_system_memory_mb",
            "max_gpu_count",
            "max_cpu_count",
            "other_user_running",
            "max_duration_s",
            "slave_cuda_version",
            "slave_gpu_models",
        ):
            params.pop(ignored_key, None)

        # translate backward compatible parameters
        for old, new in (
            ("userurn", "user_urn"),
            ("username", "user_name"),
            ("projecturn", "project_urn"),
            ("projectname", "project_name"),
        ):
            backward_compat_version = params.pop(old, None)
            if params.get(new, None) is None and backward_compat_version:
                params[new] = backward_compat_version

        allowed_states_filter = params.get(
            "allowed_states", None
        )  # overrules pending, finished, running and deleted if present
        pending_filter = _process_bool_arg(params, "pending", default=False)
        finished_filter = _process_bool_arg(params, "finished", default=False)
        running_filter = _process_bool_arg(params, "running", default=False)
        deleted_filter = _process_bool_arg(params, "deleted", default=False)

        # If nothing is filtered, show all states, except delete
        if (
            not pending_filter
            and not finished_filter
            and not running_filter
            and not deleted_filter
        ):
            pending_filter = True
            finished_filter = True
            running_filter = True

        allowed_states = []
        if allowed_states_filter:
            try:
                states_str_list = list(allowed_states_filter.strip().split(","))
                states_str_list = [s.strip() for s in states_str_list]
                # backward compatible: ignore TRANSFER
                allowed_states = [
                    JobStatus[s] for s in states_str_list if s != "TRANSFER"
                ]
            except Exception:
                raise ValueError(
                    'Invalid state in parameter allowed_states="{}"'.format(
                        allowed_states_filter
                    )
                )
        else:
            if pending_filter:
                allowed_states.append(JobStatus.ONHOLD)
                allowed_states.append(JobStatus.QUEUED)
            if finished_filter:
                allowed_states.append(JobStatus.FINISHED)
                allowed_states.append(JobStatus.FAILED)
                allowed_states.append(JobStatus.CANCELLED)
                allowed_states.append(JobStatus.HALTED)
            if running_filter:
                allowed_states.append(JobStatus.RUNNING)
                allowed_states.append(JobStatus.STARTING)
                allowed_states.append(JobStatus.MUSTHALT)
                allowed_states.append(JobStatus.HALTING)
            if deleted_filter:
                allowed_states.append(JobStatus.DELETED)

        res = {}
        for key, val in params.items():
            translated_key = camelcase(key)
            val = val.split(",")
            if translated_key == "clusterId" and val:
                res[translated_key] = list(map(int, val))
            elif translated_key == "reservationId" and val:
                res[translated_key] = val[0] if isinstance(val, list) else val
            elif translated_key in ("interactive", "waste") and val:
                assert val[0] in ('false', 'true'), f"value for param {translated_key} is not true/false: {val[0]!r}"
                res[translated_key] = val[0] == 'true'
            else:
                res[translated_key] = val
        if allowed_states:
            res["allowedStates"] = list(map(lambda state: state.name, allowed_states))
        return JobFilter3.from_dict(res)


@dataclass
class JobSort:
    column: str
    ascending: bool = True


VALID_SORT_COLUMNS = [
    "project_name",
    "user_name",
    "name",
    "waste",
    "tallyIncrement",
    "status",
    "gpus",
    "cpus",
    "cpuMemoryGb",
    "updated",
    "created",
    "start_date",
    "end_date",
    "cluster_id",
    "runhost",
]


def parse_sort_param(sort: Optional[str]):
    if not sort:
        return None
        
    sort_parts = sort.split(",")

    result = []

    for part in sort_parts:
        descending = part[0] in ["+", "-"] and part[0] == "-"
        part = part[1:] if part[0] in ["+", "-"] else part

        if part not in VALID_SORT_COLUMNS:
            raise ValueError(f"Unknown column name: {part}")

        result.append(JobSort(part, not descending))

    return result


T = TypeVar("T")


def as_optional_list(value: Union[None, T, List[T]]):
    if value is None:
        return None
    else:
        return as_list(value)


def as_list(value: Union[T, List[T]]):
    if value is None:
        return None
    elif isinstance(list, value):
        return value
    else:
        return [value]
