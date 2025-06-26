# 📊 Insurance Product Performance Analytics Platform

A scalable analytics solution built on **Databricks** to ingest, validate, transform, and visualize insurance premium and claims data for detailed product performance reporting.

---

## 🚀 Project Overview

This platform utilizes **Databricks Delta Lake** and **Delta Live Tables (DLT)** to implement an end-to-end analytics pipeline. It supports:

- UI-based data ingestion
- Automated data quality checks
- ETL pipelines for transformation and aggregation
- Curated datasets for advanced analytics and visualization

---

## 🧱 Architecture Workflow

<details>
<summary>Click to expand Mermaid diagram</summary>

```mermaid
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

