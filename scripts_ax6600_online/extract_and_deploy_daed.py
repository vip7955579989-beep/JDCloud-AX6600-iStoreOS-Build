import paramiko
import tarfile
import io

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

sftp = client.open_sftp()

print("1. Reading remote APK files from /tmp/daede-install/...")

for apk_name in ["daed.apk", "luci-app-daede.apk"]:
    remote_path = f"/tmp/daede-install/{apk_name}"
    print(f"\nProcessing {apk_name}...")
    try:
        remote_file = sftp.open(remote_path, 'rb')
        content = remote_file.read()
        remote_file.close()
        
        # 打开外部 tar 包
        tar = tarfile.open(fileobj=io.BytesIO(content), mode="r:*")
        print("Files inside APK container:", tar.getnames())
        
        # 寻找控制数据包和二进制数据包
        for member in tar.getmembers():
            if member.name.endswith(".tar.gz") or member.name.endswith(".tar.xz") or member.name == "data.tar.gz":
                print(f"  Extracting inner data tar: {member.name}")
                sub_data = tar.extractfile(member).read()
                sub_tar = tarfile.open(fileobj=io.BytesIO(sub_data), mode="r:*")
                for sub_member in sub_tar.getmembers():
                    print(f"    -> Component file: {sub_member.name}")
                    if sub_member.isfile():
                        file_data = sub_tar.extractfile(sub_member).read()
                        dest_path = "/" + sub_member.name.lstrip("/")
                        print(f"    Deploying to system: {dest_path}")
                        # 创建远程父目录
                        remote_dir = "/".join(dest_path.split("/")[:-1])
                        client.exec_command(f"mkdir -p '{remote_dir}'")
                        
                        f = sftp.open(dest_path, 'wb')
                        f.write(file_data)
                        f.close()
    except Exception as e:
        print(f"Error extracting {apk_name}: {e}")

sftp.close()

print("\n2. Activating DAED Services & Refreshing LuCI...")
activate_cmd = """
chmod +x /usr/bin/daed /usr/sbin/daed /usr/bin/dae /usr/sbin/dae 2>/dev/null || true
chmod +x /etc/init.d/daed /etc/init.d/dae /etc/init.d/daede 2>/dev/null || true

/etc/init.d/daed enable 2>/dev/null || true
/etc/init.d/daed start 2>/dev/null || true
/etc/init.d/daede enable 2>/dev/null || true
/etc/init.d/daede start 2>/dev/null || true

rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
/etc/init.d/uhttpd restart 2>/dev/null || true
luci-reload 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(activate_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n3. Final Verification of DAED Components...")
stdin, stdout, stderr = client.exec_command("which daed dae; ls -ld /etc/init.d/daed /etc/init.d/dae /etc/init.d/daede /www/luci-static/resources/view/dae* /usr/share/luci/menu.d/*dae* 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
