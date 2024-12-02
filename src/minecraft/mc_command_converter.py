from typing import Optional, Dict
import socket
from datetime import datetime
import json
import os
from mcrcon import MCRcon
from src.models.message_store import MessageStore, MessageType, Message

class MinecraftCommandConverter:
    def __init__(self, message_store: MessageStore, host: str = 'localhost', port: int = 25575, password: str = 'Pzx030709'):
        """
        初始化Minecraft命令转换器
        
        Args:
            message_store: 消息存储系统实例
            host: Minecraft服务器地址
            port: RCON端口
            password: RCON密码
        """
        self.message_store = message_store
        self.host = host
        self.port = port
        self.password = password
        self.last_processed_time = datetime.now()
        
        # 记录已处理的消息ID
        self.processed_messages = set()
        
        # 加载配置文件
        self.config_file = os.path.join('config', 'minecraft_commands.json')
        self.config = self.load_config()  # 确保config属性被设置
        print("配置文件加载完成:", self.config)  # 添加调试信息
        
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "gift_commands": {},  # 移除默认的礼物命令配置
            "chat_commands": {
                "生成僵尸": {
                    "command": "/summon minecraft:zombie ~ ~ ~",
                    "count": 1
                },
                "生成骷髅": {
                    "command": "/summon minecraft:skeleton ~ ~ ~",
                    "count": 1
                },
                "生成苦力怕": {
                    "command": "/summon minecraft:creeper ~ ~ ~",
                    "count": 1
                },
                "清除怪物": {
                    "command": "/kill @e[type=!player]",
                    "count": 1
                }
            }
        }
        
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 确保配置文件包含所有必要的键
                    if 'gift_commands' not in loaded_config:
                        loaded_config['gift_commands'] = {}
                    if 'chat_commands' not in loaded_config:
                        loaded_config['chat_commands'] = default_config['chat_commands']
                    return loaded_config
            else:
                # 如果文件不存在，使用默认配置
                self.save_config(default_config)  # 保存默认配置到文件
                return default_config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            import traceback
            print(traceback.format_exc())
            return default_config
            
    def save_config(self, config=None):
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 如果没有提供配置，使用当前的配置
            if config is None:
                config = self.config
                
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            import traceback
            print(traceback.format_exc())
            
    def update_gift_command(self, gift_md5: str, command: str, count: int = 1):
        """
        更新礼物命令配置
        
        Args:
            gift_md5: 礼物的MD5值
            command: 要执行的命令
            count: 每个礼物的基础执行次数（将与礼物数量相乘）
        """
        if not command.startswith('/'):
            command = '/' + command  # 确保命令以/开头
            
        self.config['gift_commands'][gift_md5] = {
            "command": command,
            "count": count
        }
        self.save_config()
        print(f"已更新礼物命令配置: MD5={gift_md5}, 命令={command}, 基础执行次数={count}")
        
    def update_chat_command(self, trigger: str, command: str, count: int = 1):
        """
        更新聊天命令配置
        
        Args:
            trigger: 触发词
            command: 要执行的命令
            count: 每次触发的执行次数
        """
        if not command.startswith('/'):
            command = '/' + command  # 确保命令以/开头
            
        self.config['chat_commands'][trigger] = {
            "command": command,
            "count": count
        }
        self.save_config()
        print(f"已更新聊天命令配置: 触发词='{trigger}', 命令={command}, 执行次数={count}")
    
    def clear_all_commands(self):
        """清空所有命令配置"""
        self.config['gift_commands'] = {}
        self.config['chat_commands'] = {}
        self.save_config()
        print("已清空所有命令配置")
    
    def process_new_messages(self):
        """处理新消息并转换为Minecraft命令"""
        current_time = datetime.now()
        
        # 获取所有类型的新消息
        chat_messages = self.message_store.get_messages(MessageType.CHAT)
        gift_messages = self.message_store.get_messages(MessageType.GIFT)
        
        commands = []
        
        # 处理礼物消息
        for message in gift_messages:
            # 检查消息是否已处理
            if message.message_id in self.processed_messages:
                continue
                
            if message.gift_md5:
                command = self._convert_gift_to_command(message)
                if command:
                    commands.append(command)
                    # 记录已处理的消息ID
                    self.processed_messages.add(message.message_id)
        
        # 处理聊天消息
        for message in chat_messages:
            # 检查消息是否已处理
            if message.message_id in self.processed_messages:
                continue
                
            command = self._convert_chat_to_command(message)
            if command:
                commands.append(command)
                # 记录已处理的消息ID
                self.processed_messages.add(message.message_id)
        
        self.last_processed_time = current_time
        
        # 清理旧的消息ID记录（保留最近1000条）
        if len(self.processed_messages) > 1000:
            self.processed_messages = set(list(self.processed_messages)[-1000:])
        
        # 执行命令
        if commands:
            self._execute_commands(commands)
        
        return commands
    
    def _convert_gift_to_command(self, message: Message) -> Optional[str]:
        """将礼物消息转换为Minecraft命令"""
        if not message.gift_md5:
            return None
            
        gift_config = self.config['gift_commands'].get(message.gift_md5)
        if gift_config:
            base_command = gift_config['command']
            base_count = gift_config.get('count', 1)  # 基础执行次数
            
            # 计算实际执行次数 = 礼物数量 × 基础执行次数
            actual_count = (message.gift_count or 1) * base_count
            print(f"收到礼物 {message.gift_md5}:")
            print(f"- 礼物数量: {message.gift_count}")
            print(f"- 基础执行次数: {base_count}")
            print(f"- 实际执行次数: {actual_count}")
            
            # 生成多次命令
            commands = []
            for i in range(actual_count):
                commands.append(base_command)
                print(f"- 生成第 {i+1}/{actual_count} 条命令: {base_command}")
            
            # 返回所有命令，每个命令独立一行
            result = "\n".join(commands)
            print(f"最终生成的命令:\n{result}")
            return result
        return None
    
    def _convert_chat_to_command(self, message: Message) -> Optional[str]:
        """将聊天消息转换为Minecraft命令"""
        command_config = self.config['chat_commands'].get(message.content)
        if command_config:
            base_command = command_config['command']
            base_count = command_config.get('count', 1)  # 基础执行次数
            
            # 计算实际执行次数
            actual_count = base_count
            print(f"检测到聊天触发词 '{message.content}'，基础执行次数 {base_count}，实际执行次数 {actual_count}")
            
            # 生成多次命令
            commands = []
            for i in range(actual_count):
                commands.append(base_command)
                print(f"生成第 {i+1}/{actual_count} 条命令: {base_command}")
            
            # 返回所有命令，每个命令独立一行
            return "\n".join(commands)
        return None
    
    def _execute_commands(self, commands: list):
        """执行Minecraft命令"""
        try:
            print(f"尝试连接RCON - 地址: {self.host}:{self.port}")
            print(f"使用密码: {self.password}")  # 临时添加，调试后记得删除
            with MCRcon(self.host, self.password, self.port) as mcr:
                print("RCON连接成功")
                for command in commands:
                    # 如果命令包含多行，分别执行
                    for cmd in command.split('\n'):
                        if cmd.strip():  # 确保命令不为空
                            try:
                                print(f"正在执行命令: {cmd}")
                                # 测试连接是否有效
                                test_response = mcr.command("/say RCON测试")
                                print(f"连接测试响应: {test_response}")
                                
                                # 执行实际命令
                                response = mcr.command(cmd)
                                print(f"命令执行响应: {response}")
                            except Exception as cmd_error:
                                print(f"执行单个命令失败: {cmd}")
                                print(f"错误信息: {str(cmd_error)}")
                                import traceback
                                print(traceback.format_exc())
                                continue
        except ConnectionRefusedError:
            print(f"RCON连接被拒绝 - 请检查服务器是否启动以及端口{self.port}是否正确")
            raise
        except Exception as e:
            print(f"RCON连接或执行失败")
            print(f"地址: {self.host}")
            print(f"端口: {self.port}")
            print(f"密码: {self.password}")  # 临时添加，调试后记得删除
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise