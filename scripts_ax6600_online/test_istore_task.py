import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== Checking File Executable Permissions ===")
stdin, stdout, stderr = client.exec_command("ls -l /etc/init.d/tasks /usr/libexec/taskd /bin/opkg")
print(stdout.read().decode('utf-8'))

print("=== Testing Task & OPKG Command ===")
stdin, stdout, stderr = client.exec_command("/etc/init.d/tasks status; opkg update")
print("Output:\n", stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("Stderr:", err)

client.close()
