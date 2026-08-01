import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Checking local /tmp/daede-install directory or system repos for daed...")
check_cmd = """
if [ -d /tmp/daede-install ]; then
    ls -la /tmp/daede-install/
fi
"""
stdin, stdout, stderr = client.exec_command(check_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Attempting to install daed and luci-app-daed / luci-app-daede...")
install_cmd = """
installed=0
if [ -d /tmp/daede-install ]; then
    echo "[DAED Installer] Installing from local cached packages in /tmp/daede-install/..."
    apk add /tmp/daede-install/*.apk 2>&1
    installed=1
fi

if [ "$installed" = "0" ]; then
    echo "[DAED Installer] Trying online package repository..."
    apk add daed luci-app-daed luci-app-daede 2>&1
fi

# Enable and start service
chmod +x /etc/init.d/daed 2>/dev/null || true
chmod +x /etc/init.d/dae 2>/dev/null || true
/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true
/etc/init.d/dae enable 2>/dev/null || true
/etc/init.d/dae start 2>/dev/null || true

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
luci-reload 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(install_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n3. Verifying daed installation & UI files...")
stdin, stdout, stderr = client.exec_command("which daed dae; ls -ld /etc/init.d/daed /etc/init.d/dae /www/luci-static/resources/view/dae* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
