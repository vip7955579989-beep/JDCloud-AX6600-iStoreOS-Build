import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Querying installed files of 'daed' package...")
stdin, stdout, stderr = client.exec_command("/sbin/apk.real info -L daed 2>/dev/null; /sbin/apk.real info -L luci-app-daede 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Checking /etc/init.d/ /usr/bin/ /usr/sbin/ for newly installed dae files...")
stdin, stdout, stderr = client.exec_command("find /etc/init.d /usr/bin /usr/sbin /www/luci-static/resources/view /usr/share/luci -iname '*dae*' 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
