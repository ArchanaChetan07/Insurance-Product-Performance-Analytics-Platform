# 📊 Insurance Product Performance Analytics Platform
Overview
This platform provides a robust and scalable solution for analyzing insurance product and claims data. Built on Databricks with Delta Lake architecture, it enables seamless ingestion, quality validation, transformation, and visualization of insurance performance metrics.

🏗️ Architecture Workflow
Data Ingestion

Input via UI (Excel upload)

Stored in Azure Blob Storage

Raw Data Load

Loaded into Delta Lake (Bronze Layer)

Data Quality Checks

Implemented via Delta Live Tables (DLT) / Workflows

Failed vs. passed records routed accordingly

QC Review

UI-enabled review and reprocessing of failed records

Transformations & Aggregation

ETL via DLT to compute curated metrics (Gold Layer)

Reporting Layer

Curated data consumed by Power BI/Tableau dashboards

📥 Source Data Formats
Premium Data Fields
policy, insured_name, broker_name, effective_date, etc.

Key: policy + endorsement_number

Claims Data Fields
claim_number, policy, risk_state, amount, date, etc.

Key: claim_number + date + amount + type + coverage

✅ Data Quality Rules
Premium Data:
Fields like policy, effective_date, deductible, etc. must be valid and non-null.

Claims Data:
Fields like claim_number, date_of_loss, company, amount, etc. are validated similarly.

Records failing these checks are routed to a “QC Failed” table for user review.

🔄 Derived & Transformed Fields
Premium:
written_policy_premium

exposure_unit_years

earned_policy_premium

price_per_exposure_unit

unit_rank, unit_range

Claims:
incurred_loss

incurred_loss_ratio

