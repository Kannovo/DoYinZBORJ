from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QColor, QTextCursor
from datetime import datetime

from .mc_command_converter import MinecraftCommandConverter

class MinecraftCommandWindow(QMainWindow):
    def __init__(self, message_store):
        super().__init__()
        self.message_store = message_store
        self.unsaved_changes = False
        
        # 创建命令转换器
        self.converter = MinecraftCommandConverter(message_store)
        print("创建命令转换器完成")
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Minecraft 命令转换器")
        self.setGeometry(200, 200, 800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
                color: #333;
            }
            QLineEdit, QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QPushButton {
                padding: 5px 15px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
                font-family: Consolas, Monaco, monospace;
            }
            QTableWidget {
                border: 1px solid #ccc;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-top: 2px solid #4a90e2;
            }
        """)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标签页
        tabs = QTabWidget()
        layout.addWidget(tabs)
        print("创建标签页完成")
        
        # 主控制页面
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setSpacing(10)
        
        # 服务器配置区域
        server_group = QGroupBox("服务器配置")
        server_layout = QHBoxLayout(server_group)
        
        server_layout.addWidget(QLabel("服务器地址:"))
        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        server_layout.addWidget(self.host_input)
        
        server_layout.addWidget(QLabel("端口:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(25575)
        server_layout.addWidget(self.port_input)
        
        server_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setText("Pzx030709")
        self.password_input.setEchoMode(QLineEdit.Password)
        server_layout.addWidget(self.password_input)
        
        main_layout.addWidget(server_group)
        
        # 命令显示区域
        log_group = QGroupBox("命令日志")
        log_layout = QVBoxLayout(log_group)
        
        self.command_display = QTextEdit()
        self.command_display.setReadOnly(True)
        self.command_display.setMinimumHeight(200)
        log_layout.addWidget(self.command_display)
        
        main_layout.addWidget(log_group)
        
        # 控制按钮区域
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_button = QPushButton("开始转换")
        self.start_button.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止转换")
        self.stop_button.clicked.connect(self.stop_conversion)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("清除日志")
        self.clear_button.clicked.connect(self.command_display.clear)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addWidget(button_group)
        
        # 添加主页面到标签页
        tabs.addTab(main_tab, "主控制")
        
        # 礼物命令配置页面
        gift_tab = QWidget()
        gift_layout = QVBoxLayout(gift_tab)
        gift_layout.setSpacing(10)
        
        # 添加说明标签
        gift_help_label = QLabel("""
配置说明：
- 礼物MD5：从礼物消息中获取的MD5值
- 命令：要执行的Minecraft命令（会自动添加/前缀）
- 执行次数：每收到1个礼物要执行的次数
例如：设置执行次数为3，收到2个礼物，将执行6次命令（2×3=6）
        """)
        gift_help_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        gift_layout.addWidget(gift_help_label)
        
        # 礼物命令表格
        self.gift_table = QTableWidget()
        self.gift_table.setColumnCount(3)
        self.gift_table.setHorizontalHeaderLabels(["礼物MD5", "命令", "执行次数"])
        self.gift_table.horizontalHeader().setStretchLastSection(True)
        self.gift_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
        """)
        self.gift_table.itemChanged.connect(self.on_gift_table_changed)
        gift_layout.addWidget(self.gift_table)
        
        # 礼物命令操作按钮
        gift_button_layout = QHBoxLayout()
        
        save_gift_button = QPushButton("保存所有更改")
        save_gift_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_gift_button.clicked.connect(self.save_gift_commands)
        gift_button_layout.addWidget(save_gift_button)
        
        delete_gift_button = QPushButton("删除选中")
        delete_gift_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_gift_button.clicked.connect(self.delete_selected_gift)
        gift_button_layout.addWidget(delete_gift_button)
        
        gift_button_layout.addStretch()
        gift_layout.addLayout(gift_button_layout)
        
        # 礼物命令添加区域
        gift_add_group = QGroupBox("添加新命令")
        gift_add_layout = QHBoxLayout(gift_add_group)
        gift_add_layout.setSpacing(10)
        
        self.gift_md5_input = QLineEdit()
        self.gift_md5_input.setPlaceholderText("礼物MD5")
        self.gift_md5_input.setMinimumWidth(200)
        gift_add_layout.addWidget(self.gift_md5_input)
        
        self.gift_command_input = QLineEdit()
        self.gift_command_input.setPlaceholderText("输入命令（无需/前缀）")
        gift_add_layout.addWidget(self.gift_command_input, 1)  # 1表示可伸缩
        
        self.gift_count_input = QSpinBox()
        self.gift_count_input.setRange(1, 100)
        self.gift_count_input.setValue(1)
        self.gift_count_input.setPrefix("执行次数: ")
        self.gift_count_input.setMinimumWidth(100)
        gift_add_layout.addWidget(self.gift_count_input)
        
        add_gift_button = QPushButton("添加命令")
        add_gift_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        add_gift_button.clicked.connect(self.add_gift_command)
        gift_add_layout.addWidget(add_gift_button)
        
        gift_layout.addWidget(gift_add_group)
        
        # 添加礼物配置页面到标签页
        tabs.addTab(gift_tab, "礼物命令配置")
        
        # 聊天命令配置页面
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)
        chat_layout.setSpacing(10)
        
        # 添加说明标签
        chat_help_label = QLabel("""
配置说明：
- 触发词：聊天中输入的触发命令的词语
- 命令：要执行的Minecraft命令（会自动添加/前缀）
- 执行次数：每次触发要执行的次数
例如：设置执行次数为3，每次触发会连续执行3次命令
        """)
        chat_help_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 11px;
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
        """)
        chat_layout.addWidget(chat_help_label)
        
        # 聊天命令表格
        self.chat_table = QTableWidget()
        self.chat_table.setColumnCount(3)
        self.chat_table.setHorizontalHeaderLabels(["触发词", "命令", "执行次数"])
        self.chat_table.horizontalHeader().setStretchLastSection(True)
        self.chat_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
        """)
        self.chat_table.itemChanged.connect(self.on_chat_table_changed)
        chat_layout.addWidget(self.chat_table)
        
        # 聊天命令操作按钮
        chat_button_layout = QHBoxLayout()
        
        save_chat_button = QPushButton("保存所有更改")
        save_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_chat_button.clicked.connect(self.save_chat_commands)
        chat_button_layout.addWidget(save_chat_button)
        
        delete_chat_button = QPushButton("删除选中")
        delete_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_chat_button.clicked.connect(self.delete_selected_chat)
        chat_button_layout.addWidget(delete_chat_button)
        
        chat_button_layout.addStretch()
        chat_layout.addLayout(chat_button_layout)
        
        # 聊天命令添加区域
        chat_add_group = QGroupBox("添加新命令")
        chat_add_layout = QHBoxLayout(chat_add_group)
        chat_add_layout.setSpacing(10)
        
        self.chat_trigger_input = QLineEdit()
        self.chat_trigger_input.setPlaceholderText("触发词")
        self.chat_trigger_input.setMinimumWidth(150)
        chat_add_layout.addWidget(self.chat_trigger_input)
        
        self.chat_command_input = QLineEdit()
        self.chat_command_input.setPlaceholderText("输入命令（无需/前缀）")
        chat_add_layout.addWidget(self.chat_command_input, 1)  # 1表示可伸缩
        
        self.chat_count_input = QSpinBox()
        self.chat_count_input.setRange(1, 100)
        self.chat_count_input.setValue(1)
        self.chat_count_input.setPrefix("执行次数: ")
        self.chat_count_input.setMinimumWidth(100)
        chat_add_layout.addWidget(self.chat_count_input)
        
        add_chat_button = QPushButton("添加命令")
        add_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        add_chat_button.clicked.connect(self.add_chat_command)
        chat_add_layout.addWidget(add_chat_button)
        
        chat_layout.addWidget(chat_add_group)
        
        # 添加聊天配置页面到标签页
        tabs.addTab(chat_tab, "聊天命令配置")
        
        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_messages)
        
        # 加载现有配置
        self.load_command_tables()
        
    def on_gift_table_changed(self, item):
        """当礼物命令表格内容改变时触发"""
        self.unsaved_changes = True
        
    def save_gift_commands(self):
        """保存礼物命令配置"""
        try:
            # 先清空现有的礼物命令配置
            self.converter.config['gift_commands'] = {}
            
            # 收集所有命令
            for row in range(self.gift_table.rowCount()):
                md5 = self.gift_table.item(row, 0).text()
                command = self.gift_table.item(row, 1).text()
                count = int(self.gift_table.item(row, 2).text())
                if md5 and command:
                    self.converter.update_gift_command(md5, command, count)
            
            self.unsaved_changes = False
            QMessageBox.information(self, "保存成功", "礼物命令配置已保存")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存时发生错误：{str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def delete_selected_gift(self):
        """删除选中的礼物命令"""
        selected_rows = set(item.row() for item in self.gift_table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的命令")
            return
            
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除选中的 {len(selected_rows)} 条命令吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for row in sorted(selected_rows, reverse=True):
                self.gift_table.removeRow(row)
            self.unsaved_changes = True
    
    def add_gift_command(self):
        """添加新的礼物命令"""
        md5 = self.gift_md5_input.text().strip()
        command = self.gift_command_input.text().strip()
        count = self.gift_count_input.value()
        
        if not md5 or not command:
            QMessageBox.warning(self, "输入错误", "礼物MD5和命令都不能为空")
            return
            
        # 直接添加新行
        row = self.gift_table.rowCount()
        self.gift_table.insertRow(row)
        self.gift_table.setItem(row, 0, QTableWidgetItem(md5))
        self.gift_table.setItem(row, 1, QTableWidgetItem(command))
        self.gift_table.setItem(row, 2, QTableWidgetItem(str(count)))
        
        # 清空输入框
        self.gift_md5_input.clear()
        self.gift_command_input.clear()
        self.gift_count_input.setValue(1)
        
        self.unsaved_changes = True
        
    def add_chat_command(self):
        """添加聊天命令"""
        trigger = self.chat_trigger_input.text().strip()
        command = self.chat_command_input.text().strip()
        count = self.chat_count_input.value()
        
        if not trigger or not command:
            QMessageBox.warning(self, "错误", "请填写完整的聊天命令信息")
            return
            
        # 直接添加新行
        row = self.chat_table.rowCount()
        self.chat_table.insertRow(row)
        self.chat_table.setItem(row, 0, QTableWidgetItem(trigger))
        self.chat_table.setItem(row, 1, QTableWidgetItem(command))
        self.chat_table.setItem(row, 2, QTableWidgetItem(str(count)))
        
        # 清空输入框
        self.chat_trigger_input.clear()
        self.chat_command_input.clear()
        self.chat_count_input.setValue(1)
        
        self.unsaved_changes = True
        
    def load_command_tables(self):
        """加载命令配置到表格"""
        try:
            print("开始加载命令配置到表格")
            # 加载礼物命令
            self.gift_table.setRowCount(0)
            for md5, config in self.converter.config['gift_commands'].items():
                if isinstance(config, dict) and 'command' in config:
                    row = self.gift_table.rowCount()
                    self.gift_table.insertRow(row)
                    self.gift_table.setItem(row, 0, QTableWidgetItem(str(md5)))
                    self.gift_table.setItem(row, 1, QTableWidgetItem(str(config['command'])))
                    self.gift_table.setItem(row, 2, QTableWidgetItem(str(config.get('count', 1))))
            
            # 加载聊天命令
            self.chat_table.setRowCount(0)
            for trigger, config in self.converter.config['chat_commands'].items():
                if isinstance(config, dict) and 'command' in config:
                    row = self.chat_table.rowCount()
                    self.chat_table.insertRow(row)
                    self.chat_table.setItem(row, 0, QTableWidgetItem(str(trigger)))
                    self.chat_table.setItem(row, 1, QTableWidgetItem(str(config['command'])))
                    self.chat_table.setItem(row, 2, QTableWidgetItem(str(config.get('count', 1))))
            print("命令配置加载完成")
        except Exception as e:
            print(f"加载命令配置失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
    def start_conversion(self):
        """开始转换消息"""
        self.converter.host = self.host_input.text().strip()
        self.converter.port = self.port_input.value()
        self.converter.password = self.password_input.text()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.host_input.setEnabled(False)
        self.port_input.setEnabled(False)
        self.password_input.setEnabled(False)
        
        self.timer.start(1000)  # 每秒检查一次新消息
        self.log_message("开始转换消息...")
        
    def stop_conversion(self):
        """停止转换消息"""
        self.timer.stop()
        
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.host_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.password_input.setEnabled(True)
        
        self.log_message("停止转换消息")
        
    def process_messages(self):
        """处理新消息"""
        try:
            commands = self.converter.process_new_messages()
            for command in commands:
                self.log_message(f"生成命令: {command}")
        except ConnectionRefusedError as e:
            self.log_message("错误: RCON连接被拒绝，请检查:")
            self.log_message("1. Minecraft服务器是否已启动")
            self.log_message("2. server.properties中enable-rcon是否设为true")
            self.log_message("3. rcon.port是否与配置的端口匹配")
            self.log_message("4. rcon.password是否与配置的密码匹配")
            self.stop_conversion()  # 停止转换
        except Exception as e:
            self.log_message(f"错误: {str(e)}")
            if "Authentication failed" in str(e):
                self.log_message("RCON密码验证失败，请检查密码是否正确")
                self.stop_conversion()  # 停止转换
            elif "Connection refused" in str(e):
                self.log_message("无法连接到服务器，请检查地址和端口是否正确")
                self.stop_conversion()  # 停止转换
            
    def log_message(self, message: str):
        """添加日志消息到显示区域"""
        try:
            time_str = datetime.now().strftime('%H:%M:%S')
            formatted_message = f"[{time_str}] {message}"
            self.command_display.append(formatted_message)
            
            # 自动滚动到底部
            scrollbar = self.command_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
            # 如果日志太长，清除旧的内容
            if self.command_display.document().lineCount() > 1000:
                cursor = self.command_display.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 100)
                cursor.removeSelectedText()
        except Exception as e:
            print(f"添加日志失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.stop_conversion()
        event.accept()
    
    def on_chat_table_changed(self, item):
        """当聊天命令表格内容改变时触发"""
        self.unsaved_changes = True
        
    def save_chat_commands(self):
        """保存聊天命令配置"""
        try:
            # 先清空现有的聊天命令配置
            self.converter.config['chat_commands'] = {}
            
            # 收集所有命令
            for row in range(self.chat_table.rowCount()):
                trigger = self.chat_table.item(row, 0).text()
                command = self.chat_table.item(row, 1).text()
                count = int(self.chat_table.item(row, 2).text())
                if trigger and command:
                    self.converter.update_chat_command(trigger, command, count)
            
            self.unsaved_changes = False
            QMessageBox.information(self, "保存成功", "聊天命令配置已保存")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存时发生错误：{str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def delete_selected_chat(self):
        """删除选中的聊天命令"""
        selected_rows = set(item.row() for item in self.chat_table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的命令")
            return
            
        reply = QMessageBox.question(self, "确认删除", 
                                   f"确定要删除选中的 {len(selected_rows)} 条命令吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for row in sorted(selected_rows, reverse=True):
                self.chat_table.removeRow(row)
            self.unsaved_changes = True