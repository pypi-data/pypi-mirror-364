# Docs infra

This directory contains the terraform templates needed to configure the S3 buckets and other AWS resources for hosting the docs website.

The website is hosted in the appcd.io AWS account

## Commands

```sh
export AWS_DEFAULT_PROFILE="584974133937_AdministratorAccess"
aws sso login

cd infra/docs
tofu plan
```
