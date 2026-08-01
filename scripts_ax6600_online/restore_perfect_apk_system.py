import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Restoring pure ELF binary from /rom/usr/bin/apk to /sbin/apk.real...")
restore_cmd = """
cp -f /rom/usr/bin/apk /sbin/apk.real
chmod 755 /sbin/apk.real

cat << 'EOF' > /sbin/apk
#!/bin/sh
has_add=0
for arg in "$@"; do
    if [ "$arg" = "add" ]; then
        has_add=1
        break
    fi
done

if [ "$has_add" = "1" ]; then
    exec /sbin/apk.real "$@" --allow-untrusted
else
    exec /sbin/apk.real "$@"
fi
EOF

chmod 755 /sbin/apk
cp -f /sbin/apk /usr/bin/apk 2>/dev/null || true
cp -f /sbin/apk /bin/apk 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(restore_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Verifying restored APK system...")
stdin, stdout, stderr = client.exec_command("/sbin/apk --version; /usr/bin/apk --version; /bin/apk --version")
print("Version Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

print("\n3. Testing 'apk add' with untrusted package simulation...")
stdin, stdout, stderr = client.exec_command("touch /tmp/test_pkg.apk; apk add /tmp/test_pkg.apk")
print("Add Simulation Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
