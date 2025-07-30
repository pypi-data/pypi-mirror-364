# bili-listener

- [协议解释](https://open-live.bilibili.com/document/657d8e34-f926-a133-16c0-300c1afc6e6b)
- 原属于 [xfgryujk/blivedm](https://github.com/xfgryujk/blivedm)
- 基于本库开发的应用：[BiliListener](https://github.com/Shadow403/BiliListener)

### 使用说明

- 需要Python 3.10及以上版本
- 创建虚拟环境
- 安装依赖 `pdm install`
- web端例程在 [`sample.py`](./blivedm/test/example/sample.py)，直播开放平台例程在[`open_live_sample.py`](./blivedm/test/example/open_live_sample.py)
- `cmd` 类型在 [`ws_json`](./blivedm/test/ws_json/) 文件夹下

### 打包
- 创建虚拟环境
- 安装依赖 `pdm install`
- 打包 `pdm build`
