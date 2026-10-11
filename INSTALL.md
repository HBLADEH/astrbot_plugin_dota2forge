# Dota2Forge · AstrBot 安装与更新

本次版本为0.1.0-alpha.10（适配器a10、Assets a1、Core a7、Renderer a6），要求Python 3.12+、AstrBot >=4.5.0。发行状态见主项目[发行记录](https://github.com/HBLADEH/Dota2Forge/blob/main/docs/cookbook/plugin-release.md)与本插件Releases。requirements通过固定SHA256的GitHub Release wheel地址取得四个运行组件；旧alpha.7为三个组件；全新商店安装由AstrBot执行依赖安装，不需要PyPI上的项目包。商店发布状态需在版本页核实，GitHub更新不会替换Cloud缓存的旧版ZIP。

## 官方商店安装

2026-10-07实际alpha.7 Cloud ZIP下载成功；用户部署曾连接GitHub超时，后续授权SSH诊断时网络恢复，同requirements与57条宿主约束安装通过。Linux/Python3.12.13/AstrBot4.28.1冷启动加载为awaiting_config；尚未另行重试商店按钮完整API流程。安装后填写stratz_token和独立namespace，保存/重载；运行环境须能访问GitHub Releases和第三方依赖源。

旧版alpha.6若报`No matching distribution found for astrbot-plugin-dota2forge==0.1.0a6`，表示pip在索引中找不到未发布PyPI的项目包。更换PyPI镜像无法解决；需使用更新的商店包，或按下面流程手动安装。只有`error code 1`不足以判断原因，应查看它之前的pip ERROR。

若alpha.7已下载却报`Connection to github.com timed out`，则Cloud可达但运行组件下载不可达；更换PyPI镜像不改变requirements中的GitHub直链。按[AstrBot FAQ](https://docs.astrbot.app/faq.html)在设置→网络→代理与依赖源配置HTTP代理，地址必须可从运行AstrBot的环境访问。4.28.1启动时将此设置传给pip，并清理未在AstrBot中配置的小写系统代理变量；仅在宿主机浏览器配置代理不证明容器可用。配置后重启/重试，仍失败则按新的pip ERROR诊断。

## 手动安装

1. 停止AstrBot。在AstrBot根目录把插件下载到 `data/plugins/astrbot_plugin_dota2forge`：

   ```sh
   git clone https://github.com/HBLADEH/astrbot_plugin_dota2forge.git data/plugins/astrbot_plugin_dota2forge
   ```

2. 用**运行AstrBot的Python**执行安装器。以下假定Windows宿主环境为 `.venv`；桌面版、Docker和其他安装方式请替换成实际解释器路径，不要用另一个Python：

   ```sh
   .venv/Scripts/python.exe data/plugins/astrbot_plugin_dota2forge/install_runtime.py --host-python .venv/Scripts/python.exe
   ```

   Linux通常将 `.venv/Scripts/python.exe` 替换为 `.venv/bin/python`。安装需要能访问GitHub Releases及第三方依赖源；安装器保留宿主对Pillow的限制，并运行 `pip check`。失败时先处理冲突，不要跳过检查。

3. 重新启动AstrBot，在插件配置中填写 `stratz_token` 和独立 `namespace`，保存后重载。空密钥会提示等待配置；密钥只填本机配置，不发到聊天或GitHub。
4. 发送 `/do菜单`、`/do绑定 <账号ID>`、`/do查询`、`/do比赛 <比赛ID>`、`/do主宰出装`。斜线按宿主唤醒前缀调整。

## 更新与图片

停用插件并退出AstrBot，备份配置和插件数据后，在插件目录 `git pull --ff-only`，用相同Python重新执行上述安装器，成功后重新启动。不要在运行过程中替换共享库；不要覆盖实际配置或数据库。回退应同时恢复匹配版本的插件目录及运行包，并保留数据备份。

alpha.10默认 reply_mode=image、asset_download_mode=auto、illustration_path=""。首次启动后台下载到持久化插件数据下 illustrations 托管根；首次完成前用占位卡，已有完整有效快照不重复联网。Token未填也可准备公共素材，业务仍等待配置。下载无需玩家凭据，ZIP/wheel不含Valve图片；新版生产部署和真实聊天另行验收。

使用 /do素材状态 查看进度与可用/404/失败数量；Bot管理员或主人可用 /do下载素材 补缺、/do更新素材 刷新，不接受URL或其他参数。asset_download_mode=manual 仅按管理员命令下载；off 禁止素材联网。已有非空 illustration_path 优先，不覆盖自定义目录；相对路径以 data/plugin_data/astrbot_plugin_dota2forge 为基准。UI镜像失败仍保留成功英雄/装备，网络失败不会写成官方缺图。素材代理用 asset_proxy，留空可继承 AstrBot http_proxy，必须从容器可达。

旧alpha.7没有自动功能；继续使用主项目v0.1.0a4的[显式下载工具](https://github.com/HBLADEH/Dota2Forge/blob/v0.1.0a4/scripts/download_dota_assets.py)或准备已有完整素材。alpha.10安装Assets包后可直接运行打包CLI，无需复制源码：

```sh
docker exec astrbot python -m dota2forge_assets.cli --output /AstrBot/data/plugin_data/astrbot_plugin_dota2forge/illustrations-v1
```

该显式CLI用于自定义目录，更新期间先停用渲染，成功后将 illustration_path 设为 illustrations-v1 并重载；不要填宿主机上容器不可见的路径。托管自动下载不需要手填生成路径，整组分页发送后安全切换快照。其他来源、冷却、版权和失败边界见主项目[素材指南](https://github.com/HBLADEH/Dota2Forge/blob/main/docs/cookbook/illustrations.md)。

历史alpha.7已包含出装和比赛卡、装备简称和详细统计。alpha.7已在一份真实Linux部署完成依赖安装，用户提供近期战绩基础出图；配置Token和独立素材后冷启动ready/image，同宿主合成卡和全部558张素材解码通过。新素材真实聊天效果、商店按钮完整重试与订阅递送仍待确认。订阅默认关闭；合成测试不替代真实业务验收。容器重建会移除安装在容器层的运行包，需重新按清单安装；已挂载配置/数据应保留。
