terraform {
  required_version = "~> 1.0"
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "~>0.53.1"
    }
    github = {
      source  = "integrations/github"
      version = "~>5.12.0"
    }
  }
}
