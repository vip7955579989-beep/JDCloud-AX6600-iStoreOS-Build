# 🤖 京东云雅典娜 AX6600 专属持久化记忆库 (AGENTS.md)

## 📌 项目核心全量上下文
- **设备**: 京东云无线宝 雅典娜 AX6600 (Qualcomm IPQ6018 + QCN9074 三频 Wi-Fi 6, 64G/128G eMMC)
- **本地工程路径**: `d:\Antigravity IDE数据文件夹\JDCloud-AX6600-iStoreOS-Build`
- **GitHub 远程仓库**: `https://github.com/vip7955579989-beep/JDCloud-AX6600-iStoreOS-Build.git`
- **原厂旧系统物理路径**: `G:\雅典娜AX6600原来系统`
- **刷机与 U-Boot 逻辑**:
  1. 不死 U-Boot 界面刷入带 `factory` 关键字的 `.bin` / `.ubi` 固件。
  2. 传统旧版 U-Boot 需要手动改电脑 IP `192.168.1.2` 访问 `192.168.1.1`，界面高级科技风；新版 uBootKit 支持 DHCP，但界面偏朴素。建议保留好看的旧版 U-Boot！
- **固件提取**: Actions 使用 `find openwrt/bin/targets/ -type f` 递归提取镜像到 `bin_out` 打包。
