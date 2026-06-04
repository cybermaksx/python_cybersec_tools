import requests
import os

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
    pass










