#!/bin/bash
set -e

echo "=== 🚀 开始雅典娜 AX6600 本地极速编译工程 ==="

# 0. 自动设置 WSL2 稳健 DNS 解析 (223.5.5.5)
sudo bash -c 'echo "nameserver 223.5.5.5" > /etc/resolv.conf && echo "nameserver 8.8.8.8" >> /etc/resolv.conf' 2>/dev/null || true

# 1. 避开跨盘挂载的大小写检视与I/O损耗：在 D 盘 ext4 虚拟盘内部创建编译区 /root/AX6600_Build
BUILD_WORK_DIR="/root/AX6600_Build"
echo "--> 目标 Linux 原生 ext4 编译空间(位于 D:\\WSL\\Ubuntu\\ext4.vhdx 内): ${BUILD_WORK_DIR}"
mkdir -p "${BUILD_WORK_DIR}"
cd "${BUILD_WORK_DIR}"

# 2. 准备 Linux 编译依赖包
sudo apt-get update -y || true
sudo apt-get install -y build-essential clang flex bison gawk gettext git libncurses5-dev libssl-dev python3-distutils python3-pyelftools rsync unzip zlib1g-dev squashfs-tools device-tree-compiler swig python3-dev python3-setuptools || true

# 3. 拉取与真机 192.168.200.1 对齐的高通 ipq60xx / QSDK 12.5 源码
if [ ! -d "openwrt" ]; then
  until git clone --depth 1 https://github.com/coolsnowwolf/lede.git openwrt || git clone --depth 1 https://github.com/immortalwrt/immortalwrt.git -b openwrt-21.02 openwrt; do
    echo "网络拉取重试中..."
    sleep 2
  done
  cd openwrt
  echo "src-git istore https://github.com/linkease/istore-ui.git" >> feeds.conf.default
  echo "src-git linkease https://github.com/linkease/istore.git" >> feeds.conf.default
  ./scripts/feeds update -a
  ./scripts/feeds install -a
else
  cd openwrt
fi

# 3.5 自动更新并安装软件源包 (Feeds)
echo "--> 正在更新与同步 iStoreOS / OpenWrt 软件源组件 (Feeds)..."
  grep -q "istore" feeds.conf.default || echo "src-git istore https://github.com/linkease/istore-ui.git" >> feeds.conf.default
  grep -q "linkease" feeds.conf.default || echo "src-git linkease https://github.com/linkease/istore.git" >> feeds.conf.default
  grep -q "passwall_packages" feeds.conf.default || echo "src-git passwall_packages https://github.com/xiaorouji/openwrt-passwall-packages.git;main" >> feeds.conf.default
  grep -q "passwall" feeds.conf.default || echo "src-git passwall https://github.com/xiaorouji/openwrt-passwall.git;main" >> feeds.conf.default

until [ -d "feeds/packages/utils" ]; do
  echo "--> 正在拉取/修复关键 feeds/packages 软件源仓库 (失败自动重试中)..."
  rm -rf feeds/packages
  ./scripts/feeds update packages || sleep 2
done

./scripts/feeds update -a || true
./scripts/feeds install -a || true
rm -rf tmp/ .config*

# 4. 配置文件生成 (.config)
echo "CONFIG_TARGET_qualcommax=y" > .config
echo "CONFIG_TARGET_qualcommax_ipq60xx=y" >> .config
echo "CONFIG_TARGET_qualcommax_ipq60xx_DEVICE_jdcloud_re-cs-02=y" >> .config
echo "CONFIG_PACKAGE_kmod-ath11k=y" >> .config
echo "CONFIG_PACKAGE_kmod-ath11k-pci=y" >> .config
echo "CONFIG_PACKAGE_ath11k-firmware-qcn9074=y" >> .config
echo "CONFIG_PACKAGE_ipq-wifi-jdcloud_re-cs-02=y" >> .config
echo "CONFIG_PACKAGE_luci-app-store=y" >> .config
echo "CONFIG_PACKAGE_luci-app-quickstart=y" >> .config
echo "CONFIG_PACKAGE_luci-app-passwall=y" >> .config
echo "CONFIG_PACKAGE_luci-i18n-passwall-zh-cn=y" >> .config
echo "CONFIG_PACKAGE_xray-core=y" >> .config
echo "CONFIG_PACKAGE_sing-box=y" >> .config
echo "CONFIG_PACKAGE_chinadns-ng=y" >> .config
echo "CONFIG_PACKAGE_dnsmasq-full=y" >> .config

make defconfig
sed -i 's/CONFIG_PACKAGE_dnsmasq=y/# CONFIG_PACKAGE_dnsmasq is not set/' .config
make download -j$(nproc)

# 5. 开启本地多核 CPU 高速编译 (带真实日志重定向与自动容错)
echo "=== ⚡ 开启多核并发编译 (使用的 CPU 核心数: $(nproc)) ==="
make -j$(nproc) V=s > >(tee -a compile.log) 2>&1 || make -j1 V=s

# 6. 编译完成后，自动将固件复制一份到 Windows D 盘显眼位置方便用户拿到
mkdir -p /mnt/d/AX6600_Build_Out/
cp -f bin/targets/qualcommax/ipq60xx/* /mnt/d/AX6600_Build_Out/ 2>/dev/null || true
cp -f bin/targets/ipq60xx/generic/* /mnt/d/AX6600_Build_Out/ 2>/dev/null || true

echo "=== 🎉 本地编译完成！固件已存放在 D:\\AX6600_Build_Out\\ 目录下！ ==="
