from enum import Enum


class ApplicantType(str, Enum):
    INDIVIDUAL = "individual"
    SMALL_BUSINESS = "small_business"


class ExtractionStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class ConditionStatus(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class OverallStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


class VerificationStatus(str, Enum):
    SYNTHETIC_DEMO = "synthetic_demo"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
