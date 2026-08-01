import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Injecting virtual kernel modules 'kmod-sched-bpf' & 'kmod-xdp-sockets-diag' into APK db...")

inject_script = """
DB_FILE="/lib/apk/db/installed"

if [ -f "$DB_FILE" ]; then
    if ! grep -q "P:kmod-sched-bpf" "$DB_FILE"; then
        echo "" >> "$DB_FILE"
        echo "C:Q1virtual_bpf" >> "$DB_FILE"
        echo "P:kmod-sched-bpf" >> "$DB_FILE"
        echo "V:6.10.0-r1" >> "$DB_FILE"
        echo "A:aarch64_cortex-a53" >> "$DB_FILE"
        echo "S:100" >> "$DB_FILE"
        echo "I:100" >> "$DB_FILE"
        echo "T:Built-in Kernel BPF Scheduler Module" >> "$DB_FILE"
    fi

    if ! grep -q "P:kmod-xdp-sockets-diag" "$DB_FILE"; then
        echo "" >> "$DB_FILE"
        echo "C:Q1virtual_xdp" >> "$DB_FILE"
        echo "P:kmod-xdp-sockets-diag" >> "$DB_FILE"
        echo "V:6.10.0-r1" >> "$DB_FILE"
        echo "A:aarch64_cortex-a53" >> "$DB_FILE"
        echo "S:100" >> "$DB_FILE"
        echo "I:100" >> "$DB_FILE"
        echo "T:Built-in Kernel XDP Socket Diag Module" >> "$DB_FILE"
    fi
fi
"""

stdin, stdout, stderr = client.exec_command(inject_script)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Verifying 'apk info kmod-sched-bpf kmod-xdp-sockets-diag' status...")
stdin, stdout, stderr = client.exec_command("apk info kmod-sched-bpf kmod-xdp-sockets-diag")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
