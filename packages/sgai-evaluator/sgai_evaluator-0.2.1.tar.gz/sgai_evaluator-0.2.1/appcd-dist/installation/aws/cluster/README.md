# EKS provisioner

## Inputs

Certificate, region and cluster name have default value in [variable.tf](./variable.tf)

- Region `export AWS_DEFAULT_REGION=us-west-2`

- List certificates ARN from aws

```sh
aws acm list-certificates --region ${AWS_DEFAULT_REGION} --query 'CertificateSummaryList[*].CertificateArn' --output text
```

```bash
# Plan
tofu plan
```

### Output

```bash
## Configure kubectl
$(tofu output -raw configure_kubectl)
```

[terraform.tfvars](https://developer.hashicorp.com/terraform/language/values/variables) required for namespace will be stored in the SecretManager

```sh
$(tofu output -raw tf_vars_for_namespace) > terraform.tfvars
```
