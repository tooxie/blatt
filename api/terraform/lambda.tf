resource "aws_lambda_function" "start_transcoder" {
  filename = "../build/transcode-start-transcoder.zip"
  function_name = "${var.project}-${var.stage}-start-transcoder"
  role = "${aws_iam_role.lambda.arn}"
  handler = "index.handler"
  source_code_hash = "${base64sha256(file("../build/transcode-start-transcoder.zip"))}"
  runtime = "${local.lambda_runtime}"

  environment {
    variables = {
      PROD = "${var.stage == "prod" ? "1" : ""}"
      OUTPUT_BUCKET = "${aws_s3_bucket.transcode_output.bucket}"
      MEDIACONVERT_ENDPOINT = "${var.mediaconvert_api_endpoint}"
      TRANSCODING_ROLE_ARN = "${aws_iam_role.mediaconvert.arn}"
      DYNAMODB_NAME = "${aws_dynamodb_table.start_transcoder.name}"
      LOG_LEVEL = "${var.log_level}"
    }
  }

  tags = {
    Environment = "${var.stage}"
    Terraform = "1"
    Tier = "backend"
  }
}
