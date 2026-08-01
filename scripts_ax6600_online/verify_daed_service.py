import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Checking DAED binary & service status...")
check_cmd = """
which daed dae;
ls -la /usr/bin/daed /etc/init.d/daed /etc/init.d/dae 2>/dev/null;

# Enable & start service
chmod +x /etc/init.d/daed 2>/dev/null || true
chmod +x /etc/init.d/dae 2>/dev/null || true
/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true
/etc/init.d/dae enable 2>/dev/null || true
/etc/init.d/dae start 2>/dev/null || true

# Refresh LuCI menu & index cache
rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
luci-reload 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(check_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Checking process status of daed...")
stdin, stdout, stderr = client.exec_command("ps | grep -i daed | grep -v grep")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
