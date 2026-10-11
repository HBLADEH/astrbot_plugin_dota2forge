<p align="center">
  <img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/logo.png" width="128" height="128" alt="Dota2Forge 图标">
</p>

<h1 align="center">Dota2Forge · AstrBot</h1>

<p align="center">在聊天中查询 Dota 2 玩家、战绩、比赛报告和英雄热门出装。</p>

<p align="center">
  <a href="https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/INSTALL.md">安装指南</a> ·
  <a href="https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/CHANGELOG.md">更新日志</a> ·
  <a href="https://github.com/HBLADEH/Dota2Forge/blob/15e1a50a07273c645f0a1066b61fe266dde216cc/README.md">Dota2Forge</a> ·
  <a href="https://github.com/HBLADEH/Dota2Forge/issues">问题反馈</a>
</p>

> 发行版本：`0.1.0-alpha.11` · [目标分发仓库](https://github.com/HBLADEH/astrbot_plugin_dota2forge)。由主仓同一源码生成。

适用于 AstrBot 的 Dota 2 查询插件，插件标识为 `astrbot_plugin_dota2forge`。与 GsCore 插件 Dota2UID 共用 Dota2Forge 核心和图片渲染器。当前处于 **M0 预发行**阶段。

## 功能

- **玩家查询**：账号绑定、玩家概况、段位和预估 MMR。
- **近期战绩**：查询最近 1–100 场比赛，支持分页和按列表序号查看详情。
- **比赛报告**：总览与两队详情，展示英雄、装备、统计、团队优势曲线及来源提供的 STRATZ IMP。
- **英雄热门出装**：按出门、前期、中期、后期展示 OpenDota 职业比赛物品购买统计。
- **订阅通知**：玩家新比赛、指定比赛完成、段位变化和每日战报；默认关闭。

默认使用“远古锻炉”主题图片回复，也可配置文字模式。来源未提供的字段保留缺失说明。

## 效果展示

以下截图来自 **GsCore / Dota2UID**，两端共用图片渲染器与“远古锻炉”主题。昵称和账号／比赛 ID 已脱敏，原图分辨率保留；来源见[截图记录](https://github.com/HBLADEH/Dota2Forge/blob/15e1a50a07273c645f0a1066b61fe266dde216cc/docs/assets/screenshots/README.md)。

<table>
  <tr>
    <th>玩家概况与预估 MMR</th>
    <th>近期战绩</th>
  </tr>
  <tr>
    <td valign="top"><img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/player.png" width="360" alt="玩家概况与预估 MMR"></td>
    <td valign="top"><img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/recent.png" width="360" alt="近期战绩第一页"></td>
  </tr>
</table>

[查看玩家原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/player.png) · [查看战绩原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/recent.png)

<details>
<summary>查看命令菜单</summary>

<img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/menu.png" width="600" alt="Dota2UID 命令菜单">

[查看原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/menu.png)

</details>

<details>
<summary>查看比赛报告：总览与优势曲线</summary>

<img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/match-overview.png" width="800" alt="比赛总览、STRATZ IMP 与团队优势曲线">

[查看原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/match-overview.png)

</details>

<details>
<summary>查看比赛报告：天辉详细数据</summary>

<img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/match-radiant.png" width="800" alt="天辉五人统计与装备">

[查看原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/match-radiant.png)

</details>

<details>
<summary>查看比赛报告：夜魇详细数据</summary>

<img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/match-dire.png" width="800" alt="夜魇五人统计与装备">

[查看原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/match-dire.png)

</details>

<details>
<summary>查看英雄热门出装</summary>

<img src="https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/hero-items.png" width="600" alt="主宰热门出装">

[查看原图](https://raw.githubusercontent.com/HBLADEH/astrbot_plugin_dota2forge/main/screenshots/hero-items.png)

</details>

## 安装与首次配置

要求 **Python 3.12+、AstrBot >=4.5.0**，运行环境需能访问 GitHub Releases 和数据来源。最低版本的公开 API 已核对，真实宿主测试记录以[接入指南](https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/INSTALL.md)为准。

以下为手动安装流程；商店安装与依赖问题见[安装指南](https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/INSTALL.md)。

1. 停止 AstrBot，在其根目录克隆插件：

   ```sh
   git clone https://github.com/HBLADEH/astrbot_plugin_dota2forge.git data/plugins/astrbot_plugin_dota2forge
   ```

2. 使用 **运行 AstrBot 的 Python** 安装运行组件。Windows `.venv` 示例：

   ```sh
   .venv/Scripts/python.exe data/plugins/astrbot_plugin_dota2forge/install_runtime.py --host-python .venv/Scripts/python.exe
   ```

   Linux 将解释器路径替换为 `.venv/bin/python`；Docker 使用容器内的实际解释器。

3. 启动 AstrBot，在插件配置中填写 `stratz_token`，确认独立的 `namespace`，保存并重载插件。
4. 发送 `/do菜单` 检查命令入口，再按下方示例查询。

四个组件从本插件 GitHub Releases 下载，安装器核对版本与摘要，并检查依赖冲突。Token 留空时为 `awaiting_config`；凭据只填写在插件配置中。

## 快速开始

示例采用 `/` 唤醒前缀，请按 AstrBot 的实际设置调整。将 `<…>` 替换为自己的值；命令表中的 `[…]` 表示可省略。

```text
/do绑定 <Dota账号ID或SteamID64>
/do查询
/do战绩 20
/do战绩 第3页
/do比赛 第1场
/do主宰出装
```

显式查询其他账号或直接查询比赛无需绑定；绑定只保存自己的查询偏好，不证明 Steam 账号所有权。

## 命令

| 命令 | 说明 |
| --- | --- |
| `/do菜单` / `/do帮助` | 查看命令帮助 |
| `/do绑定 <ID>` / `/do改绑 <ID>` | 绑定自己的账号 / 更换绑定 |
| `/do账号` / `/do解绑` | 查看绑定 / 解除绑定 |
| `/do查询 [ID]` / `/do段位 [ID]` | 玩家概况、段位和预估 MMR |
| `/do战绩 [条数]` | 查询自己的近期比赛，默认 10 场 |
| `/do战绩 <ID> <条数>` | 查询指定账号的近期比赛 |
| `/do战绩 第N页` | 查看本会话最后一次有效战绩的指定页 |
| `/do比赛 <比赛ID>` / `/do比赛 第N场` | 查询比赛报告 / 按列表绝对序号选择比赛 |
| `/do主宰出装` / `/doAM出装` / `/do出装 Shadow Fiend` | 按英雄中文名、英文名或简称查询热门出装 |

账号参数接受数字形式的 Dota account ID 或 SteamID64，不接受主页 URL、vanity 或 `@他人`。战绩每页五场，首次最多发送两页；列表在同一会话保留十分钟，改绑、解绑、停用或重载后需重新查询。

### 订阅

启用 `subscriptions_enabled` 后可使用以下命令。主动推送目前仅支持 **OneBot v11 反向 WebSocket**；群内创建订阅和重试推送需要 Bot 管理员权限。

| 命令 | 说明 |
| --- | --- |
| `/do订阅玩家 <玩家ID>` | 发现玩家新完成的比赛后发送报告 |
| `/do订阅比赛 <比赛ID>` | 指定比赛完成后通知一次 |
| `/do订阅 [比赛\|段位\|日报] [ID]` | 订阅玩家通知，省略 ID 时使用绑定账号 |
| `/do订阅列表 [游标]` / `/do取消订阅 <订阅ID>` | 查看本人当前会话的订阅 / 取消订阅 |
| `/do重试推送 <事件ID>` | 核实是否已送达后人工重试，可能重复 |

首次比赛、段位轮询只建立基线，不补发历史。日报按北京时间统计前一天开始的有限比赛窗口，最多 100 场。失败推送不自动重发；双端部署时需确定推送归属。配置和投递规则见[订阅指南](https://github.com/HBLADEH/Dota2Forge/blob/15e1a50a07273c645f0a1066b61fe266dde216cc/docs/cookbook/subscriptions.md)，真实主动推送仍待验收。

### 管理

| 命令 | 权限与说明 |
| --- | --- |
| `/do素材状态` | 查看素材准备进度 |
| `/do下载素材` / `/do更新素材` | Bot 管理员；补齐 / 更新托管素材 |
| `/do状态` / `/do停用` | Bot 管理员；查看运行状态 / 关闭插件资源 |

## 配置

| 参数 | 默认值 | 用途 |
| --- | --- | --- |
| `stratz_token` | 空 | STRATZ 访问凭据，玩家和比赛查询需要 |
| `namespace` | `astrbot-local` | 部署身份分区；不同部署使用不同值，修改后旧绑定不会自动迁移 |
| `reply_mode` | `image` | `image` 图片或 `text` 文字 |
| `asset_download_mode` | `auto` | 首次图片模式后台准备素材；也可选 `manual` 或 `off` |
| `illustration_path` | 空 | 留空使用托管素材；非空优先使用自定义目录 |
| `subscriptions_enabled` | `false` | 启用订阅与主动推送 |

首次素材准备完成前可使用占位卡片，已有完整快照会复用。用 `/do素材状态` 查看进度；素材代理、超时和订阅周期等设置见[安装指南](https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/INSTALL.md)与[素材指南](https://github.com/HBLADEH/Dota2Forge/blob/15e1a50a07273c645f0a1066b61fe266dde216cc/docs/cookbook/illustrations.md)。Docker 自定义路径需在容器内可见。

## 数据说明

- 玩家和比赛来自 **STRATZ**，热门出装来自 **OpenDota**；数据覆盖取决于账号隐私、来源解析状态和接口可用性。
- MMR 是根据段位换算的区间或下界，**不是精确天梯分**。STRATZ IMP 是来源的本局表现分，不等同官方 MVP。
- 热门出装展示购买次数，不代表最优出装或购买顺序；缺失字段不会补零，请求失败不会伪装成无战绩。
- 图片绘制失败时回退为同次查询的文字结果；消息发送失败不自动重发。

英雄攻略和 AI Tool 尚未实现；其他平台及当前主题的完整聊天效果仍需独立验收。

## 更新与排障

更新前停用插件、退出 AstrBot 并备份配置和数据；更新分发目录后，用相同解释器重新运行安装器，再启动宿主。卸载前先停用，绑定和订阅数据保留。

- **等待配置**：填写 Token 和 namespace，保存后重载。
- **命令无响应**：检查唤醒前缀、插件加载状态和已安装版本。
- **找不到第 N 场**：在同一会话重新查询战绩，或直接传比赛 ID。
- **英雄或装备缺图**：查看素材状态；检查下载模式、代理或自定义目录。

完整步骤见[安装与更新指南](https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/INSTALL.md)。反馈问题时附插件版本、宿主版本、复现命令及脱敏错误信息。开发贡献见[开发指南](https://github.com/HBLADEH/Dota2Forge/blob/15e1a50a07273c645f0a1066b61fe266dde216cc/docs/cookbook/development.md)。

## 致谢与许可

感谢 AstrBot、STRATZ 和 OpenDota。代码使用 [MIT 许可证](https://github.com/HBLADEH/astrbot_plugin_dota2forge/blob/main/LICENSE)。Dota 2 及相关角色、美术权利属于 Valve；项目图标为独立生成的同人插画。第三方素材与字体遵循各自许可，见[素材说明](https://github.com/HBLADEH/Dota2Forge/blob/15e1a50a07273c645f0a1066b61fe266dde216cc/docs/cookbook/illustrations.md)。
