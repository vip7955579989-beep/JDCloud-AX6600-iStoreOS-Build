import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Inspecting file type and tar structure of daed.apk...")
inspect_cmd = """
file /tmp/daede-install/daed.apk
tar -ztvf /tmp/daede-install/daed.apk 2>&1 | head -n 10
tar -tvf /tmp/daede-install/daed.apk 2>&1 | head -n 10
"""
stdin, stdout, stderr = client.exec_command(inspect_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Testing apk help options for dependency override...")
stdin, stdout, stderr = client.exec_command("/sbin/apk.real add --help | grep -i dep")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
