import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Installing daed.apk and luci-app-daede.apk with --nodeps...")
install_cmd = """
/sbin/apk.real add --allow-untrusted --nodeps /tmp/daede-install/daed.apk /tmp/daede-install/luci-app-daede.apk 2>&1

# Check if binaries and init scripts are placed correctly
if [ ! -f /etc/init.d/daed -a ! -f /etc/init.d/dae ]; then
    echo "[DAED] Extracting data from apk files manually..."
    cd /tmp/daede-install
    tar -xzf daed.apk 2>/dev/null || tar -xf daed.apk 2>/dev/null || true
    tar -xzf luci-app-daede.apk 2>/dev/null || tar -xf luci-app-daede.apk 2>/dev/null || true
fi

chmod +x /etc/init.d/daed 2>/dev/null || true
chmod +x /etc/init.d/dae 2>/dev/null || true
chmod +x /usr/bin/daed 2>/dev/null || true
chmod +x /usr/bin/dae 2>/dev/null || true

/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
luci-reload 2>/dev/null || true
"""

stdin, stdout, stderr = client.exec_command(install_cmd)
print("Install Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

print("\n2. Verifying DAED installation & LuCI view...")
stdin, stdout, stderr = client.exec_command("which daed dae; ls -la /etc/init.d/daed /etc/init.d/dae /www/luci-static/resources/view/dae* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
