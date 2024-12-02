from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class MessageType(Enum):
    CHAT = auto()    # 聊天消息
    GIFT = auto()    # 礼物消息
    LIKE = auto()    # 点赞消息
    ENTER = auto()   # 进入消息

@dataclass
class Message:
    message_id: str              # 消息唯一ID
    type: MessageType           # 消息类型
    content: str               # 消息内容
    user_name: str            # 用户名
    timestamp: datetime = None  # 消息时间戳
    gift_md5: Optional[str] = None  # 礼物MD5值，仅在type为GIFT时有效
    gift_count: Optional[int] = None # 礼物数量，仅在type为GIFT时有效
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __str__(self):
        if self.type == MessageType.GIFT:
            return f"{self.user_name} 送出了 [md5: {self.gift_md5}] × {self.gift_count}"
        elif self.type == MessageType.LIKE:
            return f"{self.user_name} {self.content}"
        elif self.type == MessageType.ENTER:
            return f"{self.user_name} {self.content}"
        else:
            return f"{self.user_name}: {self.content}"