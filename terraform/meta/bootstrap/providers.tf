terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.53.1"
    }
  }
}

provider "cloudfoundry" {
  api_url      = local.cf_api_url
  user         = var.cf_user
  password     = var.cf_password
  app_logs_max = 30
}
