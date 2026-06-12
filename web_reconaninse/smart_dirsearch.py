import requests
import re
import sys
import os 


target_url = input("\nPlease write your target's url here\n")

if not 'http' or 'https' in target_url:
    target_url = f"http://{target_url}"

target_port = ("\nPlease choose port where application runs\n(Default port is 80)")

if target_port_input.strip() ==  "":
    target_port = 80

else:
    try:
        target_port = int(target_port)

    except ValueError:
        print("Invalid port number! Using default port 80.")
        target_port = 80


target = f"{target_url}:{target_port}"

print("\nAttacking {target}\n")


def tech_enumeration(target):

    ext = subprocess.run(f"whatweb {target}",shell = True , capture_output = True , text = True)

    ext = result.stdout.lower()

    if 'php' in ext:
        tech = "php"

    elif 'python' in ext or 'flask' in ext:
         tech = "py"

    elif 'ruby' in ext or 'rails' in ext:
        tech = "ruby"

    elif 'node.js' in ext:
        tech = "js"

#I will more after i succesfully test this script


def smart_brute(target):
    try:
        with open("common.txt", "r") as f:
            directories = [line.strip() for line in f if line.strip()]
    except FileNotFound:
        print("You don't have common.txt in this directory")
        sys.exit(1)


    for directory in directories:
        try:
            response = requests.get(f"{target}/{directory}.{tech}")

        except requests.exceptions.RequestException as e:
                    print(f"Mistake with {directory}")
                    continue
            
    if response.status_code == 200 or response.status_code == 301 or response.status_code == 302 :
        print(f"{directory}")

    if response.status_code == 401 or response.status_code == 403:
        print(f"It exsists but we don't have access for this asset {directory}")


    print(f"Brute force attack to {target} is finished. Go and check assets manually ") 
           
    












