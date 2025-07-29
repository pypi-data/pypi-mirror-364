terraform {
  backend "azurerm" {
    resource_group_name  = "cesarappcdstates-rg"
    storage_account_name = "cesarappcdstatessa"
    container_name       = "tfstate"
    key                  = "statestorage.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

// get the account id
data "azurerm_client_config" "current" {}

locals {
}

resource "azurerm_resource_group" "this" {
  name     = "${var.prefix}-rg"
  location = "West US"
  # enable lock
  tags = var.tags
  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_account" "this" {
  name                     = "${var.prefix}sa"
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  tags                     = var.tags
}

resource "azurerm_storage_container" "this" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}
