#!/bin/bash -exu

update() {
    sudo apt-get update
    sudo apt-get install -y curl unzip
}

install_deps(){
    sudo snap install --classic opentofu
    sudo snap install --classic kubectl
    sudo snap install --classic helm3
    sudo snap install --classic aws-cli
}

setup_git() {
    git config --global user.email "support@stackgen.com"
    git config --global user.name "StackGen Support"
}

install_stackgen() {
    mkdir -p ~/stackgen
    cd ~/stackgen
    curl -o stackgen.zip https://releases.stackgen.com/appcd-dist/aws-enterprise/latest.zip
    unzip stackgen.zip -d .
    rm stackgen.zip
    git init . && git add . && git commit -am "Initial commit"
    ./install.sh
}

main() {
    update
    install_deps
    setup_git
    install_stackgen
}

main
