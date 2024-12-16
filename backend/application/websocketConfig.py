# -*- coding: utf-8 -*-
import urllib

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
import json

from channels.layers import get_channel_layer
from jwt import InvalidSignatureError
from rest_framework.request import Request

from application import settings
from dvadmin.utils.serializers import CustomModelSerializer

send_dict = {}


# 发送消息结构体
def set_message(sender, msg_type, msg, unread=0):
    text = {
        'sender': sender,
        'contentType': msg_type,
        'content': msg,
        'unread': unread
    }
    return text


def request_data(scope):
    query_string = scope.get('query_string', b'').decode('utf-8')
    qs = urllib.parse.parse_qs(query_string)
    return qs


class DvadminWebSocket(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            import jwt
            self.service_uid = self.scope["url_route"]["kwargs"]["service_uid"]
            decoded_result = jwt.decode(self.service_uid, settings.SECRET_KEY, algorithms=["HS256"])
            if decoded_result:
                self.user_id = decoded_result.get('user_id')
                self.chat_group_name = "user_" + str(self.user_id)
                # 收到连接时候处理，
                await self.channel_layer.group_add(
                    self.chat_group_name,
                    self.channel_name
                )
                await self.accept()
                # 主动推送消息
                unread_count = await _get_message_unread(self.user_id)
                if unread_count == 0:
                    # 发送连接成功
                    await self.send_json(set_message('system', 'SYSTEM', '您已上线'))
                else:
                    await self.send_json(
                        set_message('system', 'SYSTEM', "请查看您的未读消息~",
                                    unread=unread_count))
        except InvalidSignatureError:
            await self.disconnect(None)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        print("连接关闭")
        try:
            await self.close(close_code)
        except Exception:
            pass

def websocket_push(user_id, message):
    username = "user_" + str(user_id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        username,
        {
            "type": "push.message",
            "json": message
        }
    )
