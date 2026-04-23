"""
Gerador de conteúdo para o carrossel das 14h.
Foco: autoridade, educação e viralização para profissionais de negócios que usam IA.
Estrutura: Gancho → Problema → Custo → Virada → Sistema → Prova → Decisão+CTA
Dois passos: (1) Claude escolhe o tema com maior potencial viral, (2) gera os 7 slides.
"""
import anthropic
import json
import random
from datetime import datetime
from src.config import ANTHROPIC_API_KEY
from src.trending_fetcher import fetch_trending

_CTA_OPTIONS = [
    "Segue o perfil pra não perder o próximo.",
    "Salva esse post. Você vai precisar mostrar pra alguém essa semana.",
    "Compartilha com alguém do seu time que ainda não está usando IA no trabalho.",
    "Comenta: qual parte disso você ainda não estava fazendo?",
    "Marca aquela pessoa do escritório que precisa ver isso agora.",
    "Segue pra mais conteúdo que te deixa à frente no mercado.",
    "Comenta 'quero' que te mando o próximo passo.",
]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _fix_json_newlines(s: str) -> str:
    result = []
    in_string = False
    escape_next = False
    for ch in s:
        if escape_next:
            result.append(ch)
            escape_next = False
        elif ch == "\\":
            result.append(ch)
            escape_next = True
        elif ch == '"':
            in_string = not in_string
            result.append(ch)
        elif in_string and ch == "\n":
            result.append("\\n")
        elif in_string and ch == "\r":
            pass
        else:
            result.append(ch)
    return "".join(result)


def _select_viral_topic(trending_context: str, today: str) -> str:
    """Passo 1: Claude escolhe o tema com maior potencial viral para o público-alvo."""
    prompt = f"""Você é um estrategista de conteúdo especializado em Instagram para profissionais de negócios brasileiros.

DATA: {today}

PÚBLICO-ALVO: Profissionais de escritório (gerentes, analistas, coordenadores, diretores) que usam ou querem usar IA para aumentar produtividade e se destacar no trabalho. Faixa de 28 a 50 anos. Querem resultados práticos, não tecnologia pela tecnologia.

OBJETIVO DO CONTEÚDO: Crescimento de seguidores, retenção, autoridade e educação sobre IA aplicada ao trabalho.

CONTEXTO DE TENDÊNCIAS DO DIA:
{trending_context}

SUA TAREFA:
Analisar as tendências acima e escolher O ÚNICO tema com maior potencial de viralização para esse público específico.

Critérios de escolha (em ordem de prioridade):
1. Gera reação imediata: "não sabia disso", "preciso mostrar pro meu chefe", "isso muda como trabalho"
2. Conecta IA com situação real do dia a dia no escritório (reuniões, relatórios, e-mails, apresentações)
3. Tem um dado surpreendente ou contraintuitivo que poucos conhecem
4. Não é óbvio — profissionais que já usam ChatGPT ainda não ouviram esse ângulo
5. Gera tanto medo de ficar pra trás quanto esperança de se destacar

NÃO escolha temas muito técnicos (modelos, parâmetros, benchmarks). Escolha o ângulo de impacto prático.

Responda APENAS com um JSON no formato:
{{"topic": "tema específico e concreto", "angle": "ângulo de abordagem (o que vai surpreender o leitor)", "hook_idea": "primeira frase de impacto em no máximo 7 palavras"}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])
    raw = _fix_json_newlines(raw)
    return json.loads(raw)


def generate_carousel_content_14h(topic: str = None) -> dict:
    today = datetime.now().strftime("%d/%m/%Y")
    trending_context = fetch_trending()
    cta_follow = random.choice(_CTA_OPTIONS)

    # Passo 1: selecionar tema viral (a menos que um tema fixo seja passado)
    if topic:
        topic_data = {"topic": topic, "angle": "", "hook_idea": ""}
    else:
        topic_data = _select_viral_topic(trending_context, today)

    topic_name = topic_data["topic"]
    angle = topic_data.get("angle", "")
    hook_idea = topic_data.get("hook_idea", "")

    # Passo 2: gerar os 7 slides
    prompt = f"""Você é um copywriter estratégico especializado em carrosseis de Instagram para profissionais de negócios brasileiros.

DATA: {today}
TEMA: {topic_name}
ÂNGULO: {angle}
IDEIA DE GANCHO: {hook_idea}

PÚBLICO: Profissionais de escritório (gerentes, analistas, coordenadores, diretores) que usam ou querem usar IA para aumentar produtividade. Querem resultados práticos no trabalho, não papo de tecnologia.

OBJETIVO: Gerar autoridade, educar e aumentar seguidores.

TOM: Claro, direto, sem termos técnicos. Quando tiver algum termo técnico, explique em uma palavra o que significa. Escreva como um mentor que já passou por isso, não como um professor explicando teoria.

════════════════════════════════════════════
ESTRUTURA DOS 7 SLIDES
════════════════════════════════════════════

SLIDE 1 — GANCHO (capa)
A capa que para o scroll. Mesmo estilo visual dos melhores criadores.
Headline: frase de impacto em no máximo 7 palavras, SEM ponto final
Subtítulo: expande o choque sem resolver, máx 12 palavras
O leitor precisa sentir que vai perder algo importante se não continuar.

SLIDE 2 — PROBLEMA
O problema real que o leitor tem mas talvez não tenha nomeado ainda.
Seja específico: "aquela reunião de segunda que poderia ser um e-mail", não "falta de produtividade".
Termine com uma frase que cria tensão para o próximo slide.

SLIDE 3 — CUSTO
O custo concreto de ignorar esse problema: tempo perdido, oportunidades, posição na empresa.
Use números quando possível: "isso representa X horas por mês", "equivale a Y dias por ano".
Torne tangível o preço do status quo.

SLIDE 4 — VIRADA
O insight que muda tudo. A perspectiva que o leitor não tinha.
Não é uma solução ainda. É o momento "ah, agora entendi por que estava errando".
Deve gerar um "cara, nunca tinha pensado assim".

SLIDE 5 — SISTEMA
O método prático. Como aplicar a virada do slide 4 na realidade do trabalho.
Concreto: o que fazer, como começar, em quanto tempo.
Sem jargão. Uma pessoa que nunca usou IA deve entender e conseguir aplicar.

SLIDE 6 — PROVA
Evidência de que funciona: dado real, caso de empresa, resultado mensurável.
Pode ser uma empresa conhecida, um estudo, ou um resultado típico de quem aplica.
Torna o sistema do slide 5 crível e urgente.

SLIDE 7 — DECISÃO + CTA
Fecha o loop do slide 1. O leitor deve sentir que a decisão é agora.
CTA específico e direto: {cta_follow}
Linha de seguir: @stefanreiss.ia

════════════════════════════════════════════
REGRAS DE ESCRITA
════════════════════════════════════════════

Uma ideia por slide. Texto claro e envolvente. Cada slide puxa o próximo.
Parágrafos curtos: máx 2 frases por parágrafo. Frases curtas: máx 15 palavras.
Parágrafos separados por \\n\\n.
Sem enrolação. Sem frases genéricas. Sem bullet points.
Proibido: "revolucionário", "disruptivo", "ecossistema", "neste contexto", "vale ressaltar".
Proibido: traços como separador (— ou -).

Para cada slide de conteúdo (slides 2 a 6), entregue:
- tag: nome da função estratégica em maiúsculo (PROBLEMA, CUSTO, VIRADA, SISTEMA, PROVA)
- headline: título impactante do slide (máx 6 palavras)
- body: corpo do texto em parágrafos separados por \\n\\n (mín 2, máx 3 parágrafos)

Retorne APENAS o JSON (sem markdown, sem explicações):

{{
  "topic": "{topic_name}",
  "hook_emoji": "emoji único e relevante",
  "handle": "stefanreiss.ia",
  "slides": [
    {{
      "slide_number": 1,
      "type": "hook",
      "headline": "headline de impacto em no máximo 7 palavras sem ponto final",
      "subtitle": "subtítulo que amplifica sem resolver (máx 12 palavras)",
      "cta_text": "deslize e veja como isso muda seu trabalho"
    }},
    {{
      "slide_number": 2,
      "type": "problema",
      "tag": "PROBLEMA",
      "headline": "nome do problema em no máximo 6 palavras",
      "body": "ESCREVA 2 PARÁGRAFOS separados por \\n\\n. O problema real e específico que o leitor tem.\\n\\nA última frase cria tensão para o próximo slide."
    }},
    {{
      "slide_number": 3,
      "type": "custo",
      "tag": "CUSTO",
      "headline": "o preço de ignorar isso (máx 6 palavras)",
      "body": "ESCREVA 2 PARÁGRAFOS separados por \\n\\n. Custo concreto em tempo, dinheiro ou posição.\\n\\nTorne tangível. Use números. Termine criando urgência."
    }},
    {{
      "slide_number": 4,
      "type": "virada",
      "tag": "VIRADA",
      "headline": "o insight que muda tudo (máx 6 palavras)",
      "body": "ESCREVA 2 PARÁGRAFOS separados por \\n\\n. A perspectiva que o leitor não tinha.\\n\\nO momento 'ah, agora entendi'. Termine apontando para a solução."
    }},
    {{
      "slide_number": 5,
      "type": "sistema",
      "tag": "SISTEMA",
      "headline": "como aplicar isso agora (máx 6 palavras)",
      "body": "ESCREVA 3 PARÁGRAFOS separados por \\n\\n. O método prático, concreto e sem jargão.\\n\\nO que fazer, como começar.\\n\\nEm quanto tempo dá resultado."
    }},
    {{
      "slide_number": 6,
      "type": "prova",
      "tag": "PROVA",
      "headline": "quem já faz isso e o resultado (máx 6 palavras)",
      "body": "ESCREVA 2 PARÁGRAFOS separados por \\n\\n. Dado real, empresa ou estudo que comprova.\\n\\nPor que isso torna a decisão urgente agora."
    }},
    {{
      "slide_number": 7,
      "type": "cta",
      "closing": "FRASE QUE FECHA O LOOP DO SLIDE 1 (máx 7 palavras CAPS)",
      "cta_button": "{cta_follow}",
      "urgency": "o que muda para quem agir agora vs quem esperar (máx 12 palavras)",
      "secondary_cta": "Segue pra mais conteúdo que te destaca no mercado → @stefanreiss.ia"
    }}
  ],
  "caption": "LEGENDA COMPLETA:\\n\\n[Reescreva o hook do slide 1 em 2 linhas expandidas]\\n\\nO que você vai aprender nesse carrossel:\\n[ponto 1 em forma de frase, sem traço]\\n[ponto 2 em forma de frase, sem traço]\\n[ponto 3 em forma de frase, sem traço]\\n\\n[Parágrafo de contexto: por que isso importa agora para quem trabalha com IA]\\n\\nSalva esse post. Você vai querer mostrar isso na próxima reunião.\\n\\n{cta_follow}\\n\\n#IANoTrabalho #ProdutividadeComIA #InteligenciaArtificial #IAParaNegócios #AutomacaoNoTrabalho #IA2026 #FuturoDoTrabalho #AIBrasil #CarreiraIA #TransformacaoDigital #IAGenerativa #TrabalhoComIA #GestaoComIA #PromptEngineering #IAParaProfissionais"
}}"""

    import time
    last_err = None
    for attempt in range(5):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1])
            raw = _fix_json_newlines(raw)
            return json.loads(raw)
        except Exception as e:
            last_err = e
            if "529" in str(e) or "overloaded" in str(e).lower():
                wait = 15 * (attempt + 1)
                print(f"  API sobrecarregada. Aguardando {wait}s (tentativa {attempt+1}/5)...")
                time.sleep(wait)
            else:
                raise
    raise last_err
