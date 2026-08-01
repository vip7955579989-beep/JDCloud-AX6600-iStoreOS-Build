import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Inspecting last 30 lines of /lib/apk/db/installed...")
stdin, stdout, stderr = client.exec_command("tail -n 30 /lib/apk/db/installed")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
