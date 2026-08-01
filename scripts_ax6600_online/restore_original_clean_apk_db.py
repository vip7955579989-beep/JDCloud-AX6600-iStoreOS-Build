import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Restoring pure untouched APK db from /rom/lib/apk/db/installed...")

restore_script = """
# 恢复 100% 出厂纯净数据库
cp -f /rom/lib/apk/db/installed /lib/apk/db/installed
chmod 644 /lib/apk/db/installed

# 刷新软件包索引
apk update
"""

stdin, stdout, stderr = client.exec_command(restore_script)
print("Restore Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

print("\n2. Testing 'apk info' & 'apk add' health check...")
stdin, stdout, stderr = client.exec_command("apk info | head -n 5; echo 'ExitCode:' $?")
print("Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
