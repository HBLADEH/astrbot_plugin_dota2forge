from ._dota2forge_bootstrap import verify_dependencies as _verify_dependencies

_verify_dependencies(__file__)

"""AstrBot discovery bridge; installed separately from the SDK-free library."""

import asyncio
import base64
import re
import json

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import At, AtAll, Image
from astrbot.api.star import Context, Star, StarTools
from astrbot.core.star.filter.command import GreedyStr

from astrbot_plugin_dota2forge.application import AstrImageReply, AstrReply
from astrbot_plugin_dota2forge.identity import Caller
from astrbot_plugin_dota2forge.runtime import Runtime
from dota2forge_core import DeliveryOutcome, InvalidIdentityError, SubscriptionEvent, Dota2ForgeError
from dota2forge_core.review import REVIEW_INSTRUCTION
from dota2forge_core.feature_tools import TOOL_NAMES, tool_schema


def caller_from_event(event: AstrMessageEvent) -> Caller:
    bot = event.get_self_id()
    mentioned_other = any(
        isinstance(component, AtAll)
        or (isinstance(component, At) and str(component.qq) != bot)
        for component in event.get_messages()
    )
    return Caller(
        event.get_platform_name(), event.get_platform_id(), bot, event.get_sender_id(),
        mentioned_other, event.get_message_type().value, event.get_group_id(),
        event.is_admin() is True,
    )


class Dota2ForgePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self._config_snapshot = dict(config)
        self.runtime = None
        self._subscription_timer = None

    async def _send_subscription(
        self, event: SubscriptionEvent, replies: tuple[AstrReply, ...]
    ) -> DeliveryOutcome:
        from aiocqhttp.exceptions import ApiNotAvailable, Error

        if not replies:
            return DeliveryOutcome.NOT_ATTEMPTED
        try:
            caller = self.runtime.subscription_route(event)
        except InvalidIdentityError:
            return DeliveryOutcome.NOT_ATTEMPTED
        platform = next((item for item in self.context.platform_manager.platform_insts
                         if item.meta().id == caller.connection_id
                         and item.meta().name == caller.platform == "aiocqhttp"), None)
        if platform is None:
            return DeliveryOutcome.NOT_ATTEMPTED
        client = platform.get_client()
        if caller.bot_id not in getattr(client, "_wsr_api_clients", {}):
            return DeliveryOutcome.NOT_ATTEMPTED
        session = caller.session()
        if session is None:
            return DeliveryOutcome.NOT_ATTEMPTED
        kind, target = session
        if not target.isascii() or not target.isdecimal():
            return DeliveryOutcome.NOT_ATTEMPTED
        if kind == "GroupMessage":
            config = self.context.get_config(umo=f"{caller.connection_id}:{kind}:{target}")
            if caller.user_id not in {str(value) for value in config.get("admins_id", [])}:
                return DeliveryOutcome.NOT_ATTEMPTED
        message = [
            {"type": "image", "data": {
                "file": "base64://" + base64.b64encode(reply.artifact.data).decode("ascii")
            }} if isinstance(reply, AstrImageReply)
            else {"type": "text", "data": {"text": reply.text + "\n"}}
            for reply in replies
        ]
        params = {"group_id" if kind == "GroupMessage" else "user_id": int(target)}
        try:
            receipt = await asyncio.wait_for(client.call_action(
                "send_group_msg" if kind == "GroupMessage" else "send_private_msg",
                self_id=caller.bot_id, message=message,
                **params,
            ), timeout=15)
        except ApiNotAvailable:
            return DeliveryOutcome.NOT_ATTEMPTED
        except (Error, OSError, TimeoutError):
            return DeliveryOutcome.UNCERTAIN
        return (DeliveryOutcome.ACCEPTED if isinstance(receipt, dict)
                and type(receipt.get("message_id")) in {str, int}
                and receipt["message_id"] else DeliveryOutcome.UNCERTAIN)

    async def _subscription_loop(self):
        while True:
            await asyncio.sleep(60)
            await self.runtime.poll_subscriptions(self._send_subscription)

    def _start_subscriptions(self):
        if self.runtime.subscriptions_enabled and self._subscription_timer is None:
            self._subscription_timer = asyncio.create_task(self._subscription_loop())

    async def initialize(self):
        if self.runtime is not None:
            await self.runtime.start()
            self._start_subscriptions()
            return
        if not self._config_snapshot.get("asset_proxy"):
            get_config = getattr(self.context, "get_config", None)
            proxy = get_config().get("http_proxy", "") if callable(get_config) else ""
            if isinstance(proxy, str):
                self._config_snapshot["asset_proxy"] = proxy
        try:
            directory = StarTools.get_data_dir("astrbot_plugin_dota2forge")
        except (OSError, RuntimeError):
            self._config_snapshot.clear()
            logger.warning("Dota2Forge initialization failed: data directory unavailable")
            return
        self.runtime = Runtime(self._config_snapshot, directory)
        self._config_snapshot.clear()
        await self.runtime.start()
        self._start_subscriptions()
        logger.info("Dota2Forge initialized state=%s", self.runtime.state.value)

    async def terminate(self):
        self._config_snapshot.clear()
        logger.info("Dota2Forge terminate requested")
        if self._subscription_timer is not None:
            self._subscription_timer.cancel()
            await asyncio.gather(self._subscription_timer, return_exceptions=True)
            self._subscription_timer = None
        if self.runtime is not None:
            await self.runtime.close()
            logger.info(
                "Dota2Forge terminated state=%s client_closed=%s",
                self.runtime.state.value, self.runtime.client_closed,
            )

    async def _command(self, event: AstrMessageEvent, keyword: str, text: str):
        event.stop_event()
        if self.runtime is None:
            await event.send(event.plain_result("Dota2Forge 尚未就绪，请管理员检查配置。"))
            return
        async def send(reply: AstrReply) -> object:
            result = (
                event.chain_result([Image.fromBytes(reply.artifact.data)])
                if isinstance(reply, AstrImageReply)
                else event.plain_result(reply.text)
            )
            return await event.send(result)
        await self.runtime.dispatch(caller_from_event(event), keyword, text, send)

    @filter.command("do帮助")
    async def help(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do帮助", text)

    @filter.command("do菜单")
    async def menu(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do菜单", text)

    @filter.command("do素材状态")
    async def asset_status(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do素材状态", text)

    @filter.command("do下载素材")
    async def asset_download(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do下载素材", text)

    @filter.command("do更新素材")
    async def asset_update(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do更新素材", text)

    @filter.command("do绑定")
    async def bind(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do绑定", text)

    @filter.command("do改绑")
    async def rebind(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do改绑", text)

    @filter.command("do账号")
    async def binding(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do账号", text)

    @filter.command("do解绑")
    async def unbind(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do解绑", text)

    @filter.command("do查询", alias={"do段位"})
    async def player(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do查询", text)

    @filter.command("do战绩", alias={"do最近"})
    async def recent(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do战绩", text)

    @filter.command("do比赛")
    async def match(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do比赛", text)

    @filter.command("do出装")
    async def items(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do出装", text)

    @filter.command("do强势")
    async def hero_meta(self, event: AstrMessageEvent, text: GreedyStr = ""):
        await self._command(event, "do强势", text)

    @filter.command("do攻略")
    async def hero_guide(self, event: AstrMessageEvent, text: GreedyStr = ""):
        await self._command(event, "do攻略", text)

    @filter.command("do攻略样例")
    async def hero_guide_sample(self, event: AstrMessageEvent, text: GreedyStr = ""):
        await self._command(event, "do攻略样例", text)

    @filter.regex(r"^/?do(?P<guide_hero>.{1,64})攻略(?:\s+(?P<guide_args>.{1,80}))?$")
    async def hero_guide_alias(self, event: AstrMessageEvent):
        selected = re.fullmatch(r"/?do(?P<guide_hero>.{1,64})攻略(?:\s+(?P<guide_args>.{1,80}))?", event.get_message_str())
        if selected:
            await self._command(event, "do攻略", selected["guide_hero"] + " " + (selected["guide_args"] or ""))

    async def _native_scope(self, event, create=False):
        manager = getattr(self.context, "conversation_manager", None)
        if manager is None:
            return None
        origin = event.unified_msg_origin
        cid = await manager.get_curr_conversation_id(origin)
        if cid is None and create:
            cid = await manager.new_conversation(origin)
        if cid is None:
            return None
        conversation = await manager.get_conversation(origin, cid)
        if conversation is None:
            return None
        return cid, (cid, conversation.created_at), conversation

    @filter.command("do复盘")
    async def review_match(self, event: AstrMessageEvent, text: GreedyStr = ""):
        if self.runtime is None:
            await self._command(event, "do复盘", text)
            return
        provider = getattr(self.context, "get_current_chat_provider_id", None)
        try:
            provider_id = await provider(event.unified_msg_origin) if callable(provider) else None
        except ValueError:
            provider_id = None
        scope = await self._native_scope(event, create=True) if provider_id else None
        if scope is None:
            await self._command(event, "do复盘", text)
            return
        cid, generation, conversation = scope
        try:
            facts = await self.runtime.begin_review(caller_from_event(event), cid, generation, text)
        except Dota2ForgeError as error:
            yield event.plain_result("复盘数据获取失败：" + str(getattr(error, "code", "invalid_context")) + "。请核实参数或稍后手动再试。")
            return
        except ValueError:
            yield event.plain_result("复盘参数不正确，请使用 do复盘 <比赛ID> [英雄]。")
            return
        prompt = REVIEW_INSTRUCTION + "\n用户请求：do复盘 " + text
        prompt += "\n本场来源事实（不含账号或聊天身份）：" + json.dumps(facts, ensure_ascii=False)
        if "报告" in text.split():
            prompt += "\n用户要求完整报告，请按概览、经济、出装和改进建议展开。"
        yield event.request_llm(prompt=prompt, conversation=conversation)

    @filter.on_llm_request()
    async def review_turn_hint(self, event, req):
        # Only refine tools already allowed by this request/persona; do not grant new tools.
        tool_set = getattr(req, "func_tool", None)
        if tool_set is not None and callable(getattr(tool_set, "get_tool", None)):
            for name in TOOL_NAMES:
                tool = tool_set.get_tool(name)
                if tool is not None:
                    tool.parameters = tool_schema(name)
        if self.runtime is None:
            return
        scope = await self._native_scope(event)
        if scope is None:
            return
        cid, generation, conversation = scope
        try:
            history_count = len(json.loads(conversation.history or "[]"))
        except (ValueError, TypeError):
            history_count = 0
        hint = self.runtime.review_hint(caller_from_event(event), cid, generation,
                                        event.get_message_str(), history_count)
        if hint and hasattr(req, "extra_user_content_parts"):
            from astrbot.core.agent.message import TextPart
            req.extra_user_content_parts.append(TextPart(text=hint))

    async def _dota_tool(self, event, name, args):
        scope = await self._native_scope(event)
        if self.runtime is None or scope is None:
            return '{"error":"native_session_unavailable"}'
        cid, generation, _ = scope
        try:
            payload, artifact = await self.runtime.ai_tool(caller_from_event(event), cid, generation, name, args)
            if artifact is not None:
                await event.send(event.chain_result([Image.fromBytes(artifact.data)]))
                payload["image_delivery"] = "已发送一次；文字事实随本工具结果进入原生历史，无需OCR或重复添加。"
            return json.dumps(payload, ensure_ascii=False)
        except Dota2ForgeError as error:
            return json.dumps({"error": type(error).__name__, "code": getattr(error, "code", "invalid_context"), "source": getattr(error, "source", None)}, ensure_ascii=False)
        except ValueError:
            return '{"error":"invalid_arguments_or_native_session"}'

    @filter.llm_tool(name="get_dota2_meta")
    async def get_dota2_meta(self, event: AstrMessageEvent, position: int = 0, rank: str = "ALL", days: int = 7, sort: str = "reliable"):
        """Dota2 当前版本强势英雄观察，含来源、窗口、样本和可靠度，不保证上分。

        Args:
            position(number): 0全部位置，1到5指定位置。
            rank(string): ALL或HERALD/GUARDIAN/CRUSADER/ARCHON/LEGEND/ANCIENT/DIVINE/IMMORTAL。
            days(number): 7或14；缺日明确显示。
            sort(string): reliable或win_rate。
        """
        return await self._dota_tool(event, "get_dota2_meta", {"position": position, "rank": rank, "days": days, "sort": sort})

    @filter.llm_tool(name="get_dota2_hero_guide")
    async def get_dota2_hero_guide(self, event: AstrMessageEvent, hero_name: str, position: int = 1, match_id: str = ""):
        """Dota2 攻略观察；指定比赛时查询单场样例，不混为聚合推荐。

        Args:
            hero_name(string): 英雄中文名、英文名或简称。
            position(number): 1到5号位。
            match_id(string): 可选规范比赛ID，留空查询聚合攻略。
        """
        return await self._dota_tool(event, "get_dota2_hero_guide", {"hero_name": hero_name, "position": position, "match_id": match_id})

    @filter.llm_tool(name="get_dota2_review_context")
    async def get_dota2_review_context(self, event: AstrMessageEvent, match_id: str = "", hero_name: str = "", topic: str = "overview"):
        """Dota2 复盘来源事实。追问可省略ID沿用当前会话；不把终局统计当对线事件。

        Args:
            match_id(string): 首次提供比赛ID，已定位时可留空。
            hero_name(string): 可选本场英雄；留空沿用当前视角或绑定偏好。
            topic(string): overview/economy/items/laning/team。
        """
        return await self._dota_tool(event, "get_dota2_review_context", {"match_id": match_id, "hero_name": hero_name, "topic": topic})

    @filter.llm_tool(name="render_dota2_review_data")
    async def render_dota2_review_data(self, event: AstrMessageEvent, kind: str, match_id: str = "", hero_name: str = "", start_seconds: int = 0, end_seconds: int = 0):
        """需要解释数据或用户要图时补充真实曲线/购买记录；每次调用发送一次图片及事实。

        Args:
            kind(string): economy/team_advantage/items。
            match_id(string): 可选，留空沿用当前复盘比赛。
            hero_name(string): 可选本场英雄。
            start_seconds(number): 区间开始秒数，最低-600。
            end_seconds(number): 区间结束秒数，0为实际比赛时长。
        """
        args = {"kind": kind, "match_id": match_id, "hero_name": hero_name, "start_seconds": start_seconds}
        if end_seconds != 0:
            args["end_seconds"] = end_seconds
        return await self._dota_tool(event, "render_dota2_review_data", args)

    @filter.regex(r"^/?do(?P<hero>.{1,64})出装$")
    async def named_items(self, event: AstrMessageEvent):
        selected = re.fullmatch(r"/?do(?P<hero>.{1,64})出装", event.get_message_str().strip())
        if selected is not None:
            await self._command(event, "do出装", selected["hero"])

    @filter.command("do状态")
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def status(self, event: AstrMessageEvent, text: GreedyStr):
        event.stop_event()
        caller = caller_from_event(event)
        if not caller.is_admin or caller.mentioned_other or text.strip():
            return
        state = self.runtime.state.value if self.runtime is not None else "failed"
        closed = self.runtime.client_closed if self.runtime is not None else True
        timer = self._subscription_timer is not None and not self._subscription_timer.done()
        await event.send(event.plain_result(
            f"Dota2Forge state={state} client_closed={closed} subscription_timer={timer}"
        ))

    @filter.command("do订阅")
    async def subscribe(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do订阅", text)

    @filter.command("do订阅玩家")
    async def subscribe_player(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do订阅玩家", text)

    @filter.command("do订阅比赛")
    async def subscribe_match(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do订阅比赛", text)

    @filter.command("do订阅列表")
    async def subscriptions(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do订阅列表", text)

    @filter.command("do取消订阅")
    async def unsubscribe(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do取消订阅", text)

    @filter.command("do重试推送")
    async def retry(self, event: AstrMessageEvent, text: GreedyStr):
        await self._command(event, "do重试推送", text)

    @filter.command("do停用")
    @filter.permission_type(filter.PermissionType.ADMIN)
    async def stop(self, event: AstrMessageEvent, text: GreedyStr):
        event.stop_event()
        caller = caller_from_event(event)
        if not caller.is_admin or caller.mentioned_other or text.strip():
            return
        await self.terminate()
        await event.send(event.plain_result("Dota2Forge 已停用并关闭资源；重新加载后恢复。"))
