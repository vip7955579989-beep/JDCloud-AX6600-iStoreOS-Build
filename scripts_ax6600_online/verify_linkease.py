import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== 1. Checking Linkease (易有云) Real System Files ===")
stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/linkease /usr/bin/linkease /usr/sbin/linkease /www/luci-static/resources/view/linkease/ 2>/dev/null; which linkease")
print(stdout.read().decode('utf-8', errors='ignore'))

print("=== 2. Checking APK Update Speed with Tsinghua Mirror ===")
stdin, stdout, stderr = client.exec_command("apk update")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
