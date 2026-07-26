# 概述

![logo](./doc/logo.png)

回声工坊（TRPG-Replay-Generator）是一款专注于跑团replay视频的专业制作工具：

## 特点和优势

1. **简化工作**：显著减少跑团replay视频和类视觉小说视频制作中的重复工作，将视频制作简化到如同编写文档一样简单；
2. **高度自定义**：提供多种复杂的媒体类型，支持自定义复杂的视频界面布局；
3. **生态开放**：开放的上下游软件生态
    1. 支持VScode插件编辑剧本
    2. 海豹骰提供骰系级支持，log可直接导出回声工坊剧本格式
    3. 可以将项目导出为PR项目，保留最大化的后期编辑空间
    4. 允许导出透明背景视频素材
## macOS 配置要求

本分支面向 Apple Silicon（`arm64`）Mac，当前验证环境为 macOS 15 和 Python 3.11。

**运行已构建应用：**
1. Apple Silicon（M 系列）Mac，macOS 15 或更高版本；
2. 建议 8GB 或更高内存；
3. 至少 2GB 可用硬盘空间。

**从源代码开发或构建：**
1. Apple Silicon（M 系列）Mac，macOS 15 或更高版本；
2. Git、Homebrew、Miniconda 或 Anaconda；
3. Python 3.11；
4. 建议预留 5GB 以上空间，用于 Conda 环境、PyInstaller 缓存与应用产物。

# 操作手册

[回声工坊 RplGenStudio 操作手册](https://www.wolai.com/mJpcu5LUk3cECUjNXfHaqT)

# macOS 部署与构建（Apple Silicon）

本分支已完成 Apple Silicon（`arm64`）macOS 的可用移植，已在 macOS 15、Python 3.11 上验证预览、MP4 导出、XML 导出、本地系统语音和使用自定义密钥的阿里云语音合成。Intel Mac、旧版 macOS 及正式公证发布尚未验证。

完整开发记录见 [macOS 开发文档](./doc/macos-development.md)。以下步骤可从零开始部署开发环境，或构建本地 `.app`。

## 1. 获取代码

安装 Git、Homebrew 与 Miniconda/Anaconda 后，在终端执行：

```sh
git clone git@github.com:dthylacetate/TRPG-Replay-Generator.git
cd TRPG-Replay-Generator
git checkout macos-port
```

如果使用自己的 fork，请将第一行替换为自己的仓库地址。后续命令均须在仓库根目录执行；当前源代码使用相对路径读取 `assets` 与 `intel`。

## 2. 建立开发环境

```sh
conda create --name rplgen-macos python=3.11 pip
conda run --name rplgen-macos python -m pip install -r requirements-macos.txt
brew install ffmpeg
```

`ffmpeg` 仅供直接运行源代码时使用。已构建的 `.app` 会自带 ARM64 FFmpeg，不依赖 Homebrew。

可用以下命令检查环境：

```sh
conda run --no-capture-output --name rplgen-macos python tools_scripts/check_macos_environment.py
```

## 3. 启动与基本验证

启动开发版：

```sh
conda run --no-capture-output --name rplgen-macos python gui.py
```

建议在改动媒体、FFmpeg 或平台逻辑后执行：

```sh
conda run --no-capture-output --name rplgen-macos python tools_scripts/smoke_test_macos.py
conda run --no-capture-output --name rplgen-macos python tools_scripts/validate_toy_macos.py --preview-init
```

在 macOS 中，预览、MP4 与 XML 输出会在独立进程中运行，以避免 Tk 与 Pygame/Cocoa 的线程冲突。每次操作的完整日志会写入项目媒体目录下的 `logs/<项目>_<时间>.<操作>.log`；操作开始时，软件控制台也会显示实际日志路径。

## 4. 配置语音合成

源代码和本地 macOS 构建版不使用内置语音密钥服务。请使用自己的云服务凭据：

1. 打开软件的“首选项”。
2. 关闭“使用内置密钥”。
3. 在阿里云、Azure 或腾讯云对应区域填写自己的密钥与服务参数。
4. 使用“语音音源”窗口的“试听”先验证，再对剧本执行“语音合成”。

自定义配置保存在 `~/.rplgen/preference.json`，其中可能含有访问密钥。该文件不会被 Git 跟踪，切勿复制到仓库、提交记录、日志或公开发布的应用包中。

阿里云在 macOS 上使用新版 NLS SDK：程序会用 `AccessKey` 和 `AccessKeySecret` 自动换取短期 Token，再请求合成。若服务调用失败，软件控制台会显示具体错误，例如密钥未初始化、Token 请求失败或阿里云服务端的返回信息。

## 5. 构建本地应用

安装仅在构建时需要的工具后，运行打包与启动检查：

```sh
conda run --no-capture-output --name rplgen-macos python -m pip install -r requirements-macos-build.txt
conda run --no-capture-output --name rplgen-macos python tools_scripts/build_macos_app.py
conda run --no-capture-output --name rplgen-macos python tools_scripts/smoke_test_macos_app.py
```

生成的应用位于：

```text
dist/macos/RplGenStudio.app
```

打包脚本会收集 `assets`、`intel`、Azure Speech 运行库及静态 ARM64 FFmpeg。复制该 `.app` 到本机其他目录后仍可运行；请先在目标机上用一个小项目验证预览、导出和语音合成。

## 6. 本地分发与签名

当前构建使用临时 ad-hoc 签名，适合本机测试，不适合公开发布。若 Gatekeeper 阻止打开自己构建的可信应用，可在确认来源后移除隔离属性：

```sh
xattr -dr com.apple.quarantine dist/macos/RplGenStudio.app
```

如需将应用交给其他 Apple Silicon Mac 用户测试，可生成保留应用包结构的 ZIP 与 SHA-256 校验文件：

```sh
conda run --no-capture-output --name rplgen-macos python tools_scripts/package_macos_zip.py
```

生成文件位于 `dist/macos/RplGenStudio-macos-arm64.zip` 及同目录的 `.sha256` 校验文件。接收者解压后可将 `RplGenStudio.app` 拖到“应用程序”文件夹；首次打开仍可能需要处理 Gatekeeper 提示。

对外发布前需要使用 Apple Developer 证书签名、提交 notarization，并通过 DMG 或 ZIP 分发。不要把任何云 TTS 密钥写入应用资源或提交到仓库。

## 7. 已知限制

- 实时预览中的骰子演出动画可能有显示或动画异常；同一项目的 MP4 导出结果正常，应以导出视频为准。
- `tkextrafont` 无法在 macOS 上按原方式安装，界面会自动使用 `PingFang SC` 与 `Menlo` 等系统字体。
- macOS 版本仅验证 Apple Silicon；Intel Mac 需要单独构建与测试。

# 开源协议

本软件采用[**GPL3.0**](LICENSE.md)协议开源：允许用户自由的使用、修改本软件，或者将本软件的部分代码用于自己的项目，但是，需要注意以下几点：
1. **开源要求**：如果在其他项目中使用了本项目的功能或代码，那么遵照GPL3.0协议的规范，该项目也应开源，并规范著名引用关系。
2. **使用限制**：在基于本项目，进行二次开发时，不允许使用本软件的图标、名称、吉祥物等第三方享有著作权的资产。
