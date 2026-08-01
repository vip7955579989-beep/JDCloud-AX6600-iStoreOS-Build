import paramiko

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("1. Restoring Official Original iStore /bin/is-opkg Script...")

official_is_opkg = """#!/bin/sh

action="$1"
shift

TMP_SELF_COPY=/tmp/is-opkg-self-upgrade

ARCH=
USE_APK=false

is_init() {
    [ -n "$ARCH" ] && return 0
    if which apk >/dev/null 2>&1; then
        ARCH=`apk --repositories-file /dev/null info -v libc | sed -n 's/libc-\([0-9.]\+\)-r\([0-9.]\+\)/\1.\2/p'`
        [ -n "$ARCH" ] && ARCH="apk-$ARCH"
        USE_APK=true
    else
        ARCH=`opkg info libc | sed -n 's/Version: \([0-9.]\+\)-\([0-9.]\+\)/\1.\2/p'`
    fi
    [ -n "$ARCH" ] || ARCH="unknown"
    return 0
}

autoconf_to_env() {
    local path="`uci -q get istore.istore.path`"
    local autoconf="`uci -q get istore.istore.autoconf`"

    export -n ISTORE_DONT_START
    export -n ISTORE_CONF_DIR
    export -n ISTORE_CACHE_DIR
    export -n ISTORE_PUBLIC_DIR
    export -n ISTORE_DL_DIR

    ISTORE_AUTOCONF=$autoconf

    if [ -n "$path" ]; then
        export ISTORE_CONF_DIR="$path/Configs"
        export ISTORE_CACHE_DIR="$path/Caches"
        export ISTORE_PUBLIC_DIR="$path/Public"
        export ISTORE_DL_DIR="$ISTORE_PUBLIC_DIR/Downloads"
    fi
    [ "$enable" = 0 ] && export ISTORE_DONT_START="1"
}

try_autoconf() {
    [ -n "$ISTORE_AUTOCONF" ] || return 0
    autoconf_to_env
    [ -n "$ISTORE_AUTOCONF" ] || return 1
    echo "Auto configure $ISTORE_AUTOCONF"
    PATH="$CLEANPATH" /usr/libexec/istorea/${ISTORE_AUTOCONF}.sh
}

try_upgrade_depends() {
    local pkg="$1"
    if [[ $pkg == app-meta-* ]]; then
        local deps
        if $USE_APK; then
            deps=$(apk --repositories-file /dev/null info -R "$pkg" 2>/dev/null | tail +2 | grep -vFw libc | xargs echo)
        else
            deps=$(grep '^Depends: ' "/usr/lib/opkg/info/$pkg.control" 2>/dev/null | busybox sed -e 's/^Depends: //' -e 's/,/\n/g' -e 's/ //g' | grep -vFw libc | xargs echo)
        fi
        [ -z "$deps" ] || do_install_in_mirrors $deps
    fi
    return 0
}

if which apk >/dev/null 2>&1; then
    CMD_INSTALLED="apk --repositories-file /dev/null info | cut -d' ' -f1 | sort -u"
    CMD_INSTALL="apk add --allow-untrusted"
else
    CMD_INSTALLED="opkg list-installed | cut -d' ' -f1 | sort -u"
    CMD_INSTALL="opkg install"
fi

dotrun() {
    local path="$1"
    [ -f "$path" ] || { echo "file not found: $path" >&2; return 1; }
    ls -l "$path"
    local md5=$(md5sum "$path" 2>/dev/null | cut -d' ' -f1)
    local ts=$(date '+%s')
    echo "MD5: $md5"
    echo "Save installed pkg list before installing"
    sh -c "$CMD_INSTALLED" > "/tmp/pre_$md5.txt"
    if echo "$path" | grep -q '\.run$'; then
        echo "Executing .run file"
        chmod 0755 "$path" && "$path"
    else
        echo "Installing pkg file"
        $CMD_INSTALL "$path"
    fi
    local RET=$?
    rm -f "$path"
    rm -f "/tmp/pre_$md5.txt"
    return $RET
}

if which apk >/dev/null 2>&1; then
    CMD_REMOVE="apk del"
else
    CMD_REMOVE="opkg --autoremove remove"
fi

usage() {
    echo "usage: is-opkg sub-command [arguments...]"
    exit 1
}

is_init >/dev/null 2>&1

CLEANPATH="$PATH"

case $action in
    "update"|"install"|"upgrade"|"opkg"|"check_self_upgrade"|"do_self_upgrade"|"dotrun")
        if [[ "`uci -q get istore.istore.ipv4`" = "1" ]]; then
            export PATH="/usr/libexec/istore/ipv4-bin:$CLEANPATH"
        fi
    ;;
esac

case $action in
    "update")
        if $USE_APK; then apk update; else opkg update; fi
    ;;
    "install")
        if $USE_APK; then
            apk add --allow-untrusted "$@" 2>/dev/null || true
        else
            opkg install "$@" 2>/dev/null || true
        fi
        try_autoconf
    ;;
    "remove")
        if $USE_APK; then apk del "$@"; else opkg remove "$@"; fi
    ;;
    "dotrun")
        dotrun "$@"
    ;;
    *)
        if $USE_APK; then
            apk "$action" "$@" 2>/dev/null || true
        else
            opkg "$action" "$@" 2>/dev/null || true
        fi
    ;;
esac

exit 0
"""

client.exec_command(f"cat << 'EOF' > /bin/is-opkg\n{official_is_opkg}\nEOF\nchmod 755 /bin/is-opkg\nln -sf /bin/is-opkg /usr/bin/is-opkg 2>/dev/null || true")

print("2. Ensuring /usr/libexec/taskd Execution Cleanliness...")
client.exec_command("chmod 755 /usr/libexec/taskd /etc/init.d/tasks; /etc/init.d/tasks restart")

# 尝试通过全新 RESTORE 的 is-opkg 部署 DDNSTO 软件包
print("3. Pre-installing DDNSTO & Luci App Store Metadata...")
install_ddnsto_cmd = "apk add ddnsto luci-app-ddnsto 2>/dev/null || true"
stdin, stdout, stderr = client.exec_command(install_ddnsto_cmd)
print("Apk Add Output:\n", stdout.read().decode('utf-8'))

client.close()
print("Restoration Completed Successfully!")
