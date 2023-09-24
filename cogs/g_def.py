import mysql.connector
import nextcord
from nextcord.ext import commands
import json
import os

from config import password

intents = nextcord.Intents().all()
intents.typing = True
bot = commands.Bot(command_prefix=["!"], intents=intents)

# Hàm kết nối đến cơ sở dữ liệu MySQL
async def connect_db(db_name=None):
    try:
        conn = await bot.loop.run_in_executor(None, lambda: mysql.connector.connect(
            host="localhost",
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