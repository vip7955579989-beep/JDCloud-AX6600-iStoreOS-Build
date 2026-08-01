import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

commands = """
echo "=== Searching Store Files ==="
find /www /usr /etc -name "*store*" 2>/dev/null

echo "=== Reloading RPCD & LuCI Caches ==="
/etc/init.d/rpcd restart 2>/dev/null || true
rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
/etc/init.d/uhttpd restart 2>/dev/null || true
luci-reload 2>/dev/null || true

echo "=== Current Installed / Active LuCI Menus ==="
ls -l /usr/share/luci/menu.d/ 2>/dev/null | grep store || true
ls -l /usr/lib/lua/luci/controller/ 2>/dev/null | grep store || true
"""

stdin, stdout, stderr = client.exec_command(commands)
out = stdout.read().decode('utf-8', errors='ignore')
print(out)

client.close()
