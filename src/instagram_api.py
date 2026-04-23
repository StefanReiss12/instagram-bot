import time
import requests
from src.config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID

BASE_URL = "https://graph.instagram.com/v21.0"


def _post(endpoint: str, data: dict, retries: int = 3) -> dict:
    data["access_token"] = INSTAGRAM_ACCESS_TOKEN
    for attempt in range(1, retries + 1):
        response = requests.post(f"{BASE_URL}/{endpoint}", data=data, timeout=30)
        result = response.json()
        if "error" not in result:
            return result
        error = result["error"]
        is_transient = result.get("is_transient") or error.get("is_transient", False)
        if is_transient and attempt < retries:
            wait = attempt * 30
            print(f"  ⚠️ Erro transiente, aguardando {wait}s (tentativa {attempt}/{retries})...")
            time.sleep(wait)
            continue
        raise RuntimeError(f"Erro Instagram API: {error}")
    raise RuntimeError("Máximo de tentativas atingido.")


def _get_status(container_id: str) -> str:
    """Consulta o status de um container de mídia."""
    url = f"{BASE_URL}/{container_id}"
    params = {
        "fields": "status_code,status",
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }
    response = requests.get(url, params=params, timeout=30)
    result = response.json()
    if "error" in result:
        raise RuntimeError(f"Erro ao consultar status: {result['error']}")
    return result.get("status_code", "UNKNOWN")


def _wait_until_ready(container_id: str, label: str = "container", max_wait: int = 120):
    """
    Fica consultando o status do container até que esteja FINISHED.
    Aguarda até max_wait segundos antes de desistir.
    """
    elapsed = 0
    interval = 5
    print(f"      ⏳ Aguardando {label} ficar pronto...", end="", flush=True)
    while elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval
        status = _get_status(container_id)
        print(f" {status}", end="", flush=True)
        if status == "FINISHED":
            print(" ✓")
            return
        if status == "ERROR":
            print()
            raise RuntimeError(f"Container {container_id} falhou com status ERROR.")
        if status == "EXPIRED":
            print()
            raise RuntimeError(f"Container {container_id} expirou.")
    print()
    raise RuntimeError(f"Timeout: {label} não ficou FINISHED em {max_wait}s. Último status: {status}")


def create_image_container(image_url: str, is_carousel_item: bool = True) -> str:
    """Cria um container de mídia para um item do carrossel e aguarda ficar pronto."""
    data = {
        "image_url": image_url,
        "is_carousel_item": str(is_carousel_item).lower(),
    }
    result = _post(f"{INSTAGRAM_USER_ID}/media", data)
    container_id = result["id"]
    _wait_until_ready(container_id, label=f"slide {container_id[-6:]}", max_wait=120)
    return container_id


def create_carousel_container(children_ids: list[str], caption: str) -> str:
    """Cria o container do carrossel com todos os itens e aguarda ficar pronto."""
    data = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
    }
    result = _post(f"{INSTAGRAM_USER_ID}/media", data)
    container_id = result["id"]
    _wait_until_ready(container_id, label="carrossel", max_wait=180)
    return container_id


def publish_container(container_id: str) -> str:
    """Publica o container criado."""
    data = {"creation_id": container_id}
    result = _post(f"{INSTAGRAM_USER_ID}/media_publish", data)
    return result["id"]


def post_carousel(image_urls: list[str], caption: str) -> str:
    """
    Fluxo completo para postar um carrossel.
    Retorna o ID do post publicado.
    """
    print("  1/3 Criando containers de mídia (aguardando processamento)...")
    children_ids = []
    for i, url in enumerate(image_urls, 1):
        print(f"      → Slide {i}/{len(image_urls)}")
        container_id = create_image_container(url)
        children_ids.append(container_id)

    print("  2/3 Criando container do carrossel...")
    carousel_id = create_carousel_container(children_ids, caption)

    print("  3/3 Publicando...")
    post_id = publish_container(carousel_id)

    return post_id
