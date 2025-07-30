from PIL import Image

LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
def preproces_resize_image(resize_mode: int, im: Image.Image, w: int, h: int):
    if resize_mode == 0:
        res = im.resize((w, h), LANCZOS)
    elif resize_mode == 1:
        ratio = w / h
        src_ratio = im.width / im.height
        src_w = w if ratio > src_ratio else im.width * h // im.height
        src_h = h if ratio <= src_ratio else im.height * w // im.width
        resized = im.resize((src_w, src_h), LANCZOS)
        res = Image.new("RGB", (w, h))
        res.paste(resized, box=(w // 2 - src_w // 2, h // 2 - src_h // 2))
    else:
        ratio = w / h
        src_ratio = im.width / im.height
        src_w = w if ratio < src_ratio else im.width * h // im.height
        src_h = h if ratio >= src_ratio else im.height * w // im.width
        resized = im.resize((src_w, src_h), LANCZOS)
        res = Image.new("RGB", (w, h))
        res.paste(resized, box=(w // 2 - src_w // 2, h // 2 - src_h // 2))

        if ratio < src_ratio:
            fill_h = h // 2 - src_h // 2
            if fill_h > 0:
                res.paste(resized.resize((w, fill_h), box=(0, 0, w, 0)), box=(0, 0))
                res.paste(resized.resize((w, fill_h), box=(0, resized.height, w, resized.height)), box=(0, fill_h + src_h))
        elif ratio > src_ratio:
            fill_w = w // 2 - src_w // 2
            if fill_w > 0:
                res.paste(resized.resize((fill_w, h), box=(0, 0, 0, h)), box=(0, 0))
                res.paste(resized.resize((fill_w, h), box=(resized.width, 0, resized.width, h)), box=(fill_w + src_w, 0))
    return res
    