"""QC Failed Claims Review — approve fixed rows into staging (repo-relative paths)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Data" / "processed"
FAILED_FILE = BASE / "qc_failed" / "claims_failed.csv"
STAGING_FILE = BASE / "staging" / "claims_staging.csv"

st.set_page_config(page_title="QC Failed Claims Review", layout="wide")
st.title("QC Failed Claims Review")
st.caption("Review, fix, and approve failed claims into the staging (silver) layer")

if not FAILED_FILE.exists():
    st.error(f"QC failed file not found: `{FAILED_FILE}`")
    st.stop()

df = pd.read_csv(FAILED_FILE)
st.write(f"Found **{len(df)}** QC-failed record(s).")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Approve & Move to Staging", type="primary"):
    try:
        STAGING_FILE.parent.mkdir(parents=True, exist_ok=True)
        if STAGING_FILE.exists():
            staging_df = pd.read_csv(STAGING_FILE)
            updated_df = pd.concat([staging_df, edited_df], ignore_index=True)
        else:
            updated_df = edited_df
        updated_df.to_csv(STAGING_FILE, index=False)
        FAILED_FILE.unlink(missing_ok=True)
        st.success("Approved claims moved to staging; QC failed file cleared.")
    except Exception as e:
        st.error(f"Error: {e}")
