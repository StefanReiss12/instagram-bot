import os
import json
import shutil
from datetime import datetime
from src.config import PENDING_DIR, POSTED_DIR


def save_pending_post(carousel_data: dict, image_paths: list[str]) -> str:
    """Salva um post pendente de aprovação. Retorna o ID do post."""
    post_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    post_dir = os.path.join(PENDING_DIR, post_id)
    os.makedirs(post_dir, exist_ok=True)

    # Salva metadados
    meta = {
        "id": post_id,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "topic": carousel_data.get("topic", ""),
        "caption": carousel_data.get("caption", ""),
        "slides": carousel_data.get("slides", []),
        "image_paths": image_paths,
    }
    with open(os.path.join(post_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return post_id


def list_pending_posts() -> list[dict]:
    """Retorna lista de posts pendentes de aprovação."""
    posts = []
    if not os.path.exists(PENDING_DIR):
        return posts

    for post_id in sorted(os.listdir(PENDING_DIR)):
        meta_path = os.path.join(PENDING_DIR, post_id, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                posts.append(json.load(f))

    return posts


def mark_as_posted(post_id: str, instagram_post_id: str):
    """Move um post para a pasta de postados."""
    src = os.path.join(PENDING_DIR, post_id)
    dst = os.path.join(POSTED_DIR, post_id)
    os.makedirs(POSTED_DIR, exist_ok=True)

    # Atualiza status
    meta_path = os.path.join(src, "meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    meta["status"] = "posted"
    meta["posted_at"] = datetime.now().isoformat()
    meta["instagram_post_id"] = instagram_post_id

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    shutil.move(src, dst)


def delete_pending_post(post_id: str):
    """Remove um post pendente (rejeitado)."""
    src = os.path.join(PENDING_DIR, post_id)
    if os.path.exists(src):
        shutil.rmtree(src)
