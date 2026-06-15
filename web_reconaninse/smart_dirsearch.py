import requests
import sys
import subprocess
from mini_dirsearch import detect_technology, directory_bruteforce

TECH_EXTENSIONS = {
    'php': ['.php'],
    'python': ['.py'],
    'asp': ['.asp', '.aspx'],
    'ruby': ['.rb'],
    'node.js': ['.js'],
}


def smart_bruteforce(target, tech):
    try:
        with open("common.txt", "r") as f:
            directories = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("You don't have common.txt\nThat's very sad")
        sys.exit(1)

    extensions = [''] + TECH_EXTENSIONS.get(tech, [])
    print(f"Extensions to try: {extensions}\n")

    for directory in directories:
        for ext in extensions:
            path = f"{directory}{ext}"
            try:
                response = requests.get(f"{target}/{path}", timeout=5)
            except requests.exceptions.RequestException:
                continue

            if response.status_code in (200, 302):
                print(f"[FOUND] {target}/{path}")
            elif response.status_code in (401, 403):
                print(f"[FORBIDDEN] {target}/{path} — exists but access denied")


def main():
    target_url = input("\nEnter your target's url here\n").strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = f"http://{target_url}"

    port_input = input("\nAny specific port? Press Enter for default (80)\n").strip()
    if port_input == "":
        target_port = 80
    else:
        try:
            target_port = int(port_input)
        except ValueError:
            print("Invalid port number, using 80")
            target_port = 80

    target = f"{target_url}:{target_port}"

    tech = detect_technology(target)
    print(f"Detected technology: {tech}")

    smart_bruteforce(target, tech)


if __name__ == "__main__":
    main()
