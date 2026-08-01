import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Injecting standard APK db block for kmod-xdp-sockets-diag...")

inject_script = """
DB_FILE="/lib/apk/db/installed"

# 先清理可能残存的无效行
sed -i '/kmod-xdp-sockets-diag/d' "$DB_FILE"
sed -i '/virtual_xdp/d' "$DB_FILE"

# 追加标准的 apk db 记录项
cat << 'EOF' >> "$DB_FILE"

C:Q1virtual_xdp
P:kmod-xdp-sockets-diag
V:6.10.0-r1
A:aarch64_cortex-a53
S:100
I:100
T:Built-in Kernel XDP Socket Diag Module
EOF
"""

stdin, stdout, stderr = client.exec_command(inject_script)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Verifying 'apk info kmod-xdp-sockets-diag' status...")
stdin, stdout, stderr = client.exec_command("apk info kmod-xdp-sockets-diag")
print("Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
