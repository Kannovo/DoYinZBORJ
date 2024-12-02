import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QMessageBox
from PySide6.QtCore import QThread, Signal, QTimer, Qt
from .ui.main_window import MainWindow
from .crawler.live_crawler import LiveCrawler
from .models.message import MessageType
from .models.message_store import MessageStore
from .minecraft import MinecraftCommandWindow
import time
from selenium.webdriver.common.by import By

class CrawlerThread(QThread):
    message_received = Signal(list)  # 发送新消息信号

    def __init__(self, crawler, message_store):
        super().__init__()
        self.crawler = crawler
        self.message_store = message_store
        self.is_running = True

    def run(self):
        print("爬虫线程启动")
        while self.is_running:
            try:
                new_messages = self.crawler.fetch_messages()
                if new_messages:
                    print(f"获取到 {len(new_messages)} 条新消息")
                    # 将消息添加到存储
                    for message in new_messages:
                        self.message_store.add_message(message)
                    # 发送消息到UI
                    self.message_received.emit(new_messages)
                self.msleep(200)  # 正常延迟200ms
            except Exception as e:
                print(f"爬虫错误: {str(e)}")
                import traceback
                print(traceback.format_exc())
                self.msleep(400)  # 出错时延迟400ms

    def stop(self):
        print("正在停止爬虫线程...")
        self.is_running = False

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("抖音直播数据采集")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建消息存储系统
        self.message_store = MessageStore()
        
        # 创建主窗口
        self.main_window = MainWindow(self.message_store)
        self.setCentralWidget(self.main_window)
        
        # 创建工具栏
        toolbar = self.addToolBar("工具栏")
        toolbar.setMovable(False)  # 禁止移动工具栏
        
        # 创建Minecraft命令转换器按钮
        self.mc_button = QPushButton("打开Minecraft命令转换器")
        self.mc_button.setFixedWidth(200)  # 设置固定宽度
        self.mc_button.clicked.connect(self.open_minecraft_converter)
        
        # 将按钮添加到工具栏
        toolbar.addWidget(self.mc_button)
        
        # Minecraft命令转换器窗口
        self.mc_window = None
        
        # 初始化爬虫
        self.crawler = LiveCrawler()
        self.crawler_thread = None
        
        # 连接信号
        self.main_window.start_button.clicked.connect(self.start_crawler)
        self.main_window.stop_button.clicked.connect(self.stop_crawler)
        
    def start_crawler(self):
        """启动爬虫"""
        if self.crawler_thread and self.crawler_thread.isRunning():
            print("爬虫线程已在运行中")
            return
            
        live_url = self.main_window.url_input.text().strip()
        if not live_url:
            self.main_window.status_label.setText("请输入直播间链接")
            return
            
        print(f"准备访问直播间: {live_url}")
        try:
            self.crawler.setup()
            self.crawler.start(live_url)
            
            self.crawler_thread = CrawlerThread(self.crawler, self.message_store)
            self.crawler_thread.message_received.connect(self.handle_messages)
            self.crawler_thread.start()
            
            self.main_window.status_label.setText("采集已启动")
            self.main_window.start_button.setEnabled(False)
            self.main_window.stop_button.setEnabled(True)
            print("爬虫启动成功")
        except Exception as e:
            error_msg = f"启动失败: {str(e)}"
            self.main_window.status_label.setText(error_msg)
            print(error_msg)
            
    def stop_crawler(self):
        """停止爬虫"""
        if self.crawler_thread:
            print("正在停止爬虫...")
            self.crawler_thread.stop()
            self.crawler_thread.wait()
            self.crawler.close()
            self.crawler_thread = None
            print("爬虫已停止")
            
        self.main_window.status_label.setText("采集已停止")
        self.main_window.start_button.setEnabled(True)
        self.main_window.stop_button.setEnabled(False)
        
    def handle_messages(self, messages):
        """处理新消息"""
        try:
            for message in messages:
                print(f"处理消息: 类型={message.type}, 内容={message.content}")
                if message.type == MessageType.CHAT:
                    self.main_window.chat_panel.add_message(message)
                elif message.type == MessageType.GIFT:
                    self.main_window.gift_panel.add_message(message)
                    self.handle_gift_message(message)
                elif message.type == MessageType.LIKE:
                    self.main_window.like_panel.add_message(message)
                elif message.type == MessageType.ENTER:
                    self.main_window.enter_panel.add_message(message)
        except Exception as e:
            print(f"处理消息时出错: {str(e)}")
            
    def handle_gift_message(self, message):
        """处理礼物消息，更新礼物统计"""
        if message.type == MessageType.GIFT and message.gift_md5:
            try:
                # 暂时不处理礼物图片
                self.main_window.gift_stats_panel.add_gift(message.gift_md5, "")
            except Exception as e:
                print(f"处理礼物统计失败: {str(e)}")
                import traceback
                print(traceback.format_exc())
        
    def open_minecraft_converter(self):
        """打开Minecraft命令转换器窗口"""
        try:
            if not self.mc_window:
                print("创建新的Minecraft命令转换器窗口")
                self.mc_window = MinecraftCommandWindow(self.message_store)
            print("显示Minecraft命令转换器窗口")
            self.mc_window.show()
            self.mc_window.raise_()  # 将窗口置于最前
        except Exception as e:
            print(f"打开Minecraft命令转换器失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        print("正在关闭程序...")
        self.stop_crawler()
        if hasattr(self, 'message_store'):
            self.message_store.shutdown()
        event.accept()

def main():
    print("程序启动...")
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    print("窗口显示完成，等待用户操作")
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 