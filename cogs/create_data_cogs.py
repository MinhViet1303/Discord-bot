from nextcord.ext import commands
import mysql.connector

from cogs.g_def import connect_main_db, connect_db


# Hàm tạo database "main" và bảng "user_data" nếu chưa tồn tại
async def create_main_db():
    main_connection = await connect_db()  # Kết nối đến máy chủ MySQL mà không chọn cơ sở dữ liệu cụ thể
    main_cursor = main_connection.cursor()

    try:
        main_cursor.execute("CREATE DATABASE IF NOT EXISTS main")
        main_connection.commit()
        if main_cursor.rowcount > 0:
            print("===========================")
            print("---- Đã tạo database 'main'")

        main_cursor.execute("USE main")  # Chọn cơ sở dữ liệu "main" để tạo bảng
        main_cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in main_cursor.fetchall()]

        if "global_user_data" not in existing_tables:
            main_cursor.execute("""
                CREATE TABLE IF NOT EXISTS global_user_data (
                    db_g_user_id VARCHAR(255) PRIMARY KEY,
                    db_g_user_name VARCHAR(255),
                    db_luck INT DEFAULT 0,                    
                    db_temp_luck INT DEFAULT 0,                    
                    db_exp FLOAT DEFAULT 0,
                    db_level INT DEFAULT 0,
                    db_exp_need FLOAT DEFAULT 0,
                    db_wallet FLOAT DEFAULT 0,
                    db_bank FLOAT DEFAULT 0,
                    db_last_daily DATETIME DEFAULT None,
                    db_last_random_luck DATETIME DEFAULT None,
                    db_last_random_temp_luck DATETIME DEFAULT None,
                    db_streak_daily INT DEFAULT 0
                )
            """)
            main_connection.commit()
            print("-- Đã tạo bảng 'global_user_data' cho database 'main'")
        if "utity" not in existing_tables:
            main_cursor.execute("""
                CREATE TABLE IF NOT EXISTS utity (
                    db_utity_id VARCHAR(255),
                    db_utity_name VARCHAR(255) PRIMARY KEY,
                    db_utity_value VARCHAR(255) DEFAULT NULL,
                    db_utity_boolean TINYINT(1) DEFAULT 0
                )
            """)
            
            main_connection.commit()
            print("-- Đã tạo bảng 'utity' cho database 'main'")
        
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
        # Kiểm tra xem user_id đã tồn tại trong db_g_user_id hay chưa
        main_cursor.execute('SELECT db_g_user_id FROM global_user_data WHERE db_g_user_id = %s', (user_id,))
        existing_user = main_cursor.fetchone()

        if existing_user is None:
            # Nếu user_id chưa tồn tại trong user_data, ghi thông tin cần thiết vào userlist
            luck = 0
            temp_luck = 0
            exp = 0
            level = 0
            exp_needed = 10
            wallet = 0
            bank = 0
            last_daily = None
            last_luck = None
            last_temp_luck = None
            streak_daily = 0

            main_cursor.execute("""INSERT INTO global_user_data (db_g_user_id, db_g_user_name, db_luck, db_temp_luck, db_exp, db_level, db_exp_need, db_wallet, db_bank, db_last_daily, db_last_random_luck, db_last_random_temp_luck, db_streak_daily)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, user_name, luck, temp_luck, exp, level, exp_needed, wallet, bank, last_daily, last_luck, last_temp_luck, streak_daily))
            main_connection.commit()

        # Tạo database mới bằng user_id
        db_name = f"user_{user_id}"
        main_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        main_connection.commit()
        # Kiểm tra kết quả của câu lệnh CREATE DATABASE
        if main_cursor.rowcount > 0:
            print("======================================")
            print(f"---- Đã tạo database '{db_name}'")

        user_connection = await connect_db(db_name)
        user_cursor = user_connection.cursor()
        
        user_cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in user_cursor.fetchall()]
        
        if "user_data" not in existing_tables:
            user_cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_data (
                    db_user_id VARCHAR(255) PRIMARY KEY,
                    db_user_name VARCHAR(255)
                )
            """)
            user_cursor.execute("""INSERT IGNORE INTO user_data (db_user_id, db_user_name) VALUES (%s, %s)""", (user_id, user_name))
            user_connection.commit()
            print (f"-- Đã tảo bảng 'user_data' cho database {db_name}")
        
        if "user_inventory" not in existing_tables:
            user_cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    db_item_id VARCHAR(255) PRIMARY KEY,
                    db_item_number INT
                )
            """)
            user_connection.commit()
            print (f"-- Đã tảo bảng 'user_inventory' cho database {db_name}")
        
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
    finally:
        if user_connection:
            user_cursor.close()
            user_connection.close()
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