import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Searching for any binary files named *apk* or matching ELF header...")
stdin, stdout, stderr = client.exec_command("find / -name '*apk*' 2>/dev/null; ls -l /lib/apk* /usr/lib/apk* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Checking file types of all binaries in /sbin /usr/bin /bin...")
stdin, stdout, stderr = client.exec_command("file /sbin/* /usr/bin/* /bin/* 2>/dev/null | grep -i apk")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
