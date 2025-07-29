
output "public_ip" {
  value = aws_instance.appcd_installer.public_ip
}

output "connect" {
  value = "ssh -i output/id_rsa ubuntu@${aws_instance.appcd_installer.public_ip}"
}
