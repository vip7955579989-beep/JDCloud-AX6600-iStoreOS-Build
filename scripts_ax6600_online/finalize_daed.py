import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Adding iStore run_record for DAED & Enabling service...")
final_cmd = """
# 写入 iStore 已安装记录
mkdir -p /usr/share/istore/run-records
ts=$(date '+%s')
record_file="/usr/share/istore/run-records/$ts-app-meta-daede.txt"
echo "{\\"id\\":\\"$ts-app-meta-daede\\",\\"ts\\":$ts,\\"md5\\":\\"app-meta-daede\\",\\"file\\":\\"app-meta-daede\\"}" > "$record_file"
echo "app-meta-daede" >> "$record_file"
echo "luci-app-daede" >> "$record_file"
echo "daed" >> "$record_file"

# 尝试启动守护服务
chmod +x /etc/init.d/daed
/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true

# 刷新 UI 菜单
rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
luci-reload 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(final_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Checking process status of daed...")
stdin, stdout, stderr = client.exec_command("ps | grep -i daed | grep -v grep")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
