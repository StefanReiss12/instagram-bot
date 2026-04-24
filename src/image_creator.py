"""
Criador de imagens — formato 4:5 (1080x1350).
Design rotaciona a cada carrossel via THEMES.
"""
import os
import json
import re
from PIL import Image, ImageDraw, ImageFont

W, H   = 1080, 1350
PAD    = 64

# ── Temas de design ─────────────────────────────────────────────────────────
# Cada tema define paleta de cores e variações de layout.
# A cada carrossel gerado o próximo tema é usado (rotação circular).

THEMES = [
    # 0 — Classic: Amarelo / Preto (original)
    {
        "name":         "classic",
        "accent":       (255, 224,   0),
        "accent_text":  ( 20,  20,  20),
        "bg_light":     (255, 255, 255),
        "bg_dark":      ( 20,  20,  20),
        "text_dark":    ( 20,  20,  20),
        "text_light":   (255, 255, 255),
        "gray":         (120, 120, 120),
        "lgray":        (220, 220, 220),
        "hook_split":   0.42,
        "hook_top":     "accent",   # seção superior do hook: "accent" | "dark"
        "cta_bg":       "dark",     # fundo do CTA: "dark" | "accent"
        "left_w":       370,        # largura da coluna esquerda nos slides de conteúdo
    },
    # 1 — Ocean: Azul Céu / Azul Marinho
    {
        "name":         "ocean",
        "accent":       ( 14, 165, 233),
        "accent_text":  (255, 255, 255),
        "bg_light":     (248, 250, 252),
        "bg_dark":      ( 15,  23,  42),
        "text_dark":    ( 15,  23,  42),
        "text_light":   (248, 250, 252),
        "gray":         (100, 116, 139),
        "lgray":        (203, 213, 225),
        "hook_split":   0.50,
        "hook_top":     "dark",
        "cta_bg":       "accent",
        "left_w":       340,
    },
    # 2 — Forest: Esmeralda / Verde Escuro
    {
        "name":         "forest",
        "accent":       ( 16, 185, 129),
        "accent_text":  (255, 255, 255),
        "bg_light":     (240, 253, 244),
        "bg_dark":      (  6,  78,  59),
        "text_dark":    (  6,  78,  59),
        "text_light":   (240, 253, 244),
        "gray":         ( 75, 130, 100),
        "lgray":        (187, 247, 208),
        "hook_split":   0.38,
        "hook_top":     "accent",
        "cta_bg":       "dark",
        "left_w":       400,
    },
    # 3 — Violet: Roxo / Índigo Profundo
    {
        "name":         "violet",
        "accent":       (139,  92, 246),
        "accent_text":  (255, 255, 255),
        "bg_light":     (250, 245, 255),
        "bg_dark":      ( 30,  27,  75),
        "text_dark":    ( 30,  27,  75),
        "text_light":   (250, 245, 255),
        "gray":         (107,  70, 193),
        "lgray":        (221, 214, 254),
        "hook_split":   0.45,
        "hook_top":     "dark",
        "cta_bg":       "accent",
        "left_w":       350,
    },
    # 4 — Ember: Vermelho / Preto Quente
    {
        "name":         "ember",
        "accent":       (239,  68,  68),
        "accent_text":  (255, 255, 255),
        "bg_light":     (255, 251, 245),
        "bg_dark":      ( 28,  25,  23),
        "text_dark":    ( 28,  25,  23),
        "text_light":   (255, 251, 245),
        "gray":         (120,  90,  80),
        "lgray":        (254, 202, 202),
        "hook_split":   0.55,
        "hook_top":     "accent",
        "cta_bg":       "dark",
        "left_w":       320,
    },
    # 5 — Fire: Laranja / Marrom Escuro
    {
        "name":         "fire",
        "accent":       (249, 115,  22),
        "accent_text":  (255, 255, 255),
        "bg_light":     (255, 247, 237),
        "bg_dark":      ( 67,  20,   7),
        "text_dark":    ( 67,  20,   7),
        "text_light":   (255, 247, 237),
        "gray":         (154,  52,  18),
        "lgray":        (253, 186, 116),
        "hook_split":   0.42,
        "hook_top":     "dark",
        "cta_bg":       "accent",
        "left_w":       380,
    },
]


def _get_next_theme() -> dict:
    """Lê o contador de design, retorna o próximo tema e incrementa o contador."""
    from src.config import OUTPUT_DIR
    counter_path = os.path.join(OUTPUT_DIR, "design_counter.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        with open(counter_path, encoding="utf-8") as f:
            data = json.load(f)
        idx = data.get("next", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        idx = 0
    next_idx = (idx + 1) % len(THEMES)
    with open(counter_path, "w", encoding="utf-8") as f:
        json.dump({"next": next_idx, "last_used": THEMES[idx]["name"]}, f)
    print(f"  [design] Tema: {THEMES[idx]['name']} ({idx + 1}/{len(THEMES)})")
    return THEMES[idx]


# ── Fontes ──────────────────────────────────────────────────────────────────
_BOLD_FONTS = [
    # Windows
    "C:/Windows/Fonts/Roboto-Bold.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    # Linux (Liberation / DejaVu / Ubuntu / Noto)
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
_REGULAR_FONTS = [
    # Windows
    "C:/Windows/Fonts/Roboto-Regular.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]
_IMPACT_FONTS = [
    # Windows
    "C:/Windows/Fonts/impact.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]


def _load_font(paths: list, size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    # Fallback seguro: tenta qualquer .ttf disponível no sistema
    import glob
    for pattern in ["/usr/share/fonts/**/*.ttf", "/usr/local/share/fonts/**/*.ttf"]:
        for p in glob.glob(pattern, recursive=True):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    # Último recurso: fonte bitmap com tamanho aproximado
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _roboto(size, bold=False):
    return _load_font(_BOLD_FONTS if bold else _REGULAR_FONTS, size)


def _impact(size):
    return _load_font(_IMPACT_FONTS, size)


# ── Utilitários de texto ─────────────────────────────────────────────────────
def _wh(draw, text, font):
    text = _safe_text(text)
    try:
        bx = draw.textbbox((0, 0), text, font=font, anchor="lt")
        return bx[2], bx[3]
    except (OSError, ValueError):
        try:
            _find_bad_chars(draw, text, font)
            text = _safe_text(text)
            bx = draw.textbbox((0, 0), text, font=font)
            return bx[2], bx[3]
        except Exception:
            # bitmap font fallback
            w = len(text) * (getattr(font, 'size', 10) // 2 + 2)
            h = getattr(font, 'size', 10) + 4
            return w, h


def _wrap(draw, text, font, max_w):
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if _wh(draw, test, font)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _measure(draw, text, font, max_w, gap=12):
    lines = _wrap(draw, text, font, max_w)
    h = 0
    for i, line in enumerate(lines):
        h += _wh(draw, line, font)[1]
        if i < len(lines) - 1:
            h += gap
    return h


def _txt(draw, text, font, color, x, y, max_w, gap=12):
    lines = _wrap(draw, _safe_text(text), font, max_w)
    cy = y
    for i, line in enumerate(lines):
        draw.text((x, cy), _safe_text(line), font=font, fill=color, anchor="lt")
        _, lh = _wh(draw, line, font)
        cy += lh
        if i < len(lines) - 1:
            cy += gap
    return cy - y


# ── Corpo do slide: parágrafos com justificação ──────────────────────────────

def _get_paras(text, max_paras=4, min_paras=2):
    paras = [p.strip() for p in str(text).split("\n\n") if p.strip()]
    if len(paras) < min_paras and len(paras) > 0:
        expanded = []
        for p in paras:
            parts = [s.strip() for s in p.split("\n") if s.strip()]
            expanded.extend(parts)
        if len(expanded) >= min_paras:
            paras = expanded
    return paras[:max_paras]


def _measure_paras_body(draw, text, font, max_w, line_gap=16, para_gap=52,
                        max_paras=4, min_paras=2):
    paras           = _get_paras(text, max_paras, min_paras)
    ascent, descent = font.getmetrics()
    lh              = ascent + descent
    total           = 0
    for i, p in enumerate(paras):
        lines  = _wrap(draw, p, font, max_w)
        n      = len(lines)
        total += lh * n + line_gap * (n - 1)
        if i < len(paras) - 1:
            total += para_gap
    return total


def _draw_paras_body(draw, text, font, color, x, y, max_w,
                     line_gap=16, para_gap=52, max_paras=4, min_paras=2):
    """
    Justificação completa com baseline anchor para alinhamento perfeito.
    Última linha de cada parágrafo alinhada à esquerda (padrão tipográfico).
    """
    paras           = _get_paras(text, max_paras, min_paras)
    ascent, descent = font.getmetrics()
    lh              = ascent + descent
    cy              = y

    for pi, p in enumerate(paras):
        lines   = _wrap(draw, p, font, max_w)
        n_lines = len(lines)

        for li, line in enumerate(lines):
            words        = line.split()
            is_last_line = (li == n_lines - 1)
            baseline     = cy + ascent

            if not is_last_line and len(words) > 1:
                total_word_w = sum(_wh(draw, w, font)[0] for w in words)
                gap_px       = max(2, (max_w - total_word_w) / (len(words) - 1))
                cx = float(x)
                for j, word in enumerate(words):
                    draw.text((int(cx), baseline), _safe_text(word), font=font, fill=color, anchor="ls")
                    ww, _ = _wh(draw, word, font)
                    cx += ww + (gap_px if j < len(words) - 1 else 0)
            else:
                draw.text((x, baseline), _safe_text(line), font=font, fill=color, anchor="ls")

            cy += lh + line_gap

        cy -= line_gap
        if pi < len(paras) - 1:
            cy += para_gap

    return cy - y


def _fit_paras_body(draw, text, start, fn, max_w, max_h,
                    lg=16, pg=52, max_paras=4, min_paras=2,
                    min_sz=18, step=4):
    sz = start
    while sz >= min_sz:
        f = fn(sz)
        if _measure_paras_body(draw, text, f, max_w, lg, pg, max_paras, min_paras) <= max_h:
            return f
        sz -= step
    return fn(min_sz)


def _fit(draw, text, start, fn, max_w, max_h, gap=12, min_sz=16, step=4):
    sz = start
    while sz >= min_sz:
        f = fn(sz)
        if _measure(draw, text, f, max_w, gap) <= max_h:
            return f
        sz -= step
    return fn(min_sz)


# ── Emoji detection ──────────────────────────────────────────────────────────
def _strip_emoji(text: str) -> str:
    def _ok(c):
        cp = ord(c)
        return (
            0x0020 <= cp <= 0x024F or
            0x2010 <= cp <= 0x206F or
            0x20A0 <= cp <= 0x20CF or
            c in "\n\t"
        )
    return "".join(c for c in str(text) if _ok(c)).strip()


_BAD_CHARS: set = set()


def _safe_text(text: str) -> str:
    if not _BAD_CHARS:
        return text
    return "".join(c for c in text if c not in _BAD_CHARS)


def _find_bad_chars(draw, text, font):
    for c in set(text):
        if c in _BAD_CHARS:
            continue
        try:
            draw.textbbox((0, 0), c, font=font, anchor="lt")
        except OSError:
            _BAD_CHARS.add(c)


# ── Resize/crop ──────────────────────────────────────────────────────────────
def _rcrop(img, w, h):
    sw, sh = img.size
    s      = max(w / sw, h / sh)
    nw, nh = int(sw * s) + 1, int(sh * s) + 1
    img    = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2,
                     (nw - w) // 2 + w, (nh - h) // 2 + h))


# ── Número do slide ───────────────────────────────────────────────────────────
def _num_label(draw, n, total, x, y, color):
    fn  = _roboto(22)
    txt = f"{n:02d} / {total:02d}"
    draw.text((x, y), txt, font=fn, fill=color, anchor="lt")
    return _wh(draw, txt, fn)[1]


# ════════════════════════════════════════════════════════════════════════════
#  SLIDE 1 — CAPA
# ════════════════════════════════════════════════════════════════════════════
def slide_hook(data, total, handle, theme, hook_img=None):
    t       = theme
    bg      = t["bg_light"]
    img     = Image.new("RGB", (W, H), bg)
    d       = ImageDraw.Draw(img)

    SPLIT_Y = int(H * t["hook_split"])

    # Seção superior: accent ou dark conforme o tema
    top_color = t["accent"] if t["hook_top"] == "accent" else t["bg_dark"]
    top_text  = t["accent_text"] if t["hook_top"] == "accent" else t["text_light"]
    d.rectangle([(0, 0), (W, SPLIT_Y)], fill=top_color)

    # Número do slide
    nh = _num_label(d, 1, total, PAD, PAD, top_text)
    y  = PAD + nh + 28

    aw = W - PAD * 2

    headline = _strip_emoji(data.get("headline", ""))
    sub      = _strip_emoji(data.get("subtitle", ""))

    sub_reserve = 80 if sub else 0
    hl_max = SPLIT_Y - y - PAD - sub_reserve
    fh = _fit(d, headline, 82, lambda s: _roboto(s, True), aw, hl_max, gap=30)
    hh = _txt(d, headline, fh, top_text, PAD, y, aw, gap=30)
    y += hh + 44

    if sub:
        # Subtítulo com cor levemente mais suave
        sub_color = _blend(top_text, top_color, 0.35)
        sub_max = SPLIT_Y - y - 10
        fs = _fit(d, sub, 38, lambda s: _roboto(s, False), aw, max(sub_max, 20), gap=8)
        _txt(d, sub, fs, sub_color, PAD, y, aw, gap=8)

    # Seção foto — metade inferior
    photo_h = H - SPLIT_Y
    if hook_img:
        panel = _rcrop(hook_img, W, photo_h)
        img.paste(panel, (0, SPLIT_Y))
        # Faixa de cor na base da foto para transição
        overlay = Image.new("RGBA", (W, 40), (*top_color, 60))
        img.paste(overlay, (0, SPLIT_Y), overlay)
    else:
        d2 = ImageDraw.Draw(img)
        d2.rectangle([(0, SPLIT_Y), (W, H)], fill=t["bg_dark"])

    return img


# ════════════════════════════════════════════════════════════════════════════
#  SLIDE DE CONTEÚDO
# ════════════════════════════════════════════════════════════════════════════
def _content_slide(slide_num, total, left_main, left_sub,
                   title, body, theme, left_img=None, font_body=None):
    t       = theme
    left_w  = t["left_w"]
    right_x = left_w + 88
    right_w = W - right_x - PAD

    img = Image.new("RGB", (W, H), t["bg_light"])
    d   = ImageDraw.Draw(img)

    # ── Coluna esquerda ──
    if left_img:
        panel = _rcrop(left_img, left_w, H)
        img.paste(panel, (0, 0))
        d = ImageDraw.Draw(img)
        # Barra de acento na borda da imagem
        d.rectangle([(0, 0), (6, H)], fill=t["accent"])
    else:
        d.rectangle([(0, 0), (left_w, H)], fill=t["accent"])
        d.rectangle([(left_w, 0), (left_w + 4, H)], fill=t["bg_dark"])

    # ── Coluna direita ──
    rx  = right_x
    rw  = right_w
    ry  = PAD
    nh  = _num_label(d, slide_num, total, rx, ry, t["gray"])
    ry += nh + 48
    r_end = H - PAD

    # Título
    title_max = int((r_end - ry) * 0.28)
    ft = _fit(d, title, 44, lambda s: _roboto(s, True), rw, title_max, gap=10)
    th = _txt(d, title, ft, t["text_dark"], rx, ry, rw, gap=10)
    ry += th + 26

    # Linha de acento
    if ry < r_end - 80:
        d.rectangle([(rx, ry), (rx + rw, ry + 3)], fill=t["accent"])
        ry += 28

    # Corpo
    if body and ry < r_end - 20:
        avail = r_end - ry
        max_p = 4
        while max_p > 2:
            if _measure_paras_body(d, body, font_body, rw, 12, 36, max_p, 2) <= avail:
                break
            max_p -= 1
        _draw_paras_body(d, body, font_body, t["text_dark"], rx, ry, rw,
                         line_gap=12, para_gap=36,
                         max_paras=max_p, min_paras=2)

    return img


def slide_stat(data, n, total, theme, left_img=None, font_body=None):
    return _content_slide(n, total,
        _strip_emoji(data.get("left_box_text") or data.get("number", str(n))),
        _strip_emoji(data.get("left_box_sub")  or data.get("unit", "")),
        _strip_emoji(data.get("headline", "")),
        _strip_emoji(data.get("body", "")), theme, left_img, font_body)


def slide_insight(data, n, total, theme, left_img=None, font_body=None):
    return _content_slide(n, total,
        _strip_emoji(data.get("left_box_text", str(n))),
        _strip_emoji(data.get("left_box_sub", "")),
        _strip_emoji(data.get("headline", "")),
        _strip_emoji(data.get("body") or data.get("quote", "")), theme, left_img, font_body)


def slide_tip(data, n, total, theme, left_img=None, font_body=None):
    return _content_slide(n, total,
        _strip_emoji(data.get("left_box_text") or data.get("number", str(n - 1))),
        _strip_emoji(data.get("left_box_sub", "")),
        _strip_emoji(data.get("headline", "")),
        _strip_emoji(data.get("body", "")), theme, left_img, font_body)


# ════════════════════════════════════════════════════════════════════════════
#  SLIDE CTA
# ════════════════════════════════════════════════════════════════════════════
def _txt_centered(draw, text, font, color, cx, y, max_w, gap=12):
    lines = _wrap(draw, text, font, max_w)
    cy = y
    for i, line in enumerate(lines):
        lw, lh = _wh(draw, line, font)
        draw.text((cx - lw // 2, cy), line, font=font, fill=color, anchor="lt")
        cy += lh
        if i < len(lines) - 1:
            cy += gap
    return cy - y


def slide_cta(data, n, total, theme):
    t = theme

    # Fundo do CTA: dark ou accent conforme o tema
    bg      = t["bg_dark"]  if t["cta_bg"] == "dark"   else t["accent"]
    hl_col  = t["text_light"] if t["cta_bg"] == "dark"  else t["accent_text"]
    btn_bg  = t["accent"]   if t["cta_bg"] == "dark"    else t["bg_light"]
    btn_txt = t["accent_text"] if t["cta_bg"] == "dark" else t["text_dark"]
    sec_bg  = t["accent"]   if t["cta_bg"] == "dark"    else t["bg_dark"]
    sec_txt = t["accent_text"] if t["cta_bg"] == "dark" else t["text_light"]

    img = Image.new("RGB", (W, H), bg)
    d   = ImageDraw.Draw(img)

    closing = _strip_emoji(data.get("closing", "")).upper()
    btn     = _strip_emoji(data.get("cta_button", "Salva esse post agora"))
    urgency = _strip_emoji(data.get("urgency", ""))
    sec_cta = _strip_emoji(data.get("secondary_cta", ""))
    aw      = W - PAD * 2
    cx      = W // 2

    fn_num   = _roboto(22)
    num_h    = _wh(d, "01 / 07", fn_num)[1]

    fh       = _fit(d, closing, 86, _impact, aw, int((H - PAD * 2) * 0.35), gap=14)
    cl_h     = _measure(d, closing, fh, aw, gap=14)

    fb       = _roboto(38, True)
    bw_, bh_ = _wh(d, btn, fb)
    BTN_H    = bh_ + 48
    BTN_W    = min(bw_ + 120, aw)

    fu       = _roboto(30)
    urg_h    = _measure(d, urgency, fu, aw, gap=10) if urgency else 0

    fs_s     = _roboto(36, True)
    sec_h    = _measure(d, sec_cta, fs_s, aw) if sec_cta else 0

    content_h = num_h + cl_h + BTN_H
    if urgency:  content_h += urg_h
    if sec_cta:  content_h += sec_h + 20

    n_gaps    = 2 + (1 if urgency else 0) + (1 if sec_cta else 0)
    remaining = (H - PAD * 2) - content_h
    gap       = max(56, remaining // n_gaps)

    ry = PAD

    # Número do slide
    num_txt = f"{n:02d} / {total:02d}"
    nw, _   = _wh(d, num_txt, fn_num)
    d.text((cx - nw // 2, ry), num_txt, font=fn_num, fill=t["gray"], anchor="lt")
    ry += num_h + gap

    # Closing — grande, centralizado
    for line in _wrap(d, closing, fh, aw):
        lw, lhh = _wh(d, line, fh)
        d.text((cx - lw // 2, ry), line, font=fh, fill=hl_col, anchor="lt")
        ry += lhh + 14
    ry += gap

    # Botão
    bx = cx - BTN_W // 2
    d.rounded_rectangle([(bx, ry), (bx + BTN_W, ry + BTN_H)],
                         radius=18, fill=btn_bg)
    d.text((bx + (BTN_W - bw_) // 2, ry + (BTN_H - bh_) // 2),
           btn, font=fb, fill=btn_txt, anchor="lt")
    ry += BTN_H + gap

    # Urgency
    if urgency:
        _txt_centered(d, urgency, fu, t["lgray"], cx, ry, aw, gap=10)
        ry += urg_h + gap

    # Secondary CTA — faixa de destaque
    if sec_cta:
        sec_h2 = _measure(d, sec_cta, fs_s, aw)
        band_h = sec_h2 + 36
        d.rectangle([(0, ry), (W, ry + band_h)], fill=sec_bg)
        _txt_centered(d, sec_cta, fs_s, sec_txt, cx, ry + 18, aw)

    return img


# ── Blend de cores para subtítulo ────────────────────────────────────────────
def _blend(c1, c2, t):
    """Interpola entre c1 e c2 com fator t (0=c1, 1=c2)."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ════════════════════════════════════════════════════════════════════════════
#  ORQUESTRADOR
# ════════════════════════════════════════════════════════════════════════════
def create_carousel_images(carousel_data: dict, output_dir: str) -> list:
    from src.image_fetcher import fetch_image

    theme  = _get_next_theme()
    slides = carousel_data["slides"]
    total  = len(slides)
    topic  = carousel_data.get("topic", "artificial intelligence")
    os.makedirs(output_dir, exist_ok=True)
    paths  = []

    font_body = _roboto(28)

    hook_img = fetch_image(f"{topic} technology", W, int(H * 0.58))

    for slide in slides:
        n = slide["slide_number"]
        t = slide["type"]

        left_img = None
        if t in ("stat", "insight", "tip"):
            q = slide.get("pexels_query") or topic
            left_img = fetch_image(q, theme["left_w"], H)
            if left_img:
                print(f"  [img] [{t}] {q[:40]}")

        if   t == "hook":    img = slide_hook(slide, total, carousel_data.get("handle", ""), theme, hook_img)
        elif t == "stat":    img = slide_stat(slide, n, total, theme, left_img, font_body)
        elif t == "insight": img = slide_insight(slide, n, total, theme, left_img, font_body)
        elif t == "tip":     img = slide_tip(slide, n, total, theme, left_img, font_body)
        elif t == "cta":     img = slide_cta(slide, n, total, theme)
        else:                img = slide_stat(slide, n, total, theme, left_img, font_body)

        path = os.path.join(output_dir, f"slide_{n:02d}.jpg")
        img.save(path, "JPEG", quality=97)
        paths.append(path)
        print(f"  ok Slide {n}/{total} [{t}] - tema: {theme['name']}")

    return paths
