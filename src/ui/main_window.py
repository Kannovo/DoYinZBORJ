from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import QThread, Signal
from .message_panels import MessagePanel
from .gift_stats_panel import GiftStatsPanel
from ..models.message import MessageType

class MainWindow(QWidget):
    def __init__(self, message_store):
        super().__init__()
        self.message_store = message_store
        self.init_ui()
        
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建顶部控制栏
        control_layout = QHBoxLayout()
        
        # URL输入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入抖音直播间链接")
        
        # 控制按钮
        self.start_button = QPushButton("开始采集")
        self.stop_button = QPushButton("停止采集")
        self.stop_button.setEnabled(False)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        
        # 添加控件到控制栏
        control_layout.addWidget(self.url_input)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.status_label)
        
        # 创建消息显示面板布局
        panels_layout = QHBoxLayout()
        
        # 创建左侧布局（聊天和礼物）
        left_layout = QVBoxLayout()
        self.chat_panel = MessagePanel("聊天消息", MessageType.CHAT)
        self.gift_panel = MessagePanel("礼物消息", MessageType.GIFT)
        left_layout.addWidget(self.chat_panel, 1)
        left_layout.addWidget(self.gift_panel, 1)
        
        # 创建中间布局（点赞和进入）
        middle_layout = QVBoxLayout()
        self.like_panel = MessagePanel("点赞消息", MessageType.LIKE)
        self.enter_panel = MessagePanel("进入消息", MessageType.ENTER)
        middle_layout.addWidget(self.like_panel)
        middle_layout.addWidget(self.enter_panel)
        
        # 创建右侧布局（礼物统计）
        right_layout = QVBoxLayout()
        self.gift_stats_panel = GiftStatsPanel()
        right_layout.addWidget(self.gift_stats_panel)
        
        # 将布局添加到主面板布局
        panels_layout.addLayout(left_layout, 5)    # 左侧占50%
        panels_layout.addLayout(middle_layout, 2)  # 中间占20%
        panels_layout.addLayout(right_layout, 3)   # 右侧占30%
        
        # 组装主布局
        main_layout.addLayout(control_layout)
        main_layout.addLayout(panels_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle("抖音直播数据采集")
        self.resize(1400, 800)  # 增加窗口宽度以适应新面板
        
    def handle_gift_message(self, message):
        """处理礼物消息，更新礼物统计"""
        if message.type == MessageType.GIFT and 'gift_md5' in message.raw_data:
            md5 = message.raw_data['gift_md5']
            if md5 and 'gift_image_url' in message.raw_data:
                self.gift_stats_panel.add_gift(md5, message.raw_data['gift_image_url'])