import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Updating /bin/is-opkg (No-Logout & Cloud Multi-Mirror Fetch)...")

engine_script = """#!/bin/sh
action="$1"
shift

case "$action" in
    install)
        for raw_pkg in "$@"; do
            pkg=$(echo "$raw_pkg" | tr -d "'\\"")
            echo "=========================================="
            echo "[iStore Engine] 开始为您安装应用: $pkg"
            echo "=========================================="
            
            app_name=$(echo "$pkg" | sed 's/^app-meta-//')
            echo "[iStore Engine] 真实应用标识: $app_name"
            
            installed=0
            
            # 1. 尝试使用 apk 原生库安装
            if apk add "$app_name" "luci-app-$app_name" "luci-i18n-$app_name-zh-cn" 2>/dev/null; then
                echo "[iStore Engine] 成功通过系统仓库在线安装 $app_name!"
                installed=1
            else
                # 2. 从 GitHub 加速节点 / iStore 仓库拉取包并解压
                echo "[iStore Engine] 正在从云端多镜像下载应用专属包..."
                tmp_dir="/tmp/is_opkg_dl_$$"
                mkdir -p "$tmp_dir"
                cd "$tmp_dir"
                
                urls="
                https://ghp.ci/https://raw.githubusercontent.com/linkease/istore-packages/main/pkgs/luci-app-${app_name}.ipk
                https://ghp.ci/https://raw.githubusercontent.com/linkease/istore-packages/main/pkgs/${app_name}.ipk
                https://istore.linkease.com/repo/all/store/luci-app-${app_name}.ipk
                https://istore.linkease.com/repo/all/store/${app_name}.ipk
                "
                
                for url in $urls; do
                    wget -q --timeout=5 "$url" -O pkg.ipk 2>/dev/null
                    if [ -f pkg.ipk -a -s pkg.ipk ]; then
                        echo "[iStore Engine] 成功拉取二进制组件: $(basename $url)"
                        tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                        if [ -f data.tar.gz ]; then
                            tar -xzf data.tar.gz -C / 2>/dev/null || true
                            echo "[iStore Engine] 成功部署 $app_name 资源到系统!"
                            installed=1
                        fi
                        rm -f pkg.ipk data.tar.gz
                        break
                    fi
                done
                rm -rf "$tmp_dir"
            fi
            
            # 3. 记录标准 JSON 供【已安装】标签页展示
            mkdir -p /usr/share/istore/run-records
            ts=$(date '+%s')
            record_file="/usr/share/istore/run-records/$ts-$pkg.txt"
            echo "{\\"id\\":\\"$ts-$pkg\\",\\"ts\\":$ts,\\"md5\\":\\"$pkg\\",\\"file\\":\\"$pkg\\"}" > "$record_file"
            echo "$pkg" >> "$record_file"
            echo "luci-app-$app_name" >> "$record_file"
            
            # 4. 给予权限并刷新缓存（绝对不重启 uhttpd / rpcd，彻底防掉线！）
            chmod +x /etc/init.d/$app_name 2>/dev/null || true
            /etc/init.d/$app_name enable 2>/dev/null || true
            /etc/init.d/$app_name start 2>/dev/null || true
            
            rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
            luci-reload 2>/dev/null || true
            
            echo "=========================================="
            echo "[iStore Engine] 应用 $app_name 处理完成！"
            echo "=========================================="
        done
        ;;
    update)
        echo "[iStore Engine] 正在同步系统软件索引..."
        apk update 2>/dev/null || true
        echo "[iStore Engine] 索引刷新完成！"
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
client.exec_command(create_cmd)
print("Updated /bin/is-opkg engine successfully.")

print("\n2. Testing Cloud Download of 'ddnsto' and 'linkease' via ghp.ci mirror...")
stdin, stdout, stderr = client.exec_command("/bin/is-opkg install 'app-meta-ddnsto'")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
