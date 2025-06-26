# 📊 Insurance Product Performance Analytics Platform

A scalable analytics solution built on Databricks to ingest, process, validate, and visualize insurance product and claims data for performance analysis and reporting.

---

## 🚀 Project Overview

This platform leverages Databricks Delta Lake architecture and Delta Live Tables (DLT) to deliver a complete end-to-end data pipeline. It supports the ingestion of insurance premium and claims data, applies quality checks, performs transformations, and generates curated datasets for downstream analytics.

---

## 📂 Repository Contents



graph TD
  A[UI Upload] --> B[Azure Blob Storage]
  B --> C[Raw Table (Bronze Layer)]
  C --> D[DLT / Workflow]
  D --> E[QC Passed → Staging Table]
  D --> F[QC Failed → QC Failed Table]
  F --> G[User Review via UI]
  G --> H[Fix & Approve]
  H --> E
  E --> I[DLT Aggregation / Transformation]
  I --> J[Curated Table (Gold Layer)]
  J --> K[Power BI / Tableau / Reporting Tools]
📥 Source Data Schemas
🔹 Premium Data
Primary Key: policy + endorsement_number

Field	Type	Description
policy	VARCHAR(20)	Unique policy identifier
effective_date	DATE	Policy start date
expiration_date	DATE	Policy end date
gross_policy_premium	DECIMAL	Gross premium amount
...	...	(See full document for complete schema)

🔹 Claims Data
Primary Key: claim_number + date + amount + type + coverage

Field	Type	Description
claim_number	VARCHAR(20)	Unique identifier for the claim
policy	VARCHAR(20)	Associated policy number
amount	DECIMAL	Amount of the claim
accident_state	CHAR(2)	State of the incident
...	...	(Full schema in PDF document)

✅ Data Quality Rules
Data is validated using DLT or Workflow with custom rules. Invalid records are logged and routed to the QC Failed Table.

Examples:

policy, insured_name, broker_name – must not be null

effective_date, expiration_date – valid date format required

cxl_tran – must be either 'yes' or 'no'

Claims follow similar rules for fields like claim_number, amount, and company.

🔄 Transformations & Derived Fields
🔸 Premium Metrics
Field Name	Description
written_policy_premium	Sum of total_transaction_premium
exposure_unit_years	Calculated using policy duration and unit count
earned_policy_premium	Based on current or expiration date
price_per_exposure_unit	written_policy_premium / exposure_unit_years
unit_rank, unit_range	Mapped from exposure master table

🔸 Claims Metrics
Field Name	Description
incurred_loss	Sum of claim amounts for specified claim types
incurred_loss_ratio	incurred_loss / earned_policy_premium
