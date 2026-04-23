from enum import Enum


class DocumentType(str, Enum):
    EQ_LIST = "eq_list"
    PID = "pid"
    DATASHEET = "datasheet"


class ComparisonStatus(str, Enum):
    MATCHED = "matched"
    MISMATCH = "mismatch"
    MISSING_SOURCE = "missing_source"
    MISSING_TARGET = "missing_target"
    UNREVIEWED = "unreviewed"