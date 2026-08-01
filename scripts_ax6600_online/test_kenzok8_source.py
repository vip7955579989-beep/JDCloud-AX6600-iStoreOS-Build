import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Searching for Releases in kenzok8/openwrt-daede...")
test_cmd = """
curl -s -L https://api.github.com/repos/kenzok8/openwrt-daede/releases/latest | grep -iE 'browser_download_url.*(ipk|apk)' | cut -d'"' -f4
"""
stdin, stdout, stderr = client.exec_command(test_cmd)
urls = stdout.read().decode('utf-8', errors='ignore')
print("GitHub Release URLs:\n", urls)

client.close()
