import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Downloading official kenzok8/openwrt-daede release components...")

deploy_script = """
tmp_dir="/tmp/kenzok8_daed_$$"
mkdir -p "$tmp_dir"
cd "$tmp_dir"

echo "[kenzok8-daede] Downloading daed binary package..."
wget -q --timeout=15 "https://ghp.ci/https://github.com/kenzok8/openwrt-daede/releases/download/v2026.08.01.1/daed-2026.07.31-r4-aarch64_cortex-a53.apk" -O daed.apk || \
wget -q --timeout=15 "https://github.com/kenzok8/openwrt-daede/releases/download/v2026.08.01.1/daed-2026.07.31-r4-aarch64_cortex-a53.apk" -O daed.apk

echo "[kenzok8-daede] Downloading luci-app-daede UI package..."
wget -q --timeout=15 "https://ghp.ci/https://github.com/kenzok8/openwrt-daede/releases/download/v2026.08.01.1/luci-app-daede-1.14.7-r20-aarch64_cortex-a53.apk" -O luci-app-daede.apk || \
wget -q --timeout=15 "https://github.com/kenzok8/openwrt-daede/releases/download/v2026.08.01.1/luci-app-daede-1.14.7-r20-aarch64_cortex-a53.apk" -O luci-app-daede.apk

echo "[kenzok8-daede] Extracting daed.apk into system..."
mkdir -p daed_out
cd daed_out
/sbin/apk.real extract --allow-untrusted "$tmp_dir/daed.apk" 2>&1
cp -a * / 2>/dev/null || true
cd "$tmp_dir"

echo "[kenzok8-daede] Extracting luci-app-daede.apk into system..."
mkdir -p luci_out
cd luci_out
/sbin/apk.real extract --allow-untrusted "$tmp_dir/luci-app-daede.apk" 2>&1
cp -a * / 2>/dev/null || true

rm -rf "$tmp_dir"

chmod +x /usr/bin/daed /usr/sbin/daed /usr/bin/dae /usr/sbin/dae 2>/dev/null || true
chmod +x /etc/init.d/daed /etc/init.d/dae /etc/init.d/daede 2>/dev/null || true

/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true
/etc/init.d/dae enable 2>/dev/null || true
/etc/init.d/dae start 2>/dev/null || true

# 写入 iStore 面板呈现记录
mkdir -p /usr/share/istore/run-records
ts=$(date '+%s')
record_file="/usr/share/istore/run-records/$ts-app-meta-daede.txt"
echo "{\\"id\\":\\"$ts-app-meta-daede\\",\\"ts\\":$ts,\\"md5\\":\\"app-meta-daede\\",\\"file\\":\\"app-meta-daede\\"}" > "$record_file"
echo "app-meta-daede" >> "$record_file"
echo "luci-app-daede" >> "$record_file"
echo "daed" >> "$record_file"

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
luci-reload 2>/dev/null || true
"""

stdin, stdout, stderr = client.exec_command(deploy_script)
print("Deploy Output:\n", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:\n", stderr.read().decode('utf-8', errors='ignore'))

print("\n2. Verifying kenzok8/openwrt-daede components on router...")
stdin, stdout, stderr = client.exec_command("which daed dae; ls -la /usr/bin/dae* /etc/init.d/dae* /usr/share/luci/menu.d/*dae* /www/luci-static/resources/view/*dae* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
