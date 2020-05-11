resource "aws_db_instance" "blatt" {
  name = "blatt"
  allocated_storage = 10
  storage_type = "gp2"
  engine = "mysql"
  engine_version = "5.7"
  instance_class = "db.t2.micro"
  username = "blatt"
  password = "${var.db_password}"
  parameter_group_name = "default.mysql5.7"
}

// TODO: Add secrets manager
// resource "aws_secretsmanager_secret" "blatt" {
//   name_prefix = "${var.project}-${var.stage}"
// }
