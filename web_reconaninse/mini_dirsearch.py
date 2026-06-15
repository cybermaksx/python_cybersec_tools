import requests
import sys
import subprocess


def detect_technology(target):
    result = subprocess.run(f"whatweb {target}", shell=True, capture_output=True, text=True)
    output = result.stdout.lower()

    if 'php' in output:
        return 'php'
    elif 'python' in output or 'flask' in output:
        return 'python'
    elif 'asp' in output or 'asp.net' in output:
        return 'asp'
    elif 'ruby' in output or 'rails' in output:
        return 'ruby'
    elif 'node' in output:
        return 'node.js'
    else:
        return 'unknown'


def directory_bruteforce(target):
    try:
        with open("common.txt", "r") as f:
            directories = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("You don't have common.txt\nThat's very sad")
        sys.exit(1)

    print(f"Loaded {len(directories)} directories")

    for directory in directories:
        try:
            response = requests.get(f"{target}/{directory}", timeout=5)
        except requests.exceptions.RequestException:
            print(f"Failed to reach {directory}")
            continue

        if response.status_code in (200, 302):
            print(f"[FOUND] {target}/{directory}")
        elif response.status_code in (401, 403):
            print(f"[FORBIDDEN] {target}/{directory} — exists but access denied")


def main():
    target_url = input("What is your target's url?\n").strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = f"http://{target_url}"

    target_port_input = input("Any specific port or press Enter for default (80):\n").strip()
    if target_port_input == "":
        target_port = 80
    else:
        try:
            target_port = int(target_port_input)
        except ValueError:
            print("Invalid port number! Using default port 80.")
            target_port = 80

    target = f"{target_url}:{target_port}"
    print(f"\nTarget: {target}")

    tech = detect_technology(target)
    print(f"Detected technology: {tech}\n")

    directory_bruteforce(target)


if __name__ == "__main__":
    main()
