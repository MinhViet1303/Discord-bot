import subprocess
import mysql.connector
import nextcord
from nextcord.ext import commands
import datetime
import pytz
import locale
import humanize
import re
import fileinput

from config import ready_hostname, hostnames, port, password

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def format_money(value):
    value = float(value)
    x = "%.2f"
    if value.is_integer():
        x = "%.0f"
    formatted_value = locale.format_string(x, value, grouping=True)
    formatted_text_value = humanize.intword(value)
    if '.0' in formatted_text_value:
        formatted_text_value = re.sub(r'\.0\b', '', formatted_text_value)
    formatted_text_value = formatted_text_value.replace(" thousand", " nghìn").replace(" million", " triệu").replace(" billion", " tỷ").replace(" trillion", " nghìn tỷ")
    if value < 10000:
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

async def update_config(config, value):
    file_to_edit = 'config.py'
    for line in fileinput.input(file_to_edit, inplace=True):
        if line.startswith(config):
            # Thay đổi giá trị ready_hostname
            if isinstance(value, str):
                print(f'{config} = "{value}"')
            else:
                print(f'{config} = {value}')
        else:
            print(line, end='')

async def test_connect():
    test_connect = await connect_db()
    test_main_connect = await connect_main_db()
    
    restart = 0
    
    if test_connect is not None:
        print("=================")
        print("✅Test connect")
        print("✅Connect_db")
        test_connect.close()
    else: restart = 1
    
    if test_main_connect is not None:
        print("✅Connect_main_db")
        test_main_connect.close()
    else: restart = 1
    
    if restart == 1:
        print("Bot đang khởi động lại...🔄")
        await update_config("is_restart", True)
        subprocess.Popen(["python", "-Xfrozen_modules=off", "main.py"]).wait()

# Hàm kiểm tra kết nối đến các hostname
async def check_hostnames(db_name):
    for hostname in hostnames:
        try:
            conn = await bot.loop.run_in_executor(None, lambda: mysql.connector.connect(
                host=hostname,
                user="root",
                password=password,
                port=port,
                database=db_name
            ))
            if conn is not None:
                await update_config("ready_hostname", hostname)
                print(f"========================================")
                print(f"✅Thành công kết nối mới tới {hostname}")
                print(f"========================================")
            
        except mysql.connector.Error as err:
            print(f"Lỗi khi kết nối đến database {hostname}: {err}")
            print(f"========================================")
            print(f"Tiếp tục lỗi, thử kết khác... 🔄")
    return None

# Hàm kết nối đến cơ sở dữ liệu MySQL
async def connect_db(db_name=None):
    try:
        conn = await bot.loop.run_in_executor(None, lambda: mysql.connector.connect(
            host=ready_hostname,
            user="root",
            password=password,
            port=port,
            database=db_name
        ))
        if conn is None:
            return None
        else:
            return conn
    except mysql.connector.Error as err:
        print("==================")        
        print("Connect_db: ❌🔄")
        print(f"Connect_db gặp lỗi khi kết nối đến database: {err}")
        print(f"Đang thử kết nối mới....")
        await check_hostnames(db_name)
        return None


async def connect_main_db():
    try:
        conn = await bot.loop.run_in_executor(None, lambda: mysql.connector.connect(
            host=ready_hostname,
            user="root",
            password=password,
            port=port,
            database="main"
        ))
        if conn is None:
            return None
        else:
            return conn
    except mysql.connector.Error as err:
        print("Connect_main_db: ❌🔄")
        print(f"Connect_main_db gặp lỗi khi kết nối đến database: {err}")
        print(f"Đang thử kết nối mới....")
        await check_hostnames("main")
        return None


async def load_data(table, where, where_value, select):
    test_connect = await connect_main_db()
    main_cursor = test_connect.cursor()
    try:
        main_cursor.execute(f"SELECT {', '.join(select)} FROM {table} WHERE {where} = {where_value}")
        result = main_cursor.fetchone()
        
        return result
    finally:
        if test_connect:
            main_cursor.close()
            test_connect.close()
            
async def update_global_data(data, value_data, user_id):
    test_connect = await connect_main_db() 
    main_cursor = test_connect.cursor()
    main_cursor.execute(f"UPDATE global_user_data SET {data} = %s WHERE db_g_user_id = %s", (value_data, user_id))
    test_connect.commit()
    main_cursor.close()
    test_connect.close()