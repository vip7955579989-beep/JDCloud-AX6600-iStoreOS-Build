import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Extracting daed packages using '--allow-untrusted' flag...")
extract_cmd = """
mkdir -p /tmp/daed_extracted
/sbin/apk.real extract --allow-untrusted /tmp/daede-install/daed.apk /tmp/daed_extracted 2>&1
/sbin/apk.real extract --allow-untrusted /tmp/daede-install/luci-app-daede.apk /tmp/daed_extracted 2>&1

echo "[DAED] Copying extracted files to system root..."
cp -a /tmp/daed_extracted/* / 2>/dev/null || true
rm -rf /tmp/daed_extracted

chmod +x /usr/bin/daed /usr/sbin/daed /usr/bin/dae /usr/sbin/dae 2>/dev/null || true
chmod +x /etc/init.d/daed /etc/init.d/dae /etc/init.d/daede 2>/dev/null || true

/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true
/etc/init.d/daede enable 2>/dev/null || true
/etc/init.d/daede start 2>/dev/null || true

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
/etc/init.d/uhttpd restart 2>/dev/null || true
luci-reload 2>/dev/null || true
"""

stdin, stdout, stderr = client.exec_command(extract_cmd)
print("Extract Output:", stdout.read().decode('utf-8', errors='ignore'))

print("\n2. Checking DAED executables & LuCI menu view...")
stdin, stdout, stderr = client.exec_command("which daed dae daede; ls -la /usr/bin/dae* /usr/sbin/dae* /etc/init.d/dae* /usr/share/luci/menu.d/*dae* /www/luci-static/resources/view/*dae* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
