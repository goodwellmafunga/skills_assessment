import base64
from io import BytesIO
import qrcode


def qr_data_url(data: str) -> str:
    img = qrcode.make(data)
    buff = BytesIO()
    img.save(buff, format="PNG")
    b64 = base64.b64encode(buff.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"
