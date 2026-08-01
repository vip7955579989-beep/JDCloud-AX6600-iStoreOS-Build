import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Installing DAED via '--no-deps' flag or direct extraction...")
deploy_script = """
# 1. 尝试使用 apk --no-deps 正式注册安装
/sbin/apk.real add --allow-untrusted --no-deps /tmp/daede-install/daed.apk /tmp/daede-install/luci-app-daede.apk 2>&1

# 2. 如果包管理器未写入物理二进制，直接解压部署
if [ ! -f /usr/bin/daed -a ! -f /usr/sbin/daed ]; then
    echo "[DAED] Extracting data.tar.gz to system root..."
    tmp_extract="/tmp/daed_extract_$$"
    mkdir -p "$tmp_extract"
    cd "$tmp_extract"
    
    tar -xzf /tmp/daede-install/daed.apk 2>/dev/null || true
    [ -f data.tar.gz ] && tar -xzf data.tar.gz -C / 2>/dev/null || true
    rm -rf "$tmp_extract/*"
    
    tar -xzf /tmp/daede-install/luci-app-daede.apk 2>/dev/null || true
    [ -f data.tar.gz ] && tar -xzf data.tar.gz -C / 2>/dev/null || true
    rm -rf "$tmp_extract"
fi

# 3. 授权并开机自启
chmod +x /usr/bin/daed 2>/dev/null || true
chmod +x /usr/sbin/daed 2>/dev/null || true
chmod +x /etc/init.d/daed 2>/dev/null || true
chmod +x /etc/init.d/dae 2>/dev/null || true

/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
luci-reload 2>/dev/null || true
"""

stdin, stdout, stderr = client.exec_command(deploy_script)
print("Deploy Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

print("\n2. Verifying DAED Binaries & Web Interface Files...")
stdin, stdout, stderr = client.exec_command("which daed dae; ls -ld /usr/bin/daed /etc/init.d/daed /www/luci-static/resources/view/daed* /www/luci-static/resources/view/dae* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
