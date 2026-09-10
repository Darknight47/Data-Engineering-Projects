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

# -- Azure Data Factory for Orchestration
resource "azurerm_data_factory" "adf" {
  name                = var.data_factory_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name # resource group must exist first, so we reference the resource group created above (for dependency)

  identity {
    type = "SystemAssigned"
  }
}

# -- DataBricks Workspace for Data Processing
resource "azurerm_databricks_workspace" "databricks" {
  name                = var.databricks_workspace_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name # resource group must exist first, so we reference the resource group created above (for dependency)
  sku                 = "premium"
}

# -- Access Connector for DataBricks to access Data Lake Storage Gen2
resource "azurerm_databricks_access_connector" "databricks" {
  name                = "retailsales001-dbac"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  identity {
    type = "SystemAssigned"
  }
}

# -- Giving the identity accesss to the Data Lake Storage Gen2
resource "azurerm_role_assignment" "databricks_storage" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.databricks.identity[0].principal_id
}