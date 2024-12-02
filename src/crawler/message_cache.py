from collections import deque
from datetime import datetime
from ..models.message import Message, MessageType

class MessageCache:
    def __init__(self):
        self.last_message_ids = set()  # 上一次爬取的消息ID集合
        self.message_buffer = deque(maxlen=1000)  # 消息缓冲区，用于UI显示
    
    def compare_and_store(self, current_messages):
        """比较当前消息和上次消息，找出新增的消息并存储"""
        # 获取当前消息的ID集合
        current_message_ids = {msg.message_id for msg in current_messages}
        
        # 找出新增的消息ID
        new_message_ids = current_message_ids - self.last_message_ids
        
        # 获取新增的消息对象
        new_messages = [msg for msg in current_messages if msg.message_id in new_message_ids]
        
        # 将新消息添加到缓冲区
        for msg in new_messages:
            self.message_buffer.append(msg)
        
        # 更新上次消息ID集合
        self.last_message_ids = current_message_ids
        
        return new_messages
    
    def get_new_messages(self):
        """获取并清空缓冲区中的消息"""
        messages = list(self.message_buffer)
        self.message_buffer.clear()
        return messages