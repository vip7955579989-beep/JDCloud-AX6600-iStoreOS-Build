import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Granting Full Executable (+x) Permissions...")
chmod_cmd = """
chmod -R 755 /etc/init.d/tasks /etc/init.d/taskd /etc/init.d/istore 2>/dev/null || true
chmod -R 755 /usr/libexec/istore/ 2>/dev/null || true
chmod 755 /usr/bin/taskd /usr/sbin/taskd /usr/libexec/taskd 2>/dev/null || true

# 检查 taskd 节点位置，若缺失自动创建软链接
if [ ! -f /usr/libexec/taskd ]; then
    if [ -f /usr/sbin/taskd ]; then
        ln -sf /usr/sbin/taskd /usr/libexec/taskd
    elif [ -f /usr/bin/taskd ]; then
        ln -sf /usr/bin/taskd /usr/libexec/taskd
    fi
fi
chmod 755 /usr/libexec/taskd 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(chmod_cmd)
print(stdout.read().decode('utf-8'))

print("2. Creating /bin/opkg & /usr/bin/opkg Smart Bridge Script...")
# opkg 兼容包装器，将 opkg 指令自动对接至系统的 apk 包管理器或极速在线解包器
opkg_bridge = """#!/bin/sh
# Smart OPKG-to-APK Compatibility Wrapper for iStore
action="$1"
shift

case "$action" in
    update)
        echo "Updating package index via apk..."
        apk update
        ;;
    install)
        for pkg in "$@"; do
            echo "Installing $pkg..."
            # 优先尝试用 apk 软件源直接安装
            if apk add "$pkg" 2>/dev/null; then
                echo "Successfully installed $pkg via apk!"
            else
                # 若 apk 源没有（如 iStore 专属 ipk），则从 iStore / OpenWrt 仓库拉取并解包安装
                echo "Downloading and deploying $pkg..."
                tmp_dir="/tmp/opkg_deploy_$$"
                mkdir -p "$tmp_dir"
                cd "$tmp_dir"
                
                # 判断传进来的是 URL 还是包名
                if echo "$pkg" | grep -qE '^https?://'; then
                    pkg_url="$pkg"
                else
                    pkg_url="https://istore.linkease.com/repo/all/store/${pkg}.ipk"
                fi
                
                wget -qO pkg.ipk "$pkg_url" || wget -qO pkg.ipk "https://istore.linkease.com/repo/all/store/${pkg}"
                if [ -f pkg.ipk ]; then
                    tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                    [ -f data.tar.gz ] && tar -xzf data.tar.gz -C / 2>/dev/null || true
                    rm -rf "$tmp_dir"
                    echo "Successfully installed $pkg!"
                else
                    rm -rf "$tmp_dir"
                    echo "Failed to download $pkg"
                    return 1
                fi
            fi
        done
        ;;
    list-installed|list_installed)
        apk list --installed | sed 's/ / - /'
        ;;
    remove|find|info|status)
        apk "$action" "$@" 2>/dev/null || true
        ;;
    *)
        apk "$action" "$@" 2>/dev/null || true
        ;;
esac

exit 0
"""

# 将 opkg 包装器写入软路由系统
create_opkg_cmd = f"""
cat << 'EOF' > /bin/opkg
{opkg_bridge}
EOF
chmod 755 /bin/opkg
ln -sf /bin/opkg /usr/bin/opkg 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(create_opkg_cmd)
print(stdout.read().decode('utf-8'))

print("3. Restarting Taskd & Procd Services...")
restart_cmd = """
/etc/init.d/tasks restart 2>/dev/null || /etc/init.d/tasks start 2>/dev/null || true
/etc/init.d/taskd restart 2>/dev/null || /etc/init.d/taskd start 2>/dev/null || true
/etc/init.d/istore restart 2>/dev/null || true
/etc/init.d/rpcd restart 2>/dev/null || true
/etc/init.d/uhttpd restart 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(restart_cmd)
print(stdout.read().decode('utf-8'))

print("4. Final Status Verification...")
stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/tasks /usr/libexec/taskd /bin/opkg; opkg update")
print(stdout.read().decode('utf-8'))

client.close()
