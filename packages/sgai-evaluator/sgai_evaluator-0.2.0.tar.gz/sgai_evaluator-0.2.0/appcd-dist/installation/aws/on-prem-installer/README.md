# OnPrem appCD Installer

This hcl script will allow someone to bootstrap an ec2 instance with a public IP that can run

The script will bootstrap an ec2 instance with a public IP that can run the appCD installer.

- VPC with a public subnet
- Security group that allows SSH traffic

## Commands

Check the [Makefile](Makefile) for all the commands.

```bash
## Initialize the terraform workspace and install everything
make apply/y

## Connect to the instance
$(tofu output -raw connect)
```
