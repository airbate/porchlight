"""Procedural doorstep frames for offline demos and tests.

These are clearly-labelled SYNTHETIC illustrations (not camera footage). They
exist so the full pipeline — snapshot storage, Bedrock multimodal analysis,
alert rules, dashboard thumbnails — runs end-to-end with zero hardware and
zero credentials. Once the Ring sandbox test account is wired (M0), real
doorbell frames replace these at the ingest boundary and nothing downstream
changes.
"""

import io

from PIL import Image, ImageDraw

FRAME_W, FRAME_H = 640, 480

# Palette: warm evening porch
_WALL = (214, 196, 170)
_DOOR = (96, 66, 47)
_FLOOR = (120, 104, 88)
_SKIN = (224, 190, 160)
_SHIRT = (70, 90, 130)
_JEANS = (60, 62, 78)
_BOX = (150, 108, 64)
_TAPE = (222, 214, 198)


def _porch(draw: ImageDraw.ImageDraw, *, branch_shadow: bool = False) -> None:
    draw.rectangle([0, 0, FRAME_W, 340], fill=_WALL)  # wall
    draw.rectangle([0, 340, FRAME_W, FRAME_H], fill=_FLOOR)  # porch floor
    draw.rectangle([60, 40, 220, 340], fill=_DOOR)  # door
    draw.ellipse([200, 180, 214, 194], fill=(230, 200, 120))  # knob
    draw.rectangle([260, 80, 420, 100], fill=(180, 160, 140))  # trim
    draw.ellipse([470, 120, 520, 170], fill=(250, 240, 210))  # porch light glow
    if branch_shadow:  # diagonal shadows from an overhanging tree
        for x in range(-40, FRAME_W, 90):
            draw.polygon([(x, 340), (x + 28, 340), (x + 90, FRAME_H), (x + 62, FRAME_H)],
                         fill=(105, 92, 78))


def _person(draw: ImageDraw.ImageDraw, cx: int, foot_y: int, *, fallen: bool = False) -> None:
    if fallen:  # lying on the porch floor
        draw.rectangle([cx - 70, foot_y - 22, cx + 50, foot_y + 6], fill=_SHIRT)  # torso
        draw.ellipse([cx + 50, foot_y - 20, cx + 82, foot_y + 12], fill=_SKIN)  # head
        draw.rectangle([cx - 108, foot_y - 14, cx - 66, foot_y + 4], fill=_JEANS)  # legs
        return
    draw.ellipse([cx - 16, foot_y - 130, cx + 16, foot_y - 98], fill=_SKIN)  # head
    draw.rectangle([cx - 22, foot_y - 100, cx + 22, foot_y - 34], fill=_SHIRT)  # torso
    draw.rectangle([cx - 16, foot_y - 34, cx - 4, foot_y], fill=_JEANS)  # legs
    draw.rectangle([cx + 4, foot_y - 34, cx + 16, foot_y], fill=_JEANS)


def render_frame(scenario: str) -> bytes:
    """Render one synthetic doorstep frame for the given scenario as JPEG bytes."""
    img = Image.new("RGB", (FRAME_W, FRAME_H))
    draw = ImageDraw.Draw(img)

    if scenario == "visitor":
        _porch(draw)
        _person(draw, 300, 330)
        draw.rectangle([280, 262, 322, 300], fill=(240, 238, 232))  # clipboard
    elif scenario == "package_delivery":
        _porch(draw)
        draw.rectangle([350, 296, 430, 340], fill=_BOX)  # box on the mat
        draw.rectangle([350, 314, 430, 322], fill=_TAPE)
        _person(draw, 480, 340)  # courier walking away
    elif scenario == "loitering":
        _porch(draw, branch_shadow=True)
        _person(draw, 250, 336)  # standing close to the door, no clear purpose
    elif scenario == "fall_suspected":
        _porch(draw)
        _person(draw, 300, 420, fallen=True)  # on the ground by the steps
    else:  # ambient_noise — empty porch with movement shadows
        _porch(draw, branch_shadow=True)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()
