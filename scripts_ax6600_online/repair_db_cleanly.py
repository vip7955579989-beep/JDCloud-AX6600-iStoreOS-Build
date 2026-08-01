import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Repairing /lib/apk/db/installed database cleanly...")

repair_script = """
DB_FILE="/lib/apk/db/installed"

# 清理末尾错误脏数据
sed -i '/virtual_bpf/d' "$DB_FILE"
sed -i '/virtual_xdp/d' "$DB_FILE"
sed -i '/kmod-sched-bpf/d' "$DB_FILE"
sed -i '/kmod-xdp-sockets-diag/d' "$DB_FILE"
sed -i '/Built-in Kernel/d' "$DB_FILE"

# 规范追加标准 Block
cat << 'EOF' >> "$DB_FILE"

C:Q1virtual_bpf
P:kmod-sched-bpf
V:6.10.0-r1
A:aarch64_cortex-a53
S:100
I:100
T:Built-in Kernel BPF Scheduler Module

C:Q1virtual_xdp
P:kmod-xdp-sockets-diag
V:6.10.0-r1
A:aarch64_cortex-a53
S:100
I:100
T:Built-in Kernel XDP Socket Diag Module
EOF
"""

stdin, stdout, stderr = client.exec_command(repair_script)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Verifying 'apk info kmod-sched-bpf' & 'apk info kmod-xdp-sockets-diag'...")
stdin, stdout, stderr = client.exec_command("apk info kmod-sched-bpf kmod-xdp-sockets-diag")
print("Output:\n", stdout.read().decode('utf-8', errors='ignore'))

client.close()
