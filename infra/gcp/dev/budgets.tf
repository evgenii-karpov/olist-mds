data "google_project" "current" {
  project_id = var.project_id
}

resource "google_monitoring_notification_channel" "budget_email" {
  count = var.budget_notification_email == null ? 0 : 1

  project      = var.project_id
  display_name = "Olist MDS budget email"
  type         = "email"
  labels = {
    email_address = var.budget_notification_email
  }

  depends_on = [google_project_service.apis["monitoring.googleapis.com"]]
}

resource "google_billing_budget" "dev" {
  count = var.billing_account_id == null ? 0 : 1

  billing_account = var.billing_account_id
  display_name    = "Olist MDS ${var.environment} notification budget"

  budget_filter {
    projects = ["projects/${data.google_project.current.number}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.budget_limit_usd)
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }

  threshold_rules {
    threshold_percent = 0.9
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }

  dynamic "all_updates_rule" {
    for_each = var.budget_notification_email == null ? [] : [var.budget_notification_email]

    content {
      monitoring_notification_channels = [google_monitoring_notification_channel.budget_email[0].id]
      disable_default_iam_recipients   = false
    }
  }

  depends_on = [google_project_service.apis["billingbudgets.googleapis.com"]]
}
