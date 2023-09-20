from nextcord.ext import commands
import mysql.connector

from cogs.g_def import *


# Hàm tạo database "main" và bảng "user_data" nếu chưa tồn tại
async def create_main_db():
    main_connection = await connect_db()  # Kết nối đến máy chủ MySQL mà không chọn cơ sở dữ liệu cụ thể
    main_cursor = main_connection.cursor()

    try:
        # Kiểm tra xem database "main" đã tồn tại hay chưa
        main_cursor.execute("SHOW DATABASES")
        existing_databases = [db[0] for db in main_cursor.fetchall()]

        if "main" not in existing_databases:
            main_cursor.execute("CREATE DATABASE main")
            main_connection.commit()
            print("Đã tạo database 'main'")

            main_connection.database = "main"  # Chọn cơ sở dữ liệu "main" để tạo bảng "userlist"

            # Tạo bảng "user_data" và các cột tương ứng
            main_cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_data (
                    db_user_id VARCHAR(255) PRIMARY KEY,
                    db_user_name VARCHAR(255),
                    db_exp FLOAT DEFAULT 0,
                    db_level INT DEFAULT 0,
                    db_exp_need FLOAT DEFAULT 0,
                    db_wallet FLOAT DEFAULT 0,
                    db_bank FLOAT DEFAULT 0,
                    db_last_daily DATETIME,
                    db_streak INT DEFAULT 0
                )
            """)
            main_connection.commit()
            print("Đã tạo bảng 'user_data'")
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
    finally:
        if main_connection:
            main_cursor.close()
            main_connection.close()


# Hàm tạo thông tin người dùng và database mới nếu cần
async def create_user_db(user_id, user_name):
    main_connection = await connect_main_db()
    main_cursor = main_connection.cursor()

    try:
        # Kiểm tra xem user_id đã tồn tại trong db_user_id hay chưa
        main_cursor.execute('SELECT db_user_id FROM user_data WHERE db_user_id = %s', (user_id,))
        existing_user = main_cursor.fetchone()

        if existing_user is None:
            # Nếu user_id chưa tồn tại trong user_data, ghi thông tin cần thiết vào userlist
            level = 0
            exp = 0
            exp_needed = 10
            wallet = 0
            bank = 0
            last_daily = None
            streak_daily = 0

            main_cursor.execute("""INSERT INTO user_data (db_user_id, db_user_name, db_exp, db_level, db_exp_need, db_wallet, db_bank, db_last_daily, db_streak_daily)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, user_name, exp, level, exp_needed, wallet, bank, last_daily, streak_daily))
            main_connection.commit()

        # Tạo database mới bằng user_id
        db_name = f"user_{user_id}"
        main_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        main_connection.commit()
        # Kiểm tra kết quả của câu lệnh CREATE DATABASE
        if main_cursor.rowcount > 0:
            print(f"Đã tạo database '{db_name}'")

        user_connection = await connect_db(db_name)
        user_cursor = user_connection.cursor()
        user_cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                db_item_id VARCHAR(255) PRIMARY KEY,
                db_item_number INT
            )
        """)
        user_connection.commit()
        user_cursor.close()
        user_connection.close()
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
    finally:
        if main_connection:
            main_cursor.close()
            main_connection.close()


class Create_data(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        user_id = str(message.author.id)
        user_name = str(message.author.name)
        
        await create_main_db()
        await create_user_db(user_id, user_name)


def setup(bot):
    bot.add_cog(Create_data(bot))