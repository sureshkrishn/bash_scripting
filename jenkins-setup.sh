#!/bin/bash
# Ubuntu 24.04 Jenkins Installation - Fixed for 2026

sudo apt update -y
sudo apt install -y openjdk-17-jdk fontconfig   # Use Java 17 (recommended for 24.04)

# Add correct Jenkins GPG key (2025+ version)
curl -fsSL https://pkg.jenkins.io/debian/jenkins.io.key | sudo gpg --dearmor -o /usr/share/keyrings/jenkins.gpg

# Add repo with proper signed-by
echo "deb [signed-by=/usr/share/keyrings/jenkins.gpg arch=amd64] https://pkg.jenkins.io/debian-stable binary/" | \
  sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update -y
sudo apt install -y jenkins

# Start and enable service
sudo systemctl start jenkins
sudo systemctl enable jenkins
sudo systemctl status jenkins
