content = '''from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QGroupBox, QSpinBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QComboBox)
from PySide6.QtCore import Qt
import json
import os

class MinecraftConfigWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Minecraft 互动配置")
        self.resize(800, 600)
        
        # 默认配置
        self.default_config = {
            "server": {
                "host": "localhost",
                "port": 25575,
                "password": "Pzx030709"
            },
            "rules": []
        }
        
        # 创建主布局
        layout = QVBoxLayout()
        
        # 服务器配置组
        server_group = QGroupBox("服务器配置")
        server_layout = QVBoxLayout()
        
        # 服务器地址配置
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("服务器地址:"))
        self.host_input = QLineEdit(self.default_config["server"]["host"])
        host_layout.addWidget(self.host_input)
        
        # 端口配置
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("RCON端口:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.default_config["server"]["port"])
        port_layout.addWidget(self.port_input)
        
        # 密码配置
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("RCON密码:"))
        self.password_input = QLineEdit(self.default_config["server"]["password"])
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        
        # 测试连接按钮
        test_button = QPushButton("测试连接")
        test_button.clicked.connect(self.test_connection)
        
        server_layout.addLayout(host_layout)
        server_layout.addLayout(port_layout)
        server_layout.addLayout(password_layout)
        server_layout.addWidget(test_button)
        server_group.setLayout(server_layout)
        
        # 规则配置组
        rules_group = QGroupBox("互动规则配置")
        rules_layout = QVBoxLayout()
        
        # 规则表格
        self.rules_table = QTableWidget(0, 3)
        self.rules_table.setHorizontalHeaderLabels(["触发类型", "触发值", "Minecraft命令"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 添加默认规则示例
        self.add_example_rules()
        
        # 添加/删除规则按钮
        buttons_layout = QHBoxLayout()
        add_rule_button = QPushButton("添加规则")
        add_rule_button.clicked.connect(self.add_rule)
        delete_rule_button = QPushButton("删除规则")
        delete_rule_button.clicked.connect(self.delete_rule)
        buttons_layout.addWidget(add_rule_button)
        buttons_layout.addWidget(delete_rule_button)
        
        rules_layout.addWidget(self.rules_table)
        rules_layout.addLayout(buttons_layout)
        rules_group.setLayout(rules_layout)
        
        # 保存/加载配置按钮
        config_buttons = QHBoxLayout()
        save_button = QPushButton("保存配置")
        load_button = QPushButton("加载配置")
        save_button.clicked.connect(self.save_config)
        load_button.clicked.connect(self.load_config)
        config_buttons.addWidget(save_button)
        config_buttons.addWidget(load_button)
        
        # 添加所有组件到主布局
        layout.addWidget(server_group)
        layout.addWidget(rules_group)
        layout.addLayout(config_buttons)
        
        self.setLayout(layout)
        
        # 加载配置
        self.load_config()
    
    def add_example_rules(self):
        """添加示例规则"""
        example_rules = [
            ("GIFT", "7ef47758a435313180e6b78b056dda4e", "/give {user} diamond {gift_count}"),
            ("LIKE", "点赞", "/effect give {user} speed 30 1"),
            ("ENTER", "来了", "/title {user} title \"欢迎来到直播间!\""),
            ("CHAT", "你好", "/say 欢迎 {user}!")
        ]
        
        for rule_type, value, command in example_rules:
            row = self.rules_table.rowCount()
            self.rules_table.insertRow(row)
            
            # 创建类型选择下拉框
            type_combo = QComboBox()
            type_combo.addItems(["GIFT", "LIKE", "ENTER", "CHAT"])
            type_combo.setCurrentText(rule_type)
            self.rules_table.setCellWidget(row, 0, type_combo)
            
            self.rules_table.setItem(row, 1, QTableWidgetItem(value))
            self.rules_table.setItem(row, 2, QTableWidgetItem(command))
    
    def add_rule(self):
        """添加新规则到表格"""
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)
        
        # 添加类型选择下拉框
        type_combo = QComboBox()
        type_combo.addItems(["GIFT", "LIKE", "ENTER", "CHAT"])
        self.rules_table.setCellWidget(row, 0, type_combo)
        
        # 添加触发值和命令输入框
        self.rules_table.setItem(row, 1, QTableWidgetItem(""))
        self.rules_table.setItem(row, 2, QTableWidgetItem(""))
    
    def delete_rule(self):
        """删除选中的规则"""
        current_row = self.rules_table.currentRow()
        if current_row >= 0:
            self.rules_table.removeRow(current_row)
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            "server": {
                "host": self.host_input.text(),
                "port": self.port_input.value(),
                "password": self.password_input.text()
            },
            "rules": []
        }
        
        # 保存规则
        for row in range(self.rules_table.rowCount()):
            type_combo = self.rules_table.cellWidget(row, 0)
            rule = {
                "type": type_combo.currentText(),
                "value": self.rules_table.item(row, 1).text(),
                "command": self.rules_table.item(row, 2).text()
            }
            config["rules"].append(rule)
        
        # 保存到文件
        try:
            with open("minecraft_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {str(e)}")
    
    def load_config(self):
        """从文件加载配置"""
        try:
            if not os.path.exists("minecraft_config.json"):
                # 使用默认配置
                config = self.default_config
            else:
                with open("minecraft_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            # 加载服务器配置
            server_config = config.get("server", self.default_config["server"])
            self.host_input.setText(server_config.get("host", self.default_config["server"]["host"]))
            self.port_input.setValue(server_config.get("port", self.default_config["server"]["port"]))
            self.password_input.setText(server_config.get("password", self.default_config["server"]["password"]))
            
            # 清空现有规则
            self.rules_table.setRowCount(0)
            
            # 加载规则
            rules = config.get("rules", [])
            if not rules:
                # 如果没有规则，添加示例规则
                self.add_example_rules()
            else:
                for rule in rules:
                    row = self.rules_table.rowCount()
                    self.rules_table.insertRow(row)
                    
                    # 添加类型选择下拉框
                    type_combo = QComboBox()
                    type_combo.addItems(["GIFT", "LIKE", "ENTER", "CHAT"])
                    type_combo.setCurrentText(rule["type"])
                    self.rules_table.setCellWidget(row, 0, type_combo)
                    
                    self.rules_table.setItem(row, 1, QTableWidgetItem(rule["value"]))
                    self.rules_table.setItem(row, 2, QTableWidgetItem(rule["command"]))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置失败: {str(e)}")
    
    def test_connection(self):
        """测试RCON连接"""
        from src.minecraft.rcon_client import RCONClient
        
        client = RCONClient(
            self.host_input.text(),
            self.port_input.value(),
            self.password_input.text()
        )
        
        if client.connect():
            QMessageBox.information(self, "成功", "连接成功！")
            client.disconnect()
        else:
            QMessageBox.warning(self, "错误", "连接失败，请检查配置")
    
    def closeEvent(self, event):
        """窗口关闭时提示保存"""
        reply = QMessageBox.question(self, '保存配置', 
                                   "是否保存当前配置？",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            self.save_config()
        event.accept()
'''

with open('src/ui/minecraft_config.py', 'w', encoding='utf-8') as f:
    f.write(content)