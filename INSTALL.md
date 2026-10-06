# Dota2Forge · AstrBot 安装与更新

适用于0.1.0-alpha.5文档修复版（Python适配器0.1.0a5、共享Core/Renderer 0.1.0a4），Python 3.12+，AstrBot >=4.28.2,<4.29。插件需要先安装三个运行组件；只在商店点击安装还不能直接使用。组件来自同一仓库的GitHub Releases，安装器核对版本和SHA256，不需要PyPI上的项目包。

## 首次安装

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

文字和基础卡片可直接使用。英雄、装备等Valve图片是可选本地素材，不随插件分发；没有素材时保留名称和占位。准备素材及 `illustration_path` 配置见主项目[素材指南](https://github.com/HBLADEH/Dota2Forge/blob/v0.1.0a4/docs/cookbook/illustrations.md)。

本版更新出装和比赛卡、装备简称和详细统计。合成图片与离线消费者测试不代表真实聊天验收；当前版本的在线字段、真实商店安装及Linux宿主仍需验证。订阅默认关闭，真实推送尚未验收；历史AstrBot/OneBot基础聊天记录不替代本版验收。
