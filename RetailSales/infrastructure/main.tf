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

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}