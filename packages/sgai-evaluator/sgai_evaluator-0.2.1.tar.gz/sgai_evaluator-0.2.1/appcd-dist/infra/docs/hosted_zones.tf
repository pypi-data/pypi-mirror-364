resource "aws_route53_zone" "docs" {
  name = "docs.stackgen.com"
}

resource "aws_route53_zone" "ent_docs" {
  name = "enterprise-docs.stackgen.com"
}
