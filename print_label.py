from PIL import Image, ImageDraw, ImageFont
from barcode.writer import ImageWriter
from brother_ql.devicedependent import models, label_sizes, label_type_specs, DIE_CUT_LABEL, ENDLESS_LABEL, ROUND_DIE_CUT_LABEL
from brother_ql.backends import available_backends, backend_factory
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster
import barcode
import sys

def generate_barcode(value):
    # Generate barcode
    Code128 = barcode.get_barcode_class('code128')
    ean = Code128(value, writer=ImageWriter())
    barcode_image = ean.save('barcode')
    return barcode_image

def create_image_with_text_and_barcode(description, barcode_number):
    # Create an image with given dimensions
    width, height = 590, 271
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Add description text
    try:
        font = ImageFont.truetype('arial.ttf', size=30)
    except IOError:
        print("Failed to load font")
        font = ImageFont.load_default()

    text = description
    left, top, right, bottom = draw.textbbox((0, 0), text, font)
    textwidth = right - left
    textheight = bottom - top

    # Calculate X, Y coordinates of the text
    x = (width - textwidth) / 2
    y = 10
    draw.text((x, y), text, font=font, fill="black")

    # Generate barcode and paste it under the text
    barcode_image_path = generate_barcode(barcode_number)
    barcode_image = Image.open(barcode_image_path)

    # Calculate room left for barcode
    desired_barcode_height = height - (textheight + 5)

    barcode_width = 400
    ratio = desired_barcode_height / barcode_image.height

    # Resize the barcode image
    barcode_image = barcode_image.resize((int(barcode_image.width * ratio), int(desired_barcode_height)))

    # Coordinates to paste the barcode
    bx = (width - barcode_image.width) // 2
    by = textheight + 20

    image.paste(barcode_image, (bx, by))

    # Save or display the result
    image.save("output_image.png")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("""Usage: 

	`python3 print_label.py "{label description}" "{13 digit barcode #}"`

e.g.

	`python3 print_label.py "USB Mouse" "0000000012345"
""")
        sys.exit()

    description = sys.argv[1]
    barcode_number = sys.argv[2]

    if len(barcode_number) != 13:
        print("Barcode must contain exactly 13 digits")
        sys.exit()

    # Execute the function to create the image
    create_image_with_text_and_barcode(description, barcode_number)
    qlr = BrotherQLRaster('QL-800')
    qlr.exception_on_warning = True

    # TODO(jimmy): See if you can specify a custom label size programatically
    # ~/.local/bin/brother_ql -b linux_kernel -p /dev/usb/lp0 -m QL-800 print -l 54x29 output_image.png
    instructions = convert(qlr=qlr, cut=True, label='54x29', images=['output_image.png'])
    send(instructions=instructions, printer_identifier='/dev/usb/lp0', backend_identifier='linux_kernel', blocking=True)
