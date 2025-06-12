from MainWindow import AoiWindow
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow
import sys
import os


if __name__ == "__main__":
    # 创建应用程序对象
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = AoiWindow()
    
    # 显示窗口
    window.show()
    
    # 运行应用程序主循环
    sys.exit(app.exec())
