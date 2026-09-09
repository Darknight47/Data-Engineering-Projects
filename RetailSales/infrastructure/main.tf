# Telling terraform to use Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

# Configuring the Azure provider
provider "azurerm" {
  features {}
  resource_provider_registrations = "none" # Only necessary ones should be added to avoid unnecessary registrations.
}

# Defining the resource group
# resource "azurerm_resource_group" "rg" {
#     name     = "RetailSalesRG"
#     location = "East US"
# }

# -- Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# -- Storage Account for Data Lake Storage Gen2
resource "azurerm_storage_account" "datalake" {
  name                = var.storage_account_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  is_hns_enabled = true # Enable hierarchical namespace for Data Lake Storage Gen2

  access_tier = "Hot"

  allow_nested_items_to_be_public = false
  public_network_access_enabled   = true
}

# -- Storage Container for Raw Data (Bronze Layer)
resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.datalake.id # This filesystem is associated with the storage account created above (for dependency)
}

# -- Storage Container for Processed Data (Silver Layer)
resource "azurerm_storage_data_lake_gen2_filesystem" "silver" {
  name               = "silver"
  storage_account_id = azurerm_storage_account.datalake.id # This filesystem is associated with the storage account created above (for dependency)
}

# -- Storage Container for Curated Data (Gold Layer)
resource "azurerm_storage_data_lake_gen2_filesystem" "gold" {
  name               = "gold"
  storage_account_id = azurerm_storage_account.datalake.id # This filesystem is associated with the storage account created above (for dependency)
}
