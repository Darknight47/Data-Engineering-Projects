# ------------------------ outputs ------------------------
# This makes Terraform report useful information after deployment.

output "resource_group_name" {
  value = azurerm_resource_group.main_rg.name
}

output "storage_account_name" {
  value = azurerm_storage_account.data_lake.name
}

output "adf_name" {
  value = azurerm_data_factory.data_factory.name
}

output "key_vault_name" {
  description = "Name of the project Key Vault"
  value       = azurerm_key_vault.key_vault.name
}

output "key_vault_uri" {
  description = "URI of the project Key Vault"
  value       = azurerm_key_vault.key_vault.vault_uri
}