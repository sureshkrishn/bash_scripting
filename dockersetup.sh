# Add Docker's official GPG key:
sudo apt update -y && apt upgrade -y
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update -y

#docker package
sudo apt install docker-ce -y docker-ce-cli -y containerd.io -y docker-buildx-plugin -y docker-compose-plugin -y
#docker check
sudo systemctl status docker

#post check
sudo usermod -aG docker $USER
newgrp docker
