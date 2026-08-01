import os
import sys
import io
import tarfile
import urllib.request
import paramiko

def extract_ipk_data(ipk_bytes):
    """从 ipk (ar/tar格式) 中提取 data.tar.gz 或 data.tar.* 字节流"""
    # 判断是否为 gzipped tar 格式
    if ipk_bytes.startswith(b'\x1f\x8b'):
        with tarfile.open(fileobj=io.BytesIO(ipk_bytes), mode="r:gz") as tf:
            for member in tf.getmembers():
                if 'data.tar' in member.name:
                    return tf.extractfile(member).read()
    
    # 判断是否为 ar 存档格式 (!<arch>\n)
    if ipk_bytes.startswith(b'!<arch>\n'):
        pos = 8
        length = len(ipk_bytes)
        while pos < length:
            header = ipk_bytes[pos:pos+60]
            if len(header) < 60:
                break
            filename = header[:16].decode('utf-8', errors='ignore').strip()
            try:
                size = int(header[48:58].decode('utf-8', errors='ignore').strip())
            except ValueError:
                break
            file_data = ipk_bytes[pos+60 : pos+60+size]
            if 'data.tar' in filename:
                return file_data
            pos += 60 + size + (size % 2) # ar header padding
    return None

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

# 需要物理注入的 4 个 iStore 核心与依赖包
ipk_urls = [
    "https://istore.linkease.com/repo/all/store/luci-app-store_0.2.0-r3_all.ipk",
    "https://istore.linkease.com/repo/all/store/luci-lib-taskd_1.0.25_all.ipk",
    "https://istore.linkease.com/repo/all/store/luci-lib-xterm_4.18.0_all.ipk",
    "https://istore.linkease.com/repo/all/store/taskd_1.0.3-2_all.ipk",
]

print("1. Downloading & Extracting iStore Packages locally...")
local_extract_dir = os.path.join(os.path.dirname(__file__), "istore_root_files")
os.makedirs(local_extract_dir, exist_ok=True)

for url in ipk_urls:
    pkg_name = os.path.basename(url)
    print(f"  Downloading {pkg_name}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    ipk_bytes = urllib.request.urlopen(req).read()
    
    data_bytes = extract_ipk_data(ipk_bytes)
    if data_bytes:
        print(f"    Extracted data.tar for {pkg_name} ({len(data_bytes)} bytes)")
        # 解压到本地目录
        with tarfile.open(fileobj=io.BytesIO(data_bytes)) as tf:
            tf.extractall(local_extract_dir)
    else:
        print(f"    ⚠️ Warning: Could not extract data.tar from {pkg_name}")

print(f"\n2. Connecting to Router {host} via SSH/SFTP...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port=port, username=username, password=password, timeout=10)
sftp = ssh.open_sftp()

print("\n3. Syncing Files to Router Root System...")
uploaded_count = 0
for root, dirs, files in os.walk(local_extract_dir):
    rel_path = os.path.relpath(root, local_extract_dir)
    remote_dir = "/" if rel_path == "." else "/" + rel_path.replace("\\", "/")
    
    # 确保远端目录存在
    try:
        sftp.stat(remote_dir)
    except IOError:
        ssh.exec_command(f"mkdir -p '{remote_dir}'")
    
    for f in files:
        local_file = os.path.join(root, f)
        remote_file = (remote_dir + "/" + f).replace("//", "/")
        try:
            sftp.put(local_file, remote_file)
            uploaded_count += 1
        except Exception as e:
            print(f"    Failed to upload {remote_file}: {e}")

print(f"Successfully uploaded {uploaded_count} system files to router!")

sftp.close()

print("\n4. Finalizing Configuration & Reloading LuCI UI...")
commands = """
chmod +x /etc/init.d/taskd 2>/dev/null || true
chmod +x /usr/bin/taskd 2>/dev/null || true
chmod +x /usr/sbin/taskd 2>/dev/null || true

/etc/init.d/taskd enable 2>/dev/null || true
/etc/init.d/taskd start 2>/dev/null || true

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
/etc/init.d/uhttpd restart 2>/dev/null || true
luci-reload 2>/dev/null || true
"""
stdin, stdout, stderr = ssh.exec_command(commands)
print(stdout.read().decode('utf-8', errors='ignore'))

# 验证控制点
stdin, stdout, stderr = ssh.exec_command("ls -d /usr/lib/lua/luci/controller/store /www/luci-static/resources/view/store 2>/dev/null; pgrep taskd || true")
print("Verification Result:\n", stdout.read().decode('utf-8', errors='ignore'))

ssh.close()
print("\n🎉 iStore 软件商店成功完成全自动绿色部署！")
