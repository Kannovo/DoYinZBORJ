from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QScrollArea, QGridLayout, QFrame, QHBoxLayout,
                             QPushButton, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QFont, QPalette, QColor
import json
import os
import requests
from datetime import datetime

class GiftCard(QFrame):
    """礼物卡片组件"""
    def __init__(self, image_path, md5, last_seen, count):
        super().__init__()
        self.init_ui(image_path, md5, last_seen, count)
        
    def init_ui(self, image_path, md5, last_seen, count):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                margin: 2px;
                padding: 4px;
            }
            QFrame:hover {
                border: 1px solid #b0b0b0;
                background-color: #f8f8f8;
            }
            QLabel {
                background: transparent;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 礼物图片
        image_container = QFrame()
        image_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #eee;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        image_layout = QHBoxLayout()
        image_layout.setContentsMargins(2, 2, 2, 2)
        image_label = QLabel()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(image_label)
        image_container.setLayout(image_layout)
        layout.addWidget(image_container)
        
        # 信息容器
        info_container = QFrame()
        info_container.setStyleSheet("QFrame { background: transparent; }")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # MD5值
        md5_label = QLabel(f"MD5: {md5}")
        md5_label.setStyleSheet("""
            color: #666;
            font-size: 11px;
            padding: 2px;
            background: #f5f5f5;
            border-radius: 3px;
        """)
        md5_label.setWordWrap(True)
        info_layout.addWidget(md5_label)
        
        # 最后出现时间
        time_label = QLabel(f"最后出现: {last_seen}")
        time_label.setStyleSheet("""
            color: #888;
            font-size: 11px;
        """)
        info_layout.addWidget(time_label)
        
        info_container.setLayout(info_layout)
        layout.addWidget(info_container, stretch=1)
        
        # 计数容器
        count_container = QFrame()
        count_container.setStyleSheet("""
            QFrame {
                background: #f0f7ff;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        count_layout = QHBoxLayout()
        count_layout.setSpacing(2)
        count_layout.setContentsMargins(4, 2, 4, 2)
        
        count_label = QLabel(str(count))
        count_label.setStyleSheet("""
            color: #2196F3;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
        """)
        count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        count_layout.addWidget(count_label)
        
        count_text = QLabel("次")
        count_text.setStyleSheet("""
            color: #666;
            font-size: 10px;
            text-align: center;
        """)
        count_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        count_layout.addWidget(count_text)
        
        count_container.setLayout(count_layout)
        layout.addWidget(count_container)
        
        self.setLayout(layout)

class GiftStatsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.gift_data = {}
        self.load_gift_data()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题区域
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background: #2196F3;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 5px;
            }
        """)
        title_layout = QHBoxLayout()
        
        # 左侧标题
        title_label = QLabel("礼物统计")
        title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        title_layout.addWidget(title_label)
        
        # 添加统计信息
        self.stats_label = QLabel("总计: 0 种礼物")
        self.stats_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 12px;
            margin-right: 10px;
        """)
        title_layout.addWidget(self.stats_label)
        
        # 按钮容器
        button_container = QFrame()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 重置计数按钮
        reset_button = QPushButton("重置计数")
        reset_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        reset_button.clicked.connect(self.reset_counts)
        button_layout.addWidget(reset_button)
        
        # 清除全部按钮
        clear_button = QPushButton("清除全部")
        clear_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                color: white;
                padding: 4px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        clear_button.clicked.connect(self.clear_all_data)
        button_layout.addWidget(clear_button)
        
        button_container.setLayout(button_layout)
        title_layout.addWidget(button_container)
        
        title_container.setLayout(title_layout)
        layout.addWidget(title_container)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cdcdcd;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #b0b0b0;
            }
        """)
        
        # 创建网格布局容器
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_container.setLayout(self.grid_layout)
        scroll.setWidget(self.grid_container)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
    def load_gift_data(self):
        """加载礼物数据"""
        try:
            if os.path.exists('gift_data.json'):
                with open('gift_data.json', 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    # 确保每个礼物数据都有必要的字段
                    for md5, data in loaded_data.items():
                        if 'total_count' not in data:
                            data['total_count'] = data.get('count', 0)
                        if 'last_seen' not in data:
                            data['last_seen'] = current_time
                        data['count'] = 0  # 重置临时计数
                    self.gift_data = loaded_data
                    self.update_display()
                    print(f"加载了 {len(self.gift_data)} 个礼物数据")
        except Exception as e:
            print(f"加载礼物数据失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
    def save_gift_data(self):
        """保存礼物数据"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 确保所有数据都有必要的字段
            for md5, data in self.gift_data.items():
                if 'total_count' not in data:
                    data['total_count'] = data.get('count', 0)
                if 'last_seen' not in data:
                    data['last_seen'] = current_time
            
            with open('gift_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.gift_data, f, ensure_ascii=False, indent=2)
            print(f"保存了 {len(self.gift_data)} 个礼物数据")
        except Exception as e:
            print(f"保存礼物数据失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
    def add_gift(self, md5, image_url):
        """添加新的礼物数据"""
        if not md5 or not image_url:
            print("无效的礼物数据")
            return
            
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"处理礼物: {md5}")
        
        try:
            if md5 not in self.gift_data:
                print(f"新礼物: {md5}")
                # 下载图片
                response = requests.get(image_url)
                if response.status_code == 200:
                    # 保存图片
                    os.makedirs('gift_images', exist_ok=True)
                    image_path = f'gift_images/{md5}.png'
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    
                    # 更新数据
                    self.gift_data[md5] = {
                        'image_path': image_path,
                        'last_seen': current_time,
                        'count': 1,
                        'total_count': 1
                    }
                    print(f"已保存新礼物图片: {image_path}")
                else:
                    print(f"下载礼物图片失败: {response.status_code}")
                    return
            else:
                print(f"更新已有礼物: {md5}")
                # 更新时间和计数
                self.gift_data[md5]['last_seen'] = current_time
                self.gift_data[md5]['count'] += 1
                self.gift_data[md5]['total_count'] += 1
            
            self.update_display()
            self.save_gift_data()
            
        except Exception as e:
            print(f"处理礼物出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            
    def update_display(self):
        """更新显示"""
        try:
            # 清除现有内容
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            if not self.gift_data:
                print("没有礼物数据")
                return
                
            # 更新统计信息
            self.stats_label.setText(f"总计: {len(self.gift_data)} 种礼物")
            
            # 按总计数排序
            sorted_gifts = sorted(
                self.gift_data.items(),
                key=lambda x: x[1].get('total_count', 0),
                reverse=True
            )
            
            # 添加礼物卡片（堆叠显示）
            for row, (md5, data) in enumerate(sorted_gifts):
                if not os.path.exists(data.get('image_path', '')):
                    print(f"礼物图片不存在: {data.get('image_path', '未知路径')}")
                    continue
                    
                try:
                    card = GiftCard(
                        data['image_path'],
                        md5,
                        data.get('last_seen', '未知时间'),
                        data.get('total_count', 0)
                    )
                    self.grid_layout.addWidget(card, row, 0)
                except Exception as e:
                    print(f"创建礼物卡片失败: {str(e)}")
                    continue
            
            # 添加弹性空间
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.grid_layout.addWidget(spacer, len(self.gift_data), 0)
            
            print(f"显示更新完成，共 {len(self.gift_data)} 个礼物")
            
        except Exception as e:
            print(f"更新显示出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
    def clear_all_data(self):
        """清除所有礼物数据"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有礼物统计数据吗？\n此操作不可恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 清除内存中的数据
                self.gift_data.clear()
                
                # 删除JSON文件
                if os.path.exists('gift_data.json'):
                    os.remove('gift_data.json')
                
                # 删除图片文件夹
                if os.path.exists('gift_images'):
                    for file in os.listdir('gift_images'):
                        try:
                            os.remove(os.path.join('gift_images', file))
                        except:
                            pass
                    os.rmdir('gift_images')
                
                # 更新显示
                self.update_display()
                
                QMessageBox.information(
                    self,
                    "清除成功",
                    "所有礼物统计数据已清除。"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "清除失败",
                    f"清除数据时出错：{str(e)}"
                )
        
    def reset_counts(self):
        """重置所有礼物的计数"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要重置所有礼物的计数吗？\n此操作不会删除礼物记录，只会将计数归零。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 重置所有礼物的计数
                for md5, data in self.gift_data.items():
                    data['count'] = 0
                    data['total_count'] = 0
                
                # 更新显示和保存数据
                self.update_display()
                self.save_gift_data()
                
                QMessageBox.information(
                    self,
                    "重置成功",
                    "所有礼物的计数已重置为0。"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "重置失败",
                    f"重置计数时出错：{str(e)}"
                )