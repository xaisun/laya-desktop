## laya 决策引擎 · Windows 桌面版 v1.0

把 laya（非自回归 System-1 决策引擎）封装成本地桌面软件：**不联网、不装 Python、双击即用**。

### 附件
- **laya-desktop-setup.exe**（约 1.5GB，含 1.5GB 模型权重）：7z 自解压安装包。双击即解压到同级 `laya\` 文件夹、桌面建启动器并启动，弹出 pywebview 原生无边框窗口。
- 便携版（laya-onefile）请按仓库 README / 使用教程 自行构建，或联系作者获取。

### 使用
双击安装包 → 确定解压 → 双击桌面 `laya-launch.bat` 启动。详见仓库 [使用教程.md](使用教程.md)。

### 注意
- 首次启动约 40–90s 加载模型，正常。
- 杀软可能误报 PyInstaller 打包的 exe，加白名单即可。
- 需系统已装 WebView2 运行时（Win10/11 基本自带）。
- 已知短板：`noul`（是/否）对中文不可靠，跨语言请用 choice/score 型。

### License
Apache-2.0（与上游 laya 同协议），见 NOTICE。
