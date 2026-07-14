"""Silver layer: QC gate → staging vs qc_failed (+ HITL queue)."""

from __future__ import annotations

import pandas as pd

from insurance_pipeline.paths import (
    FAILED_CSV,
    FAILED_PARQUET,
    STAGING_CSV,
    STAGING_PARQUET,
    ensure_dirs,
)

# Columns that must be present and non-null for automatic staging admission.
ESSENTIAL_QC = [
    "CLAIM_NUMBER",
    "POLICY",
    "AMOUNT",
    "DATE",
    "COMPANY",
    "ACCIDENT_STATE",
]


def _blank_policy(series: pd.Series) -> pd.Series:
    return series.isna() | (series.astype(str).str.strip() == "") | (
        series.astype(str).str.strip().str.upper() == "NAN"
    )


def apply_qc(bronze: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Split bronze into staging (auto-pass) and qc_failed (HITL queue).

    Failures: null essential fields, blank POLICY, non-positive AMOUNT.
    """
    df = bronze.copy()
    reasons: list[str] = []

    missing = df[ESSENTIAL_QC].isna().any(axis=1)
    blank_pol = _blank_policy(df["POLICY"])
    bad_amt = ~(pd.to_numeric(df["AMOUNT"], errors="coerce") > 0)

    fail_mask = missing | blank_pol | bad_amt
    for idx in df.index:
        if not fail_mask.loc[idx]:
            reasons.append("")
            continue
        parts = []
        if blank_pol.loc[idx] or pd.isna(df.loc[idx, "POLICY"]):
            parts.append("Missing Policy Number")
        if pd.isna(df.loc[idx, "AMOUNT"]) or not (df.loc[idx, "AMOUNT"] > 0):
            parts.append("Invalid Amount")
        if pd.isna(df.loc[idx, "DATE"]):
            parts.append("Missing Date")
        if pd.isna(df.loc[idx, "COMPANY"]):
            parts.append("Missing Company")
        if pd.isna(df.loc[idx, "ACCIDENT_STATE"]):
            parts.append("Missing Accident State")
        if pd.isna(df.loc[idx, "CLAIM_NUMBER"]):
            parts.append("Missing Claim Number")
        reasons.append("; ".join(parts) if parts else "QC failure")

    df["ERROR_REASON"] = reasons
    passed = df.loc[~fail_mask].drop(columns=["ERROR_REASON"]).copy()
    failed = df.loc[fail_mask, ["CLAIM_NUMBER", "ERROR_REASON"]].copy()
    failed = failed.rename(columns={"CLAIM_NUMBER": "CLAIM_ID"})

    # Staging projection used by gold notebooks / Streamlit approve path
    staging_cols = [
        c
        for c in [
            "DATE",
            "AMOUNT",
            "COMPANY",
            "ACCIDENT_STATE",
            "CLAIM_NUMBER",
            "POLICY",
            "TYPE",
            "COVERAGE",
            "DAYS_TO_NOTICE",
            "MONTH_YEAR",
            "COMPANY_NORMALIZED",
        ]
        if c in passed.columns
    ]
    staging = passed[staging_cols].copy()
    if "CLAIM_NUMBER" in staging.columns:
        staging = staging.rename(columns={"CLAIM_NUMBER": "CLAIM_ID"})

    for col in staging.select_dtypes(include="object").columns:
        staging[col] = staging[col].astype(str)
    for col in failed.select_dtypes(include="object").columns:
        failed[col] = failed[col].astype(str)

    stats = {
        "bronze_rows": len(bronze),
        "staging_rows": len(staging),
        "failed_rows": len(failed),
        "auto_pass_rate": len(staging) / len(bronze) if len(bronze) else 0.0,
    }
    return staging, failed, stats


def write_qc_outputs(staging: pd.DataFrame, failed: pd.DataFrame) -> None:
    ensure_dirs()
    staging.to_csv(STAGING_CSV, index=False)
    staging.to_parquet(STAGING_PARQUET, index=False)
    failed.to_csv(FAILED_CSV, index=False)
    failed.to_parquet(FAILED_PARQUET, index=False)
