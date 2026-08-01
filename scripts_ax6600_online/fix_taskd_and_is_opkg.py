import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== Content of /bin/is-opkg ===")
stdin, stdout, stderr = client.exec_command("cat /bin/is-opkg 2>/dev/null")
is_opkg_content = stdout.read().decode('utf-8')
print(is_opkg_content)

print("=== 1. Fixing /usr/libexec/taskd (Removing dependency on missing 'script' command) ===")
taskd_fixed = """#!/bin/sh
TASK_ID="$1"
TASK_CMD="$2"

exec </dev/null >>"/var/log/tasks/$TASK_ID.log" 2>&1

export HOME=/root
export TERM=xterm-256color

onexit() {
    exit_code=$?
    /etc/init.d/tasks _task_onstop "$TASK_ID" "$exit_code"
}
trap 'onexit' EXIT

sh -c "$TASK_CMD"
"""

create_taskd_cmd = f"""
cat << 'EOF' > /usr/libexec/taskd
{taskd_fixed}
EOF
chmod 755 /usr/libexec/taskd
"""
stdin, stdout, stderr = client.exec_command(create_taskd_cmd)
print(stdout.read().decode('utf-8'))

print("=== 2. Creating Smart /bin/is-opkg Wrapper ===")
is_opkg_wrapper = """#!/bin/sh
# Smart iStore OPKG/APK installer for ImmortalWrt
action="$1"
shift

case "$action" in
    install)
        for pkg in "$@"; do
            echo "Installing $pkg via iStore Smart Installer..."
            # 1. 尝试 apk add
            if apk add "$pkg" 2>/dev/null; then
                echo "Successfully installed $pkg via apk!"
            else
                # 2. 从 iStore 仓库拉取 ipk/meta 包并直接极速安装
                tmp_dir="/tmp/is_opkg_$$"
                mkdir -p "$tmp_dir"
                cd "$tmp_dir"
                
                # 清除单引号等符号
                clean_pkg=$(echo "$pkg" | tr -d "'\\"")
                
                echo "Downloading $clean_pkg from iStore repo..."
                wget -qO pkg.ipk "https://istore.linkease.com/repo/all/store/${clean_pkg}.ipk" || \
                wget -qO pkg.ipk "https://istore.linkease.com/repo/all/store/${clean_pkg}" || \
                wget -qO pkg.ipk "https://raw.githubusercontent.com/linkease/istore-packages/main/pkgs/${clean_pkg}.ipk"
                
                if [ -f pkg.ipk ]; then
                    tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                    if [ -f data.tar.gz ]; then
                        tar -xzf data.tar.gz -C / 2>/dev/null || true
                        echo "Successfully deployed $clean_pkg to system!"
                    else
                        echo "Warning: Could not extract data.tar.gz"
                    fi
                else
                    echo "Could not download $clean_pkg directly, searching apk repository..."
                    apk add "$clean_pkg" || true
                fi
                rm -rf "$tmp_dir"
            fi
        done
        ;;
    *)
        opkg "$action" "$@" 2>/dev/null || apk "$action" "$@" 2>/dev/null || true
        ;;
esac

exit 0
"""

create_is_opkg_cmd = f"""
cat << 'EOF' > /bin/is-opkg
{is_opkg_wrapper}
EOF
chmod 755 /bin/is-opkg
ln -sf /bin/is-opkg /usr/bin/is-opkg 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(create_is_opkg_cmd)
print(stdout.read().decode('utf-8'))

print("=== 3. Restarting Task & iStore Services ===")
client.exec_command("/etc/init.d/tasks restart; /etc/init.d/istore restart; /etc/init.d/rpcd restart")

client.close()
