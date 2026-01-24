#!/bin/bash
# USE UBUNTU24.04 - INSTANCE: 2GB RAM + 2VCPU MIN - WILL ONLY WORK

###system-update&upgrade##
sudo apt update -y
sudo apt upgrade -y

###java-11,8,3,21-installation##

sudo apt install openjdk-11-jdk -y
sudo apt install openjdk-8-jdk -y
sudo apt install fontconfig openjdk-21-jre -y

###maven-installation###
sudo apt install maven -y

# Add correct Jenkins GPG key (2026+ version)
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key

# Add repo with proper signed-by

echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc]" \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update -y
sudo apt install jenkins -y

# Start and enable service
sudo systemctl start jenkins
sudo systemctl enable jenkins
sudo systemctl status jenkins
