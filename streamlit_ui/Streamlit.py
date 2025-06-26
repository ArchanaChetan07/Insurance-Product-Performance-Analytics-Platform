import streamlit as st
import pandas as pd
from pathlib import Path
import os

# --------------------------
# 📁 Path Configuration
# --------------------------
base_dir = Path("C:/Users/archa/Desktop/Databricks/Data")
qc_failed_path = base_dir / "processed/qc_failed/claims_failed.csv"
staging_path = base_dir / "processed/staging/claims_staging.csv"

# Ensure directories exist
qc_failed_path.parent.mkdir(parents=True, exist_ok=True)
staging_path.parent.mkdir(parents=True, exist_ok=True)

# If QC file doesn't exist, create empty shell
if not qc_failed_path.exists():
    pd.DataFrame(columns=["CLAIM_ID", "ERROR_REASON"]).to_csv(qc_failed_path, index=False)

# --------------------------
# 📄 Load QC Failed Data
# --------------------------
qc_df = pd.read_csv(qc_failed_path)

st.title("🚨 QC Failed Claims Review")
st.write(f"Found `{len(qc_df)}` QC-failed records.")
st.dataframe(qc_df, use_container_width=True)

# --------------------------
# 🔍 Row Selection & Editing
# --------------------------
if len(qc_df) > 0:
    selected_index = st.number_input("Select Row Index to Fix", min_value=0, max_value=len(qc_df)-1, step=1)

    if st.button("✏️ Edit Selected Row"):
        selected_row = qc_df.iloc[selected_index]
        with st.form(key="edit_form"):
            edited_row = {col: st.text_input(col, value=str(selected_row[col])) for col in qc_df.columns}
            if st.form_submit_button("✅ Save & Approve"):
                for col in qc_df.columns:
                    qc_df.at[selected_index, col] = edited_row[col]
                st.success("✅ Row updated. Ready to push to staging.")

    # --------------------------
    # 🚀 Push to Staging Logic
    # --------------------------
    if st.button("📤 Push Approved Record to Staging"):
        fixed_row = qc_df.iloc[[selected_index]]

        try:
            staging_df = pd.read_csv(staging_path)
            staging_df = pd.concat([staging_df, fixed_row], ignore_index=True)
        except FileNotFoundError:
            staging_df = fixed_row  # Create new staging file

        staging_df.to_csv(staging_path, index=False)
        st.success("✅ Record pushed to staging layer.")

        # Remove from QC failed
        qc_df = qc_df.drop(index=selected_index).reset_index(drop=True)
        qc_df.to_csv(qc_failed_path, index=False)
        st.success("🧹 Record removed from QC failed list.")

else:
    st.warning("No QC failed records to review. You're all caught up! ✅")
