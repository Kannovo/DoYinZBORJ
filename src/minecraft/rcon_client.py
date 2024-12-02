import socket
import struct
import time
from typing import Optional

class RCONClient:
    """Minecraft RCON协议客户端"""
    
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.socket: Optional[socket.socket] = None
        self.authenticated = False
        
    def connect(self) -> bool:
        """连接到RCON服务器"""
        try:
            if self.socket:
                self.disconnect()
                
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.authenticated = self._authenticate()
            return self.authenticated
        except Exception as e:
            print(f"RCON连接失败: {str(e)}")
            return False
            
    def disconnect(self):
        """断开RCON连接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.authenticated = False
        
    def send_command(self, command: str) -> Optional[str]:
        """发送命令到服务器"""
        if not self.authenticated:
            if not self.connect():
                return None
                
        try:
            # 发送命令包
            self._send_packet(2, command)
            
            # 接收响应
            response_type, response_id, response = self._receive_packet()
            
            if response_type == 0:  # 错误响应
                print(f"命令执行失败: {response}")
                return None
                
            return response
        except Exception as e:
            print(f"发送命令失败: {str(e)}")
            self.disconnect()
            return None
            
    def _authenticate(self) -> bool:
        """进行RCON认证"""
        try:
            # 发送认证包
            self._send_packet(3, self.password)
            
            # 接收响应
            response_type, response_id, response = self._receive_packet()
            
            return response_type != -1
        except Exception as e:
            print(f"RCON认证失败: {str(e)}")
            return False
            
    def _send_packet(self, packet_type: int, payload: str):
        """发送RCON数据包"""
        if not self.socket:
            raise ConnectionError("未连接到服务器")
            
        # 构建数据包
        packet_id = 0
        byte_payload = payload.encode('utf8')
        packet = struct.pack('<ii', packet_id, packet_type) + byte_payload + b'\x00\x00'
        length = len(packet)
        
        # 发送数据包
        self.socket.send(struct.pack('<i', length) + packet)
        
    def _receive_packet(self) -> tuple[int, int, str]:
        """接收RCON数据包"""
        if not self.socket:
            raise ConnectionError("未连接到服务器")
            
        # 读取数据包长度
        length_data = self._receive_all(4)
        if not length_data:
            return -1, 0, ""
            
        length = struct.unpack('<i', length_data)[0]
        
        # 读取数据包内容
        packet_data = self._receive_all(length)
        if not packet_data:
            return -1, 0, ""
            
        # 解析数据包
        packet_id = struct.unpack('<i', packet_data[:4])[0]
        packet_type = struct.unpack('<i', packet_data[4:8])[0]
        payload = packet_data[8:-2].decode('utf8')
        
        return packet_type, packet_id, payload
        
    def _receive_all(self, length: int) -> Optional[bytes]:
        """接收指定长度的数据"""
        data = b''
        while len(data) < length:
            try:
                packet = self.socket.recv(length - len(data))
                if not packet:
                    return None
                data += packet
            except socket.error as e:
                print(f"接收数据失败: {str(e)}")
                return None
        return data