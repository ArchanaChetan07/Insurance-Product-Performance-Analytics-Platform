"""Bronze layer: raw Excel → cleaned claims fact table."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from insurance_pipeline.paths import (
    BRONZE_CSV,
    BRONZE_PARQUET,
    RAW_CLAIMS_XLSX,
    ensure_dirs,
)

ESSENTIAL_BRONZE = ["CLAIM_NUMBER", "POLICY", "AMOUNT", "DATE"]


def load_raw_claims(path: Path | None = None) -> pd.DataFrame:
    """Load Sheet1 from the synthetic NTA/MTC claims workbook."""
    xlsx = path or RAW_CLAIMS_XLSX
    if not xlsx.exists():
        raise FileNotFoundError(f"Raw claims file not found: {xlsx}")
    df = pd.read_excel(xlsx, sheet_name="Sheet1", engine="openpyxl")
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.upper()
    return df


def normalize_company(name: object) -> str:
    text = str(name).strip().upper()
    if "WORLD SPECIALTY" in text:
        return "WORLD SPECIALTY INSURANCE CO"
    return text


def build_bronze(raw: pd.DataFrame | None = None) -> tuple[pd.DataFrame, dict]:
    """
    Clean raw claims into bronze.

    Rule verified against committed artifact: drop rows with null
    CLAIM_NUMBER / POLICY / AMOUNT / DATE after parsing → 18,928 rows.
    """
    if raw is None:
        raw = load_raw_claims()
    bronze = raw.copy()
    for col in ("DATE_OF_LOSS", "NOTICE_DATE", "DATE"):
        if col in bronze.columns:
            bronze[col] = pd.to_datetime(bronze[col], errors="coerce")
    bronze["AMOUNT"] = pd.to_numeric(bronze["AMOUNT"], errors="coerce")

    raw_count = len(bronze)
    mask_ok = ~bronze[ESSENTIAL_BRONZE].isna().any(axis=1)
    rejected = int((~mask_ok).sum())
    bronze = bronze.loc[mask_ok].copy()

    bronze["DAYS_TO_NOTICE"] = (
        bronze["NOTICE_DATE"] - bronze["DATE_OF_LOSS"]
    ).dt.days
    bronze["MONTH_YEAR"] = bronze["DATE"].dt.to_period("M").astype(str)
    bronze["COMPANY_NORMALIZED"] = bronze["COMPANY"].map(normalize_company)

    # Homogenize object columns for Parquet (source mixes int/str state codes)
    for col in bronze.columns:
        if bronze[col].dtype == object:
            bronze[col] = bronze[col].map(
                lambda x: "" if x is None or (isinstance(x, float) and pd.isna(x)) else str(x)
            )

    stats = {
        "raw_rows": raw_count,
        "bronze_rows": len(bronze),
        "rejected_rows": rejected,
        "reject_rate": rejected / raw_count if raw_count else 0.0,
        "amount_sum": float(bronze["AMOUNT"].sum()),
    }
    return bronze, stats


def write_bronze(bronze: pd.DataFrame) -> None:
    ensure_dirs()
    bronze.to_csv(BRONZE_CSV, index=False)
    bronze.to_parquet(BRONZE_PARQUET, index=False)
