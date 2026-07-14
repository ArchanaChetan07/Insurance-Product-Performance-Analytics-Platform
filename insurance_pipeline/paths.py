"""Repo-relative path helpers."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
STAGING = PROCESSED / "staging"
QC_FAILED = PROCESSED / "qc_failed"
GOLD = PROCESSED / "gold"

RAW_CLAIMS_XLSX = RAW / "NTA_MTC_Claims_Synthetic_Data.xlsx"
BRONZE_CSV = PROCESSED / "claims_cleaned.csv"
BRONZE_PARQUET = PROCESSED / "claims_cleaned.parquet"
STAGING_CSV = STAGING / "claims_staging.csv"
STAGING_PARQUET = STAGING / "claims_staging.parquet"
FAILED_CSV = QC_FAILED / "claims_failed.csv"
FAILED_PARQUET = QC_FAILED / "claims_failed.parquet"
GOLD_TRENDS_CSV = GOLD / "claims_gold.csv"
GOLD_TRENDS_PARQUET = GOLD / "claims_gold.parquet"
GOLD_COMPANY_CSV = GOLD / "claims_cleaned.csv"


def ensure_dirs() -> None:
    for path in (RAW, PROCESSED, STAGING, QC_FAILED, GOLD):
        path.mkdir(parents=True, exist_ok=True)
