from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from ..models.message import Message, MessageType
from .message_cache import MessageCache
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

class LiveCrawler:
    def __init__(self):
        self.driver = None
        self.message_cache = MessageCache()
        
    def setup(self):
        """设置Chrome浏览器"""
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--ignore-certificate-errors')
        
        # 尝试多个可能的 Chrome 路径
        chrome_paths = [
            r"C:\Users\Administrator\AppData\Local\Google\Chrome\Bin\chrome.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe"
        ]
        
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                break
                
        if chrome_binary:
            options.binary_location = chrome_binary
            
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def start(self, live_url: str):
        """开始访问直播间"""
        self.driver.get(live_url)
        # 等待聊天框加载
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='webcast-chatroom']"))
        )
        
    def fetch_messages(self):
        """获取新消息"""
        try:
            # 使用WebDriverWait等待聊天容器加载
            wait = WebDriverWait(self.driver, 5)
            chat_container = None
            
            # 尝试获取聊天容器
            for selector in [
                "div[class*='webcast-chatroom___items']",
                "div[class*='webcast-chatroom___list']",
                "div[class*='ChatRoom-ScrollContent']"
            ]:
                try:
                    chat_container = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if chat_container:
                        break
                except:
                    continue
            
            if not chat_container:
                return []
            
            # 获取所有消息项
            chat_items = []
            try:
                # 使用WebDriverWait等待消息项加载
                items = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div[class*='webcast-chatroom___item']")
                    )
                )
                chat_items.extend(items)
            except:
                return []
            
            # 解析所有消息
            current_messages = []
            for item in chat_items:
                try:
                    # 立即获取必要的信息，避免stale element
                    message_data = {
                        'id': item.get_attribute('data-id'),
                        'html': item.get_attribute('outerHTML'),
                        'text': '',
                        'user_id': ''
                    }
                    
                    # 尝试获取用户名
                    try:
                        username_element = item.find_element(By.CLASS_NAME, "u2QdU6ht")
                        if username_element:
                            message_data['user_id'] = username_element.text.strip()
                            if message_data['user_id'].endswith('：'):
                                message_data['user_id'] = message_data['user_id'][:-1]
                    except:
                        message_data['user_id'] = "未知用户"
                    
                    # 尝试获取消息内容
                    try:
                        content_element = item.find_element(By.CLASS_NAME, "webcast-chatroom___content-with-emoji-text")
                        if content_element:
                            message_data['text'] = content_element.text.strip()
                    except:
                        try:
                            content_element = item.find_element(By.CLASS_NAME, "WsJsvMP9")
                            if content_element:
                                message_data['text'] = content_element.text.strip()
                        except:
                            continue
                    
                    if not message_data['text'] or not message_data['id']:
                        continue
                    
                    # 判断消息类型并处理礼物信息
                    message_type = MessageType.CHAT
                    if "送出了" in message_data['text']:
                        message_type = MessageType.GIFT
                        try:
                            # 获取礼物数量
                            gift_count = 1
                            if "×" in message_data['text']:
                                count_str = message_data['text'].split("×")[1].strip()
                                try:
                                    gift_count = int(count_str)
                                except:
                                    gift_count = 1
                            
                            # 获取礼物图片信息
                            img_elements = item.find_elements(By.TAG_NAME, "img")
                            gift_md5 = None
                            gift_image_url = None
                            for img in img_elements:
                                try:
                                    gift_src = img.get_attribute("src")
                                    # 排除用户等级图标
                                    if not gift_src:
                                        continue
                                    if "new_user_grade_level" in gift_src:
                                        continue
                                    if "fansclub" in gift_src:
                                        continue
                                    if "webcast_admin_badge" in gift_src:
                                        continue
                                        
                                    # 只处理礼物图片
                                    if ("~tplv-obj" in gift_src or "webcast/gift" in gift_src):
                                        if "~tplv-obj" in gift_src:
                                            gift_md5 = gift_src.split("/")[-1].split("~")[0]
                                        else:
                                            gift_md5 = gift_src.split("/")[-1].split(".")[0]
                                        
                                        if gift_md5.endswith('.png'):
                                            gift_md5 = gift_md5[:-4]
                                        
                                        gift_image_url = gift_src
                                        break
                                except:
                                    continue
                            
                            # 更新礼物消息文本和数据
                            if gift_md5:
                                message_data['text'] = f"送出了 [md5: {gift_md5}] × {gift_count}"
                                message_data['gift_md5'] = gift_md5
                                message_data['gift_image_url'] = gift_image_url
                            else:
                                message_data['text'] = f"送出了礼物 × {gift_count}"
                            message_data['gift_count'] = gift_count
                        except Exception as e:
                            print(f"处理礼物信息出错: {str(e)}")
                    elif "为主播点赞了" in message_data['text'] or "点赞" in message_data['text']:
                        message_type = MessageType.LIKE
                    elif any(x in message_data['text'] for x in ["来了", "进入直播间", "欢迎光临"]):
                        message_type = MessageType.ENTER
                    elif "欢迎来到直播间！抖音严禁" in message_data['text']:
                        continue
                    
                    # 创建消息对象
                    message = Message(
                        message_id=message_data['id'],
                        type=message_type,
                        content=message_data['text'],
                        user_name=message_data['user_id'],
                        timestamp=datetime.now(),
                        gift_md5=message_data.get('gift_md5'),
                        gift_count=message_data.get('gift_count', 1) if message_type == MessageType.GIFT else None
                    )
                    current_messages.append(message)
                    
                except Exception as e:
                    continue
            
            # 比较并获取新消息
            new_messages = self.message_cache.compare_and_store(current_messages)
            return new_messages
            
        except Exception as e:
            print(f"获取消息错误: {str(e)}")
            return []
            
    def _parse_message(self, element) -> Message:
        """解析消息元素"""
        try:
            # 使用WebDriverWait来处理stale element
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # 获取消息的唯一ID
                    message_id = element.get_attribute('data-id')
                    if not message_id:
                        return None

                    # 获取用户名
                    user_id = "未知用户"
                    try:
                        username_element = element.find_element(By.CLASS_NAME, "u2QdU6ht")
                        if username_element:
                            user_id = username_element.text.strip()
                            if user_id.endswith('：'):  # 移除末尾的冒号
                                user_id = user_id[:-1]
                    except:
                        pass

                    # 获取消息内容
                    content = ""
                    gift_md5 = None
                    gift_count = None

                    # 首先尝试获取emoji文本内容
                    try:
                        emoji_content = element.find_element(By.CLASS_NAME, "webcast-chatroom___content-with-emoji-text")
                        if emoji_content:
                            content = emoji_content.text.strip()
                    except:
                        # 如果没有emoji文本，尝试其他选择器
                        try:
                            content_element = element.find_element(By.CLASS_NAME, "WsJsvMP9")
                            if content_element:
                                content = content_element.text.strip()
                        except:
                            # 如果还是找不到，尝试其他通用选择器
                            content_selectors = [
                                "[class*='content']",
                                "[class*='message']",
                                "[class*='text']"
                            ]
                            for selector in content_selectors:
                                try:
                                    content_element = element.find_element(By.CSS_SELECTOR, selector)
                                    if content_element:
                                        content = content_element.text.strip()
                                        if content:
                                            break
                                except:
                                    continue

                    if not content:
                        return None

                    # 处理礼物消息
                    if "送出了" in content:
                        try:
                            # 获取礼物数量
                            if "×" in content:
                                count_str = content.split("×")[1].strip()
                                gift_count = int(count_str)
                            else:
                                gift_count = 1

                            # 获取礼物图片信息
                            img_elements = element.find_elements(By.TAG_NAME, "img")
                            for img in img_elements:
                                gift_src = img.get_attribute("src")
                                if gift_src and ("~tplv-obj" in gift_src or "webcast/gift" in gift_src):
                                    gift_md5 = gift_src.split("/")[-1].split("~")[0]
                                    if gift_md5.endswith('.png'):
                                        gift_md5 = gift_md5[:-4]
                                    break
                        except Exception as e:
                            print(f"处理礼物消息出错: {str(e)}")
                            gift_count = 1

                    # 创建原始数据字典
                    raw_data = {
                        "text": content,
                        "user_id": user_id,
                        "message_id": message_id,
                        "gift_md5": gift_md5,
                        "gift_count": gift_count
                    }

                    # 判断消息类型
                    message_type = MessageType.CHAT  # 默认为聊天消息
                    if "送出了" in content:
                        message_type = MessageType.GIFT
                    elif "为主播点赞了" in content or "点赞" in content:
                        message_type = MessageType.LIKE
                    elif any(x in content for x in ["来了", "进入直播间", "欢迎光临"]):
                        message_type = MessageType.ENTER
                    elif "欢迎来到直播间！抖音严禁" in content:
                        return None

                    return Message(
                        type=message_type,
                        user_id=user_id,
                        content=content,
                        timestamp=datetime.now(),
                        raw_data=raw_data,
                        message_id=message_id
                    )

                except Exception as e:
                    if retry < max_retries - 1:
                        time.sleep(0.1)  # 短暂等待后重试
                        continue
                    else:
                        raise e

        except Exception as e:
            print(f"解析消息错误: {str(e)}")
            return None
            
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit() 