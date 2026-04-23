"""
find_instagram_id.py — Descobre automaticamente o Instagram User ID.

Uso:
    python find_instagram_id.py
"""

import requests

TOKEN = input("Cole seu Access Token aqui: ").strip()

BASE = "https://graph.facebook.com/v21.0"
headers = {"Authorization": f"Bearer {TOKEN}"}


def get(endpoint, params=None):
    p = {"access_token": TOKEN}
    if params:
        p.update(params)
    r = requests.get(f"{BASE}/{endpoint}", params=p)
    return r.json()


print("\n🔍 Buscando sua conta Instagram...\n")

# Tentativa 1: me/accounts (páginas do usuário)
print("1. Verificando páginas vinculadas...")
r = get("me/accounts", {"fields": "id,name,instagram_business_account"})
pages = r.get("data", [])
if pages:
    for page in pages:
        print(f"   Página: {page.get('name')} (ID: {page.get('id')})")
        ig = page.get("instagram_business_account")
        if ig:
            print(f"\n✅ Instagram User ID encontrado: {ig['id']}")
            print(f"   Salve no .env: INSTAGRAM_USER_ID={ig['id']}")
            exit()
else:
    print("   Nenhuma página encontrada via me/accounts")

# Tentativa 2: me direto
print("\n2. Verificando conta direta...")
r = get("me", {"fields": "id,name,instagram_business_account"})
if "instagram_business_account" in r:
    ig_id = r["instagram_business_account"]["id"]
    print(f"\n✅ Instagram User ID encontrado: {ig_id}")
    print(f"   Salve no .env: INSTAGRAM_USER_ID={ig_id}")
    exit()

# Tentativa 3: buscar via ID do usuário
print("\n3. Buscando via user ID...")
r_me = get("me", {"fields": "id"})
user_id = r_me.get("id")
if user_id:
    print(f"   Facebook User ID: {user_id}")
    r = get(f"{user_id}/accounts", {"fields": "id,name,instagram_business_account"})
    pages = r.get("data", [])
    for page in pages:
        ig = page.get("instagram_business_account")
        if ig:
            print(f"\n✅ Instagram User ID encontrado: {ig['id']}")
            print(f"   Salve no .env: INSTAGRAM_USER_ID={ig['id']}")
            exit()

# Tentativa 4: token do Instagram diretamente
print("\n4. Tentando token como Instagram token...")
r = requests.get(
    "https://graph.instagram.com/me",
    params={"fields": "id,username", "access_token": TOKEN}
)
data = r.json()
if "id" in data:
    print(f"\n✅ Instagram User ID encontrado: {data['id']}")
    print(f"   Username: {data.get('username', 'N/A')}")
    print(f"   Salve no .env: INSTAGRAM_USER_ID={data['id']}")
    exit()

print("\n❌ Não foi possível encontrar automaticamente.")
print("\nResposta da tentativa 4:", data)
print("\nPor favor, copie o resultado acima e envie para o assistente.")
