#!/usr/bin/env python3
"""
Katabump Dashboard Automation Script
自动登录并根据日期条件执行操作 (Scraping版本)
"""

from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
import time
import sys

# 登录凭据
EMAIL = "16fr7y49@g147.netlib.re"
PASSWORD = "qWcQQdx8"

# Cookie登录 (优先使用)
USE_COOKIE_LOGIN = True
COOKIES = [
    {"name": "kata_t", "value": "44227421869570c5181b6d1.72312418"},
    {"name": "referral", "value": "ad22f5"},
    {"name": "katabump_s", "value": "988e26b478582e6443a3f7784a9a72118f25a8b24ddd810bc76be7e5bbe2a7a4"},
    {"name": "PHPSESSID", "value": "pmcsstfnjf8553976egq0nqrsu"},
    {"name": "cf_clearance", "value": "faT6gYxu1hljIXz1FSad_pFvIXNOH0GhM3wYqwLeSvM-1771723138-1.2.1.1-emMxSoZK6WrkYbk8bMRcYS4zAmiYqJwJmMJa0rdITe2OeUVdizgdxB3wEepMz.DF8GCxDO3N1JYs_EBSxLVn9RpXz1LAy8Fkg0B3.b0qOwhJiT.ayfrzXnVauQqZ1_EB2psH5nZ.fydLICAqshuCesRGUqyL7xponiLJRxISMivvEoTF7oQXQ_TNFbeNXRy.jucYa2TVkLttiQppsr6KIuZ8qK9EBy9AHzH6uHpzBSs"},
]

LOGIN_URL = "https://dashboard.katabump.com/auth/login"
BASE_URL = "https://dashboard.katabump.com"

# 重试配置
MAX_RETRIES = 5
RETRY_DELAY = 3


def retry_on_failure(func):
    """重试装饰器"""
    def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    print(f"第 {attempt} 次尝试失败: {e}")
                    print(f"等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"已达到最大重试次数 ({MAX_RETRIES})")
        if last_error:
            raise last_error
    return wrapper


def init_session():
    """初始化 requests session"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    return session


def login_with_cookies(session):
    """使用Cookie登录"""
    print("尝试使用Cookie登录...")
    try:
        # 先访问主页设置域名
        response = session.get(BASE_URL, timeout=30)
        print(f"访问主页状态码: {response.status_code}")
        time.sleep(2)
        
        # 添加Cookie
        for cookie in COOKIES:
            try:
                session.cookies.set(
                    cookie['name'], 
                    cookie['value'], 
                    domain='dashboard.katabump.com'
                )
                print(f"已添加Cookie: {cookie['name']}")
            except Exception as e:
                print(f"添加Cookie失败 {cookie['name']}: {e}")
        
        # 刷新页面使Cookie生效
        response = session.get(BASE_URL, timeout=30)
        print(f"Cookie登录后状态码: {response.status_code}")
        
        # 检查是否登录成功
        if response.url and ("dashboard" in response.url or "auth/login" not in response.url):
            print("Cookie登录成功!")
            return True
        else:
            print("Cookie登录失败")
            return False
            
    except Exception as e:
        print(f"Cookie登录出错: {e}")
        return False


def login(session):
    """登录流程"""
    print("正在登录...")
    
    # 优先尝试Cookie登录
    if USE_COOKIE_LOGIN:
        if login_with_cookies(session):
            return True
        print("Cookie登录失败，尝试其他方式...")
    
    return False


def get_table_value(session):
    """获取表格第一个td值"""
    print("正在获取表格值...")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(BASE_URL, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试多种选择器
            table = soup.select_one('table tbody')
            if table:
                first_td = table.select_one('tr td:first-child')
                if first_td:
                    first_td_value = first_td.text.strip()
                    if first_td_value:
                        print(f"获取到的值: {first_td_value}")
                        return first_td_value
            
            # 备选方案：直接查找第一个td
            first_td = soup.select_one('td')
            if first_td:
                first_td_value = first_td.text.strip()
                if first_td_value:
                    print(f"获取到的值: {first_td_value}")
                    return first_td_value
            
            print(f"第 {attempt} 次未能获取到值")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                
        except Exception as e:
            print(f"获取表格值失败: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    
    print("未能获取到有效值")
    return None


def get_date_value(session):
    """获取日期值"""
    print("正在获取日期值...")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(BASE_URL, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试查找日期元素 - 需要根据实际页面结构调整
            # 先尝试常见的选择器
            date_element = soup.select_one('.date, [class*="date"], .timestamp')
            if date_element:
                date_text = date_element.text.strip()
                if date_text:
                    print(f"获取到的日期文本: {date_text}")
                    return date_text
            
            # 备选：查找包含日期格式文本的元素
            import re
            date_pattern = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')
            for elem in soup.find_all(text=date_pattern):
                date_text = elem.strip()
                if date_text:
                    print(f"获取到的日期文本: {date_text}")
                    return date_text
            
            print(f"第 {attempt} 次未能获取到日期")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                
        except Exception as e:
            print(f"获取日期失败: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    
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


def click_button_drission(value):
    """使用 DrissionPage 点击按钮"""
    print("使用 DrissionPage 点击按钮...")
    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
        
        # 创建无头浏览器选项
        options = ChromiumOptions()
        options.set_argument('--headless')
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--disable-gpu')
        options.set_argument('--disable-blink-features=AutomationControlled')
        
        # 设置用户数据目录（避免每次创建新的）
        options.set_argument('--user-data-dir=/tmp/katabump_user_data')
        
        # 禁用图片加载加速
        options.set_argument('--disable-images')
        
        page = ChromiumPage(addr_or_opts=options)
        
        # 访问编辑页面
        edit_url = f"{BASE_URL}/servers/edit?id={value}"
        print(f"正在跳转到: {edit_url}")
        page.get(edit_url)
        time.sleep(3)
        
        # 添加 cookies
        for cookie in COOKIES:
            try:
                page.set.cookies({cookie['name']: cookie['value']})
            except Exception as e:
                print(f"设置Cookie失败 {cookie['name']}: {e}")
        
        # 刷新页面
        page.get(edit_url)
        time.sleep(3)
        
        # 查找并点击按钮 - 需要根据实际页面结构调整
        try:
            # 使用 ele 获取单个元素
            button = page.ele('tag:button')
            if button:
                button.click()
                print("按钮点击成功!")
                return True
        except Exception as e:
            print(f"点击按钮失败: {e}")
        
        page.quit()
        return False
        
    except Exception as e:
        print(f"DrissionPage 错误: {e}")
        return False


@retry_on_failure
def navigate_to_edit_page(session, value):
    """跳转到编辑页面"""
    edit_url = f"{BASE_URL}/servers/edit?id={value}"
    print(f"正在跳转到: {edit_url}")
    response = session.get(edit_url, timeout=30)
    print(f"编辑页面状态码: {response.status_code}")
    return response


def main():
    session = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"\n=== 第 {attempt} 次尝试 ===")
            session = init_session()
            
            # Step 1: 登录
            if not login(session):
                print("登录失败，继续尝试...")
                continue
            
            # Step 2: 获取表格值
            first_td_value = get_table_value(session)
            if not first_td_value:
                print("无法获取表格值")
                continue
            
            # Step 3: 获取日期 (先在列表页尝试)
            date_text = get_date_value(session)
            if not date_text:
                # Step 4: 跳转编辑页面获取日期
                response = navigate_to_edit_page(session, first_td_value)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 尝试查找日期元素
                import re
                date_pattern = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')
                for elem in soup.find_all(text=date_pattern):
                    date_text = elem.strip()
                    if date_text:
                        break
            
            if not date_text:
                print("无法获取日期")
                continue
            
            # Step 5: 解析并比较日期
            parsed_date = parse_date(date_text)
            if parsed_date is None:
                print("日期解析失败")
                continue
            
            today = date.today()
            print(f"今天日期: {today}")
            print(f"比较: {parsed_date} vs {today}")
            
            # Step 6: 判断并执行
            if parsed_date < today:
                print(f"日期 {parsed_date} 早于今天 {today}，不做动作，退出")
            else:
                print(f"日期 {parsed_date} >= 今天 {today}，执行点击操作")
                click_button_drission(first_td_value)
            
            # 成功，退出循环
            break
            
        except Exception as e:
            print(f"执行过程中出错: {e}")
            import traceback
            traceback.print_exc()
            if session:
                pass
            if attempt < MAX_RETRIES:
                print(f"等待 {RETRY_DELAY} 秒后重试...")
                time.sleep(RETRY_DELAY)
    
    print("\n操作完成")


if __name__ == "__main__":
    main()
