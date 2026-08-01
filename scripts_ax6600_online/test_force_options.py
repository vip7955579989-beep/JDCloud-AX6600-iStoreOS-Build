import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Checking all --force options supported by apk...")
stdin, stdout, stderr = client.exec_command("/sbin/apk.real add --help | grep -E 'force|allow|skip|ignore'")
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n2. Testing force installation of daed...")
stdin, stdout, stderr = client.exec_command("/sbin/apk.real add --allow-untrusted --force-broken-world --force /tmp/daede-install/daed.apk /tmp/daede-install/luci-app-daede.apk")
print("Output:", stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
