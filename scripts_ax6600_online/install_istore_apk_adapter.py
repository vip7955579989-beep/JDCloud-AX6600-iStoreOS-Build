import paramiko
import re
import urllib.request

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

print("1. Fetching iStore Official Package Repository...")
repo_url = "https://istore.linkease.com/repo/all/store/"
req = urllib.request.Request(repo_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8')
    ipks = re.findall(r'href=["\']([^"\']+\.ipk)["\']', html)
    ipks = sorted(list(set(ipks)))
    print(f"Found {len(ipks)} packages in iStore repo:")
    for ipk in ipks:
        print("  -", ipk)
except Exception as e:
    print("Error fetching repo:", e)
    ipks = []

# 筛选 store 和 istore 相关的 ipk
target_ipks = [f for f in ipks if 'luci-app-store' in f or 'luci-i18n-store' in f or 'istore' in f]
print("\nTarget Packages to Install:", target_ipks)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"\n2. Connecting to router {host}...")
    client.connect(host, port=port, username=username, password=password, timeout=10)
    print("SSH Connection successful!")

    # 创建工作目录
    cmd_init = "rm -rf /tmp/istore_pkg && mkdir -p /tmp/istore_pkg"
    client.exec_command(cmd_init)

    for ipk in target_ipks:
        file_url = repo_url + ipk
        print(f"\nDownloading & Deploying {ipk}...")
        deploy_cmd = f"""
        cd /tmp/istore_pkg
        wget -qO "{ipk}" "{file_url}"
        if [ -f "{ipk}" ]; then
            tar -xzf "{ipk}" data.tar.gz 2>/dev/null || true
            if [ -f "data.tar.gz" ]; then
                tar -xzf "data.tar.gz" -C / 2>/dev/null || true
                rm -f data.tar.gz
                echo "Successfully extracted {ipk} to system root!"
            fi
        fi
        """
        stdin, stdout, stderr = client.exec_command(deploy_cmd)
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        print(out)
        if err:
            print("LOG:", err)

    # 刷写 LuCI 缓存与重启服务
    print("\n3. Reloading LuCI & Web Services...")
    reload_cmd = """
    rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
    /etc/init.d/uhttpd restart || true
    /etc/init.d/nginx restart || true
    luci-reload || true
    """
    stdin, stdout, stderr = client.exec_command(reload_cmd)
    print(stdout.read().decode('utf-8'))

    # 验证文件是否就位
    print("\n4. Verification...")
    stdin, stdout, stderr = client.exec_command("ls -la /usr/lib/lua/luci/controller/store* /www/luci-static/resources/view/store* 2>/dev/null; ls -la /etc/config/luci_plugins 2>/dev/null")
    print(stdout.read().decode('utf-8'))

finally:
    client.close()
