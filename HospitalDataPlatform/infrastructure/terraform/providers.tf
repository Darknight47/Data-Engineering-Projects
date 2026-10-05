# Terraform itself doesn't inherently know what an Azure Storage Account or ADF is. The AzureRM provider gives Terraform that capability.

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  resource_provider_registrations = "none" # Only necessary ones should be added to avoid unnecessary registrations.

}

data "azurerm_client_config" "current" {}