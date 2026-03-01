#!/usr/bin/env python3
"""
Katabump Dashboard Automation Script
自动登录并根据日期条件执行操作 (DrissionPage版本)
"""

from datetime import datetime, date
import time
import os
from datetime import datetime as dt

# 登录凭据
EMAIL = "16fr7y49@g147.netlib.re"
PASSWORD = "qWcQQdx8"

LOGIN_URL = "https://dashboard.katabump.com/auth/login"
BASE_URL = "https://dashboard.katabump.com"

# 重试配置
MAX_RETRIES = 5
RETRIES_DELAY = 3


def save_screenshot(page, name="error"):
    """保存页面截图"""
    try:
        # 创建 screenshots 目录
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        # 生成文件名
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{screenshot_dir}/{name}_{timestamp}.png"
        
        # 保存截图
        page.get_screenshot(path=filename)
        print(f"截图已保存: {filename}")
        return filename
    except Exception as e:
        print(f"保存截图失败: {e}")
        return None


def parse_date(date_text):
    """解析日期"""
    if not date_text:
        return None
    
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d %b %Y",
        "%d %B %Y",
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_text, fmt).date()
            print(f"解析成功，日期格式: {fmt}, 日期: {parsed_date}")
            return parsed_date
        except ValueError:
            continue
    
    print(f"无法解析日期: {date_text}")
    return None


def login_with_drission():
    """使用 DrissionPage 登录并返回页面对象"""
    print("正在登录 (DrissionPage 账号密码模式)...")
    
    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
        
        # 创建无头浏览器选项
        options = ChromiumOptions()
        options.set_argument('--headless=new')
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--disable-gpu')
        options.set_argument('--disable-blink-features=AutomationControlled')
        options.set_argument('--disable-extensions')
        options.set_argument('--disable-images')
        options.set_argument('--window-size=1920,1080')
        
        page = ChromiumPage(addr_or_opts=options)
        
        # 访问登录页面
        print(f"访问登录页面: {LOGIN_URL}")
        page.get(LOGIN_URL)
        time.sleep(5)
        
        # 检查 Cloudflare
        if page.ele('text:=Please wait') or page.ele('text:=Checking your browser'):
            print("检测到 Cloudflare 验证，等待...")
            time.sleep(10)
        
        # 等待登录表单
        for _ in range(10):
            email_input = page.ele('tag:input', index=0)
            if email_input:
                break
            time.sleep(2)
        
        # 输入邮箱
        email_input = page.ele('tag:input', index=0)
        if email_input:
            email_input.input(EMAIL)
            print("已输入邮箱")
        else:
            print("未找到邮箱输入框")
            save_screenshot(page, "no_email_input")
            page.quit()
            return None
        
        # 输入密码
        password_input = page.ele('tag:input', index=1)
        if password_input:
            password_input.input(PASSWORD)
            print("已输入密码")
        else:
            print("未找到密码输入框")
            save_screenshot(page, "no_password_input")
            page.quit()
            return None
        
        # 点击登录按钮
        time.sleep(1)
        submit_btn = page.ele('tag:button')
        if submit_btn:
            submit_btn.click()
            print("已点击登录按钮")
        else:
            password_input.input('\n')
            print("按回车提交表单")
        
        time.sleep(5)
        
        # 检查是否登录成功
        current_url = page.url
        print(f"登录后URL: {current_url}")
        
        if "dashboard" in current_url or "auth/login" not in current_url:
            print("登录成功!")
            return page
        else:
            print("登录可能失败")
            save_screenshot(page, "login_failed")
            page.quit()
            return None
            
    except Exception as e:
        print(f"登录出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return None


def get_table_value_from_page(page):
    """从页面获取表格第一个td值"""
    print("正在获取表格值...")
    
    try:
        # 等待表格加载
        time.sleep(3)
        
        # 尝试多种选择器
        table = page.ele('tag:table')
        if table:
            first_td = table.ele('tag:td', index=0)
            if first_td:
                first_td_value = first_td.text.strip()
                if first_td_value:
                    print(f"获取到的值: {first_td_value}")
                    return first_td_value
        
        # 备选
        first_td = page.ele('tag:td')
        if first_td:
            first_td_value = first_td.text.strip()
            if first_td_value:
                print(f"获取到的值: {first_td_value}")
                return first_td_value
        
        print("未能获取到值")
        save_screenshot(page, "no_table_value")
        return None
        
    except Exception as e:
        print(f"获取表格值失败: {e}")
        save_screenshot(page, "get_table_error")
        return None


def get_date_value_from_page(page):
    """从页面获取日期值"""
    print("正在获取日期值...")
    
    try:
        time.sleep(3)
        
        # 尝试查找日期元素
        import re
        date_pattern = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')
        
        # 获取页面 HTML
        page_html = page.html
        
        matches = date_pattern.findall(page_html)
        if matches:
            date_text = matches[0]
            print(f"获取到的日期文本: {date_text}")
            return date_text
        
        print("未能获取到日期")
        save_screenshot(page, "no_date_value")
        return None
        
    except Exception as e:
        print(f"获取日期失败: {e}")
        save_screenshot(page, "get_date_error")
        return None


def click_button_on_page(page, button_index=1):
    """在页面上点击按钮"""
    try:
        buttons = page.eles('tag:button')
        if len(buttons) >= button_index + 1:
            buttons[button_index].click()
            print(f"点击了第 {button_index + 1} 个按钮")
            return True
        elif buttons:
            buttons[0].click()
            print("点击了第一个按钮")
            return True
        return False
    except Exception as e:
        print(f"点击按钮失败: {e}")
        save_screenshot(page, "click_button_error")
        return False


def main():
    page = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n=== 第 {attempt} 次尝试 ===")
            
            # Step 1: 登录
            page = login_with_drission()
            if not page:
                print("登录失败，继续尝试...")
                continue
            
            # Step 2: 获取表格值
            first_td_value = get_table_value_from_page(page)
            if not first_td_value:
                print("无法获取表格值")
                page.quit()
                continue
            
            # Step 3: 跳转到编辑页面
            edit_url = f"{BASE_URL}/servers/edit?id={first_td_value}"
            print(f"跳转到: {edit_url}")
            page.get(edit_url)
            time.sleep(3)
            
            # Step 4: 获取日期
            date_text = get_date_value_from_page(page)
            if not date_text:
                print("无法获取日期")
                page.quit()
                continue
            
            # Step 5: 解析并比较日期
            parsed_date = parse_date(date_text)
            if parsed_date is None:
                print("日期解析失败")
                page.quit()
                continue
            
            today = date.today()
            print(f"今天日期: {today}")
            print(f"比较: {parsed_date} vs {today}")
            
            # Step 6: 判断并执行
            if parsed_date < today:
                print(f"日期 {parsed_date} 早于今天 {today}，不做动作，退出")
            else:
                print(f"日期 {parsed_date} >= 今天 {today}，执行点击操作")
                click_button_on_page(page, button_index=1)
            
            # 成功，退出循环
            break
            
        except Exception as e:
            print(f"执行过程中出错: {e}")
            import traceback
            traceback.print_exc()
            # 保存截图
            if page:
                try:
                    save_screenshot(page, "exception")
                except:
                    pass
            if page:
                try:
                    page.quit()
                except:
                    pass
            if attempt < MAX_RETRIES:
                print(f"等待 {RETRIES_DELAY} 秒后重试...")
                time.sleep(RETRIES_DELAY)
    
    if page:
        print("\n操作完成")
        page.quit()


if __name__ == "__main__":
    main()
