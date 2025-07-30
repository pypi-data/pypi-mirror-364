import requests
from typing import List, Optional, Dict, Any, Literal
from .exceptions import APIRequestError
from .adaptorrubka import Client as Client_get
from .logger import logger
from typing import Callable
from .context import Message,InlineMessage
from typing import Optional, Union, Literal, Dict, Any
from pathlib import Path
import requests
import time
import datetime
API_URL = "https://botapi.rubika.ir/v3"
import sys
import subprocess
import requests
def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:return False

def get_importlib_metadata():
    try:
        from importlib.metadata import version, PackageNotFoundError
        return version, PackageNotFoundError
    except ImportError:
        if install_package("importlib-metadata"):
            try:
                from importlib_metadata import version, PackageNotFoundError
                return version, PackageNotFoundError
            except ImportError:
                return None, None
        return None, None

version, PackageNotFoundError = get_importlib_metadata()
def get_installed_version(package_name: str) -> str:
    if version is None:return "unknown"
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None
def get_latest_version(package_name: str) -> str:
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data["info"]["version"]
    except Exception:return None
def check_rubka_version():
    package_name = "rubka"
    installed_version = get_installed_version(package_name)
    if installed_version is None:return
    latest_version = get_latest_version(package_name)
    if latest_version is None:return
    if installed_version != latest_version:
        print(f"\n\nWARNING: Your installed version of '{package_name}' is OUTDATED and may cause errors or security risks!")
        print(f"Installed version : {installed_version}")
        print(f"Latest available version : {latest_version}")
        print(f"Please update IMMEDIATELY by running:")
        print(f"\npip install {package_name}=={latest_version}\n")
        print(f"Not updating may lead to malfunctions or incompatibility.")
        print(f"To see new methods : @rubka_library\n\n")

check_rubka_version()
def show_last_six_words(text):
    text = text.strip()
    return text[-6:]
import requests
from pathlib import Path
from typing import Union, Optional, Dict, Any, Literal
import tempfile
import os
class Robot:
    """
    Main class to interact with Rubika Bot API.
    Initialized with bot token.
    """

    def __init__(self, token: str,session_name : str = None,auth : str = None , Key : str = None,platform : str ="web",web_hook:str=None,timeout : int =10):
        """
    راه‌اندازی اولیه ربات روبیکا و پیکربندی پارامترهای پایه.

    Parameters:
        token (str): توکن اصلی ربات برای احراز هویت با Rubika Bot API. این مقدار الزامی است.
        session_name (str, optional): نام نشست دلخواه برای شناسایی یا جداسازی کلاینت‌ها. پیش‌فرض None.
        auth (str, optional): مقدار احراز هویت اضافی برای اتصال به کلاینت سفارشی. پیش‌فرض None.
        Key (str, optional): کلید اضافی برای رمزنگاری یا تأیید. در صورت نیاز استفاده می‌شود. پیش‌فرض None.
        platform (str, optional): پلتفرم اجرایی مورد نظر (مثل "web" یا "android"). پیش‌فرض "web".
        timeout (int, optional): مدت‌زمان تایم‌اوت برای درخواست‌های HTTP بر حسب ثانیه. پیش‌فرض 10 ثانیه.

    توضیحات:
        - این تابع یک شیء Session از requests می‌سازد برای استفاده در تمام درخواست‌ها.
        - هندلرهای مختلف مانند پیام، دکمه، کوئری اینلاین و ... در این مرحله مقداردهی اولیه می‌شوند.
        - لیست `self._callback_handlers` برای مدیریت چندین callback مختلف الزامی است.

    مثال:
        >>> bot = Robot(token="BOT_TOKEN", platform="android", timeout=15)
    """
        self.token = token
        self._inline_query_handlers = []
        self._inline_query_handlers: List[dict] = []
        self.timeout = timeout
        self.auth = auth
        self.session_name = session_name
        self.Key = Key
        self.platform = platform
        self.web_hook = web_hook
        self._offset_id = None
        self.session = requests.Session()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._callback_handler = None
        self._message_handler = None
        self._inline_query_handler = None
        self._callback_handlers = None
        self._callback_handlers = []  # ✅ این خط مهمه
        json_url = requests.get(web_hook).json()['url']
        if web_hook:
            for endpoint_type in ["ReceiveUpdate", "ReceiveInlineMessage", "ReceiveQuery", "GetSelectionItem", "SearchSelectionItems"]:
                print(self.update_bot_endpoint(web_hook, endpoint_type))
            self.web_hook = json_url


        logger.info(f"Initialized RubikaBot with token: {token[:8]}***")

    def _post(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{API_URL}/{self.token}/{method}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            try:
                json_resp = response.json()
            except ValueError:
                logger.error(f"Invalid JSON response from {method}: {response.text}")
                raise APIRequestError(f"Invalid JSON response: {response.text}")
            if method != "getUpdates":logger.debug(f"API Response from {method}: {json_resp}")
            
            return json_resp
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise APIRequestError(f"API request failed: {e}") from e


    def get_me(self) -> Dict[str, Any]:
        """Get info about the bot itself."""
        return self._post("getMe", {})
    def on_message(self, filters: Optional[Callable[[Message], bool]] = None, commands: Optional[List[str]] = None):
        def decorator(func: Callable[[Any, Message], None]):
            self._message_handler = {
                "func": func,
                "filters": filters,
                "commands": commands
            }
            return func
        return decorator

    def on_callback(self, button_id: Optional[str] = None):
        def decorator(func: Callable[[Any, Message], None]):
            if not hasattr(self, "_callback_handlers"):
                self._callback_handlers = []
            self._callback_handlers.append({
                "func": func,
                "button_id": button_id
            })
            return func
        return decorator
    def _handle_inline_query(self, inline_message: InlineMessage):
        aux_button_id = inline_message.aux_data.button_id if inline_message.aux_data else None

        for handler in self._inline_query_handlers:
            if handler["button_id"] is None or handler["button_id"] == aux_button_id:
                try:
                    handler["func"](self, inline_message)
                except Exception as e:
                    print(f"Error in inline query handler: {e}")

    def on_inline_query(self, button_id: Optional[str] = None):
        def decorator(func: Callable[[Any, InlineMessage], None]):
            self._inline_query_handlers.append({
                "func": func,
                "button_id": button_id
            })
            return func
        return decorator

    
    def _process_update(self, update: dict):
        import threading, time

        # هندل پیام inline (معمولاً type = ReceiveQuery)
        if update.get("type") == "ReceiveQuery":
            msg = update.get("inline_message", {})
            if update.get("type") == "ReceiveQuery":
                msg = update.get("inline_message", {})
                context = InlineMessage(bot=self, raw_data=msg)
                threading.Thread(target=self._handle_inline_query, args=(context,), daemon=True).start()
                return

        # هندل پیام جدید متنی
        if update.get("type") == "NewMessage":
            msg = update.get("new_message", {})
            chat_id = update.get("chat_id")
            message_id = msg.get("message_id")
            sender_id = msg.get("sender_id")
            text = msg.get("text")

            # فیلتر زمان پیام (مثلاً پیام‌های خیلی قدیمی)
            try:
                if msg.get("time") and (time.time() - float(msg["time"])) > 20:
                    return
            except Exception:
                return

            # ساخت context پیام
            context = Message(bot=self, chat_id=chat_id, message_id=message_id, sender_id=sender_id, text=text, raw_data=msg)

            # هندل callback ها (دکمه‌ها)
            if context.aux_data and hasattr(self, "_callback_handlers"):
                for handler in self._callback_handlers:
                    if not handler["button_id"] or context.aux_data.button_id == handler["button_id"]:
                        threading.Thread(target=handler["func"], args=(self, context), daemon=True).start()
                        return  # فقط یک callback اجرا شود

            # هندل پیام‌های متنی معمولی
            if hasattr(self, "_message_handler") and self._message_handler:
                handler = self._message_handler

                if handler["commands"]:
                    if not context.text or not context.text.startswith("/"):
                        return
                    parts = context.text.split()
                    cmd = parts[0][1:]
                    if cmd not in handler["commands"]:
                        return
                    context.args = parts[1:]

                if handler["filters"] and not handler["filters"](context):
                    return

                threading.Thread(target=handler["func"], args=(self, context), daemon=True).start()





    def get_updates(
        self,
        offset_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get updates."""
        data = {}
        if offset_id:
            data["offset_id"] = offset_id
        if limit:
            data["limit"] = limit
        return self._post("getUpdates", data)
    def update_webhook(
        self,
        offset_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        data = {}
        if offset_id:
            data["offset_id"] = offset_id
        if limit:
            data["limit"] = limit
        return list(requests.get(self.web_hook).json())
    def _is_duplicate(self, message_id: str, max_age_sec: int = 300) -> bool:
        now = time.time()

        # حذف پیام‌های قدیمی‌تر از max_age_sec
        expired = [mid for mid, ts in self._processed_message_ids.items() if now - ts > max_age_sec]
        for mid in expired:
            del self._processed_message_ids[mid]

        # بررسی تکراری بودن پیام
        if message_id in self._processed_message_ids:
            return True

        self._processed_message_ids[message_id] = now
        return False


    import time


    def run(self):
        print("Bot started running...")
        self._processed_message_ids: Dict[str, float] = {}
        # self._offset_id می‌تواند قبلاً مقداردهی شده باشد

        while True:
            try:
                if self.web_hook:
                    updates = self.update_webhook()

                    if isinstance(updates, list):
                        for item in updates:
                            data = item.get("data", {})

                            # بررسی زمان دریافت پیام و رد کردن پیام‌های قدیمی (بیش از 20 ثانیه)
                            received_at_str = item.get("received_at")
                            if received_at_str:
                                received_at_ts = datetime.datetime.strptime(received_at_str, "%Y-%m-%d %H:%M:%S").timestamp()
                                if time.time() - received_at_ts > 20:
                                    continue  # رد کردن پیام قدیمی

                            update = None
                            if "update" in data:
                                update = data["update"]
                            elif "inline_message" in data:
                                update = {
                                    "type": "ReceiveQuery",
                                    "inline_message": data["inline_message"]
                                }
                            else:
                                continue

                            message_id = None
                            if update.get("type") == "NewMessage":
                                message_id = update.get("new_message", {}).get("message_id")
                            elif update.get("type") == "ReceiveQuery":
                                message_id = update.get("inline_message", {}).get("message_id")
                            elif "message_id" in update:
                                message_id = update.get("message_id")

                            if message_id is not None:
                                message_id = str(message_id)

                            if message_id and self._is_duplicate(message_id):
                                continue

                            self._process_update(update)

                            # ثبت پیام به عنوان پردازش شده
                            if message_id:
                                self._processed_message_ids[message_id] = time.time()

                else:
                    updates = self.get_updates(offset_id=self._offset_id, limit=100)

                    if updates and updates.get("data"):
                        for update in updates["data"].get("updates", []):
                            message_id = None
                            if update.get("type") == "NewMessage":
                                message_id = update.get("new_message", {}).get("message_id")
                            elif update.get("type") == "ReceiveQuery":
                                message_id = update.get("inline_message", {}).get("message_id")
                            elif "message_id" in update:
                                message_id = update.get("message_id")

                            if message_id is not None:
                                message_id = str(message_id)

                            if message_id and self._is_duplicate(message_id):
                                continue

                            self._process_update(update)

                            if message_id:
                                self._processed_message_ids[message_id] = time.time()

                        self._offset_id = updates["data"].get("next_offset_id", self._offset_id)

            except Exception as e:
                print(f"❌ Error in run loop: {e}")









    def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Optional[Dict[str, Any]] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """
        Send a text message to a chat.
        """
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": disable_notification
        }
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type:
            payload["chat_keypad_type"] = chat_keypad_type

        return self._post("sendMessage", payload)

    def _get_client(self):
        if self.session_name:
            return Client_get(self.session_name,self.auth,self.Key,self.platform)
        else :
            return Client_get(show_last_six_words(self.token),self.auth,self.Key,self.platform)
    from typing import Union

    def check_join(self, channel_guid: str, chat_id: str = None) -> Union[bool, list[str]]:
        client = self._get_client()

        if chat_id:
            chat_info = self.get_chat(chat_id).get('data', {}).get('chat', {})
            username = chat_info.get('username')
            user_id = chat_info.get('user_id')

            if username:
                members = self.get_all_member(channel_guid, search_text=username).get('in_chat_members', [])
                return any(m.get('username') == username for m in members)

            elif user_id:
                member_guids = client.get_all_members(channel_guid, just_get_guids=True)
                return user_id in member_guids

            return False

        return False


    def get_all_member(
        self,
        channel_guid: str,
        search_text: str = None,
        start_id: str = None,
        just_get_guids: bool = False
    ):
        client = self._get_client()
        return client.get_all_members(channel_guid, search_text, start_id, just_get_guids)

    def send_poll(
        self,
        chat_id: str,
        question: str,
        options: List[str]
    ) -> Dict[str, Any]:
        """
        Send a poll to a chat.
        """
        return self._post("sendPoll", {
            "chat_id": chat_id,
            "question": question,
            "options": options
        })

    def send_location(
        self,
        chat_id: str,
        latitude: str,
        longitude: str,
        disable_notification: bool = False,
        inline_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        """
        Send a location to a chat.
        """
        payload = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "disable_notification": disable_notification,
            "inline_keypad": inline_keypad,
            "reply_to_message_id": reply_to_message_id,
            "chat_keypad_type": chat_keypad_type
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        return self._post("sendLocation", payload)

    def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str
    ) -> Dict[str, Any]:
        """
        Send a contact to a chat.
        """
        return self._post("sendContact", {
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number
        })

    def get_chat(self, chat_id: str) -> Dict[str, Any]:
        """Get chat info."""
        return self._post("getChat", {"chat_id": chat_id})
    def upload_media_file(self, upload_url: str, name: str, path: Union[str, Path]) -> str:
        # بررسی اینکه ورودی URL است یا مسیر محلی
        is_temp_file = False
        if isinstance(path, str) and path.startswith("http"):
            response = requests.get(path)
            if response.status_code != 200:
                raise Exception(f"Failed to download file from URL ({response.status_code})")
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(response.content)
            temp_file.close()
            path = temp_file.name
            is_temp_file = True

        with open(path, 'rb') as file:
            files = {
                'file': (name, file, 'application/octet-stream')
            }
            response = requests.post(upload_url, files=files)
            if response.status_code != 200:
                raise Exception(f"Upload failed ({response.status_code}): {response.text}")
            data = response.json()

        if is_temp_file:
            os.unlink(path)  # حذف فایل موقت

        return data.get('data', {}).get('file_id')

    def get_upload_url(self, media_type: Literal['File', 'Image', 'Voice', 'Music', 'Gif']) -> str:
        allowed = ['File', 'Image', 'Voice', 'Music', 'Gif']
        if media_type not in allowed:
            raise ValueError(f"Invalid media type. Must be one of {allowed}")
        result = self._post("requestSendFile", {"type": media_type})
        return result.get("data", {}).get("upload_url")
    def _send_uploaded_file(
        self,
        chat_id: str,
        file_id: str,
        text: Optional[str] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "None"
    ) -> Dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "file_id": file_id,
            "text": text,
            "disable_notification": disable_notification,
            "chat_keypad_type": chat_keypad_type,
        }
        if chat_keypad:
            payload["chat_keypad"] = chat_keypad
        if inline_keypad:
            payload["inline_keypad"] = inline_keypad
        if reply_to_message_id:
            payload["reply_to_message_id"] = str(reply_to_message_id)

        return self._post("sendFile", payload)

    def send_document(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New"
    ) -> Dict[str, Any]:
        if path:
            file_name = file_name or Path(path).name
            upload_url = self.get_upload_url("File")
            file_id = self.upload_media_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        return self._send_uploaded_file(
            chat_id=chat_id,
            file_id=file_id,
            text=text,
            inline_keypad=inline_keypad,
            chat_keypad=chat_keypad,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            chat_keypad_type=chat_keypad_type
        )
    def send_music(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New"
    ) -> Dict[str, Any]:
        if path:
            file_name = file_name or Path(path).name
            upload_url = self.get_upload_url("Music")
            file_id = self.upload_media_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        return self._send_uploaded_file(
            chat_id=chat_id,
            file_id=file_id,
            text=text,
            inline_keypad=inline_keypad,
            chat_keypad=chat_keypad,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            chat_keypad_type=chat_keypad_type
        )
    def send_voice(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New"
    ) -> Dict[str, Any]:
        if path:
            file_name = file_name or Path(path).name
            upload_url = self.get_upload_url("Voice")
            file_id = self.upload_media_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        return self._send_uploaded_file(
            chat_id=chat_id,
            file_id=file_id,
            text=text,
            inline_keypad=inline_keypad,
            chat_keypad=chat_keypad,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            chat_keypad_type=chat_keypad_type
        )
    def send_image(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New"
    ) -> Dict[str, Any]:
        if path:
            file_name = file_name or Path(path).name
            upload_url = self.get_upload_url("Image")
            file_id = self.upload_media_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        return self._send_uploaded_file(
            chat_id=chat_id,
            file_id=file_id,
            text=text,
            inline_keypad=inline_keypad,
            chat_keypad=chat_keypad,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            chat_keypad_type=chat_keypad_type
        )
    def send_gif(
        self,
        chat_id: str,
        path: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        file_name: Optional[str] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        chat_keypad: Optional[Dict[str, Any]] = None,
        reply_to_message_id: Optional[str] = None,
        disable_notification: bool = False,
        chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New"
    ) -> Dict[str, Any]:
        if path:
            file_name = file_name or Path(path).name
            upload_url = self.get_upload_url("Gif")
            file_id = self.upload_media_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        return self._send_uploaded_file(
            chat_id=chat_id,
            file_id=file_id,
            text=text,
            inline_keypad=inline_keypad,
            chat_keypad=chat_keypad,
            reply_to_message_id=reply_to_message_id,
            disable_notification=disable_notification,
            chat_keypad_type=chat_keypad_type
        )

    

    def forward_message(
        self,
        from_chat_id: str,
        message_id: str,
        to_chat_id: str,
        disable_notification: bool = False
    ) -> Dict[str, Any]:
        """Forward a message from one chat to another."""
        return self._post("forwardMessage", {
            "from_chat_id": from_chat_id,
            "message_id": message_id,
            "to_chat_id": to_chat_id,
            "disable_notification": disable_notification
        })

    def edit_message_text(
        self,
        chat_id: str,
        message_id: str,
        text: str
    ) -> Dict[str, Any]:
        """Edit text of an existing message."""
        return self._post("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        })

    def edit_inline_keypad(
        self,
        chat_id: str,
        message_id: str,
        inline_keypad: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Edit inline keypad of a message."""
        return self._post("editMessageKeypad", {
            "chat_id": chat_id,
            "message_id": message_id,
            "inline_keypad": inline_keypad
        })

    def delete_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        """Delete a message from chat."""
        return self._post("deleteMessage", {
            "chat_id": chat_id,
            "message_id": message_id
        })

    def set_commands(self, bot_commands: List[Dict[str, str]]) -> Dict[str, Any]:
        """Set bot commands."""
        return self._post("setCommands", {"bot_commands": bot_commands})

    def update_bot_endpoint(self, url: str, type: str) -> Dict[str, Any]:
        """Update bot endpoint (Webhook or Polling)."""
        return self._post("updateBotEndpoints", {
            "url": url,
            "type": type
        })

    def remove_keypad(self, chat_id: str) -> Dict[str, Any]:
        """Remove chat keypad."""
        return self._post("editChatKeypad", {
            "chat_id": chat_id,
            "chat_keypad_type": "Removed"
        })

    def edit_chat_keypad(self, chat_id: str, chat_keypad: Dict[str, Any]) -> Dict[str, Any]:
        """Edit or add new chat keypad."""
        return self._post("editChatKeypad", {
            "chat_id": chat_id,
            "chat_keypad_type": "New",
            "chat_keypad": chat_keypad
        })
    def get_name(self, chat_id: str) -> str:
        try:
            chat = self.get_chat(chat_id)
            chat_info = chat.get("data", {}).get("chat", {})
            first_name = chat_info.get("first_name", "")
            last_name = chat_info.get("last_name", "")
            
            if first_name and last_name:
                return f"{first_name} {last_name}"
            elif first_name:
                return first_name
            elif last_name:
                return last_name
            else:
                return "Unknown"
        except Exception:
            return "Unknown"
    def get_username(self, chat_id: str) -> str:
        chat_info = self.get_chat(chat_id).get("data", {}).get("chat", {})
        return chat_info.get("username", "None")
