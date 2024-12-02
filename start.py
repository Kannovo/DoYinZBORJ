import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from PySide6.QtWidgets import QApplication
from src.main import MainApp

def main():
    print("启动程序...")
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    print("窗口已显示，等待用户操作")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 