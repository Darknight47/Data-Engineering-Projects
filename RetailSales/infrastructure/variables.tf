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