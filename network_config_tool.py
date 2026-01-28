#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置管理工具
使用PyQt6开发的图形界面工具，用于管理和切换网络配置
"""

import json
import os
import platform
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt

class NetworkConfigTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网络配置管理工具")
        self.setGeometry(100, 100, 600, 300)
        self.setFixedSize(600, 300)
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        # 加载配置数据
        self.config_data = self.load_config()
        
        # 创建主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧树形结构
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("配置列表")
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        main_layout.addWidget(self.tree_widget, 1)
        
        # 右侧配置面板
        self.config_panel = QWidget()
        self.config_layout = QVBoxLayout(self.config_panel)
        main_layout.addWidget(self.config_panel, 2)
        
        # 创建配置字段
        self.create_config_fields()
        
        # 添加网卡选择
        self.add_network_card_selector()
        
        # 添加确定按钮
        self.add_confirm_button()
        
        # 填充树形结构
        self.populate_tree()
        
        # 设置主窗口
        self.setCentralWidget(main_widget)
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败: {str(e)}")
            return []
    
    def populate_tree(self):
        """填充树形结构"""
        for dept in self.config_data:
            dept_item = QTreeWidgetItem([dept['department']])
            for user in dept['users']:
                user_item = QTreeWidgetItem([user['name']])
                # 存储用户配置数据
                user_item.setData(0, Qt.ItemDataRole.UserRole, user)
                dept_item.addChild(user_item)
            self.tree_widget.addTopLevelItem(dept_item)
            dept_item.setExpanded(True)
    
    def create_config_fields(self):
        """创建配置字段"""
        # 创建表单布局
        form_layout = QVBoxLayout()
        
        # IP地址
        ip_layout = QHBoxLayout()
        self.ip_label = QLabel("IP地址:")
        self.ip_label.setFixedWidth(80)
        self.ip_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.ip_edit = QLineEdit()
        ip_layout.addWidget(self.ip_label)
        ip_layout.addWidget(self.ip_edit)
        form_layout.addLayout(ip_layout)
        
        # 子网掩码
        netmask_layout = QHBoxLayout()
        self.netmask_label = QLabel("子网掩码:")
        self.netmask_label.setFixedWidth(80)
        self.netmask_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.netmask_edit = QLineEdit()
        netmask_layout.addWidget(self.netmask_label)
        netmask_layout.addWidget(self.netmask_edit)
        form_layout.addLayout(netmask_layout)
        
        # 网关
        gateway_layout = QHBoxLayout()
        self.gateway_label = QLabel("网关:")
        self.gateway_label.setFixedWidth(80)
        self.gateway_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.gateway_edit = QLineEdit()
        gateway_layout.addWidget(self.gateway_label)
        gateway_layout.addWidget(self.gateway_edit)
        form_layout.addLayout(gateway_layout)
        
        # DNS
        dns_layout = QHBoxLayout()
        self.dns_label = QLabel("DNS服务器:")
        self.dns_label.setFixedWidth(80)
        self.dns_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.dns_edit = QLineEdit()
        dns_layout.addWidget(self.dns_label)
        dns_layout.addWidget(self.dns_edit)
        form_layout.addLayout(dns_layout)
        
        # MAC地址
        mac_layout = QHBoxLayout()
        self.mac_label = QLabel("MAC地址:")
        self.mac_label.setFixedWidth(80)
        self.mac_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.mac_edit = QLineEdit()
        mac_layout.addWidget(self.mac_label)
        mac_layout.addWidget(self.mac_edit)
        form_layout.addLayout(mac_layout)
        
        self.config_layout.addLayout(form_layout)
    
    def add_network_card_selector(self):
        """添加网卡选择器"""
        self.card_layout = QHBoxLayout()
        self.card_label = QLabel("选择网卡:")
        self.card_label.setFixedWidth(80)
        self.card_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.card_combo = QComboBox()
        self.card_layout.addWidget(self.card_label)
        self.card_layout.addWidget(self.card_combo)
        self.config_layout.addLayout(self.card_layout)
        
        # 加载网卡信息
        self.load_network_cards()
    
    def load_network_cards(self):
        """加载本地网卡信息"""
        cards = self.get_network_cards()
        for card in cards:
            self.card_combo.addItem(card)
    
    def get_network_cards(self):
        """跨平台获取网卡信息"""
        system = platform.system()
        cards = []
        
        try:
            if system == "Windows":
                import wmi
                w = wmi.WMI()
                for nic in w.Win32_NetworkAdapter():
                    if nic.NetConnectionStatus == 2:  # 已连接
                        cards.append(nic.Name)
            elif system == "Darwin":  # macOS
                result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                                       capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题
                cards = [line.strip() for line in lines]
            elif system == "Linux":
                result = subprocess.run(['ip', 'link', 'show'], 
                                       capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ': <' in line and not line.strip().startswith('lo:'):
                        card_name = line.split(':')[1].strip().split(' ')[0]
                        cards.append(card_name)
        except Exception as e:
            print(f"获取网卡信息失败: {str(e)}")
        
        return cards
    
    def add_confirm_button(self):
        """添加确定按钮"""
        self.button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("确定")
        self.confirm_button.clicked.connect(self.on_confirm)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.confirm_button)
        self.config_layout.addLayout(self.button_layout)
    
    def on_item_clicked(self, item, column):
        """树形节点点击事件"""
        # 检查是否是用户节点
        user_data = item.data(0, Qt.ItemDataRole.UserRole)
        if user_data:
            # 更新右侧面板
            self.ip_edit.setText(user_data['ip'])
            self.netmask_edit.setText(user_data['netmask'])
            self.gateway_edit.setText(user_data['gateway'])
            self.dns_edit.setText(user_data['dns'])
            self.mac_edit.setText(user_data['mac'])
    
    def on_confirm(self):
        """确定按钮点击事件"""
        # 获取配置值
        ip = self.ip_edit.text()
        netmask = self.netmask_edit.text()
        gateway = self.gateway_edit.text()
        dns = self.dns_edit.text()
        mac = self.mac_edit.text()
        selected_card = self.card_combo.currentText()
        
        # 验证输入
        if not all([ip, netmask, gateway, dns, mac, selected_card]):
            QMessageBox.warning(self, "警告", "请确保所有配置项都已填写")
            return
        
        # 确认对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("确认操作")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"确定要将以下配置应用到网卡 '{selected_card}' 吗？"))
        layout.addWidget(QLabel(f"IP地址: {ip}"))
        layout.addWidget(QLabel(f"子网掩码: {netmask}"))
        layout.addWidget(QLabel(f"网关: {gateway}"))
        layout.addWidget(QLabel(f"DNS: {dns}"))
        layout.addWidget(QLabel(f"MAC地址: {mac}"))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 应用配置
            success = self.apply_config(selected_card, ip, netmask, gateway, dns, mac)
            if success:
                QMessageBox.information(self, "成功", "网络配置修改成功")
            else:
                QMessageBox.critical(self, "失败", "网络配置修改失败")
    
    def apply_config(self, card, ip, netmask, gateway, dns, mac):
        """应用网络配置"""
        system = platform.system()
        
        try:
            if system == "Windows":
                return self.apply_config_windows(card, ip, netmask, gateway, dns, mac)
            elif system == "Darwin":
                return self.apply_config_macos(card, ip, netmask, gateway, dns, mac)
            elif system == "Linux":
                return self.apply_config_linux(card, ip, netmask, gateway, dns, mac)
            else:
                QMessageBox.warning(self, "警告", f"不支持的操作系统: {system}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用配置失败: {str(e)}")
            return False
    
    def apply_config_windows(self, card, ip, netmask, gateway, dns, mac):
        """在Windows上应用配置"""
        # 获取网卡索引
        import wmi
        w = wmi.WMI()
        nic_index = None
        for nic in w.Win32_NetworkAdapter():
            if nic.Name == card:
                nic_index = nic.Index
                break
        
        if not nic_index:
            return False
        
        # 设置IP地址、子网掩码和网关
        cmd = f"netsh interface ip set address name='{card}' static {ip} {netmask} {gateway} 1"
        subprocess.run(cmd, shell=True, check=True)
        
        # 设置DNS
        cmd = f"netsh interface ip set dns name='{card}' static {dns}"
        subprocess.run(cmd, shell=True, check=True)
        
        # 设置MAC地址（Windows需要禁用/启用网卡）
        # 注意：Windows下修改MAC地址可能需要重启网卡
        return True
    
    def apply_config_macos(self, card, ip, netmask, gateway, dns, mac):
        """在macOS上应用配置"""
        # 设置IP地址和子网掩码
        cmd = f"networksetup -setmanual '{card}' {ip} {netmask} {gateway}"
        subprocess.run(cmd, shell=True, check=True)
        
        # 设置DNS
        cmd = f"networksetup -setdnsservers '{card}' {dns}"
        subprocess.run(cmd, shell=True, check=True)
        
        # 设置MAC地址
        # 注意：macOS下修改MAC地址需要root权限
        return True
    
    def apply_config_linux(self, card, ip, netmask, gateway, dns, mac):
        """在Linux上应用配置"""
        # 禁用网卡
        subprocess.run(['sudo', 'ifconfig', card, 'down'], shell=True, check=True)
        
        # 设置IP地址和子网掩码
        subprocess.run(['sudo', 'ifconfig', card, ip, 'netmask', netmask], 
                      shell=True, check=True)
        
        # 设置网关
        subprocess.run(['sudo', 'route', 'add', 'default', 'gw', gateway, card], 
                      shell=True, check=True)
        
        # 设置DNS
        with open('/etc/resolv.conf', 'w') as f:
            f.write(f'nameserver {dns}\n')
        
        # 设置MAC地址
        subprocess.run(['sudo', 'ifconfig', card, 'hw', 'ether', mac], 
                      shell=True, check=True)
        
        # 启用网卡
        subprocess.run(['sudo', 'ifconfig', card, 'up'], shell=True, check=True)
        
        return True

if __name__ == "__main__":
    app = QApplication([])
    window = NetworkConfigTool()
    window.show()
    app.exec()