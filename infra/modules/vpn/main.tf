locals {
  vpn_cidr = "10.${var.second_octet}.0.0/20"
}

data "aws_vpc" "vpc" {
  id = var.vpc_id
}

data "aws_acm_certificate" "cert" {
  domain = "simpler.grants.gov"
}

data "aws_subnets" "subnets" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
  tags = {
    subnet_type = "private"
  }
}

data "aws_subnet" "subnets" {
  for_each = toset(data.aws_subnets.subnets.ids)
  id       = each.value
}

resource "aws_security_group" "vpn" {
  vpc_id      = var.vpc_id
  description = "allow all ingress and egress to VPN"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ec2_client_vpn_endpoint" "vpn" {
  description            = "vpn-${var.environment_name}"
  server_certificate_arn = data.aws_acm_certificate.cert.arn
  client_cidr_block      = local.vpn_cidr
  self_service_portal    = "enabled"
  vpc_id                 = var.vpc_id
  security_group_ids     = [aws_security_group.vpn.id]

  authentication_options {
    type                           = "federated-authentication"
    saml_provider_arn              = "arn:aws:iam::315341936575:saml-provider/AWSSSO_345521176bf03df0_DO_NOT_DELETE"
    self_service_saml_provider_arn = "arn:aws:iam::315341936575:saml-provider/AWSSSO_345521176bf03df0_DO_NOT_DELETE"
  }

  connection_log_options {
    enabled               = true
    cloudwatch_log_group  = aws_cloudwatch_log_group.vpn.name
    cloudwatch_log_stream = aws_cloudwatch_log_stream.vpn.name
  }

  tags = {
    Name = "vpn-${var.environment_name}"
  }
}

resource "aws_cloudwatch_log_group" "vpn" {
  name_prefix = "/vpn/${var.environment_name}/"

  # Conservatively retain logs for 5 years.
  # Looser requirements may allow shorter retention periods
  retention_in_days = 1827

  # TODO(https://github.com/navapbc/template-infra/issues/164) Encrypt with customer managed KMS key
  # checkov:skip=CKV_AWS_158:Encrypt service logs with customer key in future work
}

resource "aws_cloudwatch_log_stream" "vpn" {
  name           = "/vpn/${var.environment_name}/"
  log_group_name = aws_cloudwatch_log_group.vpn.name
}

resource "aws_ec2_client_vpn_network_association" "vpn" {
  for_each               = toset(data.aws_subnets.subnets.ids)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
  subnet_id              = each.value
}

resource "aws_ec2_client_vpn_authorization_rule" "vpn" {
  for_each               = toset(data.aws_subnets.subnets.ids)
  client_vpn_endpoint_id = aws_ec2_client_vpn_endpoint.vpn.id
  target_network_cidr    = data.aws_subnet.subnets[each.value].cidr_block
  authorize_all_groups   = true
}
