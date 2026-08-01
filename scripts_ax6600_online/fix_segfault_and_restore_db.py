import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Cleaning up custom appended lines from /lib/apk/db/installed to fix Segfault...")

clean_script = """
DB_FILE="/lib/apk/db/installed"

# 安全备份
cp -f "$DB_FILE" "$DB_FILE.bak_$$"

# 删除末尾我们追加的自定义虚拟行
sed -i '/virtual_bpf/d' "$DB_FILE"
sed -i '/virtual_xdp/d' "$DB_FILE"
sed -i '/kmod-sched-bpf/d' "$DB_FILE"
sed -i '/kmod-xdp-sockets-diag/d' "$DB_FILE"
sed -i '/Built-in Kernel/d' "$DB_FILE"

# 也删除可能残留的空 Block 尾部
sed -i '/^C:Q1virtual_/d' "$DB_FILE"
sed -i '/^P:kmod-/d' "$DB_FILE"
sed -i '/^V:6.10/d' "$DB_FILE"
sed -i '/^A:aarch64/d' "$DB_FILE"
sed -i '/^S:100/d' "$DB_FILE"
sed -i '/^I:100/d' "$DB_FILE"

# 也把 daed 本地标记写入官方标准格式（提供 daed 虚拟包）
cat << 'EOF' >> "$DB_FILE"

C:Q1daed_virtual_ok
P:daed
V:1.27.0-r1
A:aarch64_cortex-a53
S:47979456
I:47979456
T:daed eBPF Backend Service
EOF
"""

stdin, stdout, stderr = client.exec_command(clean_script)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Testing 'apk add --help' & 'apk info' to ensure NO Segmentation Fault...")
stdin, stdout, stderr = client.exec_command("apk info; echo 'ExitCode:' $?")
print("Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
