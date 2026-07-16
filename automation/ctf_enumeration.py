import subprocess
import json
import re
import sys

# --- Configuration ---
# List of keywords that indicate a web service in Nmap output
WEB_SERVICE_KEYWORDS = [
    "http", "https", "www", "apache", "nginx", "iis", 
    "tomcat", "jetty", "weblogic", "node.js", "express"
]

def get_user_input():
    """
    Gets target IP and scan level from the user.
    Validates input to prevent crashes on non-integer inputs.
    """
    try:
        target_ip = input("What is your target's ip: \n").strip()
        
        # Simple validation for IP format (optional but good practice)
        if not target_ip:
            print("[-] Error: IP address cannot be empty.")
            sys.exit(1)

        level_of_enumeration = int(input("What kind of enumeration you want to do?\n1) Fast enumeration\n2) Deep enumeration\n"))
        
        if level_of_enumeration not in [1, 2]:
            print("[-] Please choose 1 or 2.")
            sys.exit(1)
            
        return target_ip, level_of_enumeration

    except ValueError:
        print("[-] Error: Please enter valid numbers.")
        sys.exit(1)


def web_enumeration(target_url):
    """
    Runs dirsearch against a specific URL to find hidden directories/files.
    
    Args:
        target_url (str): The full URL including protocol and port (e.g., http://192.168.1.1:8080)
    """
    output_file = "dirsearch_results.json"
    
    try:
        print(f"\n[+] Starting web enumeration on: {target_url}")
        
        # Run dirsearch command
        # -u: target URL
        # --output-formats=json: save as JSON for easy parsing
        # -o: output file name
        # --exclude-status=404: optional, to reduce noise
        cmd = f"dirsearch -u {target_url} --output-formats=json -o {output_file}"
        
        # shell=True is used here because dirsearch is an external tool. 
        # In production, prefer subprocess.run([...]) with a list for security.
        subprocess.run(cmd, shell=True, check=True)
        
        # Parse the results
        try:
            with open(output_file, "r") as f:
                data = json.load(f)
            
            directories = []
            # Dirsearch JSON structure usually has a 'results' key
            for entry in data.get("results", []):
                directories.append({
                    "url": entry.get("url"),
                    "status": entry.get("status"),
                    "size": entry.get("content-length", "N/A"),
                })
            
            if directories:
                print(f"[!] Found {len(directories)} interesting paths:")
                for d in directories[:5]: # Show first 5 as preview
                    print(f"    - {d['url']} (Status: {d['status']})")
            else:
                print("[*] No interesting directories found.")
                
        except FileNotFoundError:
            print("[-] Could not find dirsearch output file.")
        except json.JSONDecodeError:
            print("[-] Error parsing JSON output from dirsearch.")

    except subprocess.CalledProcessError as e:
        print(f"[-] Dirsearch failed: {e}")
    except Exception as e:
        print(f"[-] An unexpected error occurred in web_enumeration: {e}")


def parse_nmap_output(filename="nmap.txt"):
    """
    Parses the Nmap output file to extract open ports and their associated services.
    
    Returns:
        list: A list of dictionaries, e.g., [{'port': '80', 'service': 'http'}, ...]
    """
    services_found = []
    
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            
        for line in lines:
            # Nmap output format example: "80/tcp   open  http"
            # We use regex to capture port number and service name
            
            # Regex explanation:
            # (\d+)/tcp  -> Capture digits before /tcp (Port)
            # \s+        -> One or more spaces
            # open       -> Literal string "open"
            # \s+        -> One or more spaces
            # (.+)       -> Capture the rest of the line (Service Name)
            match = re.search(r"(\d+)/tcp\s+open\s+(.+)", line)
            
            if match:
                port = match.group(1)
                service_name = match.group(2).strip().lower() # Convert to lowercase for easier comparison
                
                services_found.append({
                    "port": port,
                    "service": service_name
                })
                
    except FileNotFoundError:
        print(f"[-] Error: File {filename} not found. Did Nmap run successfully?")
    except Exception as e:
        print(f"[-] Error parsing Nmap output: {e}")
        
    return services_found


def is_web_service(service_name):
    """
    Checks if the given service name indicates a web server.
    
    Args:
        service_name (str): The service name from Nmap (e.g., 'http', 'https-alt')
        
    Returns:
        bool: True if it looks like a web service, False otherwise.
    """
    for keyword in WEB_SERVICE_KEYWORDS:
        if keyword in service_name:
            return True
    return False


def run_scan(target_ip, scan_type):
    """
    Runs Nmap and then processes the results to find web services.
    
    Args:
        target_ip (str): Target IP address
        scan_type (str): 'fast' or 'deep' to determine Nmap flags
    """
    # Define Nmap arguments based on scan type
    if scan_type == "fast":
        # -F: Fast mode (scans fewer ports)
        nmap_args = f"sudo nmap -sS -sV -sC -F {target_ip} -oN nmap.txt"
    else:
        # -p-: Scan all 65535 ports
        nmap_args = f"sudo nmap -sS -sV -sC -p- {target_ip} -oN nmap.txt"
        
    try:
        print(f"\n[*] Running Nmap ({scan_type} scan) against {target_ip}...")
        print("[*] This may take a while depending on the network speed.")
        
        # Run Nmap
        subprocess.run(nmap_args, shell=True, check=True)
        
        print("[+] Nmap scan completed. Parsing results...")
        
        # Parse the output file
        services = parse_nmap_output("nmap.txt")
        
        if not services:
            print("[-] No open ports found or unable to parse results.")
            return
        
        print(f"[+] Found {len(services)} open ports.")
        
        # Filter for web services and run enumeration
        web_targets = []
        for svc in services:
            if is_web_service(svc['service']):
                # Determine protocol (http vs https)
                # If service name contains 'ssl' or 'https', use https, else http
                protocol = "https" if ("ssl" in svc['service'] or "https" in svc['service']) else "http"
                
                # Construct URL
                url = f"{protocol}://{target_ip}:{svc['port']}"
                web_targets.append(url)
                
        if web_targets:
            print(f"\n[!] Detected {len(web_targets)} potential web services:")
            for url in web_targets:
                print(f"    -> {url}")
                # Run web enumeration for each detected web service
                web_enumeration(url)
        else:
            print("[*] No web services detected based on service names.")
            
    except subprocess.CalledProcessError as e:
        print(f"[-] Nmap failed: {e}")
    except Exception as e:
        print(f"[-] An error occurred during scanning: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    target_ip, level = get_user_input()
    
    if level == 1:
        run_scan(target_ip, "fast")
    elif level == 2:
        run_scan(target_ip, "deep")
