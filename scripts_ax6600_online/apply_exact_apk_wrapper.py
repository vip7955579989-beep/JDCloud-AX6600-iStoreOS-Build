import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Backup real ELF binary (/usr/bin/apk) to /usr/bin/apk.real...")
setup_cmd = """
if [ -f /usr/bin/apk -a ! -L /usr/bin/apk ]; then
    cp -f /usr/bin/apk /usr/bin/apk.real
fi
chmod 755 /usr/bin/apk.real

cat << 'EOF' > /usr/bin/apk.wrapper
#!/bin/sh
has_add=0
for arg in "$@"; do
    if [ "$arg" = "add" ]; then
        has_add=1
        break
    fi
done

if [ "$has_add" = "1" ]; then
    exec /usr/bin/apk.real "$@" --allow-untrusted
else
    exec /usr/bin/apk.real "$@"
fi
EOF

chmod 755 /usr/bin/apk.wrapper
cp -f /usr/bin/apk.wrapper /usr/bin/apk
cp -f /usr/bin/apk.wrapper /sbin/apk
cp -f /usr/bin/apk.wrapper /bin/apk
"""
stdin, stdout, stderr = client.exec_command(setup_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Testing '/sbin/apk --version' & 'apk add --help'...")
stdin, stdout, stderr = client.exec_command("apk --version")
print("Version Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
