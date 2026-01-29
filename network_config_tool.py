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
    QMessageBox, QDialog, QDialogButtonBox, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

class NetworkConfigTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网络配置管理工具")
        self.setGeometry(100, 100, 600, 300)
        self.setFixedSize(600, 300)
        
        # 设置窗口图标
        from PyQt6.QtGui import QIcon
        import sys
        import os
        
        def resource_path(relative_path):
            """获取资源文件的绝对路径"""
            try:
                # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
                base_path = sys._MEIPASS
            except Exception:
                # 未打包时的路径
                base_path = os.path.abspath('.')
            
            return os.path.join(base_path, relative_path)
        
        def get_config_path():
            """获取配置文件路径，优先使用程序所在目录"""
            # 获取程序所在目录
            if hasattr(sys, '_MEIPASS'):
                # 打包后：获取可执行文件所在目录
                # 注意：sys._MEIPASS是临时目录，不是可执行文件所在目录
                # 所以需要通过sys.executable获取可执行文件路径，然后获取其所在目录
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                # 未打包：获取当前工作目录
                exe_dir = os.path.abspath('.')
            
            # 检查程序所在目录是否存在config.json
            config_path = os.path.join(exe_dir, 'config.json')
            if os.path.exists(config_path):
                return config_path
            
            # 如果不存在，回退到resource_path逻辑
            return resource_path('config.json')
        
        # 使用resource_path函数获取图标路径
        icon_path = resource_path("network.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # 配置文件路径
        self.config_file = get_config_path()
        
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
        
        # 创建带边框的配置组
        from PyQt6.QtWidgets import QGroupBox
        self.config_group = QGroupBox("网络配置")
        self.config_group_layout = QVBoxLayout(self.config_group)
        self.config_layout.addWidget(self.config_group)
        
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
        
        # 初始化系统托盘
        self.init_tray()
    
    def load_config(self):
        """加载配置文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.config_file):
                QMessageBox.warning(self, "警告", f"配置文件不存在: {self.config_file}\n将使用默认空配置")
                return []
            
            # 检查文件是否可读
            if not os.access(self.config_file, os.R_OK):
                QMessageBox.warning(self, "警告", f"配置文件不可读: {self.config_file}\n将使用默认空配置")
                return []
            
            # 读取配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 验证配置文件格式
            if not isinstance(config_data, list):
                QMessageBox.warning(self, "警告", "配置文件格式不正确，应为列表格式\n将使用默认空配置")
                return []
            
            return config_data
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "警告", f"配置文件格式错误: {str(e)}\n将使用默认空配置")
            return []
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载配置文件失败: {str(e)}\n将使用默认空配置")
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
        
        # 设备类型
        device_layout = QHBoxLayout()
        self.device_label = QLabel("设备类型:")
        self.device_label.setFixedWidth(80)
        self.device_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.device_edit = QLineEdit()
        self.device_edit.setReadOnly(True)  # 设备类型设为只读
        device_layout.addWidget(self.device_label)
        device_layout.addWidget(self.device_edit)
        form_layout.addLayout(device_layout)
        
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
        
        # 备用DNS
        s_dns_layout = QHBoxLayout()
        self.s_dns_label = QLabel("备用DNS:")
        self.s_dns_label.setFixedWidth(80)
        self.s_dns_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.s_dns_edit = QLineEdit()
        s_dns_layout.addWidget(self.s_dns_label)
        s_dns_layout.addWidget(self.s_dns_edit)
        form_layout.addLayout(s_dns_layout)
        
        # MAC地址
        mac_layout = QHBoxLayout()
        self.mac_label = QLabel("MAC地址:")
        self.mac_label.setFixedWidth(80)
        self.mac_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.mac_edit = QLineEdit()
        mac_layout.addWidget(self.mac_label)
        mac_layout.addWidget(self.mac_edit)
        form_layout.addLayout(mac_layout)
        
        # 物理地址名称
        mac_name_layout = QHBoxLayout()
        self.mac_name_label = QLabel("物理地址名称:")
        self.mac_name_label.setFixedWidth(80)
        self.mac_name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.mac_name_edit = QLineEdit()
        self.mac_name_edit.setText("Network Address")
        mac_name_layout.addWidget(self.mac_name_label)
        mac_name_layout.addWidget(self.mac_name_edit)
        form_layout.addLayout(mac_name_layout)
        
        self.config_group_layout.addLayout(form_layout)
    
    def add_network_card_selector(self):
        """添加网卡选择器"""
        self.card_layout = QHBoxLayout()
        self.card_label = QLabel("选择网卡:")
        self.card_label.setFixedWidth(80)
        self.card_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.card_combo = QComboBox()
        self.card_layout.addWidget(self.card_label)
        self.card_layout.addWidget(self.card_combo)
        self.config_group_layout.addLayout(self.card_layout)
        
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
                        # 使用NetConnectionID获取显示名称，如"以太网 3"
                        if hasattr(nic, 'NetConnectionID') and nic.NetConnectionID:
                            cards.append(nic.NetConnectionID)
                        else:
                            # 如果没有NetConnectionID属性，使用Name属性
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
            # 检查是否有设备类型
            if 'deviceType' in user_data:
                self.device_edit.setText(user_data['deviceType'])
            else:
                self.device_edit.setText('')
            self.ip_edit.setText(user_data['ip'])
            self.netmask_edit.setText(user_data['netmask'])
            self.gateway_edit.setText(user_data['gateway'])
            self.dns_edit.setText(user_data['dns'])
            # 检查是否有备用DNS
            if 's_dns' in user_data:
                self.s_dns_edit.setText(user_data['s_dns'])
            else:
                self.s_dns_edit.setText('')
            self.mac_edit.setText(user_data['mac'])
            # 检查是否有物理地址名称
            if 'mac_name' in user_data:
                self.mac_name_edit.setText(user_data['mac_name'])
            else:
                self.mac_name_edit.setText('Network Address')
    
    def on_confirm(self):
        """确定按钮点击事件"""
        # 获取配置值
        ip = self.ip_edit.text()
        netmask = self.netmask_edit.text()
        gateway = self.gateway_edit.text()
        dns = self.dns_edit.text()
        s_dns = self.s_dns_edit.text()
        mac = self.mac_edit.text()
        mac_name = self.mac_name_edit.text()
        selected_card = self.card_combo.currentText()
        
        # 验证输入
        if not all([ip, netmask, gateway, dns]):
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
        if s_dns:
            layout.addWidget(QLabel(f"备用DNS: {s_dns}"))
        layout.addWidget(QLabel(f"MAC地址: {mac}"))
        layout.addWidget(QLabel(f"物理地址名称: {mac_name}"))
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 应用配置
            success = self.apply_config(selected_card, ip, netmask, gateway, dns, s_dns, mac, mac_name)
            if success:
                QMessageBox.information(self, "成功", "网络配置修改成功")
            else:
                QMessageBox.critical(self, "失败", "网络配置修改失败")
    
    def apply_config(self, card, ip, netmask, gateway, dns, s_dns, mac, mac_name):
        """应用网络配置"""
        system = platform.system()
        
        try:
            if system == "Windows":
                return self.apply_config_windows(card, ip, netmask, gateway, dns, s_dns, mac, mac_name)
            elif system == "Darwin":
                return self.apply_config_macos(card, ip, netmask, gateway, dns, s_dns, mac, mac_name)
            elif system == "Linux":
                return self.apply_config_linux(card, ip, netmask, gateway, dns, s_dns, mac, mac_name)
            else:
                QMessageBox.warning(self, "警告", f"不支持的操作系统: {system}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用配置失败: {str(e)}")
            return False
    
    def apply_config_windows(self, card, ip, netmask, gateway, dns, s_dns, mac, mac_name):
        """在Windows上应用配置"""
        try:
            # 检查是否以管理员身份运行
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if not is_admin:
                QMessageBox.warning(self, "权限提示", "请以管理员身份运行程序，否则网络配置可能无法生效")
            
            # 获取网卡索引
            import wmi
            w = wmi.WMI()
            nic_index = None
            for nic in w.Win32_NetworkAdapter():
                # 检查NetConnectionID是否匹配（显示名称，如"以太网 3"）
                if hasattr(nic, 'NetConnectionID') and nic.NetConnectionID == card:
                    nic_index = nic.Index
                    break
                # 如果NetConnectionID不匹配，检查Name属性
                elif nic.Name == card:
                    nic_index = nic.Index
                    break
            
            if not nic_index:
                QMessageBox.critical(self, "错误", f"找不到网卡: {card}")
                return False
            
            # 打印网卡信息

            
            # 设置IP地址、子网掩码和网关
            cmd = f"netsh interface ip set addr \"{card}\" static {ip} {netmask} {gateway}"
            # 使用正确的编码处理输出
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "未知错误"
                QMessageBox.critical(self, "错误", f"设置IP地址失败: {error_msg}")
                return False
            
            # 设置DNS
            cmd = f"netsh interface ip set dns \"{card}\" static {dns} primary"
            # 使用正确的编码处理输出
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "未知错误"
                QMessageBox.critical(self, "错误", f"设置DNS失败: {error_msg}")
                return False
            
            # 设置备用DNS
            if s_dns:
                cmd = f"netsh interface ip add dns \"{card}\" {s_dns} index=2"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "未知错误"
                    print(f"设置备用DNS失败: {error_msg}")
                    # 备用DNS设置失败不影响其他配置
            
            # 验证配置是否生效
            cmd = f"netsh interface ip show addresses \"{card}\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            cmd = f"netsh interface ip show dnsservers \"{card}\""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # 尝试修改MAC地址
            if mac:
                try:
                    # 禁用网卡
                    cmd = f"netsh interface set interface \"{card}\" admin=disable"
                    subprocess.run(cmd, shell=True, check=True)
                    
                    # 等待网卡完全禁用
                    import time
                    time.sleep(2)
                    
                    # 修改MAC地址（使用PowerShell）
                    # 使用用户提供的PowerShell代码格式
                    ps_mac_script = f"$adapter = Get-NetAdapter -Name '{card}'; if ($adapter) {{ Set-NetAdapterAdvancedProperty -Name '{card}' -DisplayName '{mac_name}' -DisplayValue '{mac}'; Write-Output 'MAC地址修改成功'; }}"
                    
                    result = subprocess.run(
                        ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_mac_script],
                        shell=True,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    
                    # 启用网卡
                    cmd = f"netsh interface set interface \"{card}\" admin=enable"
                    subprocess.run(cmd, shell=True, check=True)
                    
                    # 等待网卡完全启用
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"修改MAC地址失败: {str(e)}")
                    # MAC地址修改失败不影响其他配置
                    # 尝试重新启用网卡
                    try:
                        cmd = f"netsh interface set interface \"{card}\" admin=enable"
                        subprocess.run(cmd, shell=True, check=True)
                    except:
                        pass
                
                # 验证MAC地址
                ps_mac_check = f"Get-NetAdapter -Name '{card}' | Select-Object Name, MacAddress"
                result = subprocess.run(
                    ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_mac_check],
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                print("MAC地址为空，跳过修改")
            
            # 提示用户可能需要重启网卡
            QMessageBox.information(self, "提示", "网络配置已应用，某些更改可能需要重启网卡才能完全生效。")
            
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用配置失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def apply_config_macos(self, card, ip, netmask, gateway, dns, s_dns, mac, mac_name):
        """在macOS上应用配置"""
        # 设置IP地址和子网掩码
        cmd = f"networksetup -setmanual '{card}' {ip} {netmask} {gateway}"
        subprocess.run(cmd, shell=True, check=True)
        
        # 设置DNS
        if s_dns:
            cmd = f"networksetup -setdnsservers '{card}' {dns} {s_dns}"
        else:
            cmd = f"networksetup -setdnsservers '{card}' {dns}"
        subprocess.run(cmd, shell=True, check=True)
        
        # 设置MAC地址
        # 注意：macOS下修改MAC地址需要root权限
        return True
    
    def apply_config_linux(self, card, ip, netmask, gateway, dns, s_dns, mac, mac_name):
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
            if s_dns:
                f.write(f'nameserver {s_dns}\n')
        
        # 设置MAC地址
        subprocess.run(['sudo', 'ifconfig', card, 'hw', 'ether', mac], 
                      shell=True, check=True)
        
        # 启用网卡
        subprocess.run(['sudo', 'ifconfig', card, 'up'], shell=True, check=True)
        
        return True
    
    def init_tray(self):
        """初始化系统托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setToolTip("网络配置管理工具")
        
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
    app = QApplication([])
    window = NetworkConfigTool()
    window.show()
    app.exec()