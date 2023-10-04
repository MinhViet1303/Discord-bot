from PIL import Image, ImageDraw, ImageFont
import re
import requests

from make_image.img_g_def import round_corners
from cogs.g_def import format_money

async def make_level_img(avt, user_name, name_color, lv, xp, xp_need):
    
    default_text_font = ImageFont.truetype("assets/font/PatrickHand-Regular.ttf", 40)
    user_name_font = ImageFont.truetype("assets/font/PatrickHand-Regular.ttf", 60)    
    int_font = ImageFont.truetype("assets/font/StyleScript-Regular.ttf",60)
    exp_font = ImageFont.truetype("assets/font/StyleScript-Regular.ttf",45)
    percent_font = ImageFont.truetype("assets/font/StyleScript-Regular.ttf",80)
    
    background = Image.open("assets/level/background_1.png")
    background = background.convert("RGBA")
    background = round_corners(background, 30, (0, 0, 0, 0))
    
    draw = ImageDraw.Draw(background)
    
    response = requests.get(avt, stream=True)
    
    avatar = Image.open(response.raw)
    # avatar = Image.open("assets/level/avatar.png")    
    avatar = avatar.convert("RGBA")
    avatar = avatar.resize((300, 300))
    avatar = round_corners(avatar, 20, (0, 0, 0, 0))
    avatar_x_position = 25
    avatar_y_position = 25
    
    transparent_image = Image.open("assets/level/transparent_image.png")
    transparent_image = transparent_image.convert("RGBA")
    transparent_image = transparent_image.resize((950, 350))
    transparent_image = round_corners(transparent_image, 30, (0, 0, 0, 0))
    transparent_image_position = (25, background.size[1] - transparent_image.size[1] - 25)
    
    transparent_image.paste(avatar, (avatar_x_position, avatar_y_position), avatar)
    background.paste(transparent_image, transparent_image_position, transparent_image)
    
    name_text = f"User name: "  
    name_text_color = (255, 255, 255) 
    name_text_x_position = avatar_x_position + 335  
    name_text_y_position = 50
    draw.text((name_text_x_position, name_text_y_position), name_text, fill=name_text_color, font=default_text_font)
    
    name = user_name
    name_color = name_color
    name_x_position = name_text_x_position + 170
    name_y_position = name_text_y_position - 20
    draw.text((name_x_position, name_y_position), name, fill=name_color, font=user_name_font)    
    
    level_text = f"Level: "  
    level_text_color = (255, 255, 255) 
    level_x_position = avatar_x_position + 335  
    level_y_position = 120
    draw.text((level_x_position, level_y_position), level_text, fill=level_text_color, font=default_text_font)
    
    level_number = str(lv)  
    number_color = (255, 255, 0) 
    level_number_x_position = level_x_position + 90  
    level_number_y_position = level_y_position - 20
    draw.text((level_number_x_position, level_number_y_position), level_number, fill=number_color, font=int_font)
    
    xp = 1 if xp == 0 else xp
    progress = xp / xp_need if xp_need > 0 else 0
    progress = 1 if progress > 1 else progress
    
    xp_bar = Image.open("assets/level/xp_bar.png")
    xp_bar_width = int(xp_bar.width * progress)
    xp_bar_width = 1 if xp_bar_width < 1 else xp_bar_width
    xp_bar = xp_bar.resize((xp_bar_width,40))
    xp_bar_x_position = avatar_x_position + 330
    xp_bar_y_position = 210
    
    background.paste(xp_bar, (xp_bar_x_position, xp_bar_y_position), xp_bar)
    
    percent_text = str(round(progress*100, 1) if progress < 1 else round(progress*100)) + "%"  
    number_color = (255, 128, 0) 
    percent_x_position = xp_bar_x_position + 210
    percent_y_position = xp_bar_y_position - 60
    if '.0' in percent_text:
        percent_text = re.sub(r'\.0\b', '', percent_text)
        percent_x_position = xp_bar_x_position + 230
    draw.text((percent_x_position, percent_y_position), percent_text, fill=number_color, font=percent_font)
    
    exp_text = f"Exp: " 
    text_color = (255, 255, 255) 
    exp_text_x_position = avatar_x_position + 330 
    exp_text_y_position = xp_bar_y_position + 40
    draw.text((exp_text_x_position, exp_text_y_position), exp_text, fill=text_color, font=default_text_font)
    
    xp_number, xp_number_text = format_money(xp)
    xp_need_number, xp_need_number_text = format_money(xp_need)
    
    if xp and xp_need < 10000:
        exp_number = str(f"{xp_number}/{xp_need_number}")
        exp_number_color = (0, 255, 255)
        exp_number_x_position = exp_text_x_position + 65  
        exp_number_y_position = exp_text_y_position 
        draw.text((exp_number_x_position, exp_number_y_position), exp_number, fill=exp_number_color, font=exp_font)
    else:
        exp_number_text = str(f"{xp_number_text} / {xp_need_number_text}")
        number_color = (255, 255, 0)
        exp_number_text_x_position = exp_text_x_position + 65  
        exp_number_text_y_position = exp_text_y_position 
        draw.text((exp_number_text_x_position, exp_number_text_y_position), exp_number_text, fill=number_color, font=exp_font)
        
        exp_number = str(f"{xp_number}/{xp_need_number}")
        exp_number_color = (0, 255, 255)
        exp_number_x_position = exp_text_x_position + 65  
        exp_number_y_position = exp_text_y_position + 55
        if xp or xp_need > 10000000000:
            exp_number_x_position = exp_text_x_position  
        draw.text((exp_number_x_position, exp_number_y_position), exp_number, fill=exp_number_color, font=exp_font)
    
    background.save("make_image/level.png")
