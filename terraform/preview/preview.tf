module "preview" {
  source                = "../shared/modules/env"
  cf_space_name         = "preview"
  new_relic_license_key = var.new_relic_license_key

  database_plan         = "medium-gp-psql"
  postgrest_instances   = 1
  swagger_instances     = 1
  https_proxy_instances = 1
  smtp_proxy_instances  = 1
  recursive_delete      = true
}