from ._dota2forge_bootstrap import verify_dependencies as _verify_dependencies

_verify_dependencies(__file__)

"""AstrBot discovery bridge; installed separately from the SDK-free library."""

import asyncio
import re

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import At, AtAll, Image
from astrbot.api.star import Context, Star, StarTools
from astrbot.core.star.filter.command import GreedyStr

from astrbot_plugin_dota2forge.application import AstrImageReply, AstrReply
from astrbot_plugin_dota2forge.identity import Caller
from astrbot_plugin_dota2forge.runtime import Runtime
from dota2forge_core import DeliveryOutcome, InvalidIdentityError, SubscriptionEvent


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

    async def _send_subscription(self, event: SubscriptionEvent, text: str) -> DeliveryOutcome:
        from aiocqhttp.exceptions import ApiNotAvailable, Error

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
        params = {"group_id" if kind == "GroupMessage" else "user_id": int(target)}
        try:
            receipt = await asyncio.wait_for(client.call_action(
                "send_group_msg" if kind == "GroupMessage" else "send_private_msg",
                self_id=caller.bot_id, message=[{"type": "text", "data": {"text": text}}],
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
