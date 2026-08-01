import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

activate_cmds = """
# 运行 uci-defaults 默认激活脚本
if [ -f /etc/uci-defaults/luci-app-store ]; then
    sh /etc/uci-defaults/luci-app-store || true
fi

# 启动并使能 iStore 后台守护进程与 taskd
/etc/init.d/istore enable 2>/dev/null || true
/etc/init.d/istore start 2>/dev/null || true

/etc/init.d/taskd enable 2>/dev/null || true
/etc/init.d/taskd start 2>/dev/null || true

# 清理缓存重启 LuCI Web 服务
rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
/etc/init.d/uhttpd restart 2>/dev/null || true
/etc/init.d/rpcd restart 2>/dev/null || true
luci-reload 2>/dev/null || true
"""

stdin, stdout, stderr = client.exec_command(activate_cmds)
print("Activation Output:\n", stdout.read().decode('utf-8', errors='ignore'))

# 验证状态
stdin, stdout, stderr = client.exec_command("ps | grep -E 'istore|taskd'; uci show istore 2>/dev/null")
print("Running Services & UCI Config:\n", stdout.read().decode('utf-8', errors='ignore'))

client.close()
