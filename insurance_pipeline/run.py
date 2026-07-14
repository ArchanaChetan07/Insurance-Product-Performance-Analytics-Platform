"""CLI entry: run raw → bronze → staging/qc_failed → gold."""

from __future__ import annotations

import argparse
import json

from insurance_pipeline.bronze import build_bronze, write_bronze
from insurance_pipeline.gold import build_gold, write_gold
from insurance_pipeline.paths import PROCESSED, ensure_dirs
from insurance_pipeline.qc import apply_qc, write_qc_outputs


def run_pipeline(write: bool = True) -> dict:
    ensure_dirs()
    bronze, bronze_stats = build_bronze()
    staging, failed, qc_stats = apply_qc(bronze)
    trends, by_company, gold_stats = build_gold(staging)

    report = {
        "bronze": bronze_stats,
        "qc": qc_stats,
        "gold": gold_stats,
        "headline": {
            "bronze_claims": bronze_stats["bronze_rows"],
            "raw_reject_rate_pct": round(100 * bronze_stats["reject_rate"], 2),
            "raw_rejected_rows": bronze_stats["rejected_rows"],
            "qc_auto_pass_rate_pct": round(100 * qc_stats["auto_pass_rate"], 2),
            "staging_rows": qc_stats["staging_rows"],
            "qc_failed_rows": qc_stats["failed_rows"],
            "gold_states": gold_stats["states"],
            "gold_months": gold_stats["months"],
            "gold_claim_count": gold_stats["claim_count_sum"],
        },
    }

    if write:
        write_bronze(bronze)
        write_qc_outputs(staging, failed)
        write_gold(trends, by_company)
        out = PROCESSED / "pipeline_metrics.json"
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run insurance medallion ELT pipeline")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute metrics without writing Data/processed outputs",
    )
    args = parser.parse_args(argv)
    report = run_pipeline(write=not args.dry_run)
    print(json.dumps(report["headline"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
