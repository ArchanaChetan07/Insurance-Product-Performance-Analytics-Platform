"""Gold layer: month×state and company×state KPI aggregates."""

from __future__ import annotations

import pandas as pd

from insurance_pipeline.paths import (
    GOLD_COMPANY_CSV,
    GOLD_TRENDS_CSV,
    GOLD_TRENDS_PARQUET,
    ensure_dirs,
)


def build_gold(staging: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Aggregate staging into gold KPI tables."""
    df = staging.copy()
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
    df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")
    df = df.dropna(subset=["DATE", "AMOUNT", "ACCIDENT_STATE"])
    df["CLAIM_MONTH"] = df["DATE"].dt.to_period("M").astype(str)

    trends = (
        df.groupby(["CLAIM_MONTH", "ACCIDENT_STATE"], as_index=False)
        .agg(
            TOTAL_CLAIMS=("AMOUNT", "sum"),
            AVERAGE_CLAIM=("AMOUNT", "mean"),
            CLAIM_COUNT=("AMOUNT", "count"),
        )
        .sort_values(["CLAIM_MONTH", "ACCIDENT_STATE"])
        .reset_index(drop=True)
    )

    company_col = "COMPANY" if "COMPANY" in df.columns else "COMPANY_NORMALIZED"
    by_company = (
        df.groupby([company_col, "ACCIDENT_STATE"], as_index=False)["AMOUNT"]
        .sum()
        .rename(columns={"AMOUNT": "TOTAL_CLAIMED_AMOUNT", company_col: "COMPANY"})
    )

    stats = {
        "gold_trend_rows": len(trends),
        "gold_company_rows": len(by_company),
        "states": int(df["ACCIDENT_STATE"].nunique()),
        "months": int(df["CLAIM_MONTH"].nunique()),
        "total_claims_amount": float(trends["TOTAL_CLAIMS"].sum()) if len(trends) else 0.0,
        "claim_count_sum": int(trends["CLAIM_COUNT"].sum()) if len(trends) else 0,
    }
    return trends, by_company, stats


def write_gold(trends: pd.DataFrame, by_company: pd.DataFrame) -> None:
    ensure_dirs()
    trends.to_csv(GOLD_TRENDS_CSV, index=False)
    trends.to_parquet(GOLD_TRENDS_PARQUET, index=False)
    by_company.to_csv(GOLD_COMPANY_CSV, index=False)
