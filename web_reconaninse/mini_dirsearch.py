import requests
import os
import sys

target_url = input("What is your target's IP?\n")

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

def directory_bruteforce(target):
    with open("common.txt","r") as f:
        directories = [line.strip() for line in f if line.strip()]

    print(directories)





directory_bruteforce(target)





