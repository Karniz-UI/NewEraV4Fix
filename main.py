import asyncio
import os
import sys
import time
import psutil
import importlib
import importlib.util
import shutil
from datetime import datetime
from telethon import TelegramClient, events

class NewEraV4Fix:
    def __init__(self):
        self.start_time = time.time()
        self.modules_dir = "modules"
        self.loaded_modules = {}
        self.module_commands = {}
        self.config = {}
        self.client = None
        
        self.styled_chars = {
            'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
            'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
            'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
            'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
            'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
            'z': 'ᴢ', '0': '𝟢', '1': '𝟣', '2': '𝟤', '3': '𝟥',
            '4': '𝟦', '5': '𝟧', '6': '𝟨', '7': '𝟩', '8': '𝟪',
            '9': '𝟫'
        }
        
        self.languages = {
            "ru": {
                "uptime": "Аптайм",
                "user": "Юзер", 
                "cpu": "Процессор",
                "ram": "Оперативка",
                "host": "Хост",
                "commands": "Команды",
                "help_text": """**NewEraV4Fix - команды:**

`.help` - Показать команды
`.info` - Информация о системе
`.lm` - Загрузить модуль (реплай на файл)
`.ulm <имя>` - Выгрузить модуль
`.modules` - Список модулей
`.setlang <ru/en>` - Сменить язык
`.restart` - Перезагрузка
`.stop` - Остановка
`.backup` - Создать бэкап
`.clean` - Очистить временные файлы""",
                "module_loaded": "Модуль {} загружен",
                "module_unloaded": "Модуль {} выгружен",
                "module_not_found": "Модуль {} не найден",
                "lang_changed": "Язык изменен на {}",
                "restarting": "Перезагрузка...",
                "stopping": "Остановка...",
                "no_modules": "Нет загруженных модулей",
                "modules_list": "**Загруженные модули:**",
                "backup_created": "Бэкап создан: {}",
                "temp_cleaned": "Временные файлы очищены: {} файлов"
            },
            "en": {
                "uptime": "Uptime",
                "user": "User",
                "cpu": "CPU", 
                "ram": "RAM",
                "host": "Host",
                "commands": "Commands",
                "help_text": """**NewEraV4Fix - Main commands:**

`.help` - Show commands
`.info` - System information  
`.lm` - Load module (reply to file)
`.ulm <name>` - Unload module
`.modules` - Modules list
`.setlang <ru/en>` - Change language
`.restart` - Restart
`.stop` - Stop
`.backup` - Create backup
`.clean` - Clean temp files""",
                "module_loaded": "Module {} loaded",
                "module_unloaded": "Module {} unloaded", 
                "module_not_found": "Module {} not found",
                "lang_changed": "Language changed to {}",
                "restarting": "Restarting...",
                "stopping": "Stopping...",
                "no_modules": "No modules loaded",
                "modules_list": "**Loaded modules:**",
                "backup_created": "Backup created: {}",
                "temp_cleaned": "Temp files cleaned: {} files"
            }
        }

    def print_banner(self):
        """ASCII-арт при запуске"""
        banner = r"""
  _   _               _____           
 | \ | | _____      _| ____|_ __ __ _ 
 |  \| |/ _ \ \ /\ / /  _| | '__/ _` |
 | |\  |  __/\ V  V /| |___| | | (_| |
 |_| \_|\___| \_/\_/ |_____|_|  \__,_|

Build: #Fix7HxBy9w
Update: No
GoodLuck ♡
"""
        print(banner)

    def load_config(self):
        """Динамическая настройка без config.json"""
        if not hasattr(self, 'config'):
            self.config = {}
        
        defaults = {
            "prefix": ".",
            "language": "ru",
            "owner_id": None
        }
        
        if not all(k in self.config for k in ['api_id', 'api_hash']):
            self.print_banner()
            print(" Первый запуск ".center(40, '='))
            
            try:
                self.config['api_id'] = int(input("API ID: ").strip())
                self.config['api_hash'] = input("API Hash: ").strip()
                
                for key, value in defaults.items():
                    user_input = input(f"{key} ({value}): ").strip()
                    self.config[key] = user_input if user_input else value
                
                print("=" * 40)
                return True
                
            except ValueError:
                print("[ОШИБКА] API ID должен быть числом!")
                return False
        return True

    def get_text(self, key):
        """Локализация текста"""
        return self.languages[self.config["language"]].get(key, key)
        
    def get_uptime(self):
        """Форматированное время работы"""
        uptime = int(time.time() - self.start_time)
        return f"{uptime // 3600:02d}:{(uptime % 3600) // 60:02d}:{uptime % 60:02d}"
        
    def get_system_info(self):
        """Системная информация"""
        try:
            memory = psutil.virtual_memory()
            return {
                "uptime": self.get_uptime(),
                "ram": f"{memory.percent:.1f}%"
            }
        except:
            return {
                "uptime": self.get_uptime(),
                "ram": "N/A"
            }

    def style_text(self, text):
        """Стилизация текста для .info"""
        return ''.join([self.styled_chars.get(c.lower(), c) for c in text])
        
    async def create_backup(self):
        """Создание резервной копии"""
        backup_dir = "newera_backup"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        
        try:
            shutil.make_archive(
                os.path.join(backup_dir, f"backup_{timestamp}"), 
                'zip', 
                '.', 
                [self.modules_dir, "main.py"]
            )
            return backup_name
        except Exception as e:
            print(f"Backup error: {e}")
            return None
            
    async def clean_temp_files(self):
        """Очистка временных файлов"""
        temp_dir = "/tmp"
        if not os.path.exists(temp_dir):
            return 0
            
        count = 0
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    count += 1
            except Exception:
                continue
        return count
        
    async def load_module(self, file_path, module_name):
        """Загрузка модуля"""
        try:
            os.makedirs(self.modules_dir, exist_ok=True)
            module_path = os.path.join(self.modules_dir, f"{module_name}.py")
            
            with open(file_path, "rb") as src, open(module_path, "wb") as dst:
                dst.write(src.read())
                
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "register"):
                handlers = await module.register(self.client)
                if hasattr(module, "commands"):
                    self.module_commands[module_name] = module.commands
                self.loaded_modules[module_name] = module
                return True
            return False
            
        except Exception as e:
            print(f"Ошибка загрузки модуля: {str(e)}")
            return False
            
    async def unload_module(self, module_name):
        """Выгрузка модуля"""
        if module_name in self.loaded_modules:
            module = self.loaded_modules[module_name]
            if hasattr(module, "unregister"):
                await module.unregister(self.client)
                
            if module_name in self.module_commands:
                del self.module_commands[module_name]
                
            del self.loaded_modules[module_name]
            
            module_path = os.path.join(self.modules_dir, f"{module_name}.py")
            if os.path.exists(module_path):
                os.remove(module_path)
                
            return True
        return False
        
    async def setup_handlers(self):
        """Регистрация обработчиков"""
        prefix = self.config["prefix"]
        
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}help$"))
        async def help_handler(event):
            await event.edit(self.get_text("help_text"))
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}info$"))
        async def info_handler(event):
            info = self.get_system_info()
            me = await self.client.get_me()
            username = me.username or me.first_name
            
            text = f"""`╭─────────────────────
│     NewEraV4Fix     
├─────────────────────
│ {self.style_text('uptime')}: {info["uptime"]}      
│ {self.style_text('user')}: {username}       
│ {self.style_text('ram')}: {info["ram"]}           
│ {self.style_text('host')}: Termux         
╰─────────────────────
`"""
            await event.edit(text)
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}backup$"))
        async def backup_handler(event):
            backup_name = await self.create_backup()
            text = self.get_text("backup_created").format(backup_name) if backup_name else "Ошибка создания бэкапа"
            await event.edit(text)
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}clean$"))
        async def clean_handler(event):
            count = await self.clean_temp_files()
            await event.edit(self.get_text("temp_cleaned").format(count))
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}lm$"))
        async def load_module_handler(event):
            if not event.is_reply:
                return await event.edit("Ответьте на файл модуля")
                
            reply = await event.get_reply_message()
            if not reply.document:
                return await event.edit("Это не файл")
                
            file_name = reply.document.attributes[0].file_name
            if not file_name.endswith('.py'):
                return await event.edit("Нужен .py файл")
                
            module_name = file_name[:-3]
            await event.edit("Загрузка модуля...")
            
            file_path = await reply.download_media()
            success = await self.load_module(file_path, module_name)
            
            text = self.get_text("module_loaded").format(module_name) if success else f"Ошибка загрузки {module_name}"
            await event.edit(text)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}ulm (.+)$"))
        async def unload_module_handler(event):
            module_name = event.pattern_match.group(1)
            success = await self.unload_module(module_name)
            
            text = self.get_text("module_unloaded").format(module_name) if success \
                else self.get_text("module_not_found").format(module_name)
            await event.edit(text)
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}modules$"))
        async def modules_handler(event):
            if not self.loaded_modules:
                return await event.edit(self.get_text("no_modules"))
                
            text = self.get_text("modules_list") + "\n"
            for name, module in self.loaded_modules.items():
                text += f"• `{name}`\n"
                if name in self.module_commands:
                    text += "  └ " + ", ".join(f"`{prefix}{cmd}`" for cmd in self.module_commands[name]) + "\n"
            await event.edit(text)
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}setlang (ru|en)$"))
        async def setlang_handler(event):
            lang = event.pattern_match.group(1)
            self.config["language"] = lang
            await event.edit(self.get_text("lang_changed").format(lang.upper()))
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}restart$"))
        async def restart_handler(event):
            await event.edit(self.get_text("restarting"))
            await self.client.disconnect()
            os.execl(sys.executable, sys.executable, *sys.argv)
            
        @self.client.on(events.NewMessage(outgoing=True, pattern=f"^\\{prefix}stop$"))
        async def stop_handler(event):
            await event.edit(self.get_text("stopping"))
            await self.client.disconnect()
            sys.exit(0)
            
    async def start(self):
        """Основной цикл"""
        if not self.load_config():
            print("Ошибка конфигурации!")
            return
            
        self.client = TelegramClient(
            "newerav4fix_session",
            self.config["api_id"],
            self.config["api_hash"]
        )
        
        await self.client.start()
        await self.setup_handlers()
        
        me = await self.client.get_me()
        print(f"Бот запущен как @{me.username}")
        print(f"Префикс: {self.config['prefix']}")
        print("Для списка команд используйте .help")
        
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    bot = NewEraV4Fix()
    asyncio.run(bot.start())
