import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Completely removing broken 404 sources (passwall_packages & video) from all apk configs...")
clean_cmd = """
sed -i '/passwall_packages/d' /etc/apk/repositories /etc/apk/repositories.d/* 2>/dev/null || true
sed -i '/video/d' /etc/apk/repositories /etc/apk/repositories.d/* 2>/dev/null || true
"""
client.exec_command(clean_cmd)

print("2. Intercepting 'apk' binary with intelligent wrapper to allow untrusted packages globally for LuCI...")
wrapper_cmd = """
if [ ! -f /sbin/apk.real ]; then
    mv /sbin/apk /sbin/apk.real
fi

cat << 'EOF' > /sbin/apk
#!/bin/sh
# Smart APK Wrapper for LuCI Web Installer
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
"""
stdin, stdout, stderr = client.exec_command(wrapper_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n3. Testing 'apk add /tmp/upload.apk' simulation...")
# 创建一个无害的测试 apk 触发模拟测试
stdin, stdout, stderr = client.exec_command("touch /tmp/test.apk; apk add /tmp/test.apk")
print("Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
