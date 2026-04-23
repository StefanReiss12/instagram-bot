"""
Upload de imagens para o Cloudinary.
URLs do Cloudinary são 100% acessíveis pelos servidores do Instagram.
"""
import hashlib
import time
import requests
from src.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET


def upload_to_cloudinary(image_path: str) -> str:
    """
    Faz upload de uma imagem para o Cloudinary e retorna a URL segura.
    O Cloudinary é o CDN mais confiável para uso com a API do Instagram.
    """
    timestamp = str(int(time.time()))

    # Assinatura SHA1 obrigatória pela API do Cloudinary
    sig_string = f"timestamp={timestamp}{CLOUDINARY_API_SECRET}"
    signature  = hashlib.sha1(sig_string.encode()).hexdigest()

    with open(image_path, "rb") as f:
        response = requests.post(
            f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/image/upload",
            data={
                "api_key":   CLOUDINARY_API_KEY,
                "timestamp": timestamp,
                "signature": signature,
            },
            files={"file": f},
            timeout=60,
        )

    response.raise_for_status()
    result = response.json()

    if "error" in result:
        raise RuntimeError(f"Cloudinary erro: {result['error']['message']}")

    url = result.get("secure_url", "")
    if not url:
        raise RuntimeError(f"Cloudinary não retornou URL. Resposta: {result}")

    return url


def upload_all_images(image_paths: list) -> list:
    """Faz upload de todas as imagens e retorna lista de URLs públicas."""
    urls = []
    for i, path in enumerate(image_paths, 1):
        print(f"  ↑ Enviando imagem {i}/{len(image_paths)} para Cloudinary...")
        url = upload_to_cloudinary(path)
        urls.append(url)
        print(f"  ✓ {url[:70]}...")
    return urls
