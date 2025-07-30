from dataclasses import dataclass
from stringcase import camelcase

from dataclass_dict_convert import dataclass_dict_convert,dataclass_auto_type_check


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass_auto_type_check
@dataclass(frozen=True)
class ActiveJobsCounts:
    """Returns the number of jobs for a given cluster (and optionally for a specific slave) in any of the 'active' job states."""
    onhold: int
    queued: int
    assigned: int
    starting: int
    running: int
    musthalt: int
    halting: int

    @classmethod
    def zero(cls):
        """Returns an ActiveJobsCounts with all counters on zero"""
        return cls(0,0,0,0,0,0,0)