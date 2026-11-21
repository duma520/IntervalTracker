import sys
import os
import shutil
import sqlite3
import datetime
import json
import hashlib
import threading
import time
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import pypinyin

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QTimeEdit, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QTabWidget, QSplitter, QHeaderView, QProgressBar,
    QCheckBox, QSpinBox, QGroupBox, QRadioButton, QButtonGroup,
    QFileDialog, QMenu, QMenuBar, QStatusBar, QToolBar, QApplication,
    QAbstractItemView, QDateTimeEdit, QCalendarWidget, QTextEdit,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QGridLayout, QFrame, QScrollArea, QTableView, QColorDialog
)
from PySide6.QtCore import (
    Qt, QDate, QTime, QDateTime, QTimer, Signal, Slot, QThread,
    QSize, QSettings, QPoint, QByteArray, QSortFilterProxyModel,
    QAbstractTableModel, QModelIndex, QPropertyAnimation, QEasingCurve,
    QRect, QEvent, QCoreApplication
)
from PySide6.QtGui import (
    QIcon, QFont, QColor, QPalette, QPixmap, QAction,
    QKeySequence, QBrush, QPen, QPainter, QLinearGradient,
    QGuiApplication, QScreen
)

# ==================== 项目信息元数据 ====================
class ProjectInfo:
    """项目信息元数据（集中管理所有项目相关信息）"""
    VERSION = "1.4.0"  # 更新版本号
    BUILD_DATE = "2026-03-20"
    AUTHOR = "杜玛"
    LICENSE = "GNU Affero General Public License v3.0"
    COPYRIGHT = "© 永久 杜玛"
    URL = "https://github.com/duma520/IntervalTracker"
    MAINTAINER_EMAIL = "不提供"
    NAME = "IntervalTracker"
    DESCRIPTION = "IntervalTracker 间隔追踪器（支持多标识分类和间隔统计）"
    
    @classmethod
    def get_full_name(cls) -> str:
        """获取完整的程序名称（带版本）"""
        return f"{cls.NAME} v{cls.VERSION}"
    
    @classmethod
    def get_full_title(cls, username: str = None) -> str:
        """获取完整的窗口标题"""
        base = f"{cls.get_full_name()} 构建:{cls.BUILD_DATE}"
        if username:
            return f"{base} - 当前用户: {username}"
        return base
    
    @classmethod
    def get_about_text(cls) -> str:
        """获取关于信息文本"""
        return f"""
        <h2>{cls.NAME}</h2>
        <p><b>版本:</b> {cls.VERSION}</p>
        <p><b>构建日期:</b> {cls.BUILD_DATE}</p>
        <p><b>作者:</b> {cls.AUTHOR}</p>
        <p><b>版权:</b> {cls.COPYRIGHT}</p>
        <p><b>许可证:</b> {cls.LICENSE}</p>
        <p><b>项目主页:</b> <a href='{cls.URL}'>{cls.URL}</a></p>
        <p><b>描述:</b> {cls.DESCRIPTION}</p>
        """

# ====================  马卡龙色系定义 ====================
class MacaronColors:
    """马卡龙色系完整定义"""
    # 粉色系
    PINK_SAKURA = QColor('#FFB7CE')      # 樱花粉
    PINK_ROSE = QColor('#FF9AA2')        # 玫瑰粉
    PINK_COTTON = QColor('#FFD1DC')      # 棉花粉
    PINK_BALLET = QColor('#FCC9D3')      # 芭蕾粉
    
    # 蓝色系
    BLUE_SKY = QColor('#A2E1F6')         # 天空蓝
    BLUE_MIST = QColor('#C2E5F9')        # 雾霾蓝
    BLUE_PERIWINKLE = QColor('#C5D0E6')  # 长春花蓝
    BLUE_LAVENDER = QColor('#D6EAF8')    # 薰衣草蓝
    
    # 绿色系
    GREEN_MINT = QColor('#B5EAD7')       # 薄荷绿
    GREEN_APPLE = QColor('#D4F1C7')      # 苹果绿
    GREEN_PISTACHIO = QColor('#D8E9D6')  # 开心果绿
    GREEN_SAGE = QColor('#C9DFC5')       # 鼠尾草绿
    
    # 黄色/橙色系
    YELLOW_LEMON = QColor('#FFEAA5')      # 柠檬黄
    YELLOW_CREAM = QColor('#FFF8B8')      # 奶油黄
    YELLOW_HONEY = QColor('#FCE5B4')      # 蜂蜜黄
    ORANGE_PEACH = QColor('#FFDAC1')      # 蜜桃橙
    ORANGE_APRICOT = QColor('#FDD9B5')    # 杏色
    
    # 紫色系
    PURPLE_LAVENDER = QColor('#C7CEEA')   # 薰衣草紫
    PURPLE_TARO = QColor('#D8BFD8')       # 香芋紫
    PURPLE_WISTERIA = QColor('#C9B6D9')   # 紫藤
    PURPLE_MAUVE = QColor('#E0C7D7')      # 淡紫
    
    # 中性色
    NEUTRAL_CARAMEL = QColor('#F0E6DD')   # 焦糖奶霜
    NEUTRAL_CREAM = QColor('#F7F1E5')     # 奶油白
    NEUTRAL_MOCHA = QColor('#EAD7C7')     # 摩卡
    NEUTRAL_ALMOND = QColor('#F2E4D4')    # 杏仁
    
    # 其他颜色
    RED_CORAL = QColor('#FFB3A7')          # 珊瑚红
    RED_WATERMELON = QColor('#FFC5C5')     # 西瓜红
    TEAL_MINT = QColor('#B8E2DE')          # 薄荷绿蓝
    
    # 文字颜色定义
    TEXT_DARK = QColor('#2C3E50')          # 深蓝灰（用于浅色背景的主要文字）
    TEXT_LIGHT = QColor('#FFFFFF')         # 白色（用于深色背景）
    TEXT_MUTED = QColor('#7F8C8D')         # 中灰色（用于次要文字）
    TEXT_LINK = QColor('#3498DB')          # 链接蓝色
    TEXT_SUCCESS = QColor('#27AE60')       # 成功绿色
    TEXT_WARNING = QColor('#F39C12')       # 警告橙色
    TEXT_ERROR = QColor('#E74C3C')         # 错误红色
    TEXT_INFO = QColor('#2980B9')          # 信息蓝色
    
    @staticmethod
    def get_text_color(background_color: QColor) -> QColor:
        """根据背景色返回合适的文字颜色"""
        # 计算背景色的亮度（0-255）
        brightness = (background_color.red() * 299 + 
                     background_color.green() * 587 + 
                     background_color.blue() * 114) / 1000
        
        # 亮度阈值，小于128认为是深色背景，用白色文字；否则用深色文字
        if brightness < 128:
            return QColor('#FFFFFF')  # 白色文字
        else:
            return QColor('#2C3E50')  # 深蓝灰文字
    
    @classmethod
    def get_color_list(cls):
        """获取所有马卡龙颜色列表"""
        return [
            cls.PINK_SAKURA, cls.PINK_ROSE, cls.PINK_COTTON, cls.PINK_BALLET,
            cls.BLUE_SKY, cls.BLUE_MIST, cls.BLUE_PERIWINKLE, cls.BLUE_LAVENDER,
            cls.GREEN_MINT, cls.GREEN_APPLE, cls.GREEN_PISTACHIO, cls.GREEN_SAGE,
            cls.YELLOW_LEMON, cls.YELLOW_CREAM, cls.YELLOW_HONEY, cls.ORANGE_PEACH,
            cls.ORANGE_APRICOT, cls.PURPLE_LAVENDER, cls.PURPLE_TARO, cls.PURPLE_WISTERIA,
            cls.PURPLE_MAUVE, cls.NEUTRAL_CARAMEL, cls.NEUTRAL_CREAM, cls.NEUTRAL_MOCHA,
            cls.NEUTRAL_ALMOND, cls.RED_CORAL, cls.RED_WATERMELON, cls.TEAL_MINT
        ]
    
    @classmethod
    def get_color_names(cls):
        """获取马卡龙颜色名称列表"""
        return [
            "樱花粉", "玫瑰粉", "棉花粉", "芭蕾粉",
            "天空蓝", "雾霾蓝", "长春花蓝", "薰衣草蓝",
            "薄荷绿", "苹果绿", "开心果绿", "鼠尾草绿",
            "柠檬黄", "奶油黄", "蜂蜜黄", "蜜桃橙",
            "杏色", "薰衣草紫", "香芋紫", "紫藤",
            "淡紫", "焦糖奶霜", "奶油白", "摩卡",
            "杏仁", "珊瑚红", "西瓜红", "薄荷绿蓝"
        ]

# 数据库版本信息
DATABASE_VERSION = "1.4.0"
DATABASE_SCHEMA_VERSION = 3

class SingletonMeta(type):
    """元类实现单例模式"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class DatabaseConnectionPool(metaclass=SingletonMeta):
    """数据库连接池单例类（线程安全版）"""
    
    def __init__(self):
        self._connections = {}
        self._lock = threading.Lock()
        self._thread_local = threading.local()
        
    def get_connection(self, db_path: str) -> sqlite3.Connection:
        """获取数据库连接（线程安全）"""
        # 获取当前线程ID
        thread_id = threading.get_ident()
        
        with self._lock:
            # 为每个线程维护独立的连接字典
            if not hasattr(self._thread_local, 'connections'):
                self._thread_local.connections = {}
            
            if db_path not in self._thread_local.connections:
                conn = sqlite3.connect(db_path, timeout=30.0)
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.row_factory = sqlite3.Row
                self._thread_local.connections[db_path] = conn
                
                # 同时在全局字典中记录，用于关闭所有连接
                if thread_id not in self._connections:
                    self._connections[thread_id] = {}
                self._connections[thread_id][db_path] = conn
            
            return self._thread_local.connections[db_path]
    
    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for thread_id, connections in self._connections.items():
                for conn in connections.values():
                    try:
                        conn.close()
                    except:
                        pass
            self._connections.clear()
            
            # 清理线程局部存储
            if hasattr(self._thread_local, 'connections'):
                self._thread_local.connections.clear()

    def close_connection(self, db_path: str):
        """关闭特定数据库的连接"""
        with self._lock:
            thread_id = threading.get_ident()
            if thread_id in self._connections and db_path in self._connections[thread_id]:
                try:
                    self._connections[thread_id][db_path].close()
                    del self._connections[thread_id][db_path]
                    
                    if hasattr(self._thread_local, 'connections') and db_path in self._thread_local.connections:
                        del self._thread_local.connections[db_path]
                    
                    return True
                except Exception as e:
                    print(f"关闭连接失败 {db_path}: {e}")
            return False

class UserManager:
    """用户管理器类"""
    
    def __init__(self):
        self.db_pool = DatabaseConnectionPool()
        self.config_dir = Path.cwd() / ".scheduling_system"
        self.config_dir.mkdir(exist_ok=True)
        self.users_db_path = self.config_dir / "users.db"
        self._init_users_database()
        
    def _init_users_database(self):
        """初始化用户数据库"""
        conn = self.db_pool.get_connection(str(self.users_db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                db_file TEXT UNIQUE NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                settings TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self.add_user("默认用户", "default_user")
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        conn = self.db_pool.get_connection(str(self.users_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, display_name, created_at, last_login, db_file 
            FROM users ORDER BY display_name
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def add_user(self, display_name: str, username: str = None) -> bool:
        """添加用户"""
        conn = None
        try:
            conn = self.db_pool.get_connection(str(self.users_db_path))
            cursor = conn.cursor()
            
            if username is None:
                base_username = display_name.lower().replace(" ", "_")
                username = base_username
                counter = 1
                while True:
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if not cursor.fetchone():
                        break
                    username = f"{base_username}_{counter}"
                    counter += 1
            
            db_filename = f"user_{username}_{int(time.time())}.db"
            db_path = self.config_dir / db_filename
            
            cursor.execute("""
                INSERT INTO users (username, display_name, db_file)
                VALUES (?, ?, ?)
            """, (username, display_name, db_filename))
            
            conn.commit()
            self._init_user_database(str(db_path))
            return True
        except Exception as e:
            print(f"添加用户失败: {e}")
            if conn:
                conn.rollback()
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        conn = None
        try:
            conn = self.db_pool.get_connection(str(self.users_db_path))
            cursor = conn.cursor()
            
            # 先获取用户的数据库文件信息
            cursor.execute("SELECT db_file FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            db_filename = result[0]
            db_path = self.config_dir / db_filename
            db_path_str = str(db_path)
            
            # 关闭该用户的数据库连接
            self.db_pool.close_connection(db_path_str)
            
            # 短暂延迟确保文件句柄完全释放
            time.sleep(0.1)
            
            # 删除用户记录
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            
            # 删除数据库文件
            if db_path.exists():
                max_retries = 3
                for i in range(max_retries):
                    try:
                        db_path.unlink()
                        print(f"数据库文件删除成功: {db_filename}")
                        break
                    except PermissionError as e:
                        if i < max_retries - 1:
                            print(f"删除文件失败，正在重试 ({i+1}/{max_retries})...")
                            time.sleep(0.3)  # 等待300ms后重试
                        else:
                            print(f"删除文件失败，已达到最大重试次数: {e}")
                    except Exception as e:
                        print(f"删除文件时发生未知错误: {e}")
                        break
            
            return True
        except Exception as e:
            print(f"删除用户失败: {e}")
            if conn:
                conn.rollback()
            return False
    
    def update_user(self, user_id: int, display_name: str = None, username: str = None) -> bool:
        """更新用户信息"""
        try:
            conn = self.db_pool.get_connection(str(self.users_db_path))
            cursor = conn.cursor()
            
            updates = []
            params = []
            if display_name is not None:
                updates.append("display_name = ?")
                params.append(display_name)
            if username is not None:
                updates.append("username = ?")
                params.append(username)
            
            if updates:
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                params.append(user_id)
                cursor.execute(query, params)
                conn.commit()
            
            return True
        except Exception as e:
            print(f"更新用户失败: {e}")
            return False
    
    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """获取用户设置"""
        conn = self.db_pool.get_connection(str(self.users_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT settings FROM user_settings WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return {}
    
    def save_user_settings(self, user_id: int, settings: Dict[str, Any]):
        """保存用户设置"""
        conn = self.db_pool.get_connection(str(self.users_db_path))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (user_id, settings)
            VALUES (?, ?)
        """, (user_id, json.dumps(settings)))
        conn.commit()
    
    def _init_user_database(self, db_path: str):
        """初始化用户数据库"""
        conn = self.db_pool.get_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#B5EAD7',
                icon TEXT,
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduling_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                record_date DATE NOT NULL,
                record_time TIME NOT NULL,
                content TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_category_id ON scheduling_records(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_date_time_category ON scheduling_records(record_date, record_time, category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_content ON scheduling_records(content)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_sort ON categories(sort_order)")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        cursor.execute("INSERT OR REPLACE INTO db_info (key, value) VALUES (?, ?)", ("version", DATABASE_VERSION))
        cursor.execute("INSERT OR REPLACE INTO db_info (key, value) VALUES (?, ?)", ("schema_version", str(DATABASE_SCHEMA_VERSION)))
        cursor.execute("INSERT OR REPLACE INTO db_info (key, value) VALUES (?, ?)", ("created_at", datetime.datetime.now().isoformat()))
        
        default_categories = [
            # 核心分类 (0-9)
            ("默认", "默认分类", MacaronColors.GREEN_MINT, 0),
            ("工作", "工作相关记录", MacaronColors.BLUE_SKY, 1),
            ("生活", "日常生活记录", MacaronColors.GREEN_APPLE, 2),
            ("学习", "学习进度记录", MacaronColors.PURPLE_LAVENDER, 3),
            ("运动", "运动健康记录", MacaronColors.ORANGE_PEACH, 4),
            ("娱乐", "娱乐休闲记录", MacaronColors.YELLOW_LEMON, 5),
            ("健康", "健康状况记录", MacaronColors.TEAL_MINT, 6),
            ("饮食", "饮食记录", MacaronColors.ORANGE_APRICOT, 7),
            ("其他", "其他记录", MacaronColors.NEUTRAL_CARAMEL, 8),
            
            # 工作相关扩展 (10-19)
            ("会议", "会议记录", MacaronColors.BLUE_MIST, 10),
            ("项目", "项目进度", MacaronColors.BLUE_PERIWINKLE, 11),
            ("任务", "任务清单", MacaronColors.BLUE_LAVENDER, 12),
            ("报告", "工作报告", MacaronColors.PINK_SAKURA, 13),
            ("邮件", "邮件处理", MacaronColors.PINK_COTTON, 14),
            ("客户", "客户沟通", MacaronColors.PINK_BALLET, 15),
            ("团队", "团队协作", MacaronColors.PINK_ROSE, 16),
            
            # 学习相关扩展 (20-29)
            ("读书", "阅读记录", MacaronColors.PURPLE_LAVENDER, 20),
            ("笔记", "学习笔记", MacaronColors.PURPLE_TARO, 21),
            ("课程", "课程学习", MacaronColors.PURPLE_WISTERIA, 22),
            ("考试", "考试准备", MacaronColors.PURPLE_MAUVE, 23),
            ("技能", "技能提升", MacaronColors.NEUTRAL_ALMOND, 24),
            
            # 健康相关扩展 (30-39)
            ("睡眠", "睡眠记录", MacaronColors.GREEN_MINT, 30),
            ("用药", "用药提醒", MacaronColors.GREEN_APPLE, 31),
            ("体检", "体检记录", MacaronColors.GREEN_PISTACHIO, 32),
            ("心理", "心理健康", MacaronColors.GREEN_SAGE, 33),
            ("医疗", "医疗就诊", MacaronColors.RED_CORAL, 34),
            
            # 运动相关扩展 (40-49)
            ("跑步", "跑步记录", MacaronColors.ORANGE_PEACH, 40),
            ("健身", "健身训练", MacaronColors.ORANGE_APRICOT, 41),
            ("瑜伽", "瑜伽练习", MacaronColors.YELLOW_CREAM, 42),
            ("徒步", "户外徒步", MacaronColors.YELLOW_HONEY, 43),
            ("游泳", "游泳记录", MacaronColors.BLUE_SKY, 44),
            
            # 生活相关扩展 (50-59)
            ("家务", "家务劳动", MacaronColors.NEUTRAL_CARAMEL, 50),
            ("购物", "购物清单", MacaronColors.NEUTRAL_CREAM, 51),
            ("财务", "财务管理", MacaronColors.NEUTRAL_MOCHA, 52),
            ("旅行", "旅行计划", MacaronColors.YELLOW_LEMON, 53),
            ("社交", "社交活动", MacaronColors.PINK_SAKURA, 54),
            ("家庭", "家庭事务", MacaronColors.PINK_COTTON, 55),
            
            # 娱乐相关扩展 (60-69)
            ("电影", "观影记录", MacaronColors.PURPLE_LAVENDER, 60),
            ("音乐", "音乐欣赏", MacaronColors.PURPLE_TARO, 61),
            ("游戏", "游戏时间", MacaronColors.PURPLE_WISTERIA, 62),
            ("阅读", "阅读休闲", MacaronColors.PURPLE_MAUVE, 63),
            ("创作", "创意创作", MacaronColors.ORANGE_PEACH, 64),
            
            # 饮食相关扩展 (70-79)
            ("早餐", "早餐记录", MacaronColors.YELLOW_LEMON, 70),
            ("午餐", "午餐记录", MacaronColors.YELLOW_CREAM, 71),
            ("晚餐", "晚餐记录", MacaronColors.YELLOW_HONEY, 72),
            ("加餐", "零食加餐", MacaronColors.ORANGE_APRICOT, 73),
            ("饮水", "饮水记录", MacaronColors.BLUE_SKY, 74),
            ("烹饪", "烹饪尝试", MacaronColors.GREEN_APPLE, 75),
            
            # 个人发展 (80-89)
            ("习惯", "习惯养成", MacaronColors.GREEN_MINT, 80),
            ("目标", "目标追踪", MacaronColors.GREEN_PISTACHIO, 81),
            ("反思", "每日反思", MacaronColors.GREEN_SAGE, 82),
            ("规划", "未来规划", MacaronColors.BLUE_LAVENDER, 83),
            ("灵感", "灵感收集", MacaronColors.PURPLE_LAVENDER, 84),
            
            # 技术与创作 (90-99)
            ("编程", "编程开发", MacaronColors.BLUE_PERIWINKLE, 90),
            ("设计", "设计工作", MacaronColors.PINK_BALLET, 91),
            ("写作", "写作记录", MacaronColors.NEUTRAL_ALMOND, 92),
            ("摄影", "摄影记录", MacaronColors.ORANGE_PEACH, 93),
            ("博客", "博客更新", MacaronColors.TEAL_MINT, 94),
            ("开源", "开源贡献", MacaronColors.GREEN_APPLE, 95),
            
            # 宠物与植物 (100-104)
            ("宠物", "宠物照料", MacaronColors.YELLOW_CREAM, 100),
            ("植物", "植物养护", MacaronColors.GREEN_MINT, 101),
            
            # 纪念与重要日期 (105-109)
            ("纪念日", "重要纪念", MacaronColors.RED_WATERMELON, 105),
            ("生日", "生日提醒", MacaronColors.RED_CORAL, 106),
            ("节日", "节日记录", MacaronColors.PINK_ROSE, 107),
            
            # 其他补充 (110-119)
            ("志愿", "志愿服务", MacaronColors.NEUTRAL_CARAMEL, 110),
            ("公益", "公益活动", MacaronColors.NEUTRAL_ALMOND, 111),
            ("环保", "环保行动", MacaronColors.GREEN_SAGE, 112),
            ("宗教", "宗教活动", MacaronColors.PURPLE_MAUVE, 113),
            ("冥想", "冥想练习", MacaronColors.PURPLE_LAVENDER, 114)
        ]
        
        for name, desc, color_obj, sort in default_categories:
            try:
                color_hex = color_obj.name()
                cursor.execute("""
                    INSERT OR IGNORE INTO categories (name, description, color, sort_order)
                    VALUES (?, ?, ?, ?)
                """, (name, desc, color_hex, sort))
            except Exception as e:
                print(f"插入默认标识失败: {e}")
        
        conn.commit()
        self._upgrade_old_database(conn)
    
    def _upgrade_old_database(self, conn: sqlite3.Connection):
        """升级旧版本数据库"""
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(scheduling_records)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'category' in columns and 'category_id' not in columns:
            print("检测到旧版本数据库，正在进行升级...")
            
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, description, color)
                SELECT DISTINCT category, '从旧版本迁移', ?
                FROM scheduling_records
                WHERE category NOT IN (SELECT name FROM categories)
            """, (MacaronColors.NEUTRAL_CARAMEL.name(),))
            
            cursor.execute("""
                ALTER TABLE scheduling_records 
                ADD COLUMN category_id INTEGER REFERENCES categories(id)
            """)
            
            cursor.execute("""
                UPDATE scheduling_records 
                SET category_id = (
                    SELECT id FROM categories 
                    WHERE categories.name = scheduling_records.category
                )
            """)
            
            cursor.execute("""
                CREATE TABLE scheduling_records_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    record_date DATE NOT NULL,
                    record_time TIME NOT NULL,
                    content TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
                )
            """)
            
            cursor.execute("""
                INSERT INTO scheduling_records_new 
                (id, category_id, record_date, record_time, content, notes, created_at, updated_at)
                SELECT id, category_id, record_date, record_time, content, notes, created_at, updated_at
                FROM scheduling_records
            """)
            
            cursor.execute("DROP TABLE scheduling_records")
            cursor.execute("ALTER TABLE scheduling_records_new RENAME TO scheduling_records")
            
            cursor.execute("CREATE INDEX idx_records_category_id ON scheduling_records(category_id)")
            cursor.execute("CREATE INDEX idx_records_date_time_category ON scheduling_records(record_date, record_time, category_id)")
            cursor.execute("CREATE INDEX idx_records_content ON scheduling_records(content)")
            
            conn.commit()
            print("数据库升级完成")

# ==================== 标识管理类 ====================
class CategoryManager:
    """标识管理器类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db_pool = DatabaseConnectionPool()
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """获取所有标识"""
        conn = self.db_pool.get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, color, icon, sort_order, is_active, 
                   created_at, updated_at
            FROM categories
            WHERE is_active = 1
            ORDER BY sort_order, name
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取标识"""
        conn = self.db_pool.get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, color, icon, sort_order, is_active, 
                   created_at, updated_at
            FROM categories
            WHERE id = ?
        """, (category_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_category(self, name: str, description: str = "", color: str = None, 
                     icon: str = None, sort_order: int = 0) -> Optional[int]:
        """添加标识"""
        if color is None:
            import random
            color_list = MacaronColors.get_color_list()
            color = random.choice(color_list).name()
        
        try:
            conn = self.db_pool.get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO categories (name, description, color, icon, sort_order)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, color, icon, sort_order))
            
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"标识名称 '{name}' 已存在")
        except Exception as e:
            print(f"添加标识失败: {e}")
            return None
    
    def update_category(self, category_id: int, **kwargs) -> bool:
        """更新标识"""
        try:
            conn = self.db_pool.get_connection(self.db_path)
            cursor = conn.cursor()
            
            allowed_fields = ['name', 'description', 'color', 'icon', 'sort_order', 'is_active']
            updates = []
            params = []
            
            for field in allowed_fields:
                if field in kwargs:
                    updates.append(f"{field} = ?")
                    params.append(kwargs[field])
            
            if not updates:
                return False
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(category_id)
            
            query = f"UPDATE categories SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            raise ValueError(f"标识名称 '{kwargs.get('name')}' 已存在")
        except Exception as e:
            print(f"更新标识失败: {e}")
            return False
    
    def delete_category(self, category_id: int) -> bool:
        """删除标识（软删除）"""
        try:
            conn = self.db_pool.get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM scheduling_records 
                WHERE category_id = ?
            """, (category_id,))
            
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    UPDATE categories SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (category_id,))
            else:
                cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"删除标识失败: {e}")
            return False
    
    def get_category_stats(self) -> List[Dict[str, Any]]:
        """获取标识统计信息"""
        conn = self.db_pool.get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                c.color,
                COUNT(r.id) as record_count,
                MAX(r.record_date || ' ' || r.record_time) as last_record_time,
                (
                    SELECT r2.content 
                    FROM scheduling_records r2 
                    WHERE r2.category_id = c.id 
                    ORDER BY r2.record_date DESC, r2.record_time DESC 
                    LIMIT 1
                ) as last_content
            FROM categories c
            LEFT JOIN scheduling_records r ON c.id = r.category_id
            WHERE c.is_active = 1
            GROUP BY c.id
            ORDER BY c.sort_order, c.name
        """)
        
        return [dict(row) for row in cursor.fetchall()]

# ==================== 标识管理对话框（增强版） ====================
class CategoryManagerDialog(QDialog):
    """标识管理对话框（增强版）"""
    
    def __init__(self, category_manager: CategoryManager, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.selected_category_ids = set()  # 用于多选删除
        self.has_changes = False  # 添加标志位，记录是否有修改
        self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 标识管理")
        self.setModal(True)
        self.setMinimumSize(900, 650)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QPushButton:disabled {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                color: {MacaronColors.TEXT_MUTED.name()};
            }}
            QTableWidget {{
                background-color: white;
                alternate-background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                gridline-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
            }}
            QTableWidget::item {{
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QTableWidget::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QHeaderView::section {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                padding: 5px;
                border: none;
                font-weight: bold;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QMenu {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
            }}
            QMenu::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        
        self._setup_ui()
        self._load_categories()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        # 左侧按钮组
        left_toolbar = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ 添加标识")
        self.add_btn.clicked.connect(self._add_category)
        left_toolbar.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ 编辑标识")
        self.edit_btn.clicked.connect(self._edit_category)
        self.edit_btn.setEnabled(False)
        left_toolbar.addWidget(self.edit_btn)
        
        # 多选删除相关按钮
        self.multi_select_btn = QPushButton("✅ 多选模式")
        self.multi_select_btn.setCheckable(True)
        self.multi_select_btn.toggled.connect(self._toggle_multi_select)
        left_toolbar.addWidget(self.multi_select_btn)
        
        self.delete_selected_btn = QPushButton("🗑️ 删除选中")
        self.delete_selected_btn.clicked.connect(self._delete_selected)
        self.delete_selected_btn.setEnabled(False)
        left_toolbar.addWidget(self.delete_selected_btn)
        
        toolbar.addLayout(left_toolbar)
        toolbar.addStretch()
        
        # 右侧按钮组
        right_toolbar = QHBoxLayout()
        
        # 一键清空按钮
        self.clear_all_btn = QPushButton("🧹 一键清空")
        self.clear_all_btn.clicked.connect(self._clear_all_categories)
        self.clear_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.RED_WATERMELON.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.RED_CORAL.name()};
            }}
        """)
        right_toolbar.addWidget(self.clear_all_btn)
        
        # 一键恢复默认按钮（带下拉菜单）
        self.reset_btn = QPushButton("🔄 一键恢复默认 ▼")
        self.reset_btn.clicked.connect(self._show_reset_menu)
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_SKY.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
        """)
        right_toolbar.addWidget(self.reset_btn)
        
        # 创建下拉菜单
        self.reset_menu = QMenu(self)
        self.reset_menu.addAction("📋 基础方案（简约）", lambda: self._reset_to_default("basic"))
        self.reset_menu.addAction("🏢 工作生活方案", lambda: self._reset_to_default("work_life"))
        self.reset_menu.addAction("📚 学习成长方案", lambda: self._reset_to_default("study"))
        self.reset_menu.addAction("🏃 健康运动方案", lambda: self._reset_to_default("health"))
        self.reset_menu.addAction("🎨 创意创作方案", lambda: self._reset_to_default("creative"))
        self.reset_menu.addAction("🏠 家庭消费方案", lambda: self._reset_to_default("family")) 
        self.reset_menu.addSeparator()
        self.reset_menu.addAction("✨ 完整方案（69项）", lambda: self._reset_to_default("full"))
        
        # 刷新按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self._load_categories)
        right_toolbar.addWidget(self.refresh_btn)
        
        toolbar.addLayout(right_toolbar)
        layout.addLayout(toolbar)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                padding: 5px;
                border-radius: 3px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        layout.addWidget(self.status_label)
        
        # 表格
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(8)
        self.category_table.setHorizontalHeaderLabels([
            "选择", "ID", "标识名称", "描述", "颜色", "记录数", "上次记录", "操作"
        ])
        self.category_table.horizontalHeader().setStretchLastSection(True)
        self.category_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.category_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.category_table.setAlternatingRowColors(True)
        self.category_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # 设置列宽
        self.category_table.setColumnWidth(0, 50)
        self.category_table.setColumnWidth(1, 60)
        self.category_table.setColumnWidth(2, 120)
        self.category_table.setColumnWidth(3, 200)
        self.category_table.setColumnWidth(4, 80)
        self.category_table.setColumnWidth(5, 70)
        self.category_table.setColumnWidth(6, 150)
        
        layout.addWidget(self.category_table)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_categories(self):
        """加载标识列表"""
        stats = self.category_manager.get_category_stats()
        
        self.category_table.setRowCount(len(stats))
        self.selected_category_ids.clear()
        self.delete_selected_btn.setEnabled(False)
        
        for row, stat in enumerate(stats):
            # 复选框
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            check_item.setData(Qt.UserRole, stat['id'])
            self.category_table.setItem(row, 0, check_item)
            
            # ID
            id_item = QTableWidgetItem(str(stat['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 1, id_item)
            
            # 标识名称
            name_item = QTableWidgetItem(stat['name'])
            name_item.setForeground(QBrush(QColor(stat['color'])))
            name_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 2, name_item)
            
            # 描述
            category = self.category_manager.get_category_by_id(stat['id'])
            desc_item = QTableWidgetItem(category.get('description', '') if category else '')
            self.category_table.setItem(row, 3, desc_item)
            
            # 颜色
            color_item = QTableWidgetItem()
            color_item.setBackground(QBrush(QColor(stat['color'])))
            color_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 4, color_item)
            
            # 记录数
            count_item = QTableWidgetItem(str(stat['record_count']))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 5, count_item)
            
            # 上次记录
            last_time = stat['last_record_time']
            if last_time:
                try:
                    dt = datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                    last_time = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            else:
                last_time = "无记录"
            time_item = QTableWidgetItem(last_time)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(row, 6, time_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("编辑")
            edit_btn.setProperty("category_id", stat['id'])
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MacaronColors.BLUE_MIST.name()};
                    border: none;
                    border-radius: 3px;
                    padding: 3px 8px;
                    color: {MacaronColors.TEXT_DARK.name()};
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {MacaronColors.BLUE_SKY.name()};
                }}
            """)
            edit_btn.clicked.connect(lambda checked, cid=stat['id']: self._edit_category(cid))
            btn_layout.addWidget(edit_btn)
            
            if stat['record_count'] == 0:
                delete_btn = QPushButton("删除")
                delete_btn.setProperty("category_id", stat['id'])
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {MacaronColors.RED_WATERMELON.name()};
                        border: none;
                        border-radius: 3px;
                        padding: 3px 8px;
                        color: {MacaronColors.TEXT_DARK.name()};
                        font-size: 11px;
                    }}
                    QPushButton:hover {{
                        background-color: {MacaronColors.RED_CORAL.name()};
                    }}
                """)
                delete_btn.clicked.connect(lambda checked, cid=stat['id']: self._delete_category(cid))
                btn_layout.addWidget(delete_btn)
            
            self.category_table.setCellWidget(row, 7, btn_widget)
        
        self.category_table.resizeColumnsToContents()
        self.category_table.setColumnWidth(2, 150)
        self.category_table.setColumnWidth(3, 200)
        
        # 连接复选框状态变化信号
        self.category_table.itemChanged.connect(self._on_item_changed)
        
        self.status_label.setText(f"共 {len(stats)} 个标识 | 选中: {len(self.selected_category_ids)}")
    
    def _on_item_changed(self, item):
        """项目变化事件（处理复选框）"""
        if item.column() == 0:
            category_id = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked:
                self.selected_category_ids.add(category_id)
            else:
                self.selected_category_ids.discard(category_id)
            
            self.delete_selected_btn.setEnabled(len(self.selected_category_ids) > 0)
            self.status_label.setText(f"共 {self.category_table.rowCount()} 个标识 | 选中: {len(self.selected_category_ids)}")
    
    def _toggle_multi_select(self, checked):
        """切换多选模式"""
        if checked:
            self.multi_select_btn.setText("❌ 退出多选")
            self.multi_select_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    color: {MacaronColors.TEXT_DARK.name()};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {MacaronColors.PURPLE_TARO.name()};
                }}
            """)
            self.category_table.setSelectionMode(QTableWidget.MultiSelection)
            self.status_label.setText(f"多选模式：勾选要删除的标识 | 共 {self.category_table.rowCount()} 个标识")
        else:
            self.multi_select_btn.setText("✅ 多选模式")
            self.multi_select_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MacaronColors.PINK_COTTON.name()};
                    border: none;
                    border-radius: 5px;
                    padding: 5px 10px;
                    color: {MacaronColors.TEXT_DARK.name()};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {MacaronColors.PINK_SAKURA.name()};
                }}
            """)
            self.category_table.setSelectionMode(QTableWidget.ExtendedSelection)
            # 清除所有勾选
            for row in range(self.category_table.rowCount()):
                item = self.category_table.item(row, 0)
                if item:
                    item.setCheckState(Qt.Unchecked)
            self.selected_category_ids.clear()
            self.delete_selected_btn.setEnabled(False)
            self.status_label.setText(f"共 {self.category_table.rowCount()} 个标识")
    
    def _on_selection_changed(self):
        """选择改变事件"""
        if not self.multi_select_btn.isChecked():
            has_selection = len(self.category_table.selectedItems()) > 0
            self.edit_btn.setEnabled(has_selection)
    
    def _delete_selected(self):
        """删除选中的标识"""
        if not self.selected_category_ids:
            QMessageBox.information(self, "提示", "请先勾选要删除的标识")
            return
        
        # 检查是否有记录关联
        categories_with_records = []
        categories_without_records = []
        
        for category_id in self.selected_category_ids:
            category = self.category_manager.get_category_by_id(category_id)
            if category:
                # 获取该标识的记录数
                stats = self.category_manager.get_category_stats()
                for stat in stats:
                    if stat['id'] == category_id:
                        if stat['record_count'] > 0:
                            categories_with_records.append(category['name'])
                        else:
                            categories_without_records.append(category['name'])
                        break
        
        warning_msg = f"确定要删除选中的 {len(self.selected_category_ids)} 个标识吗？\n\n"
        warning_msg += f"📊 统计信息：\n"
        warning_msg += f"• 有记录的标识（将被禁用）：{len(categories_with_records)} 个\n"
        warning_msg += f"• 无记录的标识（将永久删除）：{len(categories_without_records)} 个\n\n"
        
        if categories_with_records:
            warning_msg += f"⚠️ 以下标识有关联记录，将被禁用：\n"
            for i, name in enumerate(categories_with_records[:10]):
                warning_msg += f"  {i+1}. {name}\n"
            if len(categories_with_records) > 10:
                warning_msg += f"  ...等共 {len(categories_with_records)} 个\n"
        
        reply = QMessageBox.question(
            self, "确认批量删除",
            warning_msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            disabled_count = 0
            deleted_count = 0
            
            for category_id in self.selected_category_ids:
                if self.category_manager.delete_category(category_id):
                    success_count += 1
                    # 简单判断是禁用还是删除（实际delete_category已处理）
                    category = self.category_manager.get_category_by_id(category_id)
                    if category and category.get('is_active', 1) == 0:
                        disabled_count += 1
                    else:
                        deleted_count += 1
            
            self._load_categories()
            QMessageBox.information(
                self, "批量删除完成", 
                f"成功处理 {success_count} 个标识\n\n"
                f"📊 处理结果：\n"
                f"• 已禁用（有记录）：{disabled_count} 个\n"
                f"• 已删除（无记录）：{deleted_count} 个"
            )

            self.has_changes = True  # 标记有修改
    
    def _clear_all_categories(self):
        """一键清空所有标识"""
        stats = self.category_manager.get_category_stats()
        
        if not stats:
            QMessageBox.information(self, "提示", "当前没有可清空的标识")
            return
        
        # 统计有记录的标识
        categories_with_records = [stat for stat in stats if stat['record_count'] > 0]
        categories_without_records = [stat for stat in stats if stat['record_count'] == 0]
        
        warning_msg = f"确定要清空所有标识吗？\n\n"
        warning_msg += f"📊 统计信息：\n"
        warning_msg += f"• 总标识数：{len(stats)} 个\n"
        warning_msg += f"• 有记录的标识（将被禁用）：{len(categories_with_records)} 个\n"
        warning_msg += f"• 无记录的标识（将永久删除）：{len(categories_without_records)} 个\n\n"
        
        if categories_with_records:
            warning_msg += f"⚠️ 有记录的标识示例：\n"
            for i, stat in enumerate(categories_with_records[:5]):
                warning_msg += f"  {i+1}. {stat['name']}（{stat['record_count']}条记录）\n"
            if len(categories_with_records) > 5:
                warning_msg += f"  ...等共 {len(categories_with_records)} 个\n"
        
        warning_msg += f"\n此操作不可撤销！"
        
        reply = QMessageBox.question(
            self, "确认清空所有标识",
            warning_msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for stat in stats:
                if self.category_manager.delete_category(stat['id']):
                    success_count += 1
            
            self._load_categories()
            QMessageBox.information(
                self, "清空完成", 
                f"成功处理 {success_count} 个标识\n\n"
                f"📊 处理结果：\n"
                f"• 已禁用（有记录）：{len(categories_with_records)} 个\n"
                f"• 已删除（无记录）：{len(categories_without_records)} 个"
            )
            
            self.has_changes = True  # 标记有修改
    
    def _show_reset_menu(self):
        """显示恢复默认菜单"""
        self.reset_menu.exec(self.reset_btn.mapToGlobal(
            QPoint(0, self.reset_btn.height())
        ))
    
    def _reset_to_default(self, scheme: str):
        """恢复到默认标识方案"""
        schemes = {
            "basic": [
                ("默认", "默认分类", MacaronColors.GREEN_MINT),
                ("工作", "工作相关记录", MacaronColors.BLUE_SKY),
                ("生活", "日常生活记录", MacaronColors.GREEN_APPLE),
                ("学习", "学习进度记录", MacaronColors.PURPLE_LAVENDER),
                ("运动", "运动健康记录", MacaronColors.ORANGE_PEACH),
                ("娱乐", "娱乐休闲记录", MacaronColors.YELLOW_LEMON),
                ("其他", "其他记录", MacaronColors.NEUTRAL_CARAMEL),
            ],
            "work_life": [
                ("工作", "工作相关记录", MacaronColors.BLUE_SKY),
                ("会议", "会议记录", MacaronColors.BLUE_MIST),
                ("项目", "项目进度", MacaronColors.BLUE_PERIWINKLE),
                ("任务", "任务清单", MacaronColors.BLUE_LAVENDER),
                ("报告", "工作报告", MacaronColors.PINK_SAKURA),
                ("客户", "客户沟通", MacaronColors.PINK_BALLET),
                ("生活", "日常生活记录", MacaronColors.GREEN_APPLE),
                ("家务", "家务劳动", MacaronColors.NEUTRAL_CARAMEL),
                ("购物", "购物清单", MacaronColors.NEUTRAL_CREAM),
                ("财务", "财务管理", MacaronColors.NEUTRAL_MOCHA),
                ("家庭", "家庭事务", MacaronColors.PINK_COTTON),
            ],
            "study": [
                ("学习", "学习进度记录", MacaronColors.PURPLE_LAVENDER),
                ("读书", "阅读记录", MacaronColors.PURPLE_LAVENDER),
                ("笔记", "学习笔记", MacaronColors.PURPLE_TARO),
                ("课程", "课程学习", MacaronColors.PURPLE_WISTERIA),
                ("考试", "考试准备", MacaronColors.PURPLE_MAUVE),
                ("技能", "技能提升", MacaronColors.NEUTRAL_ALMOND),
                ("编程", "编程开发", MacaronColors.BLUE_PERIWINKLE),
                ("写作", "写作记录", MacaronColors.NEUTRAL_ALMOND),
                ("语言", "语言学习", MacaronColors.GREEN_MINT),
            ],
            "health": [
                ("健康", "健康状况记录", MacaronColors.TEAL_MINT),
                ("运动", "运动健康记录", MacaronColors.ORANGE_PEACH),
                ("跑步", "跑步记录", MacaronColors.ORANGE_PEACH),
                ("健身", "健身训练", MacaronColors.ORANGE_APRICOT),
                ("瑜伽", "瑜伽练习", MacaronColors.YELLOW_CREAM),
                ("饮食", "饮食记录", MacaronColors.ORANGE_APRICOT),
                ("睡眠", "睡眠记录", MacaronColors.GREEN_MINT),
                ("用药", "用药提醒", MacaronColors.GREEN_APPLE),
                ("体检", "体检记录", MacaronColors.GREEN_PISTACHIO),
                ("心理", "心理健康", MacaronColors.GREEN_SAGE),
            ],
            "creative": [
                ("创作", "创意创作", MacaronColors.ORANGE_PEACH),
                ("设计", "设计工作", MacaronColors.PINK_BALLET),
                ("摄影", "摄影记录", MacaronColors.ORANGE_PEACH),
                ("音乐", "音乐欣赏", MacaronColors.PURPLE_TARO),
                ("电影", "观影记录", MacaronColors.PURPLE_LAVENDER),
                ("写作", "写作记录", MacaronColors.NEUTRAL_ALMOND),
                ("绘画", "绘画创作", MacaronColors.PINK_SAKURA),
                ("手工", "手工制作", MacaronColors.YELLOW_CREAM),
                ("烹饪", "烹饪尝试", MacaronColors.GREEN_APPLE),
            ],
            "family": [  # 新增：日常家庭消费方案
                ("家庭消费", "家庭日常消费记录", MacaronColors.PINK_COTTON),
                ("食品采购", "食品、生鲜采购", MacaronColors.GREEN_APPLE),
                ("日用百货", "日常用品、百货", MacaronColors.BLUE_MIST),
                ("服装鞋帽", "服装、鞋子、帽子", MacaronColors.PINK_SAKURA),
                ("电子产品", "电子设备、数码产品", MacaronColors.BLUE_PERIWINKLE),
                ("家居用品", "家具、家居装饰", MacaronColors.NEUTRAL_CARAMEL),
                ("厨房用品", "厨房器具、餐具", MacaronColors.ORANGE_APRICOT),
                ("母婴用品", "母婴相关消费", MacaronColors.PINK_BALLET),
                ("宠物用品", "宠物食品、用品", MacaronColors.YELLOW_CREAM),
                ("美妆个护", "化妆品、个人护理", MacaronColors.PURPLE_LAVENDER),
                ("医疗健康", "药品、医疗服务", MacaronColors.RED_CORAL),
                ("教育支出", "培训、课程费用", MacaronColors.PURPLE_TARO),
                ("交通出行", "交通费用、加油", MacaronColors.BLUE_SKY),
                ("娱乐消费", "电影、KTV等娱乐", MacaronColors.PURPLE_WISTERIA),
                ("餐饮外卖", "外出就餐、外卖", MacaronColors.ORANGE_PEACH),
                ("水电煤气", "生活缴费", MacaronColors.GREEN_PISTACHIO),
                ("通信网络", "话费、网络费", MacaronColors.BLUE_LAVENDER),
                ("保险支出", "各类保险", MacaronColors.NEUTRAL_MOCHA),
                ("礼金红包", "随礼、红包", MacaronColors.RED_WATERMELON),
                ("捐款公益", "慈善捐款", MacaronColors.GREEN_SAGE),
            ],
            "full": [  # 完整方案69项
                ("默认", "默认分类", MacaronColors.GREEN_MINT, 0),
                ("工作", "工作相关记录", MacaronColors.BLUE_SKY, 1),
                ("生活", "日常生活记录", MacaronColors.GREEN_APPLE, 2),
                ("学习", "学习进度记录", MacaronColors.PURPLE_LAVENDER, 3),
                ("运动", "运动健康记录", MacaronColors.ORANGE_PEACH, 4),
                ("娱乐", "娱乐休闲记录", MacaronColors.YELLOW_LEMON, 5),
                ("健康", "健康状况记录", MacaronColors.TEAL_MINT, 6),
                ("饮食", "饮食记录", MacaronColors.ORANGE_APRICOT, 7),
                ("其他", "其他记录", MacaronColors.NEUTRAL_CARAMEL, 8),
                ("会议", "会议记录", MacaronColors.BLUE_MIST, 10),
                ("项目", "项目进度", MacaronColors.BLUE_PERIWINKLE, 11),
                ("任务", "任务清单", MacaronColors.BLUE_LAVENDER, 12),
                ("报告", "工作报告", MacaronColors.PINK_SAKURA, 13),
                ("客户", "客户沟通", MacaronColors.PINK_BALLET, 15),
                ("读书", "阅读记录", MacaronColors.PURPLE_LAVENDER, 20),
                ("笔记", "学习笔记", MacaronColors.PURPLE_TARO, 21),
                ("课程", "课程学习", MacaronColors.PURPLE_WISTERIA, 22),
                ("跑步", "跑步记录", MacaronColors.ORANGE_PEACH, 40),
                ("健身", "健身训练", MacaronColors.ORANGE_APRICOT, 41),
                ("瑜伽", "瑜伽练习", MacaronColors.YELLOW_CREAM, 42),
                ("家务", "家务劳动", MacaronColors.NEUTRAL_CARAMEL, 50),
                ("购物", "购物清单", MacaronColors.NEUTRAL_CREAM, 51),
                ("财务", "财务管理", MacaronColors.NEUTRAL_MOCHA, 52),
                ("电影", "观影记录", MacaronColors.PURPLE_LAVENDER, 60),
                ("音乐", "音乐欣赏", MacaronColors.PURPLE_TARO, 61),
                ("游戏", "游戏时间", MacaronColors.PURPLE_WISTERIA, 62),
                ("早餐", "早餐记录", MacaronColors.YELLOW_LEMON, 70),
                ("午餐", "午餐记录", MacaronColors.YELLOW_CREAM, 71),
                ("晚餐", "晚餐记录", MacaronColors.YELLOW_HONEY, 72),
                ("习惯", "习惯养成", MacaronColors.GREEN_MINT, 80),
                ("目标", "目标追踪", MacaronColors.GREEN_PISTACHIO, 81),
                ("编程", "编程开发", MacaronColors.BLUE_PERIWINKLE, 90),
                ("设计", "设计工作", MacaronColors.PINK_BALLET, 91),
                ("写作", "写作记录", MacaronColors.NEUTRAL_ALMOND, 92),
                ("宠物", "宠物照料", MacaronColors.YELLOW_CREAM, 100),
                ("植物", "植物养护", MacaronColors.GREEN_MINT, 101),
                ("纪念日", "重要纪念", MacaronColors.RED_WATERMELON, 105),
                # 新增家庭消费相关标识 (继续增加至69项)
                ("家庭消费", "家庭日常消费", MacaronColors.PINK_COTTON, 110),
                ("食品采购", "食品生鲜采购", MacaronColors.GREEN_APPLE, 111),
                ("日用百货", "日用品百货", MacaronColors.BLUE_MIST, 112),
                ("服装鞋帽", "服装鞋子帽子", MacaronColors.PINK_SAKURA, 113),
                ("电子产品", "电子数码产品", MacaronColors.BLUE_PERIWINKLE, 114),
                ("家居用品", "家具家居装饰", MacaronColors.NEUTRAL_CARAMEL, 115),
                ("厨房用品", "厨房器具餐具", MacaronColors.ORANGE_APRICOT, 116),
                ("母婴用品", "母婴相关消费", MacaronColors.PINK_BALLET, 117),
                ("宠物用品", "宠物食品用品", MacaronColors.YELLOW_CREAM, 118),
                ("美妆个护", "化妆品护理", MacaronColors.PURPLE_LAVENDER, 119),
                ("医疗健康", "药品医疗服务", MacaronColors.RED_CORAL, 120),
                ("教育支出", "培训课程费用", MacaronColors.PURPLE_TARO, 121),
                ("交通出行", "交通加油费用", MacaronColors.BLUE_SKY, 122),
                ("娱乐消费", "电影KTV娱乐", MacaronColors.PURPLE_WISTERIA, 123),
                ("餐饮外卖", "外出就餐外卖", MacaronColors.ORANGE_PEACH, 124),
                ("水电煤气", "生活缴费", MacaronColors.GREEN_PISTACHIO, 125),
                ("通信网络", "话费网络费", MacaronColors.BLUE_LAVENDER, 126),
                ("保险支出", "各类保险", MacaronColors.NEUTRAL_MOCHA, 127),
                ("礼金红包", "随礼红包", MacaronColors.RED_WATERMELON, 128),
                ("捐款公益", "慈善捐款", MacaronColors.GREEN_SAGE, 129),
                ("旅游度假", "旅游出行度假", MacaronColors.YELLOW_LEMON, 130),
                ("汽车养护", "汽车保养维修", MacaronColors.BLUE_MIST, 131),
                ("房屋维修", "房屋装修维修", MacaronColors.NEUTRAL_CARAMEL, 132),
                ("节日礼物", "节日送礼礼物", MacaronColors.PINK_ROSE, 133),
                ("书籍购买", "购买书籍", MacaronColors.PURPLE_LAVENDER, 134),
                ("办公用品", "办公文具用品", MacaronColors.GREEN_SAGE, 135),
                ("运动装备", "运动器材装备", MacaronColors.ORANGE_PEACH, 136),
                ("化妆品", "化妆品购买", MacaronColors.PINK_SAKURA, 137),
                ("保健品", "保健品购买", MacaronColors.GREEN_MINT, 138),
                ("儿童用品", "儿童相关用品", MacaronColors.PINK_BALLET, 139),
                ("老人用品", "老人相关用品", MacaronColors.NEUTRAL_ALMOND, 140),
            ]
        }
        
        selected_scheme = schemes.get(scheme, schemes["basic"])
        
        # 方案名称映射
        scheme_names = {
            "basic": "基础方案（简约）",
            "work_life": "工作生活方案",
            "study": "学习成长方案",
            "health": "健康运动方案",
            "creative": "创意创作方案",
            "family": "家庭消费方案",
            "full": "完整方案（69项）"
        }
        
        # 统计当前已存在的标识
        conn = self.category_manager.db_pool.get_connection(self.category_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE is_active = 1")
        existing_categories = {row[0] for row in cursor.fetchall()}
        
        # 统计将添加的标识
        to_add = []
        already_exists = []
        
        for item in selected_scheme:
            name = item[0]
            if name in existing_categories:
                already_exists.append(name)
            else:
                to_add.append(name)
        
        info_msg = f"确定要恢复到 {scheme_names.get(scheme, '默认')} 吗？\n\n"
        info_msg += f"📊 方案统计：\n"
        info_msg += f"• 方案总标识数：{len(selected_scheme)} 个\n"
        info_msg += f"• 将新增标识：{len(to_add)} 个\n"
        info_msg += f"• 已存在标识：{len(already_exists)} 个\n\n"
        
        if to_add:
            info_msg += f"✨ 将新增的标识：\n"
            for i, name in enumerate(to_add[:10]):
                info_msg += f"  {i+1}. {name}\n"
            if len(to_add) > 10:
                info_msg += f"  ...等共 {len(to_add)} 个\n"
        
        info_msg += f"\n⚠️ 注意：不会删除现有标识，只会添加不存在的标识"
        
        reply = QMessageBox.question(
            self, "确认恢复默认",
            info_msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            exist_count = 0
            failed_count = 0
            
            for item in selected_scheme:
                name = item[0]
                desc = item[1]
                color_obj = item[2]
                sort_order = item[3] if len(item) > 3 else 0
                
                try:
                    # 检查是否已存在
                    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
                    if cursor.fetchone():
                        exist_count += 1
                        continue
                    
                    if self.category_manager.add_category(
                        name=name,
                        description=desc,
                        color=color_obj.name(),
                        sort_order=sort_order
                    ):
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"添加标识 {name} 失败: {e}")
                    failed_count += 1
            
            self._load_categories()
            
            result_msg = f"恢复默认方案完成！\n\n"
            result_msg += f"📊 处理结果：\n"
            result_msg += f"• 成功新增：{success_count} 个\n"
            result_msg += f"• 已存在：{exist_count} 个\n"
            result_msg += f"• 添加失败：{failed_count} 个"
            
            QMessageBox.information(self, "恢复完成", result_msg)
    
    def _add_category(self):
        """添加标识"""
        dialog = CategoryEditDialog(self.category_manager, parent=self)
        if dialog.exec():
            self._load_categories()
            self.status_label.setText("✅ 标识添加成功")
            self.has_changes = True  # 标记有修改
    
    def _edit_category(self, category_id=None):
        """编辑标识"""
        if category_id is None:
            current_row = self.category_table.currentRow()
            if current_row >= 0:
                category_id = int(self.category_table.item(current_row, 1).text())
        
        if category_id:
            dialog = CategoryEditDialog(self.category_manager, category_id, parent=self)
            if dialog.exec():
                self._load_categories()
                self.status_label.setText("✅ 标识更新成功")
                self.has_changes = True  # 标记有修改
    
    def _delete_category(self, category_id=None):
        """删除单个标识"""
        if category_id is None:
            current_row = self.category_table.currentRow()
            if current_row >= 0:
                category_id = int(self.category_table.item(current_row, 1).text())
        
        if category_id:
            category = self.category_manager.get_category_by_id(category_id)
            if category:
                # 获取该标识的记录数
                record_count = 0
                stats = self.category_manager.get_category_stats()
                for stat in stats:
                    if stat['id'] == category_id:
                        record_count = stat['record_count']
                        break
                
                if record_count > 0:
                    msg = f"标识 '{category['name']}' 有 {record_count} 条关联记录\n"
                    msg += f"删除后将禁用该标识（记录仍保留）"
                else:
                    msg = f"确定要永久删除标识 '{category['name']}' 吗？"
                
                reply = QMessageBox.question(
                    self, "确认删除",
                    msg,
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    if self.category_manager.delete_category(category_id):
                        self._load_categories()
                        self.status_label.setText(f"✅ 标识 '{category['name']}' 删除成功")
                        self.has_changes = True  # 标记有修改
                    else:
                        QMessageBox.critical(self, "错误", "标识删除失败")


class CategoryEditDialog(QDialog):
    """标识编辑对话框"""
    
    def __init__(self, category_manager: CategoryManager, category_id: int = None, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.category_id = category_id
        
        if category_id:
            self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 编辑标识")
        else:
            self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 添加标识")
        
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QLineEdit, QTextEdit, QSpinBox {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
            QTextEdit {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {MacaronColors.GREEN_MINT.name()};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        
        self._setup_ui()
        
        if category_id:
            self._load_category()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入标识名称")
        form_layout.addRow("标识名称:", self.name_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("请输入标识描述（可选）")
        self.desc_edit.setMaximumHeight(80)
        form_layout.addRow("描述:", self.desc_edit)
        
        color_layout = QHBoxLayout()
        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("#RRGGBB")
        self.color_edit.setMaxLength(7)
        
        self.random_color_btn = QPushButton("🎨 随机")
        self.random_color_btn.clicked.connect(self._select_random_color)
        
        self.color_btn = QPushButton("选择颜色")
        self.color_btn.clicked.connect(self._select_color)
        
        color_layout.addWidget(self.color_edit)
        color_layout.addWidget(self.random_color_btn)
        color_layout.addWidget(self.color_btn)
        form_layout.addRow("颜色:", color_layout)
        
        self.sort_spin = QSpinBox()
        self.sort_spin.setRange(0, 999)
        self.sort_spin.setValue(0)
        form_layout.addRow("排序:", self.sort_spin)
        
        layout.addLayout(form_layout)
        
        preview_group = QGroupBox("预览")
        preview_layout = QHBoxLayout(preview_group)
        
        self.preview_label = QLabel("示例标识")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.name_edit.textChanged.connect(self._update_preview)
        self.color_edit.textChanged.connect(self._update_preview)
        
        self._select_random_color()
    
    def _load_category(self):
        """加载标识数据"""
        category = self.category_manager.get_category_by_id(self.category_id)
        if category:
            self.name_edit.setText(category['name'])
            self.desc_edit.setText(category.get('description', ''))
            self.color_edit.setText(category.get('color', MacaronColors.GREEN_MINT.name()))
            self.sort_spin.setValue(category.get('sort_order', 0))
            self._update_preview()
    
    def _update_preview(self):
        """更新预览"""
        name = self.name_edit.text().strip() or "示例标识"
        color = self.color_edit.text().strip()
        
        if not color or not color.startswith('#') or len(color) != 7:
            color = MacaronColors.GREEN_MINT.name()
        
        # 根据背景色自动选择合适的文字颜色
        bg_color = QColor(color)
        text_color = MacaronColors.get_text_color(bg_color)
        
        self.preview_label.setText(name)
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                background-color: {color};
                color: {text_color.name()};
            }}
        """)
    
    def _select_color(self):
        """选择颜色"""
        from PySide6.QtWidgets import QColorDialog
        current_color = QColor(self.color_edit.text() if self.color_edit.text() else MacaronColors.GREEN_MINT.name())
        color = QColorDialog.getColor(current_color)
        if color.isValid():
            self.color_edit.setText(color.name())
    
    def _select_random_color(self):
        """随机选择马卡龙颜色"""
        import random
        color_list = MacaronColors.get_color_list()
        random_color = random.choice(color_list)
        self.color_edit.setText(random_color.name())
    
    def accept(self):
        """确认"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "标识名称不能为空")
            return
        
        color = self.color_edit.text().strip()
        if not color.startswith('#') or len(color) != 7:
            QMessageBox.warning(self, "警告", "颜色格式不正确，应为 #RRGGBB 格式")
            return
        
        try:
            if self.category_id:
                self.category_manager.update_category(
                    self.category_id,
                    name=name,
                    description=self.desc_edit.toPlainText(),
                    color=color,
                    sort_order=self.sort_spin.value()
                )
            else:
                self.category_manager.add_category(
                    name=name,
                    description=self.desc_edit.toPlainText(),
                    color=color,
                    sort_order=self.sort_spin.value()
                )
            
            super().accept()
        except ValueError as e:
            QMessageBox.warning(self, "警告", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败：{e}")

# ==================== 新增标识统计类 ====================
class CategoryStats:
    """标识统计信息类"""
    
    def __init__(self, category: str, last_record: Dict[str, Any] = None):
        self.category = category
        self.last_record = last_record
        self.interval_seconds = 0
        self.interval_display = "-"
        self.record_count = 0
        
    def update_interval(self, current_record: Dict[str, Any]):
        """更新时间间隔"""
        if self.last_record and current_record:
            try:
                last_dt = datetime.datetime.strptime(
                    f"{self.last_record['record_date']} {self.last_record['record_time']}",
                    "%Y-%m-%d %H:%M:%S"
                )
                current_dt = datetime.datetime.strptime(
                    f"{current_record['record_date']} {current_record['record_time']}",
                    "%Y-%m-%d %H:%M:%S"
                )
                
                self.interval_seconds = (current_dt - last_dt).total_seconds()
                self.interval_display = self._format_interval(self.interval_seconds)
                
            except Exception as e:
                print(f"计算时间间隔失败: {e}")
                self.interval_seconds = 0
                self.interval_display = "-"
    
    def _format_interval(self, seconds: float) -> str:
        """格式化时间间隔显示"""
        if seconds < 0:
            return "时间异常"
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if secs > 0 or not parts:
            parts.append(f"{secs}秒")
        
        return " ".join(parts)

class DatabaseBackupManager:
    """数据库备份管理器类"""
    
    def __init__(self, user_manager: UserManager, user_id: int):
        self.user_manager = user_manager
        self.user_id = user_id
        self.backup_dir = Path.cwd() / "backups" / str(user_id)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.max_backups = 30
        self.last_backup_time = 0  # 记录上次备份耗时
        self._load_settings()
        
    def _load_settings(self):
        """加载备份设置"""
        settings = self.user_manager.get_user_settings(self.user_id)
        self.max_backups = settings.get("max_backups", 30)
    
    def save_settings(self):
        """保存备份设置"""
        settings = self.user_manager.get_user_settings(self.user_id)
        settings["max_backups"] = self.max_backups
        self.user_manager.save_user_settings(self.user_id, settings)
    
    def create_backup(self, backup_type: str = "manual") -> Optional[Path]:
        """创建备份（优化版）"""
        try:
            # 获取用户数据库文件路径
            conn = self.user_manager.db_pool.get_connection(
                str(self.user_manager.users_db_path)
            )
            cursor = conn.cursor()
            cursor.execute("SELECT db_file FROM users WHERE id = ?", (self.user_id,))
            result = cursor.fetchone()
            if not result:
                return None
            
            db_file = Path.cwd() / ".scheduling_system" / result[0]
            if not db_file.exists():
                return None
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{backup_type}_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            # 使用 WAL 模式进行快速备份（不创建新连接）
            import shutil
            start_time = time.time()
            
            # 直接复制文件（SQLite 在 WAL 模式下支持热备份）
            shutil.copy2(db_file, backup_path)
            
            # 如果数据库启用了 WAL，同时复制 -wal 和 -shm 文件
            if (db_file.with_suffix('.db-wal').exists()):
                shutil.copy2(db_file.with_suffix('.db-wal'), 
                            backup_path.with_suffix('.db-wal'))
            if (db_file.with_suffix('.db-shm').exists()):
                shutil.copy2(db_file.with_suffix('.db-shm'), 
                            backup_path.with_suffix('.db-shm'))
            
            elapsed = time.time() - start_time
            self.last_backup_time = elapsed
            print(f"备份完成，耗时: {elapsed:.3f}秒")
            
            # 保存备份信息
            info = {
                "backup_type": backup_type,
                "created_at": timestamp,
                "source_file": str(db_file),
                "file_size": backup_path.stat().st_size,
                "database_version": DATABASE_VERSION,
                "backup_time_ms": int(elapsed * 1000)
            }
            
            info_path = backup_path.with_suffix(".json")
            with open(info_path, "w", encoding="utf-8") as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            
            self._cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            print(f"创建备份失败: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """清理旧备份"""
        backups = self.get_all_backups()
        if len(backups) > self.max_backups:
            backups.sort(key=lambda x: x["created_at"])
            for backup in backups[:-self.max_backups]:
                try:
                    backup["path"].unlink()
                    info_path = backup["path"].with_suffix(".json")
                    if info_path.exists():
                        info_path.unlink()
                except Exception as e:
                    print(f"删除旧备份失败: {e}")
    
    def get_all_backups(self) -> List[Dict[str, Any]]:
        """获取所有备份"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.db"):
            if backup_file.is_file():
                info_path = backup_file.with_suffix(".json")
                backup_info = {
                    "path": backup_file,
                    "filename": backup_file.name,
                    "file_size": backup_file.stat().st_size,
                    "created_at": None,
                    "backup_type": "unknown"
                }
                
                if info_path.exists():
                    try:
                        with open(info_path, "r", encoding="utf-8") as f:
                            info = json.load(f)
                            backup_info.update(info)
                    except Exception as e:
                        print(f"读取备份信息失败: {e}")
                
                if backup_info["created_at"] is None:
                    parts = backup_file.stem.split("_")
                    if len(parts) >= 2:
                        backup_info["created_at"] = parts[1]
                        backup_info["backup_type"] = parts[0]
                
                backups.append(backup_info)
        
        return backups
    
    def restore_backup(self, backup_path: Path) -> bool:
        """恢复备份（修复版）"""
        try:
            conn = self.user_manager.db_pool.get_connection(
                str(self.user_manager.users_db_path)
            )
            cursor = conn.cursor()
            cursor.execute("SELECT db_file FROM users WHERE id = ?", (self.user_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            db_file = Path.cwd() / ".scheduling_system" / result[0]
            
            # 创建回滚备份
            rollback_backup = self.create_backup("rollback")
            
            # 只关闭当前用户的连接，而不是全部连接
            self.user_manager.db_pool.close_connection(str(db_file))
            
            # 短暂延迟确保文件句柄释放
            time.sleep(0.1)
            
            # 复制备份文件
            shutil.copy2(backup_path, db_file)
            
            # 如果存在 WAL 文件也一并复制
            if backup_path.with_suffix('.db-wal').exists():
                shutil.copy2(backup_path.with_suffix('.db-wal'), 
                            db_file.with_suffix('.db-wal'))
            if backup_path.with_suffix('.db-shm').exists():
                shutil.copy2(backup_path.with_suffix('.db-shm'), 
                            db_file.with_suffix('.db-shm'))
            
            return True
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def get_backup_info(self, backup_path: Path) -> Dict[str, Any]:
        """获取备份详细信息"""
        info = {
            "path": backup_path,
            "file_size": backup_path.stat().st_size,
            "created_at": None,
            "backup_type": "unknown",
            "date_range": None,
            "record_count": 0
        }
        
        info_path = backup_path.with_suffix(".json")
        if info_path.exists():
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    info.update(json.load(f))
            except Exception as e:
                print(f"读取备份信息失败: {e}")
        
        try:
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM scheduling_records")
            info["record_count"] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT MIN(record_date), MAX(record_date) 
                FROM scheduling_records
            """)
            result = cursor.fetchone()
            if result[0] and result[1]:
                info["date_range"] = f"{result[0]} 至 {result[1]}"
            
            conn.close()
        except Exception as e:
            print(f"分析备份文件失败: {e}")
        
        return info

class SearchHelper:
    """搜索辅助类，支持拼音搜索"""
    
    @staticmethod
    def chinese_to_pinyin(text: str) -> str:
        """中文转拼音"""
        return ''.join(pypinyin.lazy_pinyin(text))
    
    @staticmethod
    def chinese_to_pinyin_first_letter(text: str) -> str:
        """中文转拼音首字母"""
        return ''.join([item[0][0] for item in pypinyin.pinyin(text, style=pypinyin.Style.FIRST_LETTER)])
    
    @staticmethod
    def match_keyword(text: str, keyword: str) -> bool:
        """匹配关键词（支持中文、拼音、拼音首字母）"""
        if not keyword:
            return True
        
        keyword = keyword.lower().strip()
        if not keyword:
            return True
        
        if keyword in text.lower():
            return True
        
        pinyin = SearchHelper.chinese_to_pinyin(text)
        if keyword in pinyin.lower():
            return True
        
        first_letter = SearchHelper.chinese_to_pinyin_first_letter(text)
        if keyword in first_letter.lower():
            return True
        
        return False

class UserSelectionDialog(QDialog):
    """用户选择对话框"""
    
    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.selected_user_id = None
        self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 选择用户")
        self.setModal(True)
        self.setMinimumSize(400, 500)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QPushButton:disabled {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                color: {MacaronColors.TEXT_MUTED.name()};
            }}
            QListWidget {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                color: {MacaronColors.TEXT_DARK.name()};
                border-radius: 3px;
            }}
            QListWidget::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QListWidget::item:hover {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
        """)
        
        self._setup_ui()
        self._load_users()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        title_label = QLabel("👤 请选择用户")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {MacaronColors.TEXT_DARK.name()};
            padding: 10px;
            background-color: {MacaronColors.GREEN_MINT.name()};
            border-radius: 8px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.user_list = QListWidget()
        self.user_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.user_list)
        
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("登录")
        self.select_btn.clicked.connect(self.accept)
        
        self.add_btn = QPushButton("添加用户")
        self.add_btn.clicked.connect(self._add_user)
        
        self.edit_btn = QPushButton("编辑用户")
        self.edit_btn.clicked.connect(self._edit_user)
        
        self.delete_btn = QPushButton("删除用户")
        self.delete_btn.clicked.connect(self._delete_user)
        
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
    
    def _load_users(self):
        """加载用户列表"""
        self.user_list.clear()
        users = self.user_manager.get_all_users()
        
        for user in users:
            item = QListWidgetItem(f"👤 {user['display_name']} ({user['username']})")
            item.setData(Qt.UserRole, user['id'])
            
            color_list = [MacaronColors.BLUE_SKY, MacaronColors.GREEN_MINT, 
                         MacaronColors.PURPLE_LAVENDER, MacaronColors.YELLOW_LEMON,
                         MacaronColors.ORANGE_PEACH]
            import random
            color = random.choice(color_list)
            item.setForeground(QBrush(color))
            
            self.user_list.addItem(item)
    
    def _add_user(self):
        """添加用户"""
        dialog = UserEditDialog(self.user_manager, parent=self)
        if dialog.exec():
            self._load_users()
    
    def _edit_user(self):
        """编辑用户"""
        current_item = self.user_list.currentItem()
        if current_item:
            user_id = current_item.data(Qt.UserRole)
            dialog = UserEditDialog(self.user_manager, user_id, parent=self)
            if dialog.exec():
                self._load_users()
    
    def _delete_user(self):
        """删除用户"""
        current_item = self.user_list.currentItem()
        if current_item:
            user_id = current_item.data(Qt.UserRole)
            user_name = current_item.text()
            
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除用户 {user_name} 吗？\n该用户的所有数据将被永久删除！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.user_manager.delete_user(user_id):
                    self._load_users()
                    QMessageBox.information(self, "成功", "用户删除成功")
                else:
                    QMessageBox.critical(self, "错误", "用户删除失败")
    
    def get_selected_user_id(self):
        """获取选中的用户ID"""
        current_item = self.user_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None

class UserEditDialog(QDialog):
    """用户编辑对话框"""
    
    def __init__(self, user_manager: UserManager, user_id: int = None, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.user_id = user_id
    
        if user_id:
            self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 编辑用户")
        else:
            self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 添加用户")
        
        self.setModal(True)
        self.setMinimumWidth(300)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QLineEdit {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
        """)
        
        self._setup_ui()
        
        if user_id:
            self._load_user_data()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QFormLayout(self)
        layout.setSpacing(10)
        
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("请输入显示名称")
        layout.addRow("显示名称:", self.display_name_edit)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名（可选）")
        layout.addRow("用户名:", self.username_edit)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def _load_user_data(self):
        """加载用户数据"""
        users = self.user_manager.get_all_users()
        for user in users:
            if user['id'] == self.user_id:
                self.display_name_edit.setText(user['display_name'])
                self.username_edit.setText(user['username'])
                break
    
    def accept(self):
        """确认"""
        display_name = self.display_name_edit.text().strip()
        if not display_name:
            QMessageBox.warning(self, "警告", "显示名称不能为空")
            return
        
        username = self.username_edit.text().strip() or None
        
        if self.user_id:
            if self.user_manager.update_user(self.user_id, display_name, username):
                super().accept()
            else:
                QMessageBox.critical(self, "错误", "更新用户失败")
        else:
            if self.user_manager.add_user(display_name, username):
                super().accept()
            else:
                QMessageBox.critical(self, "错误", "添加用户失败")

class BackupRestoreDialog(QDialog):
    """备份恢复对话框"""
    
    def __init__(self, backup_manager: DatabaseBackupManager, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 数据库备份与恢复")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QPushButton:disabled {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                color: {MacaronColors.TEXT_MUTED.name()};
            }}
            QTableWidget {{
                background-color: white;
                alternate-background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                gridline-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
            }}
            QTableWidget::item {{
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QTableWidget::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QHeaderView::section {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                padding: 5px;
                border: none;
                font-weight: bold;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {MacaronColors.GREEN_MINT.name()};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QDateEdit, QComboBox {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                selection-color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        
        self._setup_ui()
        self._load_backups()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        toolbar_layout = QHBoxLayout()
        
        self.backup_btn = QPushButton("💾 手动备份")
        self.backup_btn.clicked.connect(self._manual_backup)
        toolbar_layout.addWidget(self.backup_btn)
        
        toolbar_layout.addStretch()
        
        filter_group = QGroupBox("筛选")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("备份类型:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["全部", "自动", "手动", "回滚"])
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("时间范围:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.dateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("至"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.end_date)
        
        self.apply_filter_btn = QPushButton("应用筛选")
        self.apply_filter_btn.clicked.connect(self._apply_filters)
        filter_layout.addWidget(self.apply_filter_btn)
        
        self.clear_filter_btn = QPushButton("清除筛选")
        self.clear_filter_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(self.clear_filter_btn)
        
        toolbar_layout.addWidget(filter_group)
        
        layout.addLayout(toolbar_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("📋 备份列表:"))
        
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(5)
        self.backup_table.setHorizontalHeaderLabels([
            "备份时间", "备份类型", "文件大小", "记录数", "操作"
        ])
        self.backup_table.horizontalHeader().setStretchLastSection(True)
        self.backup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.backup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.itemSelectionChanged.connect(self._on_backup_selected)
        left_layout.addWidget(self.backup_table)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        info_group = QGroupBox("备份信息")
        info_layout = QFormLayout(info_group)
        
        self.info_filename = QLabel("-")
        info_layout.addRow("文件名:", self.info_filename)
        
        self.info_type = QLabel("-")
        info_layout.addRow("备份类型:", self.info_type)
        
        self.info_time = QLabel("-")
        info_layout.addRow("备份时间:", self.info_time)
        
        self.info_size = QLabel("-")
        info_layout.addRow("文件大小:", self.info_size)
        
        self.info_records = QLabel("-")
        info_layout.addRow("记录数量:", self.info_records)
        
        self.info_daterange = QLabel("-")
        info_layout.addRow("日期范围:", self.info_daterange)
        
        self.info_version = QLabel("-")
        info_layout.addRow("数据库版本:", self.info_version)
        
        right_layout.addWidget(info_group)
        
        button_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton("🔄 恢复此备份")
        self.restore_btn.clicked.connect(self._restore_backup)
        self.restore_btn.setEnabled(False)
        button_layout.addWidget(self.restore_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除备份")
        self.delete_btn.clicked.connect(self._delete_backup)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        right_layout.addLayout(button_layout)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 300])
        
        layout.addWidget(splitter, 1)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_btn)
        
        layout.addLayout(bottom_layout)
    
    def _load_backups(self):
        """加载备份列表（修复版）"""
        backups = self.backup_manager.get_all_backups()
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        self.backup_table.setRowCount(len(backups))
        self.backup_table.setColumnCount(5)
        
        for row, backup in enumerate(backups):
            # 备份时间 - 创建新的 item
            time_text = backup.get("created_at", "-")
            time_item = QTableWidgetItem(time_text)
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setData(Qt.UserRole, str(backup["path"]))  # 存储路径
            self.backup_table.setItem(row, 0, time_item)
            
            # 备份类型 - 创建新的 item
            type_map = {
                "auto": "自动",
                "manual": "手动",
                "rollback": "回滚",
                "unknown": "未知"
            }
            type_text = type_map.get(backup.get("backup_type", "unknown"), "未知")
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)
            
            if type_text == "自动":
                type_item.setForeground(QBrush(MacaronColors.TEXT_SUCCESS))
            elif type_text == "手动":
                type_item.setForeground(QBrush(MacaronColors.TEXT_INFO))
            elif type_text == "回滚":
                type_item.setForeground(QBrush(MacaronColors.TEXT_WARNING))
            
            self.backup_table.setItem(row, 1, type_item)
            
            # 文件大小 - 创建新的 item
            size = backup.get("file_size", 0)
            if size < 1024:
                size_text = f"{size} B"
            elif size < 1024 * 1024:
                size_text = f"{size / 1024:.2f} KB"
            else:
                size_text = f"{size / (1024 * 1024):.2f} MB"
            size_item = QTableWidgetItem(size_text)
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.backup_table.setItem(row, 2, size_item)
            
            # 记录数 - 创建新的 item
            records_item = QTableWidgetItem(str(backup.get("record_count", "-")))
            records_item.setTextAlignment(Qt.AlignCenter)
            self.backup_table.setItem(row, 3, records_item)
            
            # 操作按钮（这里保持使用 cell widget）
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)
            
            view_btn = QPushButton("查看")
            view_btn.setProperty("backup_path", str(backup["path"]))
            view_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MacaronColors.BLUE_MIST.name()};
                    border: none;
                    border-radius: 3px;
                    padding: 3px 5px;
                    color: {MacaronColors.TEXT_DARK.name()};
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {MacaronColors.BLUE_SKY.name()};
                }}
            """)
            view_btn.clicked.connect(lambda checked, p=backup["path"]: self._view_backup(p))
            btn_layout.addWidget(view_btn)
            
            restore_btn = QPushButton("恢复")
            restore_btn.setProperty("backup_path", str(backup["path"]))
            restore_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MacaronColors.GREEN_APPLE.name()};
                    border: none;
                    border-radius: 3px;
                    padding: 3px 5px;
                    color: {MacaronColors.TEXT_DARK.name()};
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {MacaronColors.GREEN_MINT.name()};
                }}
            """)
            restore_btn.clicked.connect(lambda checked, p=backup["path"]: self._restore_backup(p))
            btn_layout.addWidget(restore_btn)
            
            btn_widget.setLayout(btn_layout)
            self.backup_table.setCellWidget(row, 4, btn_widget)
        
        # 设置列宽
        self.backup_table.setColumnWidth(0, 150)  # 备份时间
        self.backup_table.setColumnWidth(1, 80)   # 备份类型
        self.backup_table.setColumnWidth(2, 100)  # 文件大小
        self.backup_table.setColumnWidth(3, 80)   # 记录数
        self.backup_table.horizontalHeader().setStretchLastSection(True)  # 操作列自动拉伸
    
    def _apply_filters(self):
        """应用筛选"""
        backup_type = self.type_filter.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        for row in range(self.backup_table.rowCount()):
            show_row = True
            
            if backup_type != "全部":
                type_item = self.backup_table.item(row, 1)
                if type_item and type_item.text() != backup_type:
                    show_row = False
            
            if show_row:
                time_item = self.backup_table.item(row, 0)
                if time_item:
                    backup_time = time_item.text()[:10]
                    if backup_time < start_date or backup_time > end_date:
                        show_row = False
            
            self.backup_table.setRowHidden(row, not show_row)
    
    def _clear_filters(self):
        """清除筛选"""
        self.type_filter.setCurrentText("全部")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        
        for row in range(self.backup_table.rowCount()):
            self.backup_table.setRowHidden(row, False)
    
    def _on_backup_selected(self):
        """备份选择事件"""
        current_row = self.backup_table.currentRow()
        if current_row >= 0:
            backup_path = self.backup_table.item(current_row, 0).data(Qt.UserRole)
            if backup_path:
                self._show_backup_info(Path(backup_path))
                self.restore_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                return
        
        self.restore_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self._clear_info()
    
    def _clear_info(self):
        """清除信息显示"""
        self.info_filename.setText("-")
        self.info_type.setText("-")
        self.info_time.setText("-")
        self.info_size.setText("-")
        self.info_records.setText("-")
        self.info_daterange.setText("-")
        self.info_version.setText("-")
    
    def _show_backup_info(self, backup_path: Path):
        """显示备份信息"""
        info = self.backup_manager.get_backup_info(backup_path)
        
        self.info_filename.setText(backup_path.name)
        
        type_map = {
            "auto": "自动",
            "manual": "手动",
            "rollback": "回滚",
            "unknown": "未知"
        }
        self.info_type.setText(type_map.get(info.get("backup_type", "unknown"), "未知"))
        
        self.info_time.setText(info.get("created_at", "-"))
        
        size = info.get("file_size", 0)
        if size < 1024:
            size_text = f"{size} B"
        elif size < 1024 * 1024:
            size_text = f"{size / 1024:.2f} KB"
        else:
            size_text = f"{size / (1024 * 1024):.2f} MB"
        self.info_size.setText(size_text)
        
        self.info_records.setText(str(info.get("record_count", "-")))
        self.info_daterange.setText(info.get("date_range", "-"))
        self.info_version.setText(info.get("database_version", "-"))
    
    def _manual_backup(self):
        """手动备份（修复版）"""
        if not self.backup_manager:
            return
        
        # 显示进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 忙碌状态
        QCoreApplication.processEvents()  # 强制更新UI
        
        try:
            # 直接执行备份，不创建线程
            backup_path = self.backup_manager.create_backup("manual")
            
            # 隐藏进度条
            self.progress_bar.setVisible(False)
            
            if backup_path:
                # 获取文件大小
                file_size = backup_path.stat().st_size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                
                QMessageBox.information(
                    self, "成功", 
                    f"✅ 备份创建成功\n"
                    f"文件：{backup_path.name}\n"
                    f"大小：{size_str}\n"
                    f"耗时：{self.backup_manager.last_backup_time:.3f} 秒"
                )
                self._load_backups()
            else:
                QMessageBox.critical(self, "错误", "❌ 备份创建失败")
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "错误", f"备份失败：{e}")
    
    def _view_backup(self, backup_path: Path):
        """查看备份"""
        self._show_backup_info(backup_path)
    
    def _restore_backup(self, backup_path: Path = None):
        """恢复备份"""
        if backup_path is None:
            current_row = self.backup_table.currentRow()
            if current_row >= 0:
                backup_path = Path(self.backup_table.item(current_row, 0).data(Qt.UserRole))
        
        if backup_path:
            reply = QMessageBox.question(
                self, "确认恢复",
                f"确定要恢复备份 {backup_path.name} 吗？\n"
                "当前数据将被备份为回滚点。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.backup_manager.restore_backup(backup_path):
                    QMessageBox.information(self, "成功", "数据库恢复成功")
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", "数据库恢复失败")
    
    def _delete_backup(self):
        """删除备份"""
        current_row = self.backup_table.currentRow()
        if current_row >= 0:
            backup_path = Path(self.backup_table.item(current_row, 0).data(Qt.UserRole))
            
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除备份 {backup_path.name} 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    backup_path.unlink()
                    info_path = backup_path.with_suffix(".json")
                    if info_path.exists():
                        info_path.unlink()
                    
                    QMessageBox.information(self, "成功", "备份删除成功")
                    self._load_backups()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除失败：{e}")

class SchedulingRecordModel(QAbstractTableModel):
    """排班记录数据模型"""
    
    # 定义排序模式常量
    SORT_NEWEST_FIRST = 0  # 最新的在前面（默认）
    SORT_OLDEST_FIRST = 1  # 旧的在前面
    
    def __init__(self):
        super().__init__()
        self.records = []
        self.categories = {}
        self.simple_interval_info = {}  # 新增：与前一条记录的间隔
        self.cumulative_interval_info = {}  # 原间隔，改名为累积间隔
        self.headers = ["ID", "标识", "记录日期", "记录时间", "内容", "备注", "间隔", "累积间隔", "创建时间", "更新时间"]
        self.current_search_keyword = ""
        self.sort_mode = self.SORT_NEWEST_FIRST  # 默认最新的在前面
        
    def set_sort_mode(self, mode: int):
        """设置排序模式"""
        if mode in [self.SORT_NEWEST_FIRST, self.SORT_OLDEST_FIRST]:
            self.sort_mode = mode
            self._sort_records()
    
    def _sort_records(self):
        """根据排序模式对记录进行排序"""
        if self.sort_mode == self.SORT_NEWEST_FIRST:
            # 最新的在前面（日期降序，时间降序）
            self.records.sort(key=lambda x: (x["record_date"], x["record_time"]), reverse=True)
        else:
            # 旧的在前面（日期升序，时间升序）
            self.records.sort(key=lambda x: (x["record_date"], x["record_time"]), reverse=False)
        
        # 重新计算间隔（因为顺序变了，间隔需要重新计算）
        self._calculate_intervals()
    
    def set_records(self, records: List[Dict[str, Any]], categories: Dict[int, str]):
        """设置记录数据和标识映射，并计算间隔"""
        self.beginResetModel()
        self.records = records
        self.categories = categories
        self._sort_records()  # 排序并计算间隔
        self.endResetModel()
    
    def _calculate_intervals(self):
        """计算两种时间间隔：
        1. 简单间隔：与前一条记录的时间间隔
        2. 累积间隔：与同标识第一条记录的时间间隔
        """
        self.simple_interval_info = {}
        self.cumulative_interval_info = {}
        
        # 按标识分组记录
        records_by_category = {}
        for record in self.records:
            cat_id = record.get("category_id")
            if cat_id not in records_by_category:
                records_by_category[cat_id] = []
            records_by_category[cat_id].append(record)
        
        # 对每个标识的记录按时间排序（从旧到新，便于计算间隔）
        for cat_id, cat_records in records_by_category.items():
            # 按时间从旧到新排序
            cat_records.sort(key=lambda x: (x["record_date"], x["record_time"]), reverse=False)
            
            # 计算简单间隔（与前一条记录的间隔）
            for i in range(len(cat_records)):
                current = cat_records[i]
                if i > 0:
                    previous = cat_records[i - 1]
                    interval = self._calculate_record_interval(previous, current)
                    self.simple_interval_info[current["id"]] = interval
                else:
                    # 第一条记录，没有前一条记录
                    self.simple_interval_info[current["id"]] = {
                        "seconds": 0,
                        "display": "首次记录",
                        "color": MacaronColors.TEXT_INFO.name()
                    }
            
            # 计算累积间隔（与第一条记录的间隔）
            if len(cat_records) > 0:
                first_record = cat_records[0]
                for i in range(len(cat_records)):
                    current = cat_records[i]
                    if i > 0:
                        interval = self._calculate_record_interval(first_record, current)
                        self.cumulative_interval_info[current["id"]] = interval
                    else:
                        # 第一条记录
                        self.cumulative_interval_info[current["id"]] = {
                            "seconds": 0,
                            "display": "首次记录",
                            "color": MacaronColors.TEXT_INFO.name()
                        }
    
    def _calculate_record_interval(self, earlier: Dict[str, Any], later: Dict[str, Any]) -> Dict[str, Any]:
        """计算两条记录的时间间隔（later - earlier）"""
        try:
            earlier_dt = datetime.datetime.strptime(
                f"{earlier['record_date']} {earlier['record_time']}",
                "%Y-%m-%d %H:%M:%S"
            )
            later_dt = datetime.datetime.strptime(
                f"{later['record_date']} {later['record_time']}",
                "%Y-%m-%d %H:%M:%S"
            )
            
            seconds = (later_dt - earlier_dt).total_seconds()
            
            if seconds < 0:
                return {
                    "seconds": seconds,
                    "display": "时间异常",
                    "color": MacaronColors.TEXT_ERROR.name()
                }
            
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            
            parts = []
            if days > 0:
                parts.append(f"{days}天")
            if hours > 0:
                parts.append(f"{hours}小时")
            if minutes > 0:
                parts.append(f"{minutes}分钟")
            if secs > 0 or not parts:
                parts.append(f"{secs}秒")
            
            # 根据间隔长度设置颜色
            if days >= 30:
                color = MacaronColors.TEXT_ERROR.name()
            elif days >= 7:
                color = MacaronColors.TEXT_WARNING.name()
            elif days >= 1:
                color = MacaronColors.TEXT_INFO.name()
            else:
                color = MacaronColors.TEXT_SUCCESS.name()
            
            return {
                "seconds": seconds,
                "display": " ".join(parts),
                "color": color
            }
            
        except Exception as e:
            print(f"计算记录间隔失败: {e}")
            return {
                "seconds": 0,
                "display": "计算失败",
                "color": MacaronColors.TEXT_MUTED.name()
            }
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.records)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        record = self.records[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return str(record.get("id", ""))
            elif col == 1:
                category_id = record.get("category_id")
                return self.categories.get(category_id, "未知")
            elif col == 2:
                return record.get("record_date", "")
            elif col == 3:
                return record.get("record_time", "")
            elif col == 4:
                return record.get("content", "")
            elif col == 5:
                return record.get("notes", "")
            elif col == 6:  # 间隔（与前一条记录的间隔）
                interval = self.simple_interval_info.get(record.get("id"), {})
                return interval.get("display", "-")
            elif col == 7:  # 累积间隔（与第一条记录的间隔）
                interval = self.cumulative_interval_info.get(record.get("id"), {})
                return interval.get("display", "-")
            elif col == 8:
                return record.get("created_at", "")
            elif col == 9:
                return record.get("updated_at", "")
        
        elif role == Qt.TextAlignmentRole:
            if col in [0, 1, 2, 3, 6, 7, 8, 9]:
                return Qt.AlignCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
        
        elif role == Qt.ForegroundRole:
            if col == 6:  # 简单间隔
                interval = self.simple_interval_info.get(record.get("id"), {})
                color = interval.get("color", MacaronColors.TEXT_DARK.name())
                return QBrush(QColor(color))
            elif col == 7:  # 累积间隔
                interval = self.cumulative_interval_info.get(record.get("id"), {})
                color = interval.get("color", MacaronColors.TEXT_DARK.name())
                return QBrush(QColor(color))
            elif col == 1:
                category_id = record.get("category_id")
                return QBrush(QColor(MacaronColors.TEXT_INFO.name()))
        
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                return QBrush(QColor(MacaronColors.NEUTRAL_CREAM.name()))
            else:
                return QBrush(QColor(MacaronColors.NEUTRAL_ALMOND.name()))
        
        elif role == Qt.UserRole:
            return record
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None
    
    def filter_records(self, keyword: str):
        """过滤记录"""
        self.current_search_keyword = keyword
    
    def get_record_at_row(self, row: int) -> Dict[str, Any]:
        """获取指定行的记录"""
        if 0 <= row < len(self.records):
            return self.records[row]
        return None
    
    def get_interval_stats(self) -> Dict[str, Any]:
        """获取间隔统计信息"""
        if not self.simple_interval_info:
            return {}
        
        intervals = [info["seconds"] for info in self.simple_interval_info.values() if info["seconds"] > 0]
        
        if not intervals:
            return {}
        
        return {
            "min": min(intervals),
            "max": max(intervals),
            "avg": sum(intervals) / len(intervals),
            "count": len(intervals)
        }

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self, debug_mode=False):
        super().__init__()
        self.debug_mode = debug_mode
        self.user_manager = UserManager()
        self.current_user_id = None
        self.current_db_path = None
        self.backup_manager = None
        self.category_manager = None
        self.auto_backup_timer = QTimer()
        self.auto_backup_timer.timeout.connect(self._auto_backup)
        self.categories = []
        self.categories_dict = {}
        
        self._setup_ui()
        self._load_settings()
        self._show_user_selection()
    
    def _setup_ui(self):
        """设置UI"""
        # self.setWindowTitle("排班间隔记录系统 - 多标识管理版 (带间隔统计)")
        self.setWindowTitle(ProjectInfo.get_full_name())  # 初始不显示用户名
        self.setMinimumSize(1500, 900)
        
        # 设置全局样式 - 马卡龙色系，优化文字颜色
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
            }}
            QMenuBar {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QMenuBar::item:selected {{
                background-color: {MacaronColors.BLUE_SKY.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QMenuBar::item:pressed {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QMenu {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
            }}
            QMenu::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QToolBar {{
                background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                border: none;
                spacing: 5px;
                padding: 5px;
            }}
            QToolBar QToolButton {{
                background-color: transparent;
                color: {MacaronColors.TEXT_DARK.name()};
                padding: 5px;
                border-radius: 3px;
            }}
            QToolBar QToolButton:hover {{
                background-color: {MacaronColors.PINK_COTTON.name()};
            }}
            QStatusBar {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {MacaronColors.GREEN_MINT.name()};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QPushButton:disabled {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                color: {MacaronColors.TEXT_MUTED.name()};
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                selection-color: {MacaronColors.TEXT_DARK.name()};
            }}
            QTableWidget, QTableView {{
                background-color: white;
                alternate-background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                gridline-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
            }}
            QTableWidget::item, QTableView::item {{
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QTableWidget::item:selected, QTableView::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QHeaderView::section {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                padding: 5px;
                border: none;
                font-weight: bold;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QTabWidget::pane {{
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
            }}
            QTabBar::tab {{
                background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QTabBar::tab:selected {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {MacaronColors.BLUE_MIST.name()};
            }}
            QProgressBar {{
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                text-align: center;
                color: {MacaronColors.TEXT_DARK.name()};
                background-color: white;
            }}
            QProgressBar::chunk {{
                background-color: {MacaronColors.GREEN_APPLE.name()};
                border-radius: 5px;
            }}
            QCheckBox {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {MacaronColors.GREEN_MINT.name()};
            }}
            QRadioButton {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QScrollBar:vertical {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {MacaronColors.PINK_COTTON.name()};
            }}
            QScrollBar:horizontal {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {MacaronColors.PINK_COTTON.name()};
            }}
        """)
        
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        self._create_toolbar()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
        left_panel = self._create_input_panel()
        content_layout.addWidget(left_panel, 1)
        
        right_panel = self._create_records_panel()
        content_layout.addWidget(right_panel, 2)
        
        main_layout.addWidget(content_widget, 1)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setObjectName("mainToolbar") 
        toolbar.setMovable(False)
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                border: none;
                spacing: 5px;
                padding: 5px;
            }}
        """)
        
        self.user_label = QLabel("👤 未登录")
        self.user_label.setStyleSheet(f"""
            QLabel {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        toolbar.addWidget(self.user_label)
        toolbar.addSeparator()
        
        switch_user_action = QAction("👥 切换用户", self)
        switch_user_action.triggered.connect(self._switch_user)
        toolbar.addAction(switch_user_action)
        
        category_action = QAction("🏷️ 标识管理", self)
        category_action.triggered.connect(self._show_category_manager)
        toolbar.addAction(category_action)
        
        toolbar.addSeparator()
        
        backup_action = QAction("💾 备份管理", self)
        backup_action.triggered.connect(self._show_backup_dialog)
        toolbar.addAction(backup_action)
        
        manual_backup_action = QAction("📀 手动备份", self)
        manual_backup_action.triggered.connect(self._manual_backup)
        toolbar.addAction(manual_backup_action)
        
        toolbar.addSeparator()
        
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)
        
        if self.debug_mode:
            debug_label = QLabel("🐞 调试模式")
            debug_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {MacaronColors.RED_CORAL.name()};
                    color: {MacaronColors.TEXT_LIGHT.name()};
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }}
            """)
            toolbar.addWidget(debug_label)
    
    def _create_input_panel(self) -> QWidget:
        """创建输入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        title = QLabel("📝 新增记录")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {MacaronColors.TEXT_DARK.name()};
            padding: 10px;
            background-color: {MacaronColors.GREEN_MINT.name()};
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form_group = QGroupBox("记录信息")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        form_layout.addRow("标识:", self.category_combo)
        
        category_btn_layout = QHBoxLayout()
        self.manage_category_btn = QPushButton("🏷️ 管理标识")
        self.manage_category_btn.clicked.connect(self._show_category_manager)
        category_btn_layout.addWidget(self.manage_category_btn)
        form_layout.addRow("", category_btn_layout)
        
        self.record_date = QDateEdit()
        self.record_date.setCalendarPopup(True)
        self.record_date.setDate(QDate.currentDate())
        self.record_date.dateChanged.connect(self._calculate_interval)
        form_layout.addRow("记录日期:", self.record_date)
        
        self.record_time = QTimeEdit()
        self.record_time.setTime(QTime.currentTime())
        self.record_time.timeChanged.connect(self._calculate_interval)
        form_layout.addRow("记录时间:", self.record_time)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText("请输入记录内容")
        self.content_edit.textChanged.connect(self._update_input_status)
        form_layout.addRow("内容:", self.content_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("请输入备注信息（可选）")
        self.notes_edit.setMaximumHeight(100)
        form_layout.addRow("备注:", self.notes_edit)
        
        layout.addWidget(form_group)
        
        info_group = QGroupBox("同类记录信息")
        info_layout = QFormLayout(info_group)
        
        self.last_record_time = QLabel("无记录")
        info_layout.addRow("上次记录时间:", self.last_record_time)
        
        self.last_record_content = QLabel("无记录")
        info_layout.addRow("上次记录内容:", self.last_record_content)
        
        self.interval_display = QLabel("-")
        self.interval_display.setStyleSheet(f"font-size: 14px; font-weight: bold;")
        info_layout.addRow("时间间隔:", self.interval_display)
        
        self.category_record_count = QLabel("0")
        info_layout.addRow("同类记录数:", self.category_record_count)
        
        layout.addWidget(info_group)
        
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存记录")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_record)
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self._clear_input)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        stats_group = QGroupBox("标识统计")
        # 为统计组添加水平布局，包含标题和刷新按钮
        stats_header_layout = QHBoxLayout()
        stats_header_layout.addWidget(QLabel("📊 标识统计信息"))
        stats_header_layout.addStretch()
        
        # 添加刷新按钮
        self.refresh_stats_btn = QPushButton("🔄 刷新统计")
        self.refresh_stats_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.BLUE_MIST.name()};
                border: none;
                border-radius: 3px;
                padding: 3px 8px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-size: 11px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.BLUE_SKY.name()};
            }}
        """)
        self.refresh_stats_btn.clicked.connect(self._refresh_stats)
        stats_header_layout.addWidget(self.refresh_stats_btn)
        
        # 创建垂直布局来放置标题行和表格
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.addLayout(stats_header_layout)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)
        self.stats_table.setHorizontalHeaderLabels(["标识", "颜色", "记录数", "上次记录", "间隔"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_table)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return panel
    
    def _create_records_panel(self) -> QWidget:
        """创建记录列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        title = QLabel("📋 记录列表")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {MacaronColors.TEXT_DARK.name()};
            padding: 10px;
            background-color: {MacaronColors.BLUE_SKY.name()};
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 添加批量操作工具栏
        batch_toolbar = QHBoxLayout()
        
        # 全选/取消全选按钮
        self.select_all_btn = QPushButton("✅ 全选")
        self.select_all_btn.setCheckable(True)
        self.select_all_btn.toggled.connect(self._toggle_select_all)
        self.select_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PURPLE_TARO.name()};
            }}
            QPushButton:checked {{
                background-color: {MacaronColors.PURPLE_WISTERIA.name()};
            }}
        """)
        batch_toolbar.addWidget(self.select_all_btn)
        
        # 批量删除按钮
        self.batch_delete_btn = QPushButton("🗑️ 批量删除")
        self.batch_delete_btn.clicked.connect(self._batch_delete_records)
        self.batch_delete_btn.setEnabled(False)
        self.batch_delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.RED_WATERMELON.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.RED_CORAL.name()};
            }}
            QPushButton:disabled {{
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                color: {MacaronColors.TEXT_MUTED.name()};
            }}
        """)
        batch_toolbar.addWidget(self.batch_delete_btn)
        
        # 一键清空按钮
        self.clear_all_records_btn = QPushButton("🧹 一键清空")
        self.clear_all_records_btn.clicked.connect(self._clear_all_records)
        self.clear_all_records_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.RED_CORAL.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.RED_WATERMELON.name()};
            }}
        """)
        batch_toolbar.addWidget(self.clear_all_records_btn)
        
        batch_toolbar.addStretch()
        
        # 选中的记录数显示
        self.selected_count_label = QLabel("已选中: 0 条")
        self.selected_count_label.setStyleSheet(f"""
            QLabel {{
                background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                padding: 5px 10px;
                border-radius: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        batch_toolbar.addWidget(self.selected_count_label)
        
        layout.addLayout(batch_toolbar)
        
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("🔍 搜索:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词搜索（支持中文、拼音、首字母）")
        self.search_edit.textChanged.connect(self._search_records)
        search_layout.addWidget(self.search_edit)
        
        self.clear_search_btn = QPushButton("清除")
        self.clear_search_btn.clicked.connect(lambda: self.search_edit.clear())
        search_layout.addWidget(self.clear_search_btn)
        
        search_layout.addWidget(QLabel("🏷️ 标识筛选:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部", -1)
        self.category_filter.currentIndexChanged.connect(self._filter_by_category)
        search_layout.addWidget(self.category_filter)
        
        layout.addLayout(search_layout)
        
        self.records_table = QTableView()
        self.records_model = SchedulingRecordModel()
        self.records_table.setModel(self.records_model)
        
        # 启用多选
        self.records_table.setSelectionMode(QTableView.ExtendedSelection)
        self.records_table.setSelectionBehavior(QTableView.SelectRows)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setEditTriggers(QTableView.NoEditTriggers)
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.verticalHeader().setVisible(False)
        
        # 设置列宽
        self.records_table.setColumnWidth(0, 60)
        self.records_table.setColumnWidth(1, 100)
        self.records_table.setColumnWidth(2, 100)
        self.records_table.setColumnWidth(3, 100)
        self.records_table.setColumnWidth(4, 200)
        self.records_table.setColumnWidth(5, 150)
        self.records_table.setColumnWidth(6, 120)  # 间隔
        self.records_table.setColumnWidth(7, 120)  # 累积间隔
        self.records_table.setColumnWidth(8, 150)
        self.records_table.setColumnWidth(9, 150)
        
        # 连接选择变化信号
        selection_model = self.records_table.selectionModel()
        selection_model.selectionChanged.connect(self._on_record_selection_changed)
        
        # 设置右键菜单
        self.records_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.records_table.customContextMenuRequested.connect(self._show_record_context_menu)
        
        self.records_table.doubleClicked.connect(self._edit_record)
        
        layout.addWidget(self.records_table)
        
        return panel

    def _show_record_context_menu(self, position):
        """显示记录右键菜单"""
        # 获取当前选中行的索引
        selected_indexes = self.records_table.selectionModel().selectedRows()
        
        menu = QMenu()
        
        # 设置菜单样式 - 马卡龙色系
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 3px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QMenu::item:selected {{
                background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {MacaronColors.NEUTRAL_CARAMEL.name()};
                margin: 5px 0;
            }}
        """)
        
        if len(selected_indexes) == 1:
            # 单条记录操作
            record = self.records_model.get_record_at_row(selected_indexes[0].row())
            if record:
                # 编辑
                edit_action = QAction("✏️ 编辑记录", self)
                edit_action.triggered.connect(lambda: self._edit_record(selected_indexes[0]))
                menu.addAction(edit_action)
                
                menu.addSeparator()
                
                # 查看详情
                view_action = QAction("👁️ 查看详情", self)
                view_action.triggered.connect(lambda: self._view_record_detail(record))
                menu.addAction(view_action)
                
                menu.addSeparator()
                
                # 删除
                delete_action = QAction("🗑️ 删除记录", self)
                delete_action.setIcon(QIcon())  # 可以设置图标
                delete_action.triggered.connect(lambda: self._delete_single_record(record))
                menu.addAction(delete_action)
        
        elif len(selected_indexes) > 1:
            # 批量记录操作
            count = len(selected_indexes)
            
            # 批量删除
            batch_delete_action = QAction(f"🗑️ 批量删除 ({count} 条)", self)
            batch_delete_action.triggered.connect(lambda: self._batch_delete_records(selected_indexes))
            menu.addAction(batch_delete_action)
            
            # 批量导出（可以后续扩展）
            batch_export_action = QAction(f"📤 批量导出 ({count} 条)", self)
            batch_export_action.triggered.connect(lambda: self._batch_export_records(selected_indexes))
            menu.addAction(batch_export_action)
        
        # 添加全选操作（无论是否有选中行）
        menu.addSeparator()
        select_all_action = QAction("✅ 全选", self)
        select_all_action.triggered.connect(self._select_all_records)
        menu.addAction(select_all_action)
        
        # 取消全选
        deselect_all_action = QAction("❌ 取消全选", self)
        deselect_all_action.triggered.connect(self._deselect_all_records)
        menu.addAction(deselect_all_action)
        
        menu.addSeparator()
        
        # 按标识筛选子菜单
        if self.categories:
            filter_menu = menu.addMenu("🏷️ 按标识筛选")
            filter_menu.setStyleSheet(menu.styleSheet())
            
            for category in self.categories:
                action = QAction(category['name'], self)
                action.setData(category['id'])
                action.triggered.connect(lambda checked, cat_id=category['id']: self._filter_by_category_id(cat_id))
                
                # 设置颜色
                if 'color' in category:
                    pixmap = QPixmap(16, 16)
                    pixmap.fill(QColor(category['color']))
                    action.setIcon(QIcon(pixmap))
                
                filter_menu.addAction(action)
        
        # 一键清空
        menu.addSeparator()
        clear_all_action = QAction("🧹 一键清空所有记录", self)
        clear_all_action.triggered.connect(self._clear_all_records)
        menu.addAction(clear_all_action)
        
        # 刷新
        menu.addSeparator()
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.triggered.connect(self._refresh_all_data)
        menu.addAction(refresh_action)
        
        # 在鼠标位置显示菜单
        menu.exec(self.records_table.viewport().mapToGlobal(position))

    def _view_record_detail(self, record):
        """查看记录详情"""
        detail_dialog = QDialog(self)
        detail_dialog.setWindowTitle(f"{ProjectInfo.get_full_name()} - 记录详情")
        detail_dialog.setModal(True)
        detail_dialog.setMinimumWidth(500)
        
        # 设置样式
        detail_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
                padding: 5px;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {MacaronColors.GREEN_MINT.name()};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        
        layout = QVBoxLayout(detail_dialog)
        
        # 基本信息组
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)
        
        # 获取标识信息
        category = self.categories_dict.get(record['category_id'], {})
        category_name = category.get('name', '未知')
        
        info_layout.addRow("记录ID:", QLabel(str(record['id'])))
        info_layout.addRow("标识:", QLabel(category_name))
        info_layout.addRow("记录日期:", QLabel(record['record_date']))
        info_layout.addRow("记录时间:", QLabel(record['record_time']))
        
        layout.addWidget(info_group)
        
        # 内容组
        content_group = QGroupBox("记录内容")
        content_layout = QVBoxLayout(content_group)
        content_label = QLabel(record['content'])
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"""
            QLabel {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        content_layout.addWidget(content_label)
        layout.addWidget(content_group)
        
        # 备注组
        if record.get('notes'):
            notes_group = QGroupBox("备注")
            notes_layout = QVBoxLayout(notes_group)
            notes_label = QLabel(record['notes'])
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet(f"""
                QLabel {{
                    background-color: white;
                    border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                    border-radius: 5px;
                    padding: 10px;
                }}
            """)
            notes_layout.addWidget(notes_label)
            layout.addWidget(notes_group)
        
        # 时间信息组
        time_group = QGroupBox("时间信息")
        time_layout = QFormLayout(time_group)
        time_layout.setSpacing(10)
        
        time_layout.addRow("创建时间:", QLabel(record.get('created_at', '未知')))
        time_layout.addRow("更新时间:", QLabel(record.get('updated_at', '未知')))
        
        # 简单间隔信息
        simple_interval = self.records_model.simple_interval_info.get(record['id'], {})
        simple_interval_display = simple_interval.get('display', '-')
        simple_interval_label = QLabel(simple_interval_display)
        simple_interval_label.setStyleSheet(f"color: {simple_interval.get('color', MacaronColors.TEXT_DARK.name())}; font-weight: bold;")
        time_layout.addRow("与上次间隔:", simple_interval_label)
        
        # 累积间隔信息
        cumulative_interval = self.records_model.cumulative_interval_info.get(record['id'], {})
        cumulative_interval_display = cumulative_interval.get('display', '-')
        cumulative_interval_label = QLabel(cumulative_interval_display)
        cumulative_interval_label.setStyleSheet(f"color: {cumulative_interval.get('color', MacaronColors.TEXT_DARK.name())}; font-weight: bold;")
        time_layout.addRow("累积间隔:", cumulative_interval_label)
        
        layout.addWidget(time_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        edit_btn = QPushButton("✏️ 编辑")
        edit_btn.clicked.connect(lambda: [detail_dialog.accept(), self._edit_record_by_id(record['id'])])
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ 删除")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacaronColors.RED_WATERMELON.name()};
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.RED_CORAL.name()};
            }}
        """)
        delete_btn.clicked.connect(lambda: [detail_dialog.accept(), self._delete_single_record(record)])
        button_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(detail_dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        detail_dialog.exec()

    def _edit_record_by_id(self, record_id):
        """根据ID编辑记录"""
        # 找到对应的记录
        for row in range(self.records_model.rowCount()):
            record = self.records_model.get_record_at_row(row)
            if record and record['id'] == record_id:
                index = self.records_model.index(row, 0)
                self._edit_record(index)
                break

    def _delete_single_record(self, record):
        """删除单条记录"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除记录吗？\n\n记录内容：{record['content']}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._delete_records_by_ids([record['id']])

    def _batch_delete_records(self, selected_indexes=None):
        """批量删除记录"""
        if selected_indexes is None:
            selected_indexes = self.records_table.selectionModel().selectedRows()
        
        if not selected_indexes:
            QMessageBox.information(self, "提示", "请先选择要删除的记录")
            return
        
        record_ids = []
        record_contents = []
        
        for index in selected_indexes:
            record = self.records_model.get_record_at_row(index.row())
            if record:
                record_ids.append(record['id'])
                record_contents.append(record['content'])
        
        count = len(record_ids)
        
        # 构建确认消息
        msg = f"确定要删除选中的 {count} 条记录吗？\n\n"
        if count <= 5:
            msg += "将删除以下记录：\n"
            for i, content in enumerate(record_contents, 1):
                msg += f"{i}. {content[:30]}{'...' if len(content) > 30 else ''}\n"
        else:
            msg += "将删除以下记录（部分显示）：\n"
            for i, content in enumerate(record_contents[:5], 1):
                msg += f"{i}. {content[:30]}{'...' if len(content) > 30 else ''}\n"
            msg += f"...等共 {count} 条记录\n"
        
        msg += f"\n此操作不可撤销！"
        
        reply = QMessageBox.question(
            self, "确认批量删除",
            msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._delete_records_by_ids(record_ids)

    def _delete_records_by_ids(self, record_ids):
        """根据ID列表删除记录"""
        if not record_ids or not self.current_db_path:
            return
        
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            # 构建占位符
            placeholders = ','.join(['?' for _ in record_ids])
            
            cursor.execute(f"""
                DELETE FROM scheduling_records
                WHERE id IN ({placeholders})
            """, record_ids)
            
            conn.commit()
            
            deleted_count = cursor.rowcount
            
            # 刷新数据
            self._load_records()
            self._load_category_stats()
            
            # 更新状态栏
            self.status_bar.showMessage(f"✅ 成功删除 {deleted_count} 条记录", 3000)
            
            # 清空选择
            self.records_table.clearSelection()
            self.select_all_btn.setChecked(False)
            
        except Exception as e:
            self._show_error("删除失败", str(e))

    def _clear_all_records(self):
        """一键清空所有记录"""
        if not self.current_db_path:
            return
        
        # 获取总记录数
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM scheduling_records")
            total_count = cursor.fetchone()[0]
            
            if total_count == 0:
                QMessageBox.information(self, "提示", "当前没有记录可清空")
                return
            
            # 按标识统计记录数
            cursor.execute("""
                SELECT c.name, COUNT(r.id) as count
                FROM categories c
                LEFT JOIN scheduling_records r ON c.id = r.category_id
                WHERE c.is_active = 1
                GROUP BY c.id
                HAVING count > 0
                ORDER BY count DESC
            """)
            category_stats = cursor.fetchall()
            
            # 构建确认消息
            msg = f"⚠️ 确定要清空所有记录吗？\n\n"
            msg += f"📊 统计信息：\n"
            msg += f"• 总记录数：{total_count} 条\n"
            msg += f"• 涉及标识：{len(category_stats)} 个\n\n"
            
            msg += "各标识记录数：\n"
            for i, (cat_name, cat_count) in enumerate(category_stats[:10], 1):
                msg += f"  {i}. {cat_name}：{cat_count} 条\n"
            if len(category_stats) > 10:
                msg += f"  ...等共 {len(category_stats)} 个标识\n"
            
            msg += f"\n此操作将永久删除所有记录，不可撤销！"
            
            reply = QMessageBox.question(
                self, "确认清空所有记录",
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 二次确认
                second_reply = QMessageBox.question(
                    self, "最后确认",
                    f"⚠️ 最后一次确认：\n确定要永久删除全部 {total_count} 条记录吗？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if second_reply == QMessageBox.Yes:
                    cursor.execute("DELETE FROM scheduling_records")
                    conn.commit()
                    
                    # 刷新数据
                    self._load_records()
                    self._load_category_stats()
                    
                    self.status_bar.showMessage(f"✅ 已清空全部 {total_count} 条记录", 5000)
                    
                    # 清空选择
                    self.records_table.clearSelection()
                    self.select_all_btn.setChecked(False)
                    
        except Exception as e:
            self._show_error("清空记录失败", str(e))

    def _select_all_records(self):
        """全选所有记录"""
        self.records_table.selectAll()
        self.select_all_btn.setChecked(True)

    def _deselect_all_records(self):
        """取消全选"""
        self.records_table.clearSelection()
        self.select_all_btn.setChecked(False)

    def _toggle_select_all(self, checked):
        """切换全选状态"""
        if checked:
            self.records_table.selectAll()
        else:
            self.records_table.clearSelection()

    def _on_record_selection_changed(self, selected, deselected):
        """记录选择变化事件"""
        selected_rows = self.records_table.selectionModel().selectedRows()
        count = len(selected_rows)
        
        # 更新选中数量显示
        self.selected_count_label.setText(f"已选中: {count} 条")
        
        # 更新批量删除按钮状态
        self.batch_delete_btn.setEnabled(count > 0)
        
        # 如果所有行都被选中，勾选全选按钮；否则取消勾选
        total_rows = self.records_model.rowCount()
        if total_rows > 0 and count == total_rows:
            self.select_all_btn.setChecked(True)
        else:
            self.select_all_btn.setChecked(False)

    def _filter_by_category_id(self, category_id):
        """按标识ID筛选"""
        index = self.category_filter.findData(category_id)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)

    def _batch_export_records(self, selected_indexes):
        """批量导出记录（扩展功能）"""
        # 这是一个扩展功能的占位，可以后续实现导出为CSV/Excel等
        QMessageBox.information(
            self, "提示",
            "批量导出功能正在开发中...\n\n后续版本将支持导出为 CSV、Excel 等格式。"
        )

    def _show_user_selection(self):
        """显示用户选择对话框"""
        dialog = UserSelectionDialog(self.user_manager, self)
        if dialog.exec():
            self.current_user_id = dialog.get_selected_user_id()
            if self.current_user_id:
                self._login_user(self.current_user_id)
        else:
            QTimer.singleShot(0, self.close)
    
    def _login_user(self, user_id: int):
        """登录用户"""
        users = self.user_manager.get_all_users()
        for user in users:
            if user['id'] == user_id:
                self.current_user_id = user_id
                self.current_username = user['display_name']
                self.user_label.setText(f"👤 当前用户: {user['display_name']}")
            
                # 设置主窗口标题 - 使用 ProjectInfo
                self.setWindowTitle(ProjectInfo.get_full_title(user['display_name']))
            
                db_file = Path.cwd() / ".scheduling_system" / user['db_file']
                self.current_db_path = str(db_file)
                
                self.backup_manager = DatabaseBackupManager(self.user_manager, user_id)
                self.category_manager = CategoryManager(self.current_db_path)
                
                self._load_user_settings()
                self._load_categories()
                self._load_records()
                
                self._start_auto_backup()
                
                self.status_bar.showMessage(f"已登录用户: {user['display_name']}", 3000)
                
                break
    
    def _load_categories(self):
        """加载所有标识"""
        if not self.category_manager:
            return
        
        try:
            self.categories = self.category_manager.get_all_categories()
            self.categories_dict = {c['id']: c for c in self.categories}
            
            # 刷新主输入区的标识下拉框
            self.category_combo.clear()
            for category in self.categories:
                self.category_combo.addItem(category['name'], category['id'])
                index = self.category_combo.count() - 1
                self.category_combo.setItemData(index, QColor(category['color']), Qt.ForegroundRole)
                self.category_combo.setItemData(index, QBrush(QColor(category['color']).lighter(160)), Qt.BackgroundRole)
            
            if self.categories:
                self.category_combo.setCurrentIndex(0)
            
            # 刷新筛选下拉框
            self.category_filter.clear()
            self.category_filter.addItem("全部", -1)
            for category in self.categories:
                self.category_filter.addItem(category['name'], category['id'])
                index = self.category_filter.count() - 1
                self.category_filter.setItemData(index, QColor(category['color']), Qt.ForegroundRole)
                self.category_filter.setItemData(index, QBrush(QColor(category['color']).lighter(160)), Qt.BackgroundRole)
            
            # 刷新统计表格
            self._load_category_stats()
            
        except Exception as e:
            self._show_error("加载标识失败", str(e))
    
    def _load_records(self):
        """加载记录"""
        print("正在刷新记录列表...")  # 调试输出
        if not self.current_db_path:
            return
        
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, r.category_id, r.record_date, r.record_time, 
                       r.content, r.notes, r.created_at, r.updated_at,
                       c.name as category_name, c.color
                FROM scheduling_records r
                JOIN categories c ON r.category_id = c.id
                ORDER BY r.record_date DESC, r.record_time DESC
            """)
            
            records = []
            category_map = {}
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "category_id": row[1],
                    "record_date": row[2],
                    "record_time": row[3],
                    "content": row[4],
                    "notes": row[5],
                    "created_at": row[6],
                    "updated_at": row[7]
                })
                category_map[row[1]] = row[8]  # category_name
            
            self.records_model.set_records(records, category_map)
            
            # 更新状态栏统计信息
            stats = self.records_model.get_interval_stats()
            if stats:
                min_interval = self._format_interval(stats["min"])
                max_interval = self._format_interval(stats["max"])
                avg_interval = self._format_interval(stats["avg"])
                self.status_bar.showMessage(
                    f"📊 间隔统计 - 最短: {min_interval} | 最长: {max_interval} | 平均: {avg_interval} | 记录数: {stats['count']}",
                    5000
                )
            
            print(f"加载了 {len(records)} 条记录")  # 调试输出
        except Exception as e:
            print(f"加载记录失败: {e}")
            self._show_error("加载记录失败", str(e))
    
    def _load_category_stats(self, force_refresh=True):
        """加载所有标识的统计信息"""
        if not self.category_manager:
            return
        
        try:
            stats = self.category_manager.get_category_stats()
            self._update_stats_table(stats)  # 调用专门的方法更新表格
            
            # 添加调试输出
            print(f"统计表格已刷新，共 {len(stats)} 条记录")
            
        except Exception as e:
            print(f"加载标识统计失败: {e}")
    
    def _format_interval(self, seconds: float) -> str:
        """格式化时间间隔"""
        if seconds < 0:
            return "时间异常"
        
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if secs > 0 or not parts:
            parts.append(f"{secs}秒")
        
        return " ".join(parts)
    
    def _on_category_changed(self):
        """标识选择改变事件"""
        self._update_category_stats()
        self._calculate_interval()
    
    def _update_category_stats(self):
        """更新当前标识的统计信息"""
        category_id = self.category_combo.currentData()
        if not category_id or not self.current_db_path:
            return
        
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            # 查询最后一条记录
            cursor.execute("""
                SELECT record_date, record_time, content
                FROM scheduling_records
                WHERE category_id = ?
                ORDER BY record_date DESC, record_time DESC
                LIMIT 1
            """, (category_id,))
            
            result = cursor.fetchone()
            if result:
                last_time = f"{result[0]} {result[1]}"
                self.last_record_time.setText(last_time)
                self.last_record_content.setText(result[2])
            else:
                self.last_record_time.setText("无记录")
                self.last_record_content.setText("无记录")
            
            # 查询记录数
            cursor.execute("""
                SELECT COUNT(*) FROM scheduling_records
                WHERE category_id = ?
            """, (category_id,))
            
            count = cursor.fetchone()[0]
            self.category_record_count.setText(str(count))
            
            # 重新计算间隔
            self._calculate_interval()
            
        except Exception as e:
            print(f"更新标识统计失败: {e}")
    
    def _calculate_interval(self):
        """计算时间间隔（按当前标识）"""
        if not self.current_db_path:
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            return
        
        try:
            current_dt = QDateTime(
                self.record_date.date(),
                self.record_time.time()
            )
            
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT record_date, record_time
                FROM scheduling_records
                WHERE category_id = ?
                ORDER BY record_date DESC, record_time DESC
                LIMIT 1
            """, (category_id,))
            
            result = cursor.fetchone()
            if result:
                last_date = QDate.fromString(result[0], "yyyy-MM-dd")
                last_time = QTime.fromString(result[1], "hh:mm:ss")
                last_dt = QDateTime(last_date, last_time)
                
                seconds = last_dt.secsTo(current_dt)
                
                if seconds < 0:
                    self.interval_display.setText("当前时间早于上次记录时间")
                    self.interval_display.setStyleSheet(f"color: {MacaronColors.TEXT_ERROR.name()}; font-weight: bold;")
                else:
                    days = seconds // 86400
                    hours = (seconds % 86400) // 3600
                    minutes = (seconds % 3600) // 60
                    secs = seconds % 60
                    
                    interval_text = []
                    if days > 0:
                        interval_text.append(f"{days}天")
                    if hours > 0:
                        interval_text.append(f"{hours}小时")
                    if minutes > 0:
                        interval_text.append(f"{minutes}分钟")
                    if secs > 0 or len(interval_text) == 0:
                        interval_text.append(f"{secs}秒")
                    
                    self.interval_display.setText(" ".join(interval_text))
                    
                    if days >= 30:
                        color = MacaronColors.TEXT_ERROR.name()
                    elif days >= 7:
                        color = MacaronColors.TEXT_WARNING.name()
                    elif days >= 1:
                        color = MacaronColors.TEXT_INFO.name()
                    else:
                        color = MacaronColors.TEXT_SUCCESS.name()
                    
                    self.interval_display.setStyleSheet(f"color: {color}; font-weight: bold;")
            else:
                self.interval_display.setText("首次记录")
                self.interval_display.setStyleSheet(f"color: {MacaronColors.TEXT_INFO.name()}; font-weight: bold;")
                
        except Exception as e:
            print(f"计算时间间隔失败: {e}")
    
    def _update_input_status(self):
        """更新输入状态"""
        has_content = bool(self.content_edit.text().strip())
        self.save_btn.setEnabled(has_content)
    
    def _save_record(self):
        """保存记录"""
        if not self.current_db_path:
            return
        
        content = self.content_edit.text().strip()
        if not content:
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            QMessageBox.warning(self, "警告", "请选择标识")
            return
        
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scheduling_records 
                (category_id, record_date, record_time, content, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                category_id,
                self.record_date.date().toString("yyyy-MM-dd"),
                self.record_time.time().toString("hh:mm:ss"),
                content,
                self.notes_edit.toPlainText()
            ))
            
            conn.commit()
            
            self._clear_input()
            self._load_records()
            self._load_category_stats()
            
            self.status_bar.showMessage("✅ 记录保存成功", 3000)
            
        except Exception as e:
            self._show_error("保存失败", str(e))
    
    def _clear_input(self):
        """清空输入"""
        self.record_date.setDate(QDate.currentDate())
        self.record_time.setTime(QTime.currentTime())
        self.content_edit.clear()
        self.notes_edit.clear()
    
    def _edit_record(self, index: QModelIndex):
        """编辑记录"""
        row = index.row()
        record = self.records_model.get_record_at_row(row)
        if record:
            dialog = RecordEditDialog(self.current_db_path, self.categories_dict, record, self)
            if dialog.exec():
                self._load_records()
                self._load_category_stats()
    
    def _filter_by_category(self):
        """按标识筛选"""
        category_id = self.category_filter.currentData()
        
        if category_id == -1:
            self._load_records()
            return
        
        if not self.current_db_path:
            return
        
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.id, r.category_id, r.record_date, r.record_time, 
                       r.content, r.notes, r.created_at, r.updated_at,
                       c.name as category_name, c.color
                FROM scheduling_records r
                JOIN categories c ON r.category_id = c.id
                WHERE r.category_id = ?
                ORDER BY r.record_date DESC, r.record_time DESC
            """, (category_id,))
            
            records = []
            category_map = {}
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "category_id": row[1],
                    "record_date": row[2],
                    "record_time": row[3],
                    "content": row[4],
                    "notes": row[5],
                    "created_at": row[6],
                    "updated_at": row[7]
                })
                category_map[row[1]] = row[8]
            
            self.records_model.set_records(records, category_map)
            
        except Exception as e:
            print(f"筛选失败: {e}")
    
    def _search_records(self):
        """搜索记录"""
        keyword = self.search_edit.text().strip()
        category_id = self.category_filter.currentData()
        
        if not keyword and category_id == -1:
            self._load_records()
            return
        
        try:
            conn = self.user_manager.db_pool.get_connection(self.current_db_path)
            cursor = conn.cursor()
            
            if category_id != -1:
                cursor.execute("""
                    SELECT r.id, r.category_id, r.record_date, r.record_time, 
                           r.content, r.notes, r.created_at, r.updated_at,
                           c.name as category_name, c.color
                    FROM scheduling_records r
                    JOIN categories c ON r.category_id = c.id
                    WHERE r.category_id = ?
                    ORDER BY r.record_date DESC, r.record_time DESC
                """, (category_id,))
            else:
                cursor.execute("""
                    SELECT r.id, r.category_id, r.record_date, r.record_time, 
                           r.content, r.notes, r.created_at, r.updated_at,
                           c.name as category_name, c.color
                    FROM scheduling_records r
                    JOIN categories c ON r.category_id = c.id
                    ORDER BY r.record_date DESC, r.record_time DESC
                """)
            
            records = []
            category_map = {}
            for row in cursor.fetchall():
                record = {
                    "id": row[0],
                    "category_id": row[1],
                    "record_date": row[2],
                    "record_time": row[3],
                    "content": row[4],
                    "notes": row[5],
                    "created_at": row[6],
                    "updated_at": row[7]
                }
                category_map[row[1]] = row[8]
                
                if not keyword:
                    records.append(record)
                else:
                    category_name = row[8]
                    search_text = f"{category_name} {row[4]} {row[5] or ''}"
                    if SearchHelper.match_keyword(search_text, keyword):
                        records.append(record)
            
            self.records_model.set_records(records, category_map)
            
        except Exception as e:
            print(f"搜索失败: {e}")
    
    def _show_category_manager(self):
        """显示标识管理对话框"""
        if self.category_manager:
            dialog = CategoryManagerDialog(self.category_manager, self)
            result = dialog.exec()
            
            # 检查是否有修改，如果有则刷新数据
            if hasattr(dialog, 'has_changes') and dialog.has_changes:
                # 使用单次定时器延迟刷新，确保对话框完全关闭
                QTimer.singleShot(100, self._refresh_all_data)
                self.status_bar.showMessage("✅ 标识管理更新完成", 3000)
            else:
                # 可选：提示没有修改
                self.status_bar.showMessage("ℹ️ 标识未作修改", 2000)

    def _refresh_all_data(self):
        """刷新所有数据（完全重新加载）"""
        print("开始完全刷新所有数据...")  # 调试输出
        
        # 1. 首先重新加载所有标识（从数据库）
        self._load_categories()
        
        # 2. 强制重新加载标识统计信息（从数据库）
        if self.category_manager:
            # 清除可能的缓存
            stats = self.category_manager.get_category_stats()
            self._update_stats_table(stats)  # 使用新的方法来更新统计表格
        
        # 3. 重新加载记录列表
        self._load_records()
        
        # 4. 更新当前选中的标识信息
        self._update_category_stats()
        
        # 5. 重新计算时间间隔
        self._calculate_interval()
        
        # 6. 刷新筛选下拉框的显示
        self._refresh_filter_combo()
        
        # 7. 强制界面重绘
        self.repaint()
        self.stats_table.viewport().update()
        self.records_table.viewport().update()
        
        print("数据刷新完成")  # 调试输出

    def _update_stats_table(self, stats):
        """更新统计表格"""
        try:
            # 先清除所有现有行
            self.stats_table.setRowCount(0)
            self.stats_table.setRowCount(len(stats))
            
            for i, stat in enumerate(stats):
                # 标识名称
                name_item = QTableWidgetItem(stat['name'])
                name_item.setForeground(QBrush(QColor(stat['color'])))
                name_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 0, name_item)
                
                # 颜色
                color_item = QTableWidgetItem()
                color_item.setBackground(QBrush(QColor(stat['color'])))
                color_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 1, color_item)
                
                # 记录数
                count_item = QTableWidgetItem(str(stat['record_count']))
                count_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 2, count_item)
                
                # 上次记录
                last_time = stat['last_record_time']
                if last_time:
                    try:
                        dt = datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
                        last_time = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                else:
                    last_time = "无记录"
                time_item = QTableWidgetItem(last_time)
                time_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 3, time_item)
                
                # 间隔（暂时显示"-"，可以在后续计算）
                interval_item = QTableWidgetItem("-")
                interval_item.setTextAlignment(Qt.AlignCenter)
                self.stats_table.setItem(i, 4, interval_item)
            
            self.stats_table.resizeColumnsToContents()
            self.stats_table.viewport().update()
            
            print(f"统计表格已刷新，共 {len(stats)} 条记录")
            
        except Exception as e:
            print(f"更新统计表格失败: {e}")

    def _refresh_filter_combo(self):
        """刷新筛选下拉框"""
        try:
            current_filter = self.category_filter.currentData()
            self.category_filter.clear()
            self.category_filter.addItem("全部", -1)
            
            for category in self.categories:
                self.category_filter.addItem(category['name'], category['id'])
                index = self.category_filter.count() - 1
                self.category_filter.setItemData(index, QColor(category['color']), Qt.ForegroundRole)
                self.category_filter.setItemData(index, QBrush(QColor(category['color']).lighter(160)), Qt.BackgroundRole)
            
            # 恢复之前的筛选状态
            if current_filter != -1:
                index = self.category_filter.findData(current_filter)
                if index >= 0:
                    self.category_filter.setCurrentIndex(index)
        except Exception as e:
            print(f"刷新筛选下拉框失败: {e}")
    
    def _switch_user(self):
        """切换用户"""
        dialog = UserSelectionDialog(self.user_manager, self)
        if dialog.exec():
            new_user_id = dialog.get_selected_user_id()
            if new_user_id and new_user_id != self.current_user_id:
                self._login_user(new_user_id)
    
    def _show_backup_dialog(self):
        """显示备份对话框"""
        if self.backup_manager:
            dialog = BackupRestoreDialog(self.backup_manager, self)
            if dialog.exec():
                self._load_categories()
                self._load_records()
    
    def _manual_backup(self):
        """手动备份（修复版）"""
        if not self.backup_manager:
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 忙碌状态
        QCoreApplication.processEvents()  # 强制更新UI
        
        try:
            # 直接执行备份，不创建线程
            backup_path = self.backup_manager.create_backup("manual")
            
            # 隐藏进度条
            self.progress_bar.setVisible(False)
            
            if backup_path:
                # 获取文件大小
                file_size = backup_path.stat().st_size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                
                QMessageBox.information(
                    self, "成功", 
                    f"✅ 备份创建成功\n"
                    f"文件：{backup_path.name}\n"
                    f"大小：{size_str}\n"
                    f"耗时：{self.backup_manager.last_backup_time:.3f} 秒"
                )
            else:
                QMessageBox.critical(self, "错误", "❌ 备份创建失败")
        except Exception as e:
            self.progress_bar.setVisible(False)
            self._show_error("备份失败", str(e))
    
    def _backup_finished(self, backup_path):
        """备份完成（不再使用）"""
        pass
    
    def _auto_backup(self):
        """自动备份"""
        if self.backup_manager:
            self.backup_manager.create_backup("auto")
    
    def _start_auto_backup(self):
        """启动自动备份"""
        self.auto_backup_timer.start(3600000)
    
    def _show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self.user_manager, self.current_user_id, self)
        if dialog.exec():
            self._load_user_settings()
    
    def _load_user_settings(self):
        """加载用户设置"""
        if self.current_user_id:
            settings = self.user_manager.get_user_settings(self.current_user_id)
            
            if self.backup_manager:
                self.backup_manager.max_backups = settings.get("max_backups", 30)
            
            # 应用列表排序设置
            sort_mode = settings.get("list_sort_mode", SchedulingRecordModel.SORT_NEWEST_FIRST)
            self.records_model.set_sort_mode(sort_mode)
    
    def _load_settings(self):
        """加载程序设置"""
        settings = QSettings("SchedulingSystem", "MainWindow")
        
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """保存程序设置"""
        settings = QSettings("SchedulingSystem", "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
    
    def _show_error(self, title: str, message: str):
        """显示错误消息"""
        QMessageBox.critical(self, title, message)
    
    def closeEvent(self, event):
        """关闭事件"""
        self._save_settings()
        self.user_manager.db_pool.close_all()
        event.accept()

    def _refresh_stats(self):
        """刷新标识统计信息"""
        if not self.category_manager:
            return
        
        # 显示正在刷新状态
        self.refresh_stats_btn.setEnabled(False)
        self.refresh_stats_btn.setText("⏳ 刷新中...")
        self.status_bar.showMessage("正在刷新标识统计...", 2000)
        
        # 使用 QTimer.singleShot 让 UI 有机会更新
        QTimer.singleShot(100, self._do_refresh_stats)

    def _do_refresh_stats(self):
        """实际执行刷新统计"""
        try:
            # 重新加载所有标识
            self._load_categories()
            
            # 重新加载标识统计信息
            if self.category_manager:
                stats = self.category_manager.get_category_stats()
                self._update_stats_table(stats)
            
            # 更新当前选中的标识信息
            self._update_category_stats()
            
            # 重新计算时间间隔
            self._calculate_interval()
            
            # 强制界面重绘
            self.stats_table.viewport().update()
            
            self.status_bar.showMessage("✅ 标识统计已刷新", 3000)
            
        except Exception as e:
            print(f"刷新统计失败: {e}")
            self._show_error("刷新失败", str(e))
        finally:
            # 恢复按钮状态
            self.refresh_stats_btn.setEnabled(True)
            self.refresh_stats_btn.setText("🔄 刷新统计")

class RecordEditDialog(QDialog):
    """记录编辑对话框"""
    
    def __init__(self, db_path: str, categories: Dict[int, Dict], record: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.categories = categories
        self.record = record
        self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 编辑记录")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                selection-color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        
        self._setup_ui()
        self._load_record()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.category_combo = QComboBox()
        for cat_id, cat in self.categories.items():
            self.category_combo.addItem(cat['name'], cat_id)
            index = self.category_combo.count() - 1
            self.category_combo.setItemData(index, QColor(cat['color']), Qt.ForegroundRole)
            self.category_combo.setItemData(index, QBrush(QColor(cat['color']).lighter(160)), Qt.BackgroundRole)
        form_layout.addRow("标识:", self.category_combo)
        
        self.record_date = QDateEdit()
        self.record_date.setCalendarPopup(True)
        form_layout.addRow("记录日期:", self.record_date)
        
        self.record_time = QTimeEdit()
        form_layout.addRow("记录时间:", self.record_time)
        
        self.content_edit = QTextEdit()
        self.content_edit.setMaximumHeight(100)
        form_layout.addRow("内容:", self.content_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        form_layout.addRow("备注:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_record(self):
        """加载记录数据"""
        category_id = self.record.get("category_id")
        index = self.category_combo.findData(category_id)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        self.record_date.setDate(QDate.fromString(
            self.record["record_date"], "yyyy-MM-dd"
        ))
        self.record_time.setTime(QTime.fromString(
            self.record["record_time"], "hh:mm:ss"
        ))
        self.content_edit.setText(self.record["content"])
        self.notes_edit.setText(self.record.get("notes", ""))
    
    def accept(self):
        """确认"""
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "警告", "内容不能为空")
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            QMessageBox.warning(self, "警告", "请选择标识")
            return
        
        try:
            conn = DatabaseConnectionPool().get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE scheduling_records
                SET category_id = ?, record_date = ?, record_time = ?, 
                    content = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                category_id,
                self.record_date.date().toString("yyyy-MM-dd"),
                self.record_time.time().toString("hh:mm:ss"),
                content,
                self.notes_edit.toPlainText(),
                self.record["id"]
            ))
            
            conn.commit()
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新失败：{e}")

class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, user_manager: UserManager, user_id: int, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.user_id = user_id
        self.setWindowTitle(f"{ProjectInfo.get_full_name()} - 系统设置")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        # 设置马卡龙背景色和文字颜色
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {MacaronColors.NEUTRAL_CREAM.name()};
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QLabel {{
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QPushButton {{
                background-color: {MacaronColors.PINK_COTTON.name()};
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: {MacaronColors.TEXT_DARK.name()};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {MacaronColors.PINK_SAKURA.name()};
            }}
            QPushButton:pressed {{
                background-color: {MacaronColors.PINK_ROSE.name()};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {MacaronColors.GREEN_MINT.name()};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QSpinBox, QCheckBox, QRadioButton, QComboBox {{
                background-color: white;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 5px;
                padding: 5px;
                color: {MacaronColors.TEXT_DARK.name()};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {MacaronColors.GREEN_MINT.name()};
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {MacaronColors.NEUTRAL_CARAMEL.name()};
                border-radius: 9px;
                background-color: white;
            }}
            QRadioButton::indicator:checked {{
                background-color: {MacaronColors.GREEN_MINT.name()};
                border: 1px solid {MacaronColors.GREEN_MINT.name()};
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {MacaronColors.TEXT_DARK.name()};
                selection-background-color: {MacaronColors.PURPLE_LAVENDER.name()};
                selection-color: {MacaronColors.TEXT_DARK.name()};
            }}
        """)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 列表排序设置组
        sort_group = QGroupBox("📋 列表排序设置")
        sort_layout = QVBoxLayout(sort_group)
        sort_layout.setSpacing(10)
        
        self.sort_newest_first = QRadioButton("最新的在前面（日期降序）")
        self.sort_newest_first.setChecked(True)
        sort_layout.addWidget(self.sort_newest_first)
        
        self.sort_oldest_first = QRadioButton("旧的在前面（日期升序）")
        sort_layout.addWidget(self.sort_oldest_first)
        
        # 添加说明标签
        sort_desc = QLabel("说明：\n• 最新的在前面：新添加的记录显示在最上面\n• 旧的在前面：最早添加的记录显示在最上面")
        sort_desc.setStyleSheet(f"""
            QLabel {{
                background-color: {MacaronColors.NEUTRAL_ALMOND.name()};
                padding: 8px;
                border-radius: 5px;
                color: {MacaronColors.TEXT_MUTED.name()};
                font-size: 11px;
            }}
        """)
        sort_desc.setWordWrap(True)
        sort_layout.addWidget(sort_desc)
        
        layout.addWidget(sort_group)
        
        # 备份设置组
        backup_group = QGroupBox("💾 备份设置")
        backup_layout = QFormLayout(backup_group)
        backup_layout.setSpacing(10)
        
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        self.max_backups_spin.setValue(30)
        backup_layout.addRow("最大备份数量:", self.max_backups_spin)
        
        layout.addWidget(backup_group)
        
        # 显示设置组
        display_group = QGroupBox("🎨 显示设置")
        display_layout = QFormLayout(display_group)
        display_layout.setSpacing(10)
        
        self.auto_refresh_check = QCheckBox("自动刷新数据")
        display_layout.addRow("", self.auto_refresh_check)
        
        layout.addWidget(display_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_settings(self):
        """加载设置"""
        settings = self.user_manager.get_user_settings(self.user_id)
        
        # 加载列表排序设置
        sort_mode = settings.get("list_sort_mode", SchedulingRecordModel.SORT_NEWEST_FIRST)
        if sort_mode == SchedulingRecordModel.SORT_NEWEST_FIRST:
            self.sort_newest_first.setChecked(True)
        else:
            self.sort_oldest_first.setChecked(True)
        
        # 加载备份设置
        self.max_backups_spin.setValue(settings.get("max_backups", 30))
        
        # 加载显示设置
        self.auto_refresh_check.setChecked(settings.get("auto_refresh", False))
    
    def accept(self):
        """确认"""
        # 获取排序模式
        if self.sort_newest_first.isChecked():
            sort_mode = SchedulingRecordModel.SORT_NEWEST_FIRST
        else:
            sort_mode = SchedulingRecordModel.SORT_OLDEST_FIRST
        
        settings = {
            "list_sort_mode": sort_mode,
            "max_backups": self.max_backups_spin.value(),
            "auto_refresh": self.auto_refresh_check.isChecked()
        }
        
        self.user_manager.save_user_settings(self.user_id, settings)
        
        # 应用设置到主窗口
        if hasattr(self.parent(), "records_model"):
            self.parent().records_model.set_sort_mode(sort_mode)
            self.parent()._load_records()  # 重新加载以应用排序
        
        if hasattr(self.parent(), "backup_manager"):
            self.parent().backup_manager.max_backups = settings["max_backups"]
            self.parent().backup_manager.save_settings()
        
        super().accept()

def main():
    """主函数"""
    debug_mode = "--debug" in sys.argv
    
    app = QApplication(sys.argv)
    app.setApplicationName(ProjectInfo.NAME)
    app.setApplicationVersion(ProjectInfo.VERSION)
    app.setOrganizationName("SchedulingSystem")
    app.setOrganizationDomain("github.com/duma520")
    
    app.setStyle("Fusion")
    
    window = MainWindow(debug_mode)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()