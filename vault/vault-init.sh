#!/bin/sh

alias vault="docker exec -i $(docker ps|awk '/vault:latest/ {print $1}') vault"

# initialize vault and store the keys
vault operator init |awk -F: '/:/ { 
    if ($1 ~ /Unseal Key 1/) print "Unseal_Key_1="$2 
    if ($1 ~ /Unseal Key 2/) print "Unseal_Key_2="$2 
    if ($1 ~ /Unseal Key 3/) print "Unseal_Key_3="$2 
    if ($1 ~ /Unseal Key 4/) print "Unseal_Key_4="$2 
    if ($1 ~ /Unseal Key 5/) print "Unseal_Key_5="$2 
    if ($1 ~ /Initial Root Token/) print "Initial_Root_Token="$2 
}' \
| sed 's/ //g' \
| tee > .env

# source the env file to get the key vars
source ./.env

# unseal the vault using 3 of the keys
vault operator unseal $Unseal_Key_1
vault operator unseal $Unseal_Key_2
vault operator unseal $Unseal_Key_3

# login to the vault using the initial root token
echo $Initial_Root_Token|vault login -

# enable file audit to the mounted logs volume
vault audit enable file file_path=/vault/logs/audit.log
vault audit list

# create the app-specific policy
vault policy write app /policies/myapp-policy.json
vault policy read app

# create the app token
vault token create -policy=app | awk '/token/ {
if ($1 == "token") print "myapp_Token="$2
else if ($1 == "token_accessor") print "myapp_Token_Accessor="$2
}' \
| tee >> .env

# source the env file to get the new key vars
source ./.env

# login using the app token
echo $myapp_Token|vault login -

# create initial secrets
#cat $myapp_PRIVKEY| vault kv put secret/apps/myapp/certs/privkey.pem value=-
#cat $myapp_FULLCHAIN| vault kv put secret/apps/myapp/certs/fullchain.pem value=-