import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== 1. Testing 'apk update' Execution Speed ===")
stdin, stdout, stderr = client.exec_command("time apk update")
print(stdout.read().decode('utf-8', errors='ignore'))
err = stderr.read().decode('utf-8', errors='ignore')
if err:
    print("STDERR:", err)

print("\n=== 2. Installed Software & Menu Files Verification ===")
stdin, stdout, stderr = client.exec_command("which ddnsto linkease; ls -ld /etc/init.d/ddnsto /etc/init.d/linkease 2>/dev/null; /bin/is-opkg run_records")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
