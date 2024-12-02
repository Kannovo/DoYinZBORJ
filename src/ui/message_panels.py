from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from ..models.message import MessageType

class MessagePanel(QWidget):
    def __init__(self, title: str, message_type: MessageType):
        super().__init__()
        self.message_type = message_type
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加标题
        title_label = QLabel(title)
        layout.addWidget(title_label)
        
        # 创建文本显示区域
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)  # 设置为只读
        layout.addWidget(self.text_area)
        
        self.setLayout(layout)
        print(f"创建消息面板: {title}")
        
    def add_message(self, message):
        """添加新消息到面板"""
        try:
            time_str = message.timestamp.strftime('%H:%M:%S')
            formatted_message = f"[{time_str}] {message.user_name}: {message.content}\n"
            
            # 获取当前滚动条位置
            scrollbar = self.text_area.verticalScrollBar()
            was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
            
            # 添加消息
            self.text_area.moveCursor(QTextCursor.End)
            self.text_area.insertPlainText(formatted_message)
            
            # 如果之前在底部，保持在底部
            if was_at_bottom:
                scrollbar.setValue(scrollbar.maximum())
                
        except Exception as e:
            print(f"添加消息到面板时出错: {str(e)}")
            
    def clear(self):
        """清空面板内容"""
        self.text_area.clear()