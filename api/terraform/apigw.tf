resource "aws_api_gateway_rest_api" "api" {
  name = "${var.project}-${var.stage}-api"
  description = "[ ${var.project} ] [ ${var.stage} ] Backend API"
}

resource "aws_api_gateway_method_settings" "api" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name = "${aws_api_gateway_deployment.stage.stage_name}"
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level = "INFO"
  }

  depends_on = ["aws_api_gateway_deployment.stage"]
}

// Deployment
resource "aws_api_gateway_deployment" "stage" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name = "${var.stage}"

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    "aws_api_gateway_integration.upload_post",
    "aws_api_gateway_integration.upload_options"
  ]
}

resource "aws_api_gateway_domain_name" "api" {
  domain_name = "api.${local.domain_name}"
  certificate_arn = "${aws_acm_certificate.cert.arn}"
}

resource "aws_api_gateway_base_path_mapping" "api" {
  api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name = "${aws_api_gateway_deployment.stage.stage_name}"
  domain_name = "${aws_api_gateway_domain_name.api.domain_name}"

  depends_on = ["aws_api_gateway_deployment.stage"]
}

// Outputs
output "api" {
  value = [
    "${aws_api_gateway_rest_api.api.name}",
    "${aws_api_gateway_deployment.stage.invoke_url}",
    "${aws_api_gateway_domain_name.api.domain_name}",
  ]
}
