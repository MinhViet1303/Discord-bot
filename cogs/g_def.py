import mysql.connector
import nextcord
from nextcord.ext import commands
import datetime
import pytz
import locale
import humanize

from config import hostname,password

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

async def format_money(value):
    value = float(value)
    if value.is_integer():
        x = "%.0f"
    elif value.is_decimal():
        x = "%.2f"
    formatted_value = locale.format_string(x, value, grouping=True)
    formatted_text_value = humanize.intword(value,x)
    formatted_text_value = formatted_text_value.replace(" million", " triệu").replace(" billion", " tỷ")
    if value < 100000:
        formatted_text_value = None
    return formatted_value, formatted_text_value

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

async def load_data(table, where, where_value, select):
    main_connection = await connect_main_db()
    main_cursor = main_connection.cursor()
    try:
        main_cursor.execute(f"SELECT {', '.join(select)} FROM {table} WHERE {where} = {where_value}")
        result = main_cursor.fetchone()
        
        return result
    finally:
        if main_connection:
            main_cursor.close()
            main_connection.close()
            
async def update_global_data(data, value_data, user_id):
    main_connection = await connect_main_db() 
    main_cursor = main_connection.cursor()
    main_cursor.execute(f"UPDATE global_user_data SET {data} = %s WHERE db_g_user_id = %s", (value_data, user_id))
    main_connection.commit()
    main_cursor.close()
    main_connection.close()