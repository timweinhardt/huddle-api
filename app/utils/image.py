import base64
import io


def parse_base64_image(base64_string: str) -> tuple[io.BytesIO, str, str]:
    """
    Decode a base64 string (with or without data url prefix)
    and return an in-memory file-like object and its content type, ready for S3 upload.
    Returns (file_like_object, content_type, extension)
    """
    # Check and parse base64 header if present
    if "," in base64_string and base64_string.strip().startswith("data:"):
        header, b64_data = base64_string.split(",", 1)
        # Example header: data:image/png;base64
        content_type = None
        ext = None
        if ";" in header:
            ctype = header.split(":", 1)[1].split(";", 1)[0]
            content_type = ctype
            if "/" in ctype:
                ext = ctype.split("/")[1]
        else:
            content_type = "application/octet-stream"
            ext = None
    else:
        b64_data = base64_string
        content_type = "application/octet-stream"
        ext = None

    image_bytes = base64.b64decode(b64_data)
    buf = io.BytesIO(image_bytes)
    return buf, content_type, ext
