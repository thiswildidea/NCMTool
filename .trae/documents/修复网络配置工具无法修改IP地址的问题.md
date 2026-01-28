## 问题分析

通过比较批处理脚本和Python程序的命令，发现以下关键差异：

1. **命令格式不同**：
   - 批处理脚本：`Netsh interface IP Set Addr "以太网 3" Static 192.168.107.185 255.255.255.0 192.168.107.1`
   - Python程序：`netsh interface ip set address name='{card}' static {ip} {netmask} {gateway} 1`

2. **参数格式不同**：
   - 批处理脚本直接指定网卡名称
   - Python程序使用`name='{card}'`格式

3. **DNS设置不同**：
   - 批处理脚本：`Netsh interface IP Set dns "以太网 3" static 192.168.100.40 primary`
   - Python程序：`netsh interface ip set dns name='{card}' static {dns}`

4. **批处理脚本还添加了备用DNS**，而Python程序没有

## 修复计划

1. **修改IP地址设置命令**：
   - 将`set address name='{card}'`改为`set addr "{card}"`
   - 移除多余的`1`参数

2. **修改DNS设置命令**：
   - 将`set dns name='{card}'`改为`set dns "{card}"`
   - 添加`primary`参数

3. **添加备用DNS支持**：
   - 允许用户配置备用DNS
   - 添加相应的netsh命令

4. **优化权限检查**：
   - 确保权限检查正确执行
   - 提供更明确的权限提示

5. **改进错误处理**：
   - 提供更详细的错误信息
   - 确保命令执行失败时能够正确捕获错误

## 预期效果

修复后，网络配置工具应该能够像批处理脚本一样成功修改IP地址和DNS设置，并且支持添加备用DNS服务器。