#!/bin/env python3

# Write a python 3 application that will:
# Connect to vault to create dynamic secrets.
# Using those secrets connect to the database and retrieve some data
# Connect to Consul's KV backend to retrieve some data.

import hvac, json, os


import psycopg2, consul

#test the DB exists
#conn = psycopg2.connect(database="usda", user="AdminGuyTy", password="Ineedajob")

client = hvac.Client(url="http://localhost:8200")

# check if vault is initialized and unsealed.
if not client.sys.is_initialized():
    print("Hey looks like the vault is not initialized. Lets fix that.")
    shares = 1
    threshold = 1
    result = client.sys.initialize(shares, threshold)
    root_token = result["root_token"]
    keys = result["keys"]
    if client.sys.is_initialized():
        print("The vault is initialized.")
        client.token = root_token
    else:
        raise Exception("Vault initialization failed")
        exit(1)
    # save the keys somewhere secure... like this directory.
    with open('super_secret.json', 'w') as fp:
        json.dump(result, fp)
    # unseal the vault cluster
    unseal_responses = client.sys.submit_unseal_keys(keys)
# check if vault is just sealed since is it seems initialized
elif client.sys.is_sealed():
    print("The vault is already initialized but it is sealed.")
    # check if we can unseal it ourselves.
    try:
        #change this if we decide to be secure later on
        with open("super_secret.json", "r") as mf:
            result = json.load(mf)
            root_token = result["root_token"]
            keys = result["keys"]
            if client.sys.is_initialized():
                client.token = root_token
        # unseal the vault cluster
        unseal_responses = client.sys.submit_unseal_keys(keys)
    except FileNotFoundError as e:
        raise Exception("Vault is initialized and I don't have the keys")
        exit(1)
else:
    try:
        #change this if we decide to be secure later on
        with open("super_secret.json", "r") as mf:
            result = json.load(mf)
            root_token = result["root_token"]
            keys = result["keys"]
            if client.sys.is_initialized():
                client.token = root_token
    except FileNotFoundError as e:
        raise Exception("Vault is initialized and unsealed but I don't have the token")
        exit(1)


if (client.sys.is_initialized() and not client.sys.is_sealed()):
    print("The vault is unsealed")




try:
    result = client.secrets.database.list_connections()
except:
    #no DB exists in vault must create it.
    #setup dynamic credentials
    try:
        #inserting delay here to "make it work"
        import time
        time.sleep(2)
        client.sys.enable_secrets_engine("database")
    except hvac.exceptions.InvalidRequest as e:
        pass # already enabled I guess.


    client.secrets.database.configure("usda", "postgresql-database-plugin", allowed_roles=["read"], connection_url="postgresql://{{username}}:{{password}}@postgres:5432/usda?sslmode=disable", username="AdminGuyTy", password="Ineedajob")
    client.secrets.database.create_role("read", "usda", "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";", default_ttl="1h", max_ttl="24h")




dynamic_creds = client.secrets.database.generate_credentials("read")
print(f"""
I got you your dynamic credentials!
username = {dynamic_creds["data"]["username"]}
password = {dynamic_creds["data"]["password"]}
""")
conn = psycopg2.connect(database="usda", user=dynamic_creds["data"]["username"], password=dynamic_creds["data"]["password"])
cur = conn.cursor()
cur.execute("select * from data_src;")
results = cur.fetchall()
print(results[1],  "\r\n")

#create consul handler
c = consul.Consul()
#since nothing is in the KV store seed it.
kv = c.KV(agent=c)
kv.put(key="test", value="it worked! No way!")


results = kv.get("test")
print(results, "\r\n")
print(results[1]["Value"])
