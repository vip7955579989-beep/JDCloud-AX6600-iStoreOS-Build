import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== 1. Checking Repositories Files ===")
stdin, stdout, stderr = client.exec_command("cat /etc/apk/repositories /etc/apk/repositories.d/* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n=== 2. Testing 'apk update' Verbose Output ===")
stdin, stdout, stderr = client.exec_command("apk -v update")
print(stdout.read().decode('utf-8', errors='ignore'))
err = stderr.read().decode('utf-8', errors='ignore')
if err:
    print("STDERR:", err)

client.close()
