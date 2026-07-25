[English](./README-en.md)

# 概述

![logo](./doc/logo.png)

回声工坊（TRPG-Replay-Generator）是一款专注于跑团replay视频的专业制作工具：

回声工坊已发行在steam商店，商业发行版的名称为`回声工坊 RplGenStudio`，发行商名称为`Betelgeuse Industry`。

## 特点和优势

1. **简化工作**：显著减少跑团replay视频和类视觉小说视频制作中的重复工作，将视频制作简化到如同编写文档一样简单；
2. **高度自定义**：提供多种复杂的媒体类型，支持自定义复杂的视频界面布局；
3. **生态开放**：开放的上下游软件生态
    1. 支持VScode插件编辑剧本
    2. 海豹骰提供骰系级支持，log可直接导出回声工坊剧本格式
    3. 可以将项目导出为PR项目，保留最大化的后期编辑空间
    4. 允许导出透明背景视频素材
4. **创意分享**：支持创意工坊，允许用户分享和下载预设样式模板，利用模板实现一键成片

# 软件下载

正式在steam商店发行之后，本仓库不再提供开包即用的二进制可执行文件，仅提供源代码。

源代码版本不拥有内置语音合成服务的权限，需要自行注册语音合成账号，并填写key到【首选项】

## [steam商店](https://store.steampowered.com/app/2550090/_RplGen_Studio/)
- 回声工坊在steam商店的售价是13美元，或者人民币50元；<p>
- 自动更新、创意工坊、内置语音服务等，仅在steam平台版本提供。<p>

## [爱发电](https://afdian.net/item/68ed814c7df011eebefc52540025c377)
- 爱发电中同样销售steam的激活码（CDkey），定价为50元；<p>
- 购买之后需要在steam平台激活，功能等价于在steam商店直接购买。<p>

## 配置要求
**最低：**
1. 系统：Windows 10
2. 内存：4GB
3. 硬盘：1GB

**最佳：**
1. 系统：Windows 10
2. 内存：8GB
3. 硬盘：1GB

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

源代码和本地 macOS 构建版不使用 Windows/Steam 发行版的内置语音密钥服务。请使用自己的云服务凭据：

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

对外发布前需要使用 Apple Developer 证书签名、提交 notarization，并通过 DMG 或 ZIP 分发。不要把任何云 TTS 密钥写入应用资源或提交到仓库。

## 7. 已知限制

- 实时预览中的骰子演出动画可能有显示或动画异常；同一项目的 MP4 导出结果正常，应以导出视频为准。
- `tkextrafont` 无法在 macOS 上按原方式安装，界面会自动使用 `PingFang SC` 与 `Menlo` 等系统字体。
- macOS 版本仅验证 Apple Silicon；Intel Mac 需要单独构建与测试。

# 构建

## 环境要求：

环境和依赖项：

1. python>=3.8
1. pygame>=2.0.1
1. numpy>=1.18.5
1. pandas>=1.0.5
1. Pillow>=7.2.0
1. ffmpeg-python>=0.2.0
1. pydub>=0.25.1
1. openpyxl>=3.0.4
1. azure-cognitiveservices-speech>=1.31.0
1. ttkbootstrap>=1.10.1
1. tkextrafont==0.6.3
1. chlorophyll==0.3.1
1. pyttsx3==2.90
1. websocket-client==1.0.1
1. pinyin==0.4.0

除上述项目外，还需要：

1. 下载[ffmpeg](https://ffmpeg.org/download.html)的可执行文件，并解压到本仓库根目录。
1. 安装[阿里云智能语音服务Python SDK](https://github.com/aliyun/alibabacloud-nls-python-sdk)
1. 安装[7z](https://github.com/sparanoid/7z)，并添加到环境变量，打包时需要。（推荐）

## 构建和打包

使用[打包脚本](./bulid.ps1)，即可将软件打包。

# 开源协议

本软件采用[**GPL3.0**](LICENSE.md)协议开源：允许用户自由的使用、修改本软件，或者将本软件的部分代码用于自己的项目，但是，需要注意以下几点：
1. **开源要求**：如果在其他项目中使用了本项目的功能或代码，那么遵照GPL3.0协议的规范，该项目也应开源，并规范著名引用关系。
2. **使用限制**：在基于本项目，进行二次开发时，不允许使用本软件的图标、名称、吉祥物等第三方享有著作权的资产。
