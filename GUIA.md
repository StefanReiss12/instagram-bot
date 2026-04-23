# Guia de Configuração — Instagram Bot IA Generativa

## Pré-requisitos
- Python 3.10+
- Conta no Instagram (Business ou Creator)
- Conta no Facebook

---

## 1. ANTHROPIC_API_KEY

1. Acesse: https://console.anthropic.com
2. Crie uma conta ou faça login
3. Vá em **API Keys** > **Create Key**
4. Copie a chave e cole no `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

---

## 2. INSTAGRAM_ACCESS_TOKEN + INSTAGRAM_USER_ID

### Passo 1 — Converter conta para Business/Creator
- No Instagram: Configurações > Conta > Mudar para conta profissional

### Passo 2 — Criar página no Facebook
- Acesse facebook.com e crie uma **Página** (pode ser simples)
- Conecte a Página ao seu Instagram: Configurações do Instagram > Conta vinculada

### Passo 3 — Criar app no Meta for Developers
1. Acesse: https://developers.facebook.com/apps
2. Clique em **Criar app**
3. Tipo: **Outros** > **Empresa**
4. Preencha o nome do app e clique em **Criar**

### Passo 4 — Adicionar produto Instagram
1. No painel do app, clique em **Adicionar produto**
2. Encontre **Instagram** e clique em **Configurar**
3. Vá em **Ferramentas de API** > selecione sua página do Facebook
4. Gere o **Token de Acesso do Usuário**
5. Marque as permissões: `instagram_basic`, `instagram_content_publish`

### Passo 5 — Obter User ID
- Com o token gerado, acesse:
  ```
  https://graph.facebook.com/v21.0/me/accounts?access_token=SEU_TOKEN
  ```
- Pegue o `id` da sua conta Instagram

### Passo 6 — Configurar no .env
```
INSTAGRAM_ACCESS_TOKEN=EAAxxxxxxxx...
INSTAGRAM_USER_ID=17841xxxxxxxxx
```

> **Nota:** Para uso em produção, gere um **token de longa duração** (válido por 60 dias).
> Para token permanente, use um **token de sistema** via Business Manager.

---

## 3. IMGBB_API_KEY (hospedagem gratuita de imagens)

1. Acesse: https://imgbb.com
2. Crie uma conta gratuita
3. Acesse: https://api.imgbb.com
4. Clique em **Get API key**
5. Copie e cole no `.env`:
   ```
   IMGBB_API_KEY=xxxxxxxxxxxxxxxx
   ```

---

## Uso

```bash
# 1. Instalar e verificar configuração
python setup.py

# 2. Gerar um carrossel (tópico aleatório)
python main.py

# 3. Gerar com tópico específico
python main.py "Como usar agentes de IA no trabalho"

# 4. Revisar e publicar posts pendentes
python approve.py

# 5. Iniciar agendador automático (Seg/Qua/Sex às 9h)
python scheduler.py

# 6. Testar geração imediata
python scheduler.py --now
```

---

## Fluxo completo

```
python scheduler.py   (roda em background, gera posts automaticamente)
        ↓
python approve.py     (você revisa as imagens e aprova para publicar)
        ↓
        Post publicado no Instagram!
```
