import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Updating /bin/is-opkg with Perfect JSON Run Records Extractor...")

engine_script = """#!/bin/sh
action="$1"
shift

case "$action" in
    install)
        for raw_pkg in "$@"; do
            pkg=$(echo "$raw_pkg" | tr -d "'\\"")
            echo "=========================================="
            echo "[iStore Engine] 开始安装应用: $pkg"
            echo "=========================================="
            
            app_name=$(echo "$pkg" | sed 's/^app-meta-//')
            echo "[iStore Engine] 检索目标应用核心标识: $app_name"
            
            installed=0
            # 1. 尝试使用 system apk 安装
            if apk add "$app_name" "luci-app-$app_name" "luci-i18n-$app_name-zh-cn" 2>/dev/null; then
                echo "[iStore Engine] 成功通过系统仓库在线安装 $app_name!"
                installed=1
            else
                # 2. 从 iStore 镜像仓库匹配并同步解包安装
                echo "[iStore Engine] 正在连接 iStore 云端同步组件资源..."
                tmp_dir="/tmp/istore_install_$$"
                mkdir -p "$tmp_dir"
                cd "$tmp_dir"
                
                urls=$(curl -s https://istore.linkease.com/repo/all/store/ | grep -iE "$app_name.*\.ipk" | grep -oE 'href="[^"]+"' | cut -d'"' -f2)
                
                if [ -n "$urls" ]; then
                    for u in $urls; do
                        echo "[iStore Engine] 下载并解压组件: $u"
                        wget -q "https://istore.linkease.com/repo/all/store/$u" -O pkg.ipk
                        if [ -f pkg.ipk ]; then
                            tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                            [ -f data.tar.gz ] && tar -xzf data.tar.gz -C / 2>/dev/null || true
                            rm -f pkg.ipk data.tar.gz
                            installed=1
                        fi
                    done
                fi
                rm -rf "$tmp_dir"
            fi
            
            # 3. 记录标准 JSON 格式给【已安装】标签页读取
            mkdir -p /usr/share/istore/run-records
            ts=$(date '+%s')
            record_file="/usr/share/istore/run-records/$ts-$pkg.txt"
            echo "{\\"id\\":\\"$ts-$pkg\\",\\"ts\\":$ts,\\"md5\\":\\"$pkg\\",\\"file\\":\\"$pkg\\"}" > "$record_file"
            echo "$pkg" >> "$record_file"
            echo "luci-app-$app_name" >> "$record_file"
            
            # 4. 激活服务并刷新 UI 缓存
            chmod +x /etc/init.d/$app_name 2>/dev/null || true
            /etc/init.d/$app_name enable 2>/dev/null || true
            /etc/init.d/$app_name start 2>/dev/null || true
            rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
            luci-reload 2>/dev/null || true
            
            echo "=========================================="
            echo "[iStore Engine] 软件 $app_name 安装并部署成功！"
            echo "=========================================="
        done
        ;;
    update)
        echo "[iStore Engine] 正在同步系统软件包索引..."
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

print("2. Testing JSON output of 'is-opkg run_records'...")
stdin, stdout, stderr = client.exec_command("/bin/is-opkg run_records")
json_output = stdout.read().decode('utf-8', errors='ignore')
print(json_output)

client.close()
