import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
import io
import os

def generate_qr_code(data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "logo_no_bg.png")
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.ERROR_CORRECT_H,
        box_size = 4,
        border = 4,
        image_factory = StyledPilImage,
        mask_pattern = None,
    )
    print(data)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(
        color_mask=RadialGradiantColorMask(
            back_color=(255, 255, 255),
            edge_color=(0, 0, 0),
            center_color=(10, 99, 161),
        ),
        module_drawer=CircleModuleDrawer(),
        embeded_image_path=logo_path,
    )
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()