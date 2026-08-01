import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== 1. Testing 'is-opkg run_records' Output (Used by iStore 'Installed' Tab) ===")
stdin, stdout, stderr = client.exec_command("/bin/is-opkg run_records")
print(stdout.read().decode('utf-8', errors='ignore'))

print("=== 2. Checking DDNSTO Executables & Services ===")
stdin, stdout, stderr = client.exec_command("which ddnsto; ls -l /etc/init.d/ddnsto 2>/dev/null; ls -l /www/luci-static/resources/view/ddnsto/ 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
