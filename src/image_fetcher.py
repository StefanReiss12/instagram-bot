"""
Busca imagens relevantes do Pexels para usar nos slides.
Sempre busca fotos diferentes — sem cache entre carrosseis.
"""
import os
import random
import requests
from io import BytesIO
from PIL import Image
from src.config import PEXELS_API_KEY, BASE_DIR

# Cache de sessão: evita baixar a mesma imagem duas vezes no mesmo carrossel,
# mas é reiniciado a cada execução do bot (não persiste entre carrosseis).
_session_cache: dict = {}


def _resize_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    """Redimensiona e corta para exatamente w×h (fill mode)."""
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    new_w, new_h = int(src_w * scale) + 1, int(src_h * scale) + 1
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - w) // 2
    top  = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def fetch_image(query: str, w: int, h: int) -> Image.Image | None:
    """
    Busca uma imagem aleatória do Pexels relacionada ao query.
    Retorna PIL Image redimensionada para w×h, ou None se indisponível.
    """
    if not PEXELS_API_KEY:
        return None

    cache_key = f"{query}_{w}x{h}"
    if cache_key in _session_cache:
        return _session_cache[cache_key]

    try:
        # Página aleatória (1-3) para variar os resultados entre execuções
        page = random.randint(1, 3)
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": 15, "orientation": "portrait", "page": page},
            timeout=10,
        )
        photos = resp.json().get("photos", [])
        if not photos:
            return None

        # Escolhe foto aleatória dos resultados
        photo = random.choice(photos)
        photo_url = photo["src"]["large"]
        img_bytes = requests.get(photo_url, timeout=15).content
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = _resize_crop(img, w, h)

        _session_cache[cache_key] = img
        return img

    except Exception as e:
        print(f"  Pexels ({query}): {e}")
        return None


def with_dark_overlay(img: Image.Image, alpha: int = 155) -> Image.Image:
    """Aplica overlay escuro semi-transparente para legibilidade do texto."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, alpha))
    base    = img.convert("RGBA")
    merged  = Image.alpha_composite(base, overlay)
    return merged.convert("RGB")
