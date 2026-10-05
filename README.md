## Project 01 🎮🗄️🗃️

### Business Problem
The company has customer, product-category, and transaction data stored as separate CSV files. The data needs to be collected, standardized, transformed, and organized in Azure so that it can be reliably used for sales and customer analytics.

### Business objective
Build a cloud-based data pipeline that:
1. Ingests the source datasets into Azure.
2. Preserves the original source data.
3. Cleans and transforms the data.
4. Produces analytics-ready datasets.
5. Can be executed repeatedly and reliably.
6. Provides a foundation for future reporting and analytics.

### Stakeholders
1. Business / Sales Analysts — analyze sales, products, customers and stores.
2. Data Analysts — consume curated datasets for reporting.

---
### Project 02 

#### Hospital Data Engineering Platform

An end-to-end, metadata-driven data engineering platform for integrating hospital data from multiple sources, including PostgreSQL systems and external CSV files.

The platform uses Azure Data Factory for metadata-driven ingestion and orchestration, Azure Data Lake Storage Gen2 for the data lake, and Azure Databricks with PySpark for data transformation across Bronze, Silver, and Gold layers. Control and audit tables are used to support configurable full and incremental loads and track pipeline execution.

The project also incorporates production-oriented engineering practices such as Infrastructure as Code with Terraform, Git-based version control, CI/CD, managed identities and RBAC, data quality and auditing, and automated notifications.   Databricks/Unity Catalog and downstream dashboards are used for governance and data consumption.

The project is based on a real-world healthcare data integration scenario and is designed as a hands-on implementation of production-style Azure Data Engineering practices.
