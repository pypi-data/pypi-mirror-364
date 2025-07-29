# Install namespaces

## Required variables

This is output by [cluster terraform creation](../cluster/output.tf)

```hcl
region                             = ""
azs                                = []
cluster_certificate_authority_data = ""
cluster_endpoint                   = ""
cluster_name                       = ""
database_subnet_group_name         = ""
vpc_id                             = ""
eks_sg_id                          = ""
data_bucket_name                   = ""
```

```bash
make examples
# Requires terraform.tfvars 
make plan/<namespace>
```
