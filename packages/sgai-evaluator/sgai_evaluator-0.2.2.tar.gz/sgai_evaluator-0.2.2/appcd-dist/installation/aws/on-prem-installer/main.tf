provider "aws" {
  region = var.region
}

data "aws_availability_zones" "available" {
  state = "available"
}

# get current user
data "aws_caller_identity" "current" {}

locals {
  create_vpc = var.vpc_id == ""
  tags = merge(var.tags, {
    "Name"          = var.name
    "CreatedBy"     = data.aws_caller_identity.current.user_id
    "Reason"        = "stackgen installer"
    "maintained_by" = "support@stackgen.com"
  })
}

# create vpc if not provided
resource "aws_vpc" "appcd_installer" {
  count      = local.create_vpc ? 1 : 0
  cidr_block = "10.0.0.0/16"
  tags       = local.tags
}

# create flow log arn
resource "aws_iam_role" "flow_logs" {
  count = local.create_vpc ? 1 : 0
  name  = "${var.name}_flow_logs"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        },
        Action = "sts:AssumeRole"
    }]
  })
}

# create log group
resource "aws_cloudwatch_log_group" "flow_logs" {
  count = local.create_vpc ? 1 : 0
  name  = "flow-logs"
  tags  = local.tags
}

# create flow log
resource "aws_flow_log" "appcd_installer" {
  count           = local.create_vpc ? 1 : 0
  vpc_id          = aws_vpc.appcd_installer[0].id
  iam_role_arn    = aws_iam_role.flow_logs[0].arn
  log_destination = aws_cloudwatch_log_group.flow_logs[0].arn
  traffic_type    = "ALL"
  log_format      = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${start} $${end} $${action} $${log-status} $${ecs-cluster-name} $${ecs-cluster-arn} $${ecs-container-instance-id} $${ecs-container-instance-arn} $${ecs-service-name} $${ecs-task-definition-arn} $${ecs-task-id} $${ecs-task-arn} $${ecs-container-id} $${ecs-second-container-id}"
  tags            = local.tags
}

data "aws_iam_policy_document" "flow_policy" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "flow_role_policy" {
  count  = local.create_vpc ? 1 : 0
  name   = "flow_role_policy"
  role   = aws_iam_role.flow_logs[0].id
  policy = data.aws_iam_policy_document.flow_policy.json
}


locals {
  vpc_id = var.vpc_id != "" ? var.vpc_id : aws_vpc.appcd_installer[0].id
}

# get ami list
data "aws_ami" "ubuntu" {
  owners      = ["099720109477"] # Canonical
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "protected" {
  vpc_id = local.vpc_id
  name   = "${var.name}_protected"
  tags   = local.tags
}

# get my IP
data "http" "my_ip" {
  url = "http://checkip.amazonaws.com/"
}

# limit ssh access to the security group
resource "aws_security_group_rule" "ssh" {
  security_group_id = aws_security_group.protected.id
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks = [
    # strip the newline character
    ("${chomp(data.http.my_ip.response_body)}/32")
  ]
}

# allow egress
resource "aws_security_group_rule" "egress" {
  security_group_id = aws_security_group.protected.id
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_subnet" "this" {
  vpc_id                  = local.vpc_id
  cidr_block              = "10.0.0.0/16"
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[0]

  tags = local.tags
}

resource "aws_internet_gateway" "this" {
  vpc_id = local.vpc_id
  tags   = local.tags
}

resource "aws_route_table" "public_rt" {
  vpc_id = local.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  route {
    ipv6_cidr_block = "::/0"
    gateway_id      = aws_internet_gateway.this.id
  }

  tags = local.tags
}

resource "aws_route_table_association" "this" {
  subnet_id      = aws_subnet.this.id
  route_table_id = aws_route_table.public_rt.id
}

# create ssh key pair
resource "tls_private_key" "appcd_installer" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "appcd_installer" {
  key_name   = var.name
  public_key = tls_private_key.appcd_installer.public_key_openssh
}

# save the private key
resource "local_file" "private_key" {
  content         = tls_private_key.appcd_installer.private_key_pem
  filename        = "output/id_rsa"
  file_permission = 0600
}

resource "aws_iam_instance_profile" "appcd_installer" {
  name = var.name
  role = aws_iam_role.appcd_installer.name
}

data "aws_iam_policy_document" "deletion_policy" {
  statement {
    sid = "Global"
    actions = [
      "kms:DeleteAlias",
      "s3:DeleteBucket",
    ]
    resources = [
      "*",
    ]
  }
  statement {
    sid = "DeleteAppCD"
    actions = [
      "sqs:deletequeue",
      "s3:DeleteBucket",
      "rds:DeleteDBSubnetGroup",
      "rds:DeleteDBParameterGroup",
      "rds:DeleteDBInstance",
      "logs:DeleteLogGroup",
      "iam:RemoveRoleFromInstanceProfile",
      "iam:DetachRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:DeleteRole",
      "iam:DeletePolicy",
      "iam:DeleteOpenIDConnectProvider",
      "iam:DeleteInstanceProfile",
      "events:RemoveTargets",
      "events:DeleteRule",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:ReleaseAddress",
      "ec2:DisassociateRouteTable",
      "ec2:DisassociateAddress",
      "ec2:DetachInternetGateway",
      "ec2:DeleteVpc",
      "ec2:DeleteTags",
      "ec2:DeleteSubnet",
      "ec2:DeleteSecurityGroup",
      "ec2:DeleteRouteTable",
      "ec2:DeleteRoute",
      "ec2:DeleteNatGateway",
      "ec2:DeleteLaunchTemplate",
      "ec2:DeleteInternetGateway"
    ]
    resources = [
      "*",
    ]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/maintained_by"
      values   = ["support@stackgen.com"]
    }
  }
}

resource "aws_iam_policy" "deletion_policy" {
  name   = "${var.name}_delete_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.deletion_policy.json
  tags   = local.tags
}

resource "aws_iam_role_policy_attachment" "delete_attach" {
  role       = aws_iam_role.appcd_installer.name
  policy_arn = aws_iam_policy.deletion_policy.arn
}

data "aws_iam_policy_document" "creation_policy" {
  statement {
    sid     = "Global"
    actions = []
    resources = [
      "*",
    ]
  }
  statement {
    sid = "InstallAppCD"
    actions = [
      "sqs:setqueueattributes",
      "sqs:createqueue",
      "sqs:tagqueue",
      "s3:PutBucketTagging",
      "s3:PutBucketPublicAccessBlock",
      "s3:CreateBucket",
      "rds:ModifyDBParameterGroup",
      "rds:CreateDBInstance",
      "rds:CreateDBSubnetGroup",
      "rds:AddTagsToResource",
      "rds:CreateDBParameterGroup",
      "logs:TagResource",
      "logs:PutRetentionPolicy",
      "logs:CreateLogGroup",
      "kms:TagResource",
      "kms:EnableKeyRotation",
      "kms:CreateKey",
      "kms:CreateAlias",
      "iam:TagRole",
      "iam:TagPolicy",
      "iam:TagOpenIDConnectProvider",
      "iam:PutRolePolicy",
      "iam:TagInstanceProfile",
      "iam:PassRole",
      "iam:CreateRole",
      "iam:CreatePolicy",
      "iam:CreateOpenIDConnectProvider",
      "iam:CreateInstanceProfile",
      "iam:AttachRolePolicy",
      "iam:AddRoleToInstanceProfile",
      "events:TagResource",
      "events:PutRule",
      "events:PutTargets",
      # "eks:TagResource",
      # "eks:CreateNodegroup",
      # "eks:CreateCluster",
      # "eks:CreateAccessEntry",
      # "eks:CreateAddon",
      # "eks:AssociateAccessPolicy",
      "eks:*",
      "ec2:ModifyVpcAttribute",
      "ec2:DeleteNetworkAclEntry",
      "ec2:CreateVpc",
      "ec2:CreateTags",
      "ec2:CreateSubnet",
      "ec2:CreateSecurityGroup",
      "ec2:CreateRouteTable",
      "ec2:CreateRoute",
      "ec2:CreateNetworkAclEntry",
      "ec2:CreateNatGateway",
      "ec2:CreateLaunchTemplate",
      "ec2:CreateInternetGateway",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:AttachInternetGateway",
      "ec2:AssociateRouteTable",
      "ec2:AllocateAddress"
    ]
    resources = [
      "*",
    ]
    condition {
      test     = "ForAllValues:StringEquals"
      variable = "aws:TagKeys"
      values = [
        "maintained_by"
      ]
    }
  }
}

resource "aws_iam_policy" "creation_policy" {
  name   = "${var.name}_create_policy"
  path   = "/"
  policy = data.aws_iam_policy_document.creation_policy.json
  tags   = local.tags
}

resource "aws_iam_role_policy_attachment" "create_attach" {
  role       = aws_iam_role.appcd_installer.name
  policy_arn = aws_iam_policy.creation_policy.arn
}


resource "aws_iam_role_policy_attachment" "probe_attach" {
  role = aws_iam_role.appcd_installer.name
  # ReadOnlyAccess
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

resource "aws_iam_role" "appcd_installer" {
  name = var.name
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_instance" "appcd_installer" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  availability_zone           = data.aws_availability_zones.available.names[0]
  vpc_security_group_ids      = [aws_security_group.protected.id]
  subnet_id                   = aws_subnet.this.id
  key_name                    = aws_key_pair.appcd_installer.key_name
  iam_instance_profile        = aws_iam_instance_profile.appcd_installer.name
  associate_public_ip_address = true
  tags                        = local.tags

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = tls_private_key.appcd_installer.private_key_pem
    host        = self.public_ip
  }

  provisioner "remote-exec" {
    on_failure = fail
    script     = "scripts/install.sh"
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }
}

# save the public key
resource "local_file" "public_key" {
  content  = tls_private_key.appcd_installer.public_key_openssh
  filename = "output/id_rsa.pub"
}
