#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘功能测试脚本
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统托盘测试")
        self.setGeometry(100, 100, 300, 200)
        
        # 创建主窗口
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # 添加测试按钮
        test_button = QPushButton("测试按钮")
        layout.addWidget(test_button)
        
        self.setCentralWidget(central_widget)
        
        # 初始化系统托盘
        self.init_tray()
    
    def init_tray(self):
        """初始化系统托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        # 使用默认图标
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setToolTip("系统托盘测试")
        
        # 创建右键菜单
        self.tray_menu = QMenu(self)
        
        # 显示操作
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show_window)
        self.tray_menu.addAction(show_action)
        
        # 退出操作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_app)
        self.tray_menu.addAction(exit_action)
        
        # 设置菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 连接信号
        self.tray_icon.activated.connect(self.icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def show_window(self):
        """显示主窗口"""
        self.show()
        self.activateWindow()
    
    def exit_app(self):
        """退出应用程序"""
        self.tray_icon.hide()
        self.close()
        QApplication.instance().quit()
    
    def icon_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 创建确认对话框
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("确认操作")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("请选择关闭操作："))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No, dialog)
        buttons.button(QDialogButtonBox.StandardButton.Yes).setText("直接退出应用")
        buttons.button(QDialogButtonBox.StandardButton.No).setText("隐藏到任务栏")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 直接退出
            self.exit_app()
        else:
            # 隐藏到任务栏
            event.ignore()
            self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
