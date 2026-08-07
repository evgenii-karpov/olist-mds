terraform {
  # The bucket is created manually before the first Terraform init and is
  # intentionally not represented as a resource in this root module.
  backend "gcs" {}
}
