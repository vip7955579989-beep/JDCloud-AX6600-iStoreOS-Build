import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== Content of /usr/libexec/taskd ===")
stdin, stdout, stderr = client.exec_command("cat /usr/libexec/taskd")
print(stdout.read().decode('utf-8'))

print("\n=== Searching for is-opkg ===")
stdin, stdout, stderr = client.exec_command("which is-opkg; find /www /usr /bin /sbin /etc -name '*is-opkg*' 2>/dev/null")
print(stdout.read().decode('utf-8'))

client.close()
