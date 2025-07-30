"""
PhysioNet Database Registry

Comprehensive registry of all PhysioNet databases with their metadata,
access requirements, and download configurations.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AccessType(str, Enum):
    """Types of access required for PhysioNet databases."""

    OPEN = "open"  # No credentials needed
    CREDENTIALED = "credentialed"  # PhysioNet account required
    PROTECTED = "protected"  # Special access approval needed


class DownloadMethod(str, Enum):
    """Methods for downloading datasets."""

    WGET = "wget"  # Direct HTTP download
    AWS_S3 = "aws_s3"  # AWS S3 sync (faster for large datasets)
    WFDB = "wfdb"  # WFDB Python library
    CUSTOM = "custom"  # Custom download logic


class DatabaseInfo(BaseModel):
    """Information about a PhysioNet database."""

    name: str = Field(..., description="Database identifier")
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Brief description")

    # Access configuration
    access_type: AccessType
    download_method: DownloadMethod
    base_url: Optional[str] = None
    s3_bucket: Optional[str] = None
    wfdb_database: Optional[str] = None

    # File structure
    expected_files: List[str] = Field(default_factory=list)
    main_tables: List[str] = Field(default_factory=list)

    # Metadata
    size_gb: Optional[float] = None
    patient_count: Optional[int] = None
    record_count: Optional[int] = None

    # Special handling
    requires_preprocessing: bool = False
    custom_converter: Optional[str] = None


# Comprehensive database registry
DATABASE_REGISTRY: Dict[str, DatabaseInfo] = {
    # Major critical care databases
    "mimic-iv": DatabaseInfo(
        name="mimic-iv",
        title="MIMIC-IV Clinical Database",
        description="Comprehensive clinical data from ICU patients at Beth Israel Deaconess Medical Center",
        access_type=AccessType.CREDENTIALED,
        download_method=DownloadMethod.AWS_S3,
        s3_bucket="physionet-open/mimiciv/2.2",
        main_tables=["patients", "admissions", "icustays", "chartevents", "labevents"],
        size_gb=45.0,
        patient_count=315460,
        expected_files=[
            "core/patients.csv.gz",
            "core/admissions.csv.gz",
            "icu/icustays.csv.gz",
        ],
    ),
    "mimic-iv-demo": DatabaseInfo(
        name="mimic-iv-demo",
        title="MIMIC-IV Clinical Database Demo",
        description="Demo subset of MIMIC-IV with 100 patients for testing and learning",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WGET,
        base_url="https://physionet.org/files/mimic-iv-demo/2.2/",
        main_tables=[
            "patients",
            "admissions",
            "labevents",
            "diagnoses_icd",
            "prescriptions",
            "procedures_icd",
            "transfers",
        ],
        size_gb=0.1,
        patient_count=100,
        expected_files=[
            "hosp/patients.csv.gz",
            "hosp/admissions.csv.gz",
            "hosp/labevents.csv.gz",
        ],
    ),
    "mimic-iii": DatabaseInfo(
        name="mimic-iii",
        title="MIMIC-III Clinical Database",
        description="De-identified health data from critical care patients",
        access_type=AccessType.CREDENTIALED,
        download_method=DownloadMethod.AWS_S3,
        s3_bucket="physionet-open/mimiciii/1.4",
        main_tables=["patients", "admissions", "icustays", "chartevents", "labevents"],
        size_gb=6.3,
        patient_count=46520,
    ),
    "eicu": DatabaseInfo(
        name="eicu",
        title="eICU Collaborative Research Database",
        description="Multi-center ICU data from 335 care units across the US",
        access_type=AccessType.CREDENTIALED,
        download_method=DownloadMethod.AWS_S3,
        s3_bucket="physionet-open/eicu-crd/2.0",
        main_tables=["patient", "admissiondx", "vitalperiodic", "lab"],
        size_gb=23.0,
        patient_count=200859,
    ),
    "eicu-demo": DatabaseInfo(
        name="eicu-demo",
        title="eICU Collaborative Research Database Demo",
        description="Demo version of the eICU database with over 2,500 ICU stays from 20 hospitals (2014-2015). Multi-center deidentified health data.",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WGET,
        base_url="https://physionet.org/files/eicu-crd-demo/2.0.1/",
        main_tables=["patient", "admissionDx", "lab", "vitalPeriodic", "medication"],
        size_gb=0.13,
        patient_count=2500,
        expected_files=["patient.csv.gz", "admissionDx.csv.gz", "lab.csv.gz"],
    ),
    # Waveform databases
    "mimic-iv-wfdb": DatabaseInfo(
        name="mimic-iv-wfdb",
        title="MIMIC-IV Waveforms",
        description="High-resolution waveform data from MIMIC-IV patients",
        access_type=AccessType.CREDENTIALED,
        download_method=DownloadMethod.WFDB,
        wfdb_database="mimic4wdb",
        size_gb=18000.0,  # 18TB!
        requires_preprocessing=True,
    ),
    "mimicdb": DatabaseInfo(
        name="mimicdb",
        title="MIMIC Database",
        description="Waveforms and vital signs from ICU patients",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WFDB,
        wfdb_database="mimicdb",
        size_gb=67.0,
    ),
    # ECG databases
    "mitdb": DatabaseInfo(
        name="mitdb",
        title="MIT-BIH Arrhythmia Database",
        description="Standard arrhythmia database with expert annotations",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WFDB,
        wfdb_database="mitdb",
        size_gb=0.022,
        record_count=48,
    ),
    "ptbdb": DatabaseInfo(
        name="ptbdb",
        title="PTB Diagnostic ECG Database",
        description="Clinical ECG database with diverse pathologies",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WFDB,
        wfdb_database="ptbdb",
        size_gb=5.5,
        record_count=549,
    ),
    "ptb-xl": DatabaseInfo(
        name="ptb-xl",
        title="PTB-XL ECG Database",
        description="Large publicly available electrocardiography dataset",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WGET,
        base_url="https://physionet.org/files/ptb-xl/1.0.3/",
        size_gb=13.8,
        record_count=21837,
    ),
    # Sleep databases
    "slpdb": DatabaseInfo(
        name="slpdb",
        title="MIT-BIH Polysomnographic Database",
        description="Sleep recordings with annotations",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WFDB,
        wfdb_database="slpdb",
        size_gb=2.1,
    ),
    # Maternal-fetal databases
    "adfecgdb": DatabaseInfo(
        name="adfecgdb",
        title="Abdominal and Direct Fetal ECG Database",
        description="Fetal ECG recordings from multiple sources",
        access_type=AccessType.OPEN,
        download_method=DownloadMethod.WFDB,
        wfdb_database="adfecgdb",
        size_gb=0.15,
    ),
    # Add more databases as needed...
    # This registry can be extended to include all 200+ PhysioNet databases
}


def get_database_info(db_name: str) -> Optional[DatabaseInfo]:
    """Get database information by name."""
    return DATABASE_REGISTRY.get(db_name)


def list_databases_by_access_type(access_type: AccessType) -> List[DatabaseInfo]:
    """List all databases that require a specific access type."""
    return [db for db in DATABASE_REGISTRY.values() if db.access_type == access_type]


def list_databases_by_size(max_size_gb: float) -> List[DatabaseInfo]:
    """List databases under a certain size threshold."""
    return [
        db
        for db in DATABASE_REGISTRY.values()
        if db.size_gb is not None and db.size_gb <= max_size_gb
    ]


def estimate_storage_requirements(db_names: List[str]) -> float:
    """Estimate total storage requirements for a list of databases."""
    total_gb = 0.0
    for name in db_names:
        db_info = get_database_info(name)
        if db_info and db_info.size_gb:
            total_gb += db_info.size_gb
    return total_gb
