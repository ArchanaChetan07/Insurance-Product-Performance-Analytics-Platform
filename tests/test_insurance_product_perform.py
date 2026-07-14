"""Unit tests for insurance medallion pipeline + legacy analytics helpers."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from insurance_pipeline.bronze import build_bronze, load_raw_claims
from insurance_pipeline.gold import build_gold
from insurance_pipeline.paths import RAW_CLAIMS_XLSX, ROOT
from insurance_pipeline.qc import apply_qc
from insurance_pipeline.run import run_pipeline

# ---------------------------------------------------------------------------
# Legacy portfolio smoke tests (synthetic fixtures) — retained intentionally
# ---------------------------------------------------------------------------


class TestInsuranceDataProcessing:
    def test_premium_column_exists(self):
        df = pd.DataFrame({"age": [25, 35], "premium": [1200.0, 1800.0], "claims": [0, 1]})
        assert "premium" in df.columns

    def test_negative_premiums_removed(self):
        df = pd.DataFrame({"premium": [1200, -50, 1800, 0]})
        df_clean = df[df["premium"] > 0]
        assert (df_clean["premium"] <= 0).sum() == 0

    def test_age_binning(self):
        ages = pd.Series([22, 35, 45, 60, 70])
        bins = pd.cut(ages, bins=[0, 30, 45, 60, 100], labels=["young", "mid", "senior", "elder"])
        assert bins[0] == "young"
        assert bins[4] == "elder"

    def test_claim_rate_calculation(self):
        df = pd.DataFrame({"claims": [0, 1, 0, 0, 1, 1]})
        rate = df["claims"].mean()
        assert abs(rate - 0.5) < 0.01

    def test_no_duplicate_policies(self):
        df = pd.DataFrame({"policy_id": [1, 2, 3, 2], "premium": [100, 200, 300, 200]})
        df_unique = df.drop_duplicates("policy_id")
        assert len(df_unique) == 3


class TestPerformanceAnalytics:
    def test_regression_r2_positive(self):
        np.random.seed(42)
        X = np.random.rand(200, 4)
        y = X[:, 0] * 5000 + X[:, 1] * 2000 + np.random.randn(200) * 100
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        r2 = r2_score(y_test, model.predict(X_test))
        assert r2 > 0

    def test_profit_loss_computation(self):
        premiums = np.array([1200, 1500, 900])
        claims = np.array([800, 2000, 0])
        profit = premiums - claims
        assert profit[0] > 0
        assert profit[1] < 0


# ---------------------------------------------------------------------------
# Real medallion pipeline tests against committed sample data
# ---------------------------------------------------------------------------


class TestMedallionPipeline:
    def test_raw_workbook_present(self):
        assert RAW_CLAIMS_XLSX.exists()

    def test_raw_sheet1_shape(self):
        raw = load_raw_claims()
        assert len(raw) == 20511
        assert "CLAIM_NUMBER" in raw.columns
        assert "AMOUNT" in raw.columns

    def test_bronze_matches_verified_row_count(self):
        bronze, stats = build_bronze()
        assert stats["bronze_rows"] == 18928
        assert stats["rejected_rows"] == 1583
        assert abs(stats["reject_rate"] - 1583 / 20511) < 1e-9
        assert len(bronze) == 18928
        assert "COMPANY_NORMALIZED" in bronze.columns
        assert "DAYS_TO_NOTICE" in bronze.columns

    def test_qc_auto_pass_and_staging_projection(self):
        bronze, _ = build_bronze()
        staging, failed, stats = apply_qc(bronze)
        assert stats["staging_rows"] + stats["failed_rows"] == stats["bronze_rows"]
        # Non-positive AMOUNT is the dominant QC fail mode on this dataset
        assert stats["staging_rows"] == 11885
        assert stats["failed_rows"] == 7043
        assert stats["auto_pass_rate"] == pytest.approx(11885 / 18928)
        assert "AMOUNT" in staging.columns
        assert "ACCIDENT_STATE" in staging.columns
        assert (failed["ERROR_REASON"] == "Invalid Amount").all()

    def test_qc_flags_blank_policy(self):
        bronze, _ = build_bronze()
        # Start from rows that already auto-pass amount QC so only POLICY fails
        ok = bronze[bronze["AMOUNT"] > 0].head(5).copy()
        ok.loc[ok.index[0], "POLICY"] = ""
        staging, failed, stats = apply_qc(ok)
        assert stats["failed_rows"] == 1
        assert "Missing Policy Number" in failed.iloc[0]["ERROR_REASON"]
        assert len(staging) == 4

    def test_gold_aggregates_month_state(self):
        bronze, _ = build_bronze()
        staging, _, _ = apply_qc(bronze)
        trends, by_company, stats = build_gold(staging)
        assert stats["claim_count_sum"] == len(staging)
        assert stats["states"] >= 4
        assert {"CLAIM_MONTH", "ACCIDENT_STATE", "TOTAL_CLAIMS", "AVERAGE_CLAIM", "CLAIM_COUNT"} <= set(
            trends.columns
        )
        assert {"COMPANY", "ACCIDENT_STATE", "TOTAL_CLAIMED_AMOUNT"} <= set(by_company.columns)

    def test_pipeline_end_to_end_writes_metrics(self):
        report = run_pipeline(write=True)
        metrics = ROOT / "Data" / "processed" / "pipeline_metrics.json"
        assert metrics.exists()
        payload = json.loads(metrics.read_text(encoding="utf-8"))
        assert payload["headline"]["bronze_claims"] == 18928
        assert report["headline"]["qc_auto_pass_rate_pct"] == pytest.approx(62.79, abs=0.01)
        assert report["headline"]["raw_rejected_rows"] == 1583
        assert (ROOT / "Data" / "processed" / "gold" / "claims_gold.csv").exists()
