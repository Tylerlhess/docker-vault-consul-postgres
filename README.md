# docker-vault-consul

Dockerized Vault with Consul backend

## Overview

This is a handy repo that gets a dockerized Vault server up, using Consul as a backend. Setting this up was much harder (for me anyway) than I felt it should be, so I wanted to make this config available for anyone else struggling to make this work.

I tested this on Mac OS X, with Docker (both in swarm mode, and not) and it's working there. 


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

* You probably want to edit the `vault/vault-init.sh` and `policies/myapp-policy.json` files:
    - replace `myapp` with whatever you want to identify your app as
* Since this uses a custom network, if you want other containers to be able to get to the vault you'll need to add those networks to the docker-compose.yml file, and to the vault service.
* As configured in the repo the Vault container talks to Consul over HTTP. Since the secret is encrypted inside vault, no sensitive data is being passed in plaintext over the network (in theory), but it’s still not the best-practice to use HTTP here. 
  - The problem is that there’s a bit of a chicken/egg problem with using HTTPS… specifically: you need to securely get certificates and privatekeys into the Vault and Consul containers in order for TLS to work properly. But doing that means either checking the certs into a repo, or passing them into the container via something like a volume or ENV var. Neither of these are ideal, so I just settled for a reasonable alternative that works for local dev pretty securely. 
  - If you want to implement this in production, you should probably look at bootstrapping certs via an orchestrator or something, and tweaking the config to use HTTPS instead.
