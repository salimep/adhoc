#!/bin/python3
## nagios plugin to chck cacert certificates
import subprocess
from datetime import datetime
import sys
CRTICAL=2
OK=0
WARNING=1
UNKNOWN=3

def extract_cert(ALIAS,KEYSTORE,PASS):
    cmd = f"keytool -list -keystore {KEYSTORE} -storepass {PASS} -alias {ALIAS}  -v | grep -i -o until.* | sed 's/until\\://g'"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,universal_newlines=True)
    stdout, stderr = process.communicate()
    if not stdout:   # check output empty or not
        print ("no {} certificate found in the {} keystore ".format(ALIAS,KEYSTORE))
        sys.exit(CRTICAL)
    clean = stdout[:20] + ' '+stdout[24:].strip().lstrip() ## clean the output to convert date object Mon Dec 31 03:00:00 AST 2040
    dt_obj = datetime.strptime(clean, " %a %b %d %H:%M:%S %Y")
    return dt_obj
    if stderr:
        return None
        
def main():
    if len(sys.argv) < 4:
        print("UNKNOWN - Usage: check_java_cert.py <alias> <keystore_path> <password>")
        sys.exit(3) # UNKNOWN state
    # Configuration
    ALIAS = sys.argv[1]
    KEYSTORE = sys.argv[2]
    PASS = sys.argv[3]
    WARN_DAYS = 30
    CRIT_DAYS = 7
   
    cert_date = extract_cert(ALIAS, KEYSTORE, PASS)
    if not cert_date:
        print(f"UNKNOWN ")
        sys.exit(UNKNOWN)

    # 3. Calculate Remaining Days
    days_left = (cert_date - datetime.now()).days
    # Format: STATUS - Message | Performance Data
    perf_data = f"| days_remaining={days_left};{WARN_DAYS};{CRIT_DAYS};0;"

    if days_left < 0:
        print(f"CRITICAL - Certificate '{ALIAS}' EXPIRED on {cert_date.date()} {perf_data}")
        sys.exit(CRITICAL)
    
    if days_left <= CRIT_DAYS:
        print(f"CRITICAL - Certificate '{ALIAS}' expires in {days_left} days! {perf_data}")
        sys.exit(CRITICAL)
        
    if days_left <= WARN_DAYS:
        print(f"WARNING - Certificate '{ALIAS}' expires in {days_left} days. {perf_data}")
        sys.exit(WARNING)

    print(f"OK - Certificate '{ALIAS}' is valid for {days_left} days. {perf_data}")
    sys.exit(OK)

if __name__ == "__main__":
     main()

    

# extract_cert('ucaglobalg2root')

## example cmd python3 check_java_cert.py ucaglobalg2root /etc/pki/ca-trust/extracted/java/cacerts changeit