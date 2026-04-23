"""
Criador de imagens para o carrossel das 14h.
Layout: capa igual ao 9h (headline + subtítulo). Slides de conteúdo: texto centralizado,
sem painel esquerdo, largura total. Inclui tag estratégica por slide (PROBLEMA, CUSTO...).
"""
import os
from PIL import Image, ImageDraw, ImageFont

from src.image_creator import (
    W, H, PAD,
    THEMES, _get_next_theme,
    _roboto, _impact,
    _wh, _wrap, _measure, _txt, _txt_centered,
    _draw_paras_body, _measure_paras_body, _fit_paras_body, _fit,
    _strip_emoji, _safe_text, _blend, _rcrop,
    _num_label,
    slide_hook, slide_cta,
)


# ════════════════════════════════════════════════════════════════════════════
#  SLIDE DE CONTEÚDO — LAYOUT CENTRALIZADO (sem painel esquerdo)
# ════════════════════════════════════════════════════════════════════════════
def _content_slide_centered(slide_num, total, tag, title, body, theme, font_body=None):
    t   = theme
    img = Image.new("RGB", (W, H), t["bg_light"])
    d   = ImageDraw.Draw(img)

    # Faixa de acento no topo (fina, visual)
    d.rectangle([(0, 0), (W, 6)], fill=t["accent"])

    x  = PAD
    rw = W - PAD * 2
    ry = PAD + 6

    # Número do slide
    nh  = _num_label(d, slide_num, total, x, ry, t["gray"])
    ry += nh + 20

    # Tag estratégica (PROBLEMA, CUSTO, VIRADA...) — bloco de acento
    if tag:
        ft = _roboto(22, bold=True)
        tw, th = _wh(d, tag, ft)
        pad_h, pad_v = 18, 10
        d.rounded_rectangle(
            [(x, ry), (x + tw + pad_h * 2, ry + th + pad_v * 2)],
            radius=6, fill=t["accent"],
        )
        d.text((x + pad_h, ry + pad_v), _safe_text(tag), font=ft, fill=t["accent_text"], anchor="lt")
        ry += th + pad_v * 2 + 24

    # Título
    title_max = int((H - PAD * 2) * 0.22)
    ft_title  = _fit(d, title, 52, lambda s: _roboto(s, True), rw, title_max, gap=10)
    th_h      = _txt(d, title, ft_title, t["text_dark"], x, ry, rw, gap=10)
    ry       += th_h + 22

    # Linha de acento
    if ry < H - PAD - 80:
        d.rectangle([(x, ry), (x + rw, ry + 3)], fill=t["accent"])
        ry += 28

    # Corpo — preenche o espaço restante
    if body and ry < H - PAD - 20:
        avail = H - PAD - ry
        fb    = font_body or _roboto(30)
        max_p = 3
        while max_p > 1:
            if _measure_paras_body(d, body, fb, rw, 14, 44, max_p, 1) <= avail:
                break
            max_p -= 1
        _draw_paras_body(d, body, fb, t["text_dark"], x, ry, rw,
                         line_gap=14, para_gap=44, max_paras=max_p, min_paras=1)

    return img


# ════════════════════════════════════════════════════════════════════════════
#  SLIDE TYPES ESPECÍFICOS DO 14H
# ════════════════════════════════════════════════════════════════════════════
def slide_14h_content(data, n, total, theme, font_body=None):
    tag   = _strip_emoji(data.get("tag", ""))
    title = _strip_emoji(data.get("headline", ""))
    body  = _strip_emoji(data.get("body", ""))
    return _content_slide_centered(n, total, tag, title, body, theme, font_body)


# ════════════════════════════════════════════════════════════════════════════
#  ORQUESTRADOR
# ════════════════════════════════════════════════════════════════════════════
def create_carousel_images_14h(carousel_data: dict, output_dir: str) -> list:
    from src.image_fetcher import fetch_image

    theme  = _get_next_theme()
    slides = carousel_data["slides"]
    total  = len(slides)
    topic  = carousel_data.get("topic", "artificial intelligence productivity")
    os.makedirs(output_dir, exist_ok=True)
    paths  = []

    font_body = _roboto(30)
    hook_img  = fetch_image(f"{topic} business office", W, int(H * 0.58))

    for slide in slides:
        n = slide["slide_number"]
        t = slide["type"]

        if t == "hook":
            img = slide_hook(slide, total, carousel_data.get("handle", ""), theme, hook_img)
        elif t == "cta":
            img = slide_cta(slide, n, total, theme)
        else:
            img = slide_14h_content(slide, n, total, theme, font_body)

        path = os.path.join(output_dir, f"slide_{n:02d}.jpg")
        img.save(path, "JPEG", quality=97)
        paths.append(path)
        print(f"  ok Slide {n}/{total} [{t}] - tema: {theme['name']}")

    return paths
