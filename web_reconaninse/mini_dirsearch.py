import requests
import os
import sys
import re

target_url = input("What is your target's url?\n")
if not target_url.startswith(("http://", "https://")): 
    target_url = f"http://{target_url}"

target_port_input = input("Any specific port or press Enter for default (80):\n")

if target_port_input.strip() == "":
    target_port = 80
else:
    try:
        target_port = int(target_port_input)
    except ValueError:
        print("Invalid port number! Using default port 80.")
        target_port = 80

print(f"Target: {target_url}")
print(f"Port: {target_port}")

target = f"{target_url}:{target_port}"

def detect_technology(target):
    ext = subprocess.run(f"whatweb {target}"shell = True , capture_output = True , text = True)
    
    ext = result.stdout.lower()
    
    if 'php' in ext:
        return 'php'
    
    elif 'python' in ext or 'flask' in ext:
        return 'python' 
    
    elif 'asp' in ext or 'asp.net' in ext:
        return 'asp' 
    
    
    elif 'ruby' in ext or 'rails' in output:
        return 'ruby'
    
    
    elif 'node' in ext:
        return "node.js"
    
    else:
        return 'unknown



def directory_bruteforce(target):
    try:
        with open("common.txt","r") as f:
            directories = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("You don't have common.txt\nThat's very sad")
        sys.exit(1)
    
    print(f"Loaded {len(directories)} directories")
    print(directories[:5])


    for directory in directories:
        try:
            response = requests.get(f"{target}/{directory}")

        except requests.exceptions.RequestException as e:
            print(f"Mistake with {directory}")
            continue


        if response.status_code == 200 or response.status_code == 302:
            print(f"{directory}")
           
            
directory_bruteforce(target)





