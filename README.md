# 📊 Insurance Product Performance Analytics Platform
o

# 📊 Insurance Product Performance Analytics Platform

A scalable analytics solution built on Databricks to ingest, process, validate, and visualize insurance product and claims data for performance analysis and reporting.

---

## 🚀 Project Overview

This platform leverages Databricks Delta Lake architecture and Delta Live Tables (DLT) to deliver a complete end-to-end data pipeline. It supports the ingestion of insurance premium and claims data, applies quality checks, performs transformations, and generates curated datasets for downstream analytics.

---

## 📂 Repository Contents

| File/Directory                                | Description                                                   |
|----------------------------------------------|---------------------------------------------------------------|
| `Databricks Insurance Analytics Platform Overview.docx` | Workflow architecture and system design                      |
| `Insurance Product Performance Analytics Platform Requirement.pdf` | Data specifications, rules, and derived metrics             |
| `claims_Visualization.ipynb`                 | Jupyter notebook for claims data visualization               |

---

## 🧱 Platform Architecture

```mermaid
graph TD
  A[UI Upload] --> B[Azure Blob Storage]
  B --> C[Raw Table (Bronze Layer)]
  C --> D[DLT / Workflow]
  D -->|QC Passed| E[Staging Table]
  D -->|QC Failed| F[QC Failed Table]
  F --> G[User Review via UI]
  G -->|Fix & Approve| E
  E --> H[DLT Aggregation / Transformation]
  H --> I[Curated Table (Gold Layer)]
  I --> J[Power BI / Tableau / Reporting Tools]
