import streamlit as st
import pandas as pd
from pathlib import Path

# Paths
base_dir = Path("C:/Users/archa/Desktop/Databricks/Data/processed")
failed_path = base_dir / "qc_failed"
staging_path = base_dir / "staging"

failed_file = failed_path / "claims_failed.csv"
staging_file = staging_path / "claims_staging.csv"

# Load QC failed data
if not failed_file.exists():
    st.error("❌ QC failed file not found.")
    st.stop()

df = pd.read_csv(failed_file)

st.title("🚨 QC Failed Claims Review")
st.caption("Review, fix and approve failed claims data")

# Editable Data Table
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Approve Button
if st.button("✅ Approve & Move to Staging"):
    try:
        # Load current staging data
        staging_df = pd.read_csv(staging_file)

        # Append reviewed data
        updated_df = pd.concat([staging_df, edited_df], ignore_index=True)

        # Save updated staging file
        updated_df.to_csv(staging_file, index=False)

        # Clear failed file
        failed_file.unlink()

        st.success("✅ Approved claims moved to staging and failed claims cleared.")
    except Exception as e:
        st.error(f"Error: {e}")
