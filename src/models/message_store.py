from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .message import Message, MessageType
import threading
import time

class MessageStore:
    def __init__(self, ttl_seconds: int = 30):
        # 首先初始化线程锁
        self._lock = threading.Lock()
        
        self.ttl_seconds = ttl_seconds
        self.chat_messages: Dict[str, tuple[Message, datetime]] = {}
        self.gift_messages: Dict[str, tuple[Message, datetime]] = {}
        self.like_messages: Dict[str, tuple[Message, datetime]] = {}
        self.enter_messages: Dict[str, tuple[Message, datetime]] = {}
        
        # 启动清理线程
        self.is_running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        print("消息存储系统已初始化")
    
    def add_message(self, message: Message):
        """添加新消息到存储"""
        try:
            with self._lock:
                current_time = datetime.now()
                
                # 根据消息类型选择存储位置
                if message.type == MessageType.CHAT:
                    self.chat_messages[message.message_id] = (message, current_time)
                elif message.type == MessageType.GIFT:
                    self.gift_messages[message.message_id] = (message, current_time)
                elif message.type == MessageType.LIKE:
                    self.like_messages[message.message_id] = (message, current_time)
                elif message.type == MessageType.ENTER:
                    self.enter_messages[message.message_id] = (message, current_time)
        except Exception as e:
            print(f"添加消息失败: {str(e)}")
    
    def get_messages(self, message_type: MessageType) -> List[Message]:
        """获取指定类型的所有有效消息"""
        try:
            with self._lock:
                if message_type == MessageType.CHAT:
                    return [msg for msg, _ in self.chat_messages.values()]
                elif message_type == MessageType.GIFT:
                    return [msg for msg, _ in self.gift_messages.values()]
                elif message_type == MessageType.LIKE:
                    return [msg for msg, _ in self.like_messages.values()]
                elif message_type == MessageType.ENTER:
                    return [msg for msg, _ in self.enter_messages.values()]
        except Exception as e:
            print(f"获取消息失败: {str(e)}")
        return []
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """根据消息ID获取消息"""
        try:
            with self._lock:
                # 在所有存储中查找消息
                for storage in [self.chat_messages, self.gift_messages, 
                              self.like_messages, self.enter_messages]:
                    if message_id in storage:
                        return storage[message_id][0]
        except Exception as e:
            print(f"获取消息失败: {str(e)}")
        return None
    
    def _cleanup_expired_messages(self):
        """清理过期消息"""
        try:
            with self._lock:
                current_time = datetime.now()
                expiration_time = current_time - timedelta(seconds=self.ttl_seconds)
                
                # 清理每个存储的过期消息
                def cleanup_storage(storage: Dict[str, tuple[Message, datetime]]):
                    expired_keys = [
                        key for key, (_, timestamp) in storage.items()
                        if timestamp < expiration_time
                    ]
                    for key in expired_keys:
                        del storage[key]
                    return len(expired_keys)
                
                # 清理所有存储
                expired_count = sum([
                    cleanup_storage(self.chat_messages),
                    cleanup_storage(self.gift_messages),
                    cleanup_storage(self.like_messages),
                    cleanup_storage(self.enter_messages)
                ])
                
                if expired_count > 0:
                    print(f"已清理 {expired_count} 条过期消息")
        except Exception as e:
            print(f"清理消息失败: {str(e)}")
    
    def _cleanup_loop(self):
        """清理循环"""
        while self.is_running:
            try:
                self._cleanup_expired_messages()
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                print(f"清理循环出错: {str(e)}")
                time.sleep(5)  # 出错时等待更长时间
    
    def get_stats(self) -> Dict[str, int]:
        """获取当前存储统计信息"""
        try:
            with self._lock:
                return {
                    "chat": len(self.chat_messages),
                    "gift": len(self.gift_messages),
                    "like": len(self.like_messages),
                    "enter": len(self.enter_messages)
                }
        except Exception as e:
            print(f"获取统计信息失败: {str(e)}")
            return {"chat": 0, "gift": 0, "like": 0, "enter": 0}
    
    def shutdown(self):
        """关闭消息存储系统"""
        try:
            self.is_running = False
            if hasattr(self, 'cleanup_thread') and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=2)  # 最多等待2秒
            print("消息存储系统已关闭")
        except Exception as e:
            print(f"关闭存储系统失败: {str(e)}") 