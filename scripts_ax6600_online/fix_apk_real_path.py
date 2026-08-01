import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Locating real ELF binary for apk...")
stdin, stdout, stderr = client.exec_command("find /sbin /usr/bin /bin -name '*apk*' -type f 2>/dev/null; ls -la /sbin/apk* /usr/bin/apk* /bin/apk* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n2. Restoring clean real binary link and updating wrapper...")
fix_script = """
# 找到真实 ELF 二进制文件
REAL_APK=""
for p in /sbin/apk.real /usr/bin/apk /bin/apk /sbin/apk.bin; do
    if [ -f "$p" ] && file "$p" 2>/dev/null | grep -q "ELF"; then
        REAL_APK="$p"
        break
    fi
done

if [ -z "$REAL_APK" ]; then
    # 查找任意系统中的 ELF 格式 apk
    REAL_APK=$(file /sbin/* /usr/bin/* /bin/* 2>/dev/null | grep "ELF" | grep "apk" | cut -d: -f1 | head -n 1)
fi

echo "Detected REAL_APK path: $REAL_APK"

if [ -n "$REAL_APK" -a "$REAL_APK" != "/sbin/apk.binary" ]; then
    cp -f "$REAL_APK" /sbin/apk.binary
    chmod 755 /sbin/apk.binary
fi

# 重构 /sbin/apk 为绝对可靠的二进制包 Wrapper
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
    exec /sbin/apk.binary "$@" --allow-untrusted
else
    exec /sbin/apk.binary "$@"
fi
EOF

chmod 755 /sbin/apk
ln -sf /sbin/apk /usr/bin/apk 2>/dev/null || true
ln -sf /sbin/apk /bin/apk 2>/dev/null || true
"""

stdin, stdout, stderr = client.exec_command(fix_script)
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n3. Testing execution of '/sbin/apk --version'...")
stdin, stdout, stderr = client.exec_command("/sbin/apk --version")
print(stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
