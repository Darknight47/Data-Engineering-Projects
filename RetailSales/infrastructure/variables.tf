# --------------------------------  Configurations here
# ---- What variables exist or defining variables ----

variable "location" {
  description = "Azure region where the resources will be created"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "RetailSalesRG"
}

variable "storage_account_name" {
  description = "Globally unique name for the storage account"
  type        = string
}

variable "data_factory_name" {
  description = "Name of the Azure Data Factory instance"
  type        = string
}

variable "databricks_workspace_name" {
  description = "Name of the Azure Databricks workspace"
  type        = string
}