from PIL import Image, ImageDraw

def round_corners(image, radius, color):
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius, fill=255)
    result = Image.new("RGBA", image.size, color)
    result.paste(image, (0, 0), mask)
    return result