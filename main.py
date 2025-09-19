#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMTP邮件自动发送程序 - 错误修复版
每次运行自动发送一封提醒邮件
适用于教学演示
"""

import smtplib
import time
import sys
import os
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

class AutoEmailSender:
    def __init__(self):
        # 邮箱配置 - 在这里修改你的邮箱信息
        self.config = {
            # 发送方配置
            'sender_email': 'your_email@gmail.com',
            'sender_password': 'your_app_password',
            
            # 接收方配置
            'receiver_email': 'student@example.com',
            
            # SMTP服务器配置（Gmail示例）
            'smtp_server': 'smtp.gmail.com',
            'port': 587,
            
            # 邮件内容配置
            'subject': '提醒',
            'enable_html': False,
            
            # 网络配置
            'timeout': 30,
            'retry_count': 3,
            'connection_type': 'auto'  # 可选：auto, ssl, tls
        }
        
        # SMTP服务器预设配置
        self.smtp_configs = {
            'gmail.com': {
                'server': 'smtp.gmail.com', 
                'port': 587,
                'ssl_port': 465,
                'name': 'Gmail'
            },
            'qq.com': {
                'server': 'smtp.qq.com', 
                'port': 587,
                'ssl_port': 465,
                'name': 'QQ邮箱'
            },
            '163.com': {
                'server': 'smtp.163.com', 
                'port': 25,
                'ssl_port': 465,
                'name': '163邮箱'
            },
            'outlook.com': {
                'server': 'smtp-mail.outlook.com', 
                'port': 587,
                'ssl_port': 465,
                'name': 'Outlook'
            },
            'hotmail.com': {
                'server': 'smtp-mail.outlook.com', 
                'port': 587,
                'ssl_port': 465,
                'name': 'Hotmail'
            },
            'sina.com': {
                'server': 'smtp.sina.com', 
                'port': 587,
                'ssl_port': 465,
                'name': '新浪邮箱'
            }
        }
    
    def test_network_connection(self):
        """测试网络连接"""
        print("🔍 检查网络连接...")
        try:
            # 测试DNS解析
            socket.gethostbyname(self.config['smtp_server'])
            print(f"✅ DNS解析正常: {self.config['smtp_server']}")
            
            # 测试端口连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.config['smtp_server'], self.config['port']))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口连接正常: {self.config['smtp_server']}:{self.config['port']}")
                return True
            else:
                print(f"❌ 端口连接失败: {self.config['smtp_server']}:{self.config['port']}")
                return False
                
        except socket.gaierror as e:
            print(f"❌ DNS解析失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 网络测试失败: {e}")
            return False
    
    def load_config_from_file(self):
        """从配置文件加载配置"""
        config_file = 'email_config.txt'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                if key in self.config:
                                    if key == 'port':
                                        self.config[key] = int(value)
                                    elif key == 'enable_html':
                                        self.config[key] = value.lower() == 'true'
                                    elif key in ['timeout', 'retry_count']:
                                        self.config[key] = int(value)
                                    else:
                                        self.config[key] = value
                print("✅ 已从配置文件加载邮箱设置")
                return True
            except Exception as e:
                print(f"⚠️ 配置文件加载失败: {e}")
        return False
    
    def create_config_file(self):
        """创建配置文件模板"""
        config_content = """# SMTP邮件发送配置文件
# 请修改以下配置信息

# 发送方邮箱设置
sender_email=your_email@gmail.com
sender_password=your_app_password

# 接收方邮箱
receiver_email=student@example.com

# SMTP服务器设置（程序会自动检测，也可手动设置）
smtp_server=smtp.gmail.com
port=587

# 邮件内容设置
subject=提醒
enable_html=false

# 网络设置（可选）
timeout=30
retry_count=3
connection_type=auto

# 连接类型说明：
# auto - 自动检测（推荐）
# ssl  - 强制使用SSL（通常用于465端口）
# tls  - 强制使用TLS（通常用于587端口）

# 配置说明：
# 1. Gmail用户需要开启两步验证并使用应用专用密码
# 2. QQ邮箱需要开启SMTP服务并使用授权码
# 3. 163邮箱需要开启客户端授权密码
# 4. 如果网络不稳定，可以增加timeout和retry_count的值
# 5. 某些网络环境可能需要使用SSL端口（465）替换587端口
"""
        try:
            with open('email_config.txt', 'w', encoding='utf-8') as f:
                f.write(config_content)
            print("✅ 已创建配置文件 email_config.txt")
            print("📝 请修改配置文件中的邮箱信息后重新运行程序")
            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败: {e}")
            return False
    
    def auto_detect_smtp(self, email):
        """自动检测SMTP配置"""
        for domain, config in self.smtp_configs.items():
            if domain in email.lower():
                self.config['smtp_server'] = config['server']
                self.config['port'] = config['port']
                print(f"🔍 自动检测邮箱类型: {config['name']}")
                
                # 如果标准端口连接失败，尝试SSL端口
                if not self.test_network_connection():
                    print(f"⚠️ 尝试使用SSL端口: {config['ssl_port']}")
                    self.config['port'] = config['ssl_port']
                
                return True
        return False
    
    def validate_config(self):
        """验证配置是否完整"""
        required_fields = ['sender_email', 'sender_password', 'receiver_email']
        for field in required_fields:
            if not self.config[field] or 'your_' in str(self.config[field]):
                return False
        return True
    
    def get_email_content(self):
        """生成邮件内容"""
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if self.config['enable_html']:
            return f"""
            <html>
            <body>
                <h2>📧 自动提醒邮件</h2>
                <p>这是一封由Python程序自动发送的提醒邮件。</p>
                
                <h3>📋 邮件信息：</h3>
                <ul>
                    <li><strong>发送时间：</strong>{current_time}</li>
                    <li><strong>发送方式：</strong>Python SMTP自动发送</li>
                    <li><strong>程序版本：</strong>教学演示版 v1.1</li>
                </ul>
                
                <h3>🎯 演示内容：</h3>
                <p>本次演示展示了以下技术要点：</p>
                <ol>
                    <li>SMTP协议的自动化应用</li>
                    <li>网络连接测试和错误处理</li>
                    <li>配置文件的使用</li>
                    <li>多端口自动切换</li>
                </ol>
                
                <p><em>如果您收到这封邮件，说明SMTP自动发送功能正常工作！</em></p>
                
                <hr>
                <p><small>此邮件由教学演示程序自动生成<br>
                发送时间: {current_time}</small></p>
            </body>
            </html>
            """
        else:
            return f"""📧 自动提醒邮件

这是一封由Python程序自动发送的提醒邮件。

📋 邮件信息：
• 发送时间：{current_time}
• 发送方式：Python SMTP自动发送
• 程序版本：教学演示版 v1.1 (网络优化)

🎯 演示内容：
本次演示展示了以下技术要点：
1. SMTP协议的自动化应用
2. 网络连接诊断和错误处理
3. 配置文件的灵活使用
4. 多端口自动切换机制
5. 连接超时和重试机制

💡 技术特点：
• 自动网络连接测试
• 智能端口切换(587/465)
• 完善的错误处理机制
• 清晰的执行状态提示
• 支持网络超时和重试

如果您收到这封邮件，说明SMTP自动发送功能正常工作！

---
此邮件由教学演示程序自动生成
发送时间: {current_time}
网络诊断: 已通过连接测试"""
    
    def send_email_with_retry(self):
        """带重试机制的邮件发送"""
        for attempt in range(self.config['retry_count']):
            print(f"📤 发送尝试 {attempt + 1}/{self.config['retry_count']}")
            
            success = self.send_email()
            if success:
                return True
            
            if attempt < self.config['retry_count'] - 1:
                wait_time = (attempt + 1) * 2
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        return False
    
    def send_email(self):
        """发送邮件"""
        try:
            print("📝 邮件内容已准备完成")
            
            # 创建邮件
            message = MIMEMultipart()
            message['From'] = Header(self.config['sender_email'])
            message['To'] = Header(self.config['receiver_email'])
            message['Subject'] = Header(self.config['subject'], 'utf-8')
            
            # 添加邮件内容
            content = self.get_email_content()
            content_type = 'html' if self.config['enable_html'] else 'plain'
            message.attach(MIMEText(content, content_type, 'utf-8'))
            
            # 连接SMTP服务器
            print(f"🔗 正在连接 {self.config['smtp_server']}:{self.config['port']}")
            
            # 根据配置选择连接方式
            connection_type = self.config.get('connection_type', 'auto').lower()
            
            if connection_type == 'ssl' or (connection_type == 'auto' and self.config['port'] == 465):
                # SSL连接 (通常用于465端口)
                server = smtplib.SMTP_SSL(self.config['smtp_server'], 
                                        self.config['port'], 
                                        timeout=self.config['timeout'])
                print("🔐 使用SSL加密连接")
                
            elif connection_type == 'tls' or (connection_type == 'auto' and self.config['port'] in [587, 25]):
                # TLS连接 (通常用于587或25端口)
                server = smtplib.SMTP(self.config['smtp_server'], 
                                    self.config['port'], 
                                    timeout=self.config['timeout'])
                print("🔐 启用TLS加密...")
                server.starttls()
                
            else:
                # 默认TLS连接
                server = smtplib.SMTP(self.config['smtp_server'], 
                                    self.config['port'], 
                                    timeout=self.config['timeout'])
                print("🔐 启用TLS加密...")
                server.starttls()
            
            print("🔑 正在进行身份验证...")
            server.login(self.config['sender_email'], self.config['sender_password'])
            
            print("📬 正在发送邮件...")
            server.send_message(message)
            server.quit()
            
            print("✅ 邮件发送成功！")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print("❌ 身份验证失败！")
            print("💡 请检查邮箱地址和密码是否正确")
            print("💡 建议使用应用专用密码而非登录密码")
            print(f"🔍 错误详情: {e}")
            return False
            
        except smtplib.SMTPConnectError as e:
            print("❌ 无法连接到SMTP服务器！")
            print("💡 可能的解决方案：")
            print("   1. 检查网络连接")
            print("   2. 尝试使用其他端口（587 或 465）")
            print("   3. 检查防火墙设置")
            print(f"🔍 错误详情: {e}")
            return False
            
        except OSError as e:
            if e.errno == 99:
                print("❌ 网络地址分配失败！")
                print("💡 可能的解决方案：")
                print("   1. 检查网络连接状态")
                print("   2. 尝试重启网络服务")
                print("   3. 更换DNS设置(8.8.8.8, 114.114.114.114)")
                print("   4. 尝试使用VPN或代理")
                print("   5. 检查是否被ISP阻止SMTP端口")
            else:
                print(f"❌ 网络错误: {e}")
            return False
            
        except socket.gaierror as e:
            print("❌ 域名解析失败！")
            print("💡 可能的解决方案：")
            print("   1. 检查DNS设置")
            print("   2. 尝试使用公共DNS(8.8.8.8)")
            print("   3. 检查网络连接")
            print(f"🔍 错误详情: {e}")
            return False
            
        except socket.timeout as e:
            print("❌ 连接超时！")
            print("💡 可能的解决方案：")
            print("   1. 增加超时时间")
            print("   2. 检查网络稳定性")
            print("   3. 尝试更换网络环境")
            print(f"🔍 错误详情: {e}")
            return False
            
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            print(f"🔍 错误类型: {type(e).__name__}")
            return False
    
    def run(self):
        """主程序运行"""
        print("📧 SMTP自动邮件发送程序 v1.1")
        print("=" * 50)
        print("🎯 程序特点: 运行即发送，网络优化版")
        print("📚 适用场景: 教学演示、自动化任务")
        print("=" * 50)
        
        # 尝试加载配置文件
        config_loaded = self.load_config_from_file()
        
        # 验证配置
        if not config_loaded or not self.validate_config():
            print("⚠️ 配置不完整或不存在")
            if not os.path.exists('email_config.txt'):
                if self.create_config_file():
                    print("📋 请按以下步骤操作：")
                    print("1. 编辑 email_config.txt 文件")
                    print("2. 填入正确的邮箱信息")
                    print("3. 重新运行此程序")
                    print("\n程序将在5秒后自动退出...")
                    time.sleep(5)
                    return
            else:
                print("📝 请检查并修改 email_config.txt 中的配置信息")
                print("\n程序将在3秒后自动退出...")
                time.sleep(3)
                return
        
        # 显示配置信息
        print(f"📤 发送方: {self.config['sender_email']}")
        print(f"📥 接收方: {self.config['receiver_email']}")
        print(f"🏷️  主题: {self.config['subject']}")
        
        # 自动检测SMTP配置
        if self.auto_detect_smtp(self.config['sender_email']):
            print(f"🌐 服务器: {self.config['smtp_server']}:{self.config['port']}")
        
        print("=" * 50)
        
        # 测试网络连接
        if not self.test_network_connection():
            print("⚠️ 网络连接测试失败，但仍会尝试发送邮件")
            print("💡 如果发送失败，请检查网络设置或尝试其他端口")
        
        print("🚀 开始发送邮件...")
        print("=" * 50)
        
        # 使用重试机制发送邮件
        success = self.send_email_with_retry()
        
        print("=" * 50)
        if success:
            print("✅ 邮件发送成功！")
            print(f"⏰ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("📊 发送统计: 1封邮件成功发送")
            print("\n🎉 任务完成！程序将自动退出。")
            print("🔄 下次运行将发送新的邮件。")
            print("\n程序将在3秒后自动退出...")
            time.sleep(3)
        else:
            print("❌ 邮件发送失败！")
            print("📋 故障排除建议：")
            print("1. 检查网络连接")
            print("2. 验证邮箱配置")
            print("3. 尝试更换端口(587→465或465→587)")
            print("4. 检查防火墙设置")
            print("5. 尝试更换网络环境")
            print("\n程序将在10秒后自动退出...")
            time.sleep(10)

def main():
    """主函数"""
    try:
        sender = AutoEmailSender()
        sender.run()
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序被用户中断")
        time.sleep(1)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        print("\n程序将在5秒后自动退出...")
        time.sleep(5)

if __name__ == "__main__":
    main()