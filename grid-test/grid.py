from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

def draw_numbered_grid(image_path, square_size=100, line_color='#00b140', text_color='black', font_size=13):
    # Open the input image
    img = Image.open(image_path).convert('RGBA')

    # Create a new image with white background
    draw_img = Image.new('RGBA', img.size, color=(255, 255, 255, 0))

    # Draw grid lines
    draw = ImageDraw.Draw(draw_img)
    for x in range(0, img.width, square_size):
        draw.line([(x, 0), (x, img.height)], fill=(int(line_color.lstrip('#')[0:2], 16),
                                                   int(line_color.lstrip('#')[2:4], 16),
                                                   int(line_color.lstrip('#')[4:6], 16),
                                                   255), width=2)
    for y in range(0, img.height, square_size):
        draw.line([(0, y), (img.width, y)], fill=(int(line_color.lstrip('#')[0:2], 16),
                                                  int(line_color.lstrip('#')[2:4], 16),
                                                  int(line_color.lstrip('#')[4:6], 16),
                                                  255), width=2)

    count = 1

    # Draw numbered squares
    font = ImageFont.truetype("arial.ttf", font_size)
    for x in range(0, img.width, square_size):
        for y in range(0, img.height, square_size):
            text = str(count)

            draw.rectangle([x+10, y+10, x+45, y+30],
                           fill=(255, 255, 255, 255))

            draw.text((x+15, y+10), text, fill=(0, 0, 0, 255), font=font)

            count += 1

    # Paste the grid image onto the original image
    img.paste(draw_img, mask=draw_img)

    return img

# Usage
input_image = "windows-powerpoint-cropped-512.png"
output_image = draw_numbered_grid(input_image)

# Save the result
output_image.save("{}-grid.png".format(Path(input_image).stem))
