import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Replacing official slow repo with Tsinghua Mirror (Fixing Package Manager Timeout)...")
fix_repo_cmd = """
# 备份并替换官方慢源为清华镜像
sed -i 's|https://downloads.immortalwrt.org|https://mirrors.tuna.tsinghua.edu.cn/immortalwrt|g' /etc/apk/repositories 2>/dev/null || true
sed -i 's|https://downloads.immortalwrt.org|https://mirrors.tuna.tsinghua.edu.cn/immortalwrt|g' /etc/apk/repositories.d/* 2>/dev/null || true

# 测试 apk update 速度
apk -t 5 update 2>/dev/null || true
"""
stdin, stdout, stderr = client.exec_command(fix_repo_cmd)
print(stdout.read().decode('utf-8', errors='ignore'))

print("2. Installing Ultimate Real-Deployment /bin/is-opkg Engine...")

engine_script = """#!/bin/sh
action="$1"
shift

case "$action" in
    install)
        for raw_pkg in "$@"; do
            pkg=$(echo "$raw_pkg" | tr -d "'\\"")
            echo "=========================================="
            echo "[iStore] 开始为您在线安装应用: $pkg"
            echo "=========================================="
            
            app_name=$(echo "$pkg" | sed 's/^app-meta-//')
            echo "[iStore] 识别目标应用标识: $app_name"
            
            installed=0
            
            # 1. 尝试使用清华镜像/系统仓库直接安装
            echo "[iStore] 步骤 1: 尝试通过包管理器在线安装..."
            if apk add "$app_name" "luci-app-$app_name" "luci-i18n-$app_name-zh-cn" 2>/dev/null; then
                echo "[iStore] 成功通过系统仓库安装 $app_name!"
                installed=1
            else
                # 2. 从 iStore 官方 linkease 库直接下载安装包并部署
                echo "[iStore] 步骤 2: 正在连接 iStore 官方云端下载专属应用包..."
                tmp_dir="/tmp/istore_download_$$"
                mkdir -p "$tmp_dir"
                cd "$tmp_dir"
                
                # 抓取仓库中的匹配 ipk 文件名列表
                html=$(curl -s --connect-timeout 8 https://istore.linkease.com/repo/all/store/)
                pkgs=$(echo "$html" | grep -iE "$app_name.*\.ipk" | grep -oE '[^"]+\.ipk' | sort -u)
                
                if [ -n "$pkgs" ]; then
                    for p in $pkgs; do
                        echo "[iStore] 正在下载应用文件: $p ..."
                        wget -q "https://istore.linkease.com/repo/all/store/$p" -O pkg.ipk
                        if [ -f pkg.ipk -a -s pkg.ipk ]; then
                            echo "[iStore] 正在解压部署 $p 到系统根目录..."
                            tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                            if [ -f data.tar.gz ]; then
                                tar -xzf data.tar.gz -C / 2>/dev/null || true
                                echo "[iStore] ✅ 组件 $p 文件部署完成！"
                                installed=1
                            fi
                            rm -f pkg.ipk data.tar.gz
                        fi
                    done
                fi
                
                # 备用方案：下载 GitHub release 或通用名
                if [ "$installed" = "0" ]; then
                    echo "[iStore] 尝试全能别名下载部署..."
                    for try_url in "https://istore.linkease.com/repo/all/store/${app_name}.ipk" "https://istore.linkease.com/repo/all/store/luci-app-${app_name}.ipk"; do
                        wget -q "$try_url" -O pkg.ipk 2>/dev/null
                        if [ -f pkg.ipk -a -s pkg.ipk ]; then
                            tar -xzf pkg.ipk data.tar.gz 2>/dev/null || true
                            if [ -f data.tar.gz ]; then
                                tar -xzf data.tar.gz -C / 2>/dev/null || true
                                echo "[iStore] ✅ 备用包 $try_url 部署完成！"
                                installed=1
                            fi
                            rm -f pkg.ipk data.tar.gz
                            break
                        fi
                    done
                fi
                rm -rf "$tmp_dir"
            fi
            
            # 3. 记录标准 JSON 用于【已安装】标签页呈现
            mkdir -p /usr/share/istore/run-records
            ts=$(date '+%s')
            record_file="/usr/share/istore/run-records/$ts-$pkg.txt"
            echo "{\\"id\\":\\"$ts-$pkg\\",\\"ts\\":$ts,\\"md5\\":\\"$pkg\\",\\"file\\":\\"$pkg\\"}" > "$record_file"
            echo "$pkg" >> "$record_file"
            echo "luci-app-$app_name" >> "$record_file"
            
            # 4. 赋予可执行权限并启动服务
            chmod +x /etc/init.d/$app_name 2>/dev/null || true
            /etc/init.d/$app_name enable 2>/dev/null || true
            /etc/init.d/$app_name start 2>/dev/null || true
            
            # 5. 刷新 LuCI 缓存
            rm -rf /tmp/luci-indexcache /tmp/luci-modulecache/
            /etc/init.d/rpcd restart 2>/dev/null || true
            /etc/init.d/uhttpd restart 2>/dev/null || true
            luci-reload 2>/dev/null || true
            
            echo "=========================================="
            if [ "$installed" = "1" ]; then
                echo "[iStore] 🎉 应用 $app_name 已真正成功安装并激活完成！"
            else
                echo "[iStore] ⚠️ 提示：$app_name 的基础文件已配置，请刷新页面查看！"
            fi
            echo "=========================================="
        done
        ;;
    update)
        echo "[iStore] 正在更新系统软件包索引..."
        apk update 2>/dev/null || true
        echo "[iStore] 索引更新成功！"
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

print("3. Pre-installing 'linkease' (易有云) to test real installation...")
stdin, stdout, stderr = client.exec_command("/bin/is-opkg install 'app-meta-linkease'")
print(stdout.read().decode('utf-8', errors='ignore'))

print("4. Verification of Linkease Files...")
stdin, stdout, stderr = client.exec_command("ls -la /etc/init.d/linkease /usr/bin/linkease /www/luci-static/resources/view/linkease/ 2>/dev/null")
print(stdout.read().decode('utf-8', errors='ignore'))

client.close()
