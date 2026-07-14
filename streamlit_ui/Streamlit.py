"""Single-row QC repair UI with repo-relative Data/ paths."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
QC_FAILED_PATH = ROOT / "Data" / "processed" / "qc_failed" / "claims_failed.csv"
STAGING_PATH = ROOT / "Data" / "processed" / "staging" / "claims_staging.csv"

QC_FAILED_PATH.parent.mkdir(parents=True, exist_ok=True)
STAGING_PATH.parent.mkdir(parents=True, exist_ok=True)

if not QC_FAILED_PATH.exists():
    pd.DataFrame(columns=["CLAIM_ID", "ERROR_REASON"]).to_csv(QC_FAILED_PATH, index=False)

qc_df = pd.read_csv(QC_FAILED_PATH)

st.title("QC Failed Claims Review")
st.write(f"Found `{len(qc_df)}` QC-failed records.")
st.dataframe(qc_df, use_container_width=True)

if len(qc_df) > 0:
    selected_index = st.number_input(
        "Select Row Index to Fix",
        min_value=0,
        max_value=len(qc_df) - 1,
        step=1,
    )

    if st.button("Edit Selected Row"):
        selected_row = qc_df.iloc[int(selected_index)]
        with st.form(key="edit_form"):
            edited_row = {
                col: st.text_input(col, value=str(selected_row[col])) for col in qc_df.columns
            }
            if st.form_submit_button("Save & Approve"):
                for col in qc_df.columns:
                    qc_df.at[int(selected_index), col] = edited_row[col]
                st.success("Row updated. Ready to push to staging.")

    if st.button("Push Approved Record to Staging"):
        fixed_row = qc_df.iloc[[int(selected_index)]]
        try:
            staging_df = pd.read_csv(STAGING_PATH)
            staging_df = pd.concat([staging_df, fixed_row], ignore_index=True)
        except FileNotFoundError:
            staging_df = fixed_row

        staging_df.to_csv(STAGING_PATH, index=False)
        st.success("Record pushed to staging layer.")

        qc_df = qc_df.drop(index=int(selected_index)).reset_index(drop=True)
        qc_df.to_csv(QC_FAILED_PATH, index=False)
        st.success("Record removed from QC failed list.")
else:
    st.warning("No QC failed records to review.")
