# ----------------------------------  Resources --------

# --- Main Resource Group ---
resource "azurerm_resource_group" "main_rg" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = {
    project     = var.project_name # What project owns this?
    environment = var.environment  # Which environment?
    managed_by  = "Terraform"      # Who/what manages it?
  }
}


# --- ADLS Gen2 Storage Account ---
resource "azurerm_storage_account" "data_lake" {
  name                     = "hospital${var.environment}dl"
  resource_group_name      = azurerm_resource_group.main_rg.name
  location                 = azurerm_resource_group.main_rg.location
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  is_hns_enabled = true # Hierarchical namespace for ADLS Gen2

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "Terraform"
  }
}

# -- containers inside the storage account "data_lake"
# -- container 1: a "source" container for raw data
resource "azurerm_storage_container" "source" {
  name                  = "source"
  storage_account_id    = azurerm_storage_account.data_lake.id
  container_access_type = "private" # No public access
}

# -- container 2: a "landing" container for processed data
resource "azurerm_storage_container" "landing" {
  name                  = "landing"
  storage_account_id    = azurerm_storage_account.data_lake.id
  container_access_type = "private" # No public access
}

# --- Azure Data Factory ---
resource "azurerm_data_factory" "data_factory" {
  name                = "adf-proj02-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main_rg.location
  resource_group_name = azurerm_resource_group.main_rg.name

  identity { # for authentication rather than putting storage passwords/keys into our pipelines.
    type = "SystemAssigned"
  }

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "Terraform"
  }
}

# -- Give ADF access to ADLS Gen2 storage account
resource "azurerm_role_assignment" "adf_storage_contributor" {
  scope                = azurerm_storage_account.data_lake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.data_factory.identity[0].principal_id
}


# --- Key Vault ---
resource "azurerm_key_vault" "key_vault" {
  name                = "kv-proj2-${var.project_name}-${var.environment}-01"
  location            = azurerm_resource_group.main_rg.location
  resource_group_name = azurerm_resource_group.main_rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  rbac_authorization_enabled  = true # permissions are managed through Azure RBAC rather than legacy Key Vault access policies.
  enabled_for_disk_encryption = false
  soft_delete_retention_days  = 7 # deleted vault objects can be recovered during the retention period
  purge_protection_enabled    = true

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "Terraform"
  }
}

# -- Give ADF permission read secrets from Key Vault --
resource "azurerm_role_assignment" "adf_key_vault_secrets_user" {
  scope                = azurerm_key_vault.key_vault.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_data_factory.data_factory.identity[0].principal_id
}