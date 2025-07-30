from pathlib import Path
import requests
import json
import nonebot
from nonebot import get_plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .config import Config
from nonebot import on_command

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-simple-setu",
    description="一个简单到不能再简单的色图插件",
    usage="通过指令获取setu",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

config = get_plugin_config(Config)

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)



setu = on_command("setu", aliases={"色图", "来份色图"})

@setu.handle()
async def handle_function(event : MessageEvent ,args: Message = CommandArg(),):
    if config.api_url == 0:
        # 提取参数纯文本作为地名，并判断是否有效
        if tag := args.extract_plain_text():
            sender_qq = event.get_user_id()
            json_dict = requests.get(f"https://api.lolicon.app/setu/v2?tag={tag}").json()
            title = json_dict["data"][0]["title"]
            pid = json_dict["data"][0]["pid"]
            author = json_dict["data"][0]["author"]
            url = json_dict["data"][0]["urls"]["original"]
            await setu.send(MessageSegment.at(sender_qq)+f"\n标题:{title}\nPID:{pid}\n作者:{author}")
            await setu.finish(MessageSegment.image(f"{url}"))
        else:
            sender_qq = event.get_user_id()
            json_dict = requests.get(f"https://api.lolicon.app/setu/v2").json()
            title = json_dict["data"][0]["title"]
            pid = json_dict["data"][0]["pid"]
            author = json_dict["data"][0]["author"]
            url = json_dict["data"][0]["urls"]["original"]
            await setu.send(MessageSegment.at(sender_qq) + f"\n标题:{title}\nPID:{pid}\n作者:{author}")
            await setu.finish(MessageSegment.image(f"{url}"))
    elif config.api_url == 1:
        if tag := args.extract_plain_text():
            sender_qq = event.get_user_id()
            json_dict = requests.get(f"https://image.anosu.top/pixiv/json?keyword={tag}").json()
            title = json_dict[0]["title"]
            pid = json_dict[0]["pid"]
            author = json_dict[0]["user"]
            url = json_dict[0]["url"]
            await setu.send(MessageSegment.at(sender_qq)+f"\n标题:{title}\nPID:{pid}\n作者:{author}")
            await setu.finish(MessageSegment.image(f"{url}"))
        else:
            sender_qq = event.get_user_id()
            json_dict = requests.get(f"https://image.anosu.top/pixiv/json")
            title = json_dict[0]["title"]
            pid = json_dict[0]["pid"]
            author = json_dict[0]["user"]
            url = json_dict[0]["url"]
            await setu.send(MessageSegment.at(sender_qq) + f"\n标题:{title}\nPID:{pid}\n作者:{author}")
            await setu.finish(MessageSegment.image(f"{url}"))
leg = on_command("leg", aliases={"腿子", "来份腿子"})

@leg.handle()
async def handle_function(event : MessageEvent ,args: Message = CommandArg(),):


        # 提取参数纯文本作为地名，并判断是否有效

    sender_qq_leg = event.get_user_id()
    json_dict_leg = requests.get("https://api.lolimi.cn/API/meizi/api.php?type=json").json()
    image_leg = json_dict_leg["text"]
    at_segment_leg = MessageSegment.at(user_id=sender_qq_leg)
    await setu.send(at_segment_leg)
    await setu.finish(MessageSegment.image(image_leg))
girl = on_command("girl", aliases={"少女写真", "来份写真"})

@girl.handle()
async def handle_function(event : MessageEvent ,args: Message = CommandArg(),):


        # 提取参数纯文本作为地名，并判断是否有效

    sender_qq_girl = event.get_user_id()
    json_dict_girl = requests.get("https://api.lolimi.cn/API/meinv/api.php?type=json").json()
    image_girl = json_dict_girl["data"]["image"]
    at_segment_girl = MessageSegment.at(user_id=sender_qq_girl)
    await setu.send(at_segment_girl)
    await setu.finish(MessageSegment.image(image_girl))




