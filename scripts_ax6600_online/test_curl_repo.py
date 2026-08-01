import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

test_cmds = """
echo "=== Test 1: istore.linkease.com ==="
curl -s -L -A "Mozilla/5.0" "https://istore.linkease.com/repo/all/store/" | grep -i "ddnsto" | head -n 5

echo "=== Test 2: opkg/apk search in system ==="
apk search *ddnsto* 2>/dev/null
apk search *linkease* 2>/dev/null

echo "=== Test 3: Check /etc/opkg/customfeeds.conf or opkg repos ==="
cat /etc/opkg/customfeeds.conf 2>/dev/null
"""

stdin, stdout, stderr = client.exec_command(test_cmds)
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
