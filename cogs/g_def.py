import mysql.connector
import nextcord
from nextcord.ext import commands
import datetime
import pytz

from config import hostname,password

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)


# Define một hàm để lấy thời gian reset_daily
async def get_reset_daily_time():
    # Tạo múi giờ +7
    tz = pytz.timezone('Asia/Ho_Chi_Minh')  # Điều chỉnh múi giờ tùy theo vị trí của bạn
    
    # Lấy thời gian hiện tại và đặt giờ thành 12:00 trưa
    now = datetime.datetime.now(tz)
    reset_daily = now.replace(hour=12, minute=0, second=0, microsecond=0)
    
    # Nếu thời gian hiện tại đã vượt qua thời gian reset_daily, thì cộng thêm 1 ngày
    if now >= reset_daily:
        reset_daily += datetime.timedelta(days=1)
    
    return now, reset_daily

# Hàm kết nối đến cơ sở dữ liệu MySQL
async def connect_db(db_name=None):
    try:
        conn = await bot.loop.run_in_executor(None, lambda: mysql.connector.connect(
            host=hostname,
            user="root",
            password=password,
            port=1300,
            database=db_name
        ))
        if conn is None:
            return None
        else:
            return conn
    except mysql.connector.Error as err:
        print(f"Lỗi khi kết nối đến database: {err}")
        return None

async def connect_main_db():
    try:
        conn = await bot.loop.run_in_executor(None, lambda: mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            port=1300,
            database="main"
        ))
        if conn is None:
            return None
        else:
            return conn
    except mysql.connector.Error as err:
        print(f"Lỗi khi kết nối đến database: {err}")
        return None