import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum

from typing import Optional, List, Union, Dict, Any

from stringcase import camelcase

from dataclass_dict_convert import dataclass_dict_convert, dataclass_copy_method, dataclass_auto_type_check


def _remove_total_power_stats(d: Dict) -> Dict:
    # We always recalculate the verdict
    if 'total_mWh_used' in d:
        del d['total_mWh_used']
    if 'average_mW_used' in d:
        del d['average_mW_used']
    return d


def milli_watt_friendly_camelcase(i: str) -> str:
    if i.endswith('_mWh_used'):
        return camelcase(i[:-len('_mWh_used')]) + 'mWhUsed'
    if i.endswith('_mW_used'):
        return camelcase(i[:-len('_mW_used')]) + 'mWUsed'
    return camelcase(i)


# 2 seperate usage statistics:
#   "cpu" -> CpuUsageStatistics -> not just CPU, but everything but GPU -> reported by docker etc
#   "gpu"  -> GPUUsageStatistics -> GPU -> reported by nv libraries
# Combined in GPULabUsageStatistics

@dataclass_dict_convert(
    dict_letter_case=milli_watt_friendly_camelcase, preprocess_from_dict=_remove_total_power_stats,
    extra_field_defaults={"mem_usage_byte": 0},  # TODO remove once all slaves are new enough
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class ContainerUsageStatistics:
    first_time: datetime.datetime
    last_time: datetime.datetime
    agg_period_ns: int
    cpu_count: int
    cpu_usage: float  # in nr CPU's, so between 0 and cpu_count
    cpu_usage_total_ns: int
    cpu_usage_kernelmode_ns: int
    cpu_usage_usermode_ns: int
    max_pid_count: int
    mem_limit_byte: int
    mem_usage_byte: int
    mem_max_usage_byte: int
    network_rx_byte: int
    network_tx_byte: int
    # power measurements
    #    (None if not (yet) available/implemented)
    #    (and for backward compatibility default is 0.0)
    #
    # Power used by the host machine itself (not CPU or GPU) during period between first_time and last_time.
    #   Proportional to number of cpu's of the total used.
    #   (Might be proportional to something else in future versions, but idea is the same.)
    host_total_mWh_used: Optional[int] = None  # total Wh (Watt hour)
    host_average_mW_used: Optional[int] = None  # average W (Watt)
    #
    # Power used by all CPU's of this job, during this job.
    cpu_total_mWh_used: Optional[int] = None  # total Wh (Watt hour)
    cpu_average_mW_used: Optional[int] = None  # average W (Watt)
    #
    # Power used by all non-GPU resources of this job during this job. (= host_* and cpu_* power stats added)
    total_mWh_used: Optional[int] = None  # total Wh (Watt hour)
    average_mW_used: Optional[int] = None  # average W (Watt)

    def __post_init__(self):
        # we always recalculate the verdict
        super().__setattr__('total_mWh_used', self._calc_total_mWh_used())
        super().__setattr__('average_mW_used', self._calc_average_mW_used())

    def is_invalid(self):
        return self.agg_period_ns <= 0 \
               or self.cpu_count <= 0 \
               or self.first_time <= datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    def to_timeseriesdb_entry(self) -> dict:
        # self.total_mWh_used and self.average_mmW_used are not included in timeseries DB!
        return {
            'sample_period_ns': self.agg_period_ns,
            'pid_count': self.max_pid_count,
            'cpu_usage_total_ns': self.cpu_usage_total_ns,
            'cpu_usage_kernelmode_ns': self.cpu_usage_kernelmode_ns,
            'cpu_usage_usermode_ns': self.cpu_usage_usermode_ns,
            'mem_usage_byte': self.mem_usage_byte,  # Was mem_max_usage_byte before, but now we have mem_usage_byte and we use that.
            # 'mem_max_usage_byte': self.mem_max_usage_byte,
            'mem_limit_byte': self.mem_limit_byte,
            'cpu_usage': self.cpu_usage,
            'cpu_usage_percent_all': ((self.cpu_usage * 100.0) / self.cpu_count) if self.cpu_count > 0 else -1,  # float
            'cpu_count': self.cpu_count,
            'network_rx_byte': self.network_rx_byte,
            'network_tx_byte': self.network_tx_byte,
            "host_total_mWh_used": self.host_total_mWh_used,
            "host_average_mW_used": self.host_average_mW_used,
            "cpu_total_mWh_used": self.cpu_total_mWh_used,
            "cpu_average_mW_used": self.cpu_average_mW_used,
        }

    @classmethod
    def invalid(cls):
        return ContainerUsageStatistics(
            first_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            last_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            agg_period_ns=-1,
            cpu_count=-1,
            cpu_usage=-1.0,
            cpu_usage_total_ns=-1,
            cpu_usage_kernelmode_ns=-1,
            cpu_usage_usermode_ns=-1,
            max_pid_count=-1,
            mem_limit_byte=-1,
            mem_usage_byte=-1,
            mem_max_usage_byte=-1,
            network_rx_byte=-1,
            network_tx_byte=-1,
            host_total_mWh_used=None,
            host_average_mW_used=None,
            cpu_total_mWh_used=None,
            cpu_average_mW_used=None,
            total_mWh_used=None,
            average_mW_used=None,
        )

    def _calc_total_mWh_used(self) -> Optional[int]:
        if self.host_total_mWh_used or self.cpu_total_mWh_used:
            return (self.host_total_mWh_used or 0.0) + (self.cpu_total_mWh_used or 0.0)
        else:
            return None

    def _calc_average_mW_used(self) -> Optional[int]:
        if self.host_average_mW_used or self.cpu_average_mW_used:
            return (self.host_average_mW_used or 0.0) + (self.cpu_average_mW_used or 0.0)
        else:
            return None


@dataclass_dict_convert(dict_letter_case=milli_watt_friendly_camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GpuUsageStatistics:
    gpu_count: int
    average_utilization: float  # in number of GPU's, so between 0 and gpu_count
    average_mem_utilization: float  # in number of GPU's, so between 0 and gpu_count
    # power measurements
    #    (None if not (yet) available/implemented)
    #    (and for backward compatibility default is 0.0)
    #
    # Power used by all GPU's during the relevant period.
    total_mWh_used: Optional[int] = None  # total Wh (Watt hour)
    average_mW_used: Optional[int] = None  # average W (Watt)

    @classmethod
    def empty(cls):
        return GpuUsageStatistics(0, 0.0, 0.0, 0, 0)


# DEPRECATED
@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class WasteStat:
    # These stats are all averaged over time
    cpu_usage_perc: float  # percent of all CPUs used (average)
    cpu_memory_perc: float  # percent of CPU mem used (average)
    wasted: bool  # is this stat considered "waste of resources"?
    gpu_usage_perc: Optional[float] = None  # percent of all GPU used (average)
    gpu_active_processes_per_gpu: Optional[float] = None  # number of active processes per GPU (average)
    wasted_reason: List[str] = field(default_factory=list)

    @classmethod
    def empty(cls) -> 'WasteStat':
        return cls(
            cpu_usage_perc=0.0,
            cpu_memory_perc=0.0,
            wasted=False,
            gpu_usage_perc=None,
            gpu_active_processes_per_gpu=None,
        )


class WasteVerdict(Enum):
    GOOD = 'Good'  # Job is not wasting resources (yet, for running jobs)
    UNCERTAIN = 'Uncertain'  # Job might be wasting resources, or might not
    WASTE = 'Waste'  # Job is wasting resources
    SHORT = 'Short'  # Job was too short to verdict. It's OK if short test/failed jobs waste resources.
    UNDECIDED = 'Undecided'  # Too soon to tell if job wastes resources


def _remove_verdict_explanation(d: Dict) -> Dict:
    # We remove the deprecated verdictExplanation
    if 'verdictExplanation' in d:
        del d['verdictExplanation']
    return d


class WasteFlag(Enum):
    RED = 'Red Flag'        # Certainly unacceptable resource waste
    ORANGE = 'Orange Flag'  # Quite likely unacceptable resource waste
    YELLOW = 'Yellow Flag'  # Resource waste, but probably not unacceptable

    @classmethod
    def find_case_insensitive(cls, searched: str) -> 'WasteFlag':
        for cur_name, cur_status in WasteFlag.__members__.items():  # type: str, WasteFlag
            assert WasteFlag[cur_name] == cur_status
            assert WasteFlag[cur_name].name == cur_name
            if cur_name.lower() == searched.lower():
                return cur_status
            if cur_status.value.lower() == searched.lower():
                return cur_status
        raise ValueError(f'WasteFlag "{searched}" does not exist')


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class WasteFlagInfo:
    flag: WasteFlag
    explanation: str


@dataclass_dict_convert(dict_letter_case=camelcase,
                        preprocess_from_dict=_remove_verdict_explanation)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class WasteReview:  # AKA WasteReport2, which replaces the legacy WasteReport
    updated: str  # date in RFC3339 format
    final: bool  # this is the final report, as the job has finished. It can include details intermediate reports don't.
    verdict: WasteVerdict  # is this job wasting resources, or not?
    flags: List[WasteFlagInfo] = field(default_factory=list)  # Why is this job wasting resources? (empty if not wasting)
    debug: Dict[str, Union[bool, int, float, str]] = field(default_factory=dict)
    # verdict_explanation: List[str] = field(default_factory=list) # DEPRECATED Why is this job wasting resources? (empty if not wasting)


@dataclass_dict_convert(dict_letter_case=milli_watt_friendly_camelcase,
                        preprocess_from_dict=_remove_total_power_stats)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GPULabUsageStatistics:
    container_statistics: ContainerUsageStatistics
    gpu_statistics: GpuUsageStatistics
    #
    # power measurements
    #    (None if not (yet) available/implemented)
    #    (and for backward compatibility default is 0.0)
    #
    # Power used by all resource of this job (GPU + CPU + host) during period between
    # container_statistics.first_time and container_statistics.last_time.
    total_mWh_used: Optional[int] = None  # total Wh (Watt hour)
    average_mW_used: Optional[int] = None  # average W (Watt)

    def __post_init__(self):
        # we always recalculate the verdict
        super().__setattr__('total_mWh_used', self._calc_total_mWh_used())
        super().__setattr__('average_mW_used', self._calc_average_mW_used())

    def _calc_total_mWh_used(self) -> Optional[int]:
        if self.container_statistics.total_mWh_used or self.gpu_statistics.total_mWh_used:
            return (self.container_statistics.total_mWh_used or 0) + (self.gpu_statistics.total_mWh_used or 0)
        else:
            return None

    def _calc_average_mW_used(self) -> Optional[int]:
        if self.container_statistics.average_mW_used or self.gpu_statistics.average_mW_used:
            return (self.container_statistics.average_mW_used or 0) + (self.gpu_statistics.average_mW_used or 0)
        else:
            return None


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GpuInfo:
    index: int
    uuid: str
    serial: str
    name: str
    brand: str
    minor_number: int
    board_id: int
    bridge_chip_info: str
    is_multi_gpu_board: bool
    max_pcie_link_generation: int
    max_pcie_link_width: int
    vbios_version: str

# example:
#               board_id: 768,
#               brand: "GeForce",
#               bridge_chip_info: "N/A",
#               index: 0,
#               is_multi_gpu_board: false,
#               max_pcie_link_generation: 3,
#               max_pcie_link_width: 16,
#               minor_number: 0,
#               name: "GeForce GTX 980",
#               serial: "N/A",
#               uuid: "GPU-8a56a4bc-e184-a047-2620-be19fdf913d5",
#               vbios_version: "84.04.31.00.29"


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    direct_fields=['cuda_version_minor'],
)
@dataclass(frozen=True)
@dataclass_auto_type_check
@dataclass_copy_method
class GpuOverview:
    cuda_version_full: str  # from resource manager
    cuda_version_int: int  # from nv utils
    cuda_version_major: int
    cuda_version_minor: Union[int, float]
    driver_version: str
    nvml_version: str
    gpus: List[GpuInfo]

# Example:
#     cuda_driver_version_full: "10.2.0",
#     cuda_driver_version_int: 10020,
#     cuda_driver_version_major: 10,
#     cuda_driver_version_minor: 2, // or 2.0 !
#     driver_version: "440.33.01",
#     nvml_version: "10.440.33.01",
#     gpu: [...]
