import sys
import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to router {host}...")
    client.connect(host, port=port, username=username, password=password, timeout=10)
    print("SSH Connection successful!")

    # 安装命令方案列表 (包含 github 镜像加速)
    install_cmds = [
        "curl -fsSL https://fastly.jsdelivr.net/gh/linkease/istore@main/install/openwrt_install.sh | sh",
        "curl -fsSL https://raw.githubusercontent.com/linkease/istore/main/install/openwrt_install.sh | sh",
        "wget -qO- https://raw.githubusercontent.com/linkease/istore/main/install/openwrt_install.sh | sh",
    ]

    installed_success = False
    for idx, cmd in enumerate(install_cmds, 1):
        print(f"\n--- Trying iStore Install Option {idx} ---")
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # 实时打印安装日志
        for line in stdout:
            print(line, end="")
        err = stderr.read().decode("utf-8", errors="ignore")
        if err:
            print("STDERR/INFO:", err)

        # 检查是否成功安装 luci-app-store
        stdin, stdout, stderr = client.exec_command("opkg list-installed | grep luci-app-store")
        res = stdout.read().decode("utf-8", errors="ignore").strip()
        if res:
            print(f"\n✅ iStore 软件商店安装成功！软件包信息: {res}")
            installed_success = True
            break

    if not installed_success:
        print("\n--- Fallback: Manual OPKG Repo Configuration ---")
        # 手动向 opkg 添加 linkease 软件源并安装
        manual_script = """
        echo 'src/gz linkease_store https://istore.linkease.com/repo/all/store' >> /etc/opkg/customfeeds.conf
        opkg update
        opkg install luci-app-store
        """
        stdin, stdout, stderr = client.exec_command(manual_script)
        for line in stdout:
            print(line, end="")
        err = stderr.read().decode("utf-8", errors="ignore")
        if err:
            print("STDERR:", err)

    # 最终结果校验与重启 LuCI 界面
    print("\n--- Final Verification & Service Reload ---")
    stdin, stdout, stderr = client.exec_command("opkg list-installed | grep -E 'luci-app-store|istore'; /etc/init.d/luci-reload restart || true")
    final_res = stdout.read().decode("utf-8", errors="ignore").strip()
    print("Installed Store Packages:\n", final_res)

finally:
    client.close()
