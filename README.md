# docker-vault-consul

Dockerized Vault with Consul backend

## Overview

This is a handy repo that gets a dockerized Vault server up, using Consul as a backend. Setting this up was much harder (for me anyway) than I felt it should be, so I wanted to make this config available for anyone else struggling to make this work.

I tested this on Mac OS X, with Docker in swarm mode, and it's working there. 


## Installation

1. Clone the repo: `git clone https://github.com/rossja/docker-vault-consul.git`
1. Run: `cd docker-vault-consul`
1. Run: `docker-compose up -d`
1. Run: `sh ./vault/vault-init.sh`
1. Add secrets *(some examples of how to do this are commented out in the vault-init script)*


## Features

* Vault runs in server mode
* Consul data is persisted in a docker volume
* The vault server and consul backend run on a custom overlay network, so traffic between them is isolated from any other containers
* Docker-compose file uses version 3


## Things to watch out for

* Since this uses a custom network, if you want other containers to be able to get to the vault you'll need to add those networks to the docker-compose.yml file, and to the vault service.