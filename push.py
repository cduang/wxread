# push.py
# 支持 PushPlus、Telegram 和 Bark 的消息推送模块
import json
import os
import requests
import logging

logger = logging.getLogger(__name__)

class PushNotification:
    def __init__(self):
        self.pushplus_url = "https://www.pushplus.plus/send"
        self.telegram_url = "https://api.telegram.org/bot{}/sendMessage"
        self.headers = {'Content-Type': 'application/json'}
        # 从环境变量获取代理设置
        self.proxies = {
            'http': os.getenv('http_proxy'),
            'https': os.getenv('https_proxy')
        }

    def push_pushplus(self, content, token):
        """PushPlus消息推送"""
        try:
            response = requests.post(
                self.pushplus_url,
                data=json.dumps({
                    "token": token,
                    "title": "微信阅读推送...",
                    "content": content
                }).encode('utf-8'),
                headers=self.headers
            )
            response.raise_for_status()
            logger.info("✅ PushPlus响应: %s", response.text)
            return True
        except Exception as e:
            logger.error("❌ PushPlus推送失败: %s", e)
            return False

    def push_telegram(self, content, bot_token, chat_id):
        """Telegram消息推送，失败时自动尝试直连"""
        url = self.telegram_url.format(bot_token)
        payload = {"chat_id": chat_id, "text": content}

        try:
            response = requests.post(url, json=payload, proxies=self.proxies, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("❌ Telegram代理发送失败: %s", e)
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                return True
            except Exception as e:
                logger.error("❌ Telegram发送失败: %s", e)
                return False

    def push_bark(self, content, key):
        """Bark消息推送"""
        try:
            url = f"https://api.day.app/{key}/"  # 使用你提供的地址
            response = requests.post(url, json={"title": "通知", "body": content})
            response.raise_for_status()
            logger.info("✅ Bark响应: %s", response.text)
            return True
        except Exception as e:
            logger.error("❌ Bark推送失败: %s", e)
            return False


"""外部调用"""
def push(content, method, pushplus_token=None, telegram_bot_token=None, telegram_chat_id=None, bark_key=None):
    """统一推送接口，支持 PushPlus、Telegram 和 Bark"""
    notifier = PushNotification()

    if method == "pushplus":
        token = pushplus_token or os.getenv("PUSHPLUS_TOKEN", "Your_pushplus_token")
        return notifier.push_pushplus(content, token)
    elif method == "telegram":
        bot_token = telegram_bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
        chat_id = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
        return notifier.push_telegram(content, bot_token, chat_id)
    elif method == "bark":
        key = bark_key or os.getenv("BARK_KEY", "YOUR_BARK_KEY")
        return notifier.push_bark(content, key)
    else:
        raise ValueError("❌ 无效的通知渠道，请选择 'pushplus'、'telegram' 或 'bark'")
