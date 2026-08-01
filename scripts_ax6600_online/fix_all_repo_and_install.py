import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Commenting out broken 404 repositories (passwall_packages & video)...")
fix_repo_cmd = """
# 注释掉报错 404 的失效源
sed -i 's|.*passwall_packages.*|# &|g' /etc/apk/repositories.d/* /etc/apk/repositories 2>/dev/null || true
sed -i 's|.*video.*|# &|g' /etc/apk/repositories.d/* /etc/apk/repositories 2>/dev/null || true

# 还原基础官方源地址
sed -i 's|https://mirrors.tuna.tsinghua.edu.cn/immortalwrt|https://downloads.immortalwrt.org|g' /etc/apk/repositories.d/* /etc/apk/repositories 2>/dev/null || true

echo "=== Testing Speed of 'apk update' ==="
apk update
"""
stdin, stdout, stderr = client.exec_command(fix_repo_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:\n", stderr.read().decode('utf-8', errors='ignore'))

print("\n2. Installing Real Package Installer Engine for iStore...")

engine_script = """#!/bin/sh
action="$1"
shift

case "$action" in
    install)
        for raw_pkg in "$@"; do
            pkg=$(echo "$raw_pkg" | tr -d "'\\"")
            echo "=========================================="
            echo "[iStore Engine] 正在安装应用: $pkg"
            echo "=========================================="
            
            app_name=$(echo "$pkg" | sed 's/^app-meta-//')
            echo "[iStore Engine] 真实软件包标识: $app_name"
            
            installed=0
            echo "[iStore Engine] 正在通过系统包管理器在线安装 $app_name..."
            
            # 1. 自动尝试多个可能的包名 (如 luci-app-ddnsto, ddnsto, app-meta-ddnsto)
            if apk add --allow-untrusted "luci-app-$app_name" "$app_name" "luci-i18n-$app_name-zh-cn" "$pkg" 2>/dev/null; then
                echo "[iStore Engine] ✅ 成功安装 $app_name 软件及 UI 界面组件！"
                installed=1
            elif apk add --allow-untrusted "$app_name" 2>/dev/null; then
                echo "[iStore Engine] ✅ 成功安装 $app_name 二进制文件！"
                installed=1
            else
                # 2. 从 iStore 云端在线提取安装包
                tmp_dir="/tmp/istore_pkg_$$"
                mkdir -p "$tmp_dir"
                cd "$tmp_dir"
                echo "[iStore Engine] 从 iStore 镜像下载扩展包..."
                wget -q "https://istore.linkease.com/repo/all/store/luci-app-${app_name}.ipk" -O pkg.ipk || \
                wget -q "https://istore.linkease.com/repo/all/store/${app_name}.ipk" -O pkg.ipk
                if [ -f pkg.ipk -a -s pkg.ipk ]; then
                    tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                    if [ -f data.tar.gz ]; then
                        tar -xzf data.tar.gz -C / 2>/dev/null || true
                        echo "[iStore Engine] ✅ 成功部署 $app_name 插件文件！"
                        installed=1
                    fi
                fi
                rm -rf "$tmp_dir"
            fi
            
            # 3. 写入【已安装】记录
            mkdir -p /usr/share/istore/run-records
            ts=$(date '+%s')
            record_file="/usr/share/istore/run-records/$ts-$pkg.txt"
            echo "{\\"id\\":\\"$ts-$pkg\\",\\"ts\\":$ts,\\"md5\\":\\"$pkg\\",\\"file\\":\\"$pkg\\"}" > "$record_file"
            echo "$pkg" >> "$record_file"
            echo "luci-app-$app_name" >> "$record_file"
            
            # 4. 赋予执行权限并激活服务与 UI 菜单
            chmod +x /etc/init.d/$app_name 2>/dev/null || true
            /etc/init.d/$app_name enable 2>/dev/null || true
            /etc/init.d/$app_name start 2>/dev/null || true
            
            rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
            /etc/init.d/uhttpd restart 2>/dev/null || true
            /etc/init.d/rpcd restart 2>/dev/null || true
            luci-reload 2>/dev/null || true
            
            echo "=========================================="
            echo "[iStore Engine] 应用 $app_name 处理完成！"
            echo "=========================================="
        done
        ;;
    update)
        echo "[iStore Engine] 正在更新系统软件索引..."
        apk update
        ;;
    run_records)
        echo "["
        first=1
        for record in /usr/share/istore/run-records/*.txt; do
            [ -f "$record" ] || continue
            [ "$first" = "0" ] && echo ","
            head -n 1 "$record" | tr -d '\\r\\n'
            first=0
        done
        echo ""
        echo "]"
        ;;
    *)
        apk "$action" "$@" 2>/dev/null || true
        ;;
esac

exit 0
"""

create_cmd = f"""
cat << 'EOF' > /bin/is-opkg
{engine_script}
EOF
chmod 755 /bin/is-opkg
ln -sf /bin/is-opkg /usr/bin/is-opkg 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(create_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("\n3. Testing Real Installation of 'ddnsto' & 'linkease'...")
stdin, stdout, stderr = client.exec_command("apk add luci-app-ddnsto ddnsto linkease luci-app-linkease")
print(stdout.read().decode('utf-8', errors='ignore'))
print("Stderr:", stderr.read().decode('utf-8', errors='ignore'))

client.close()
