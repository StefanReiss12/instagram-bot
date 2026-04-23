"""
Gerador de conteúdo viral — AIDA + notícias diárias reais de IA.
"""
import anthropic
import json
import random
from datetime import datetime
from src.config import ANTHROPIC_API_KEY
from src.trending_fetcher import fetch_trending

_CTA_OPTIONS = [
    "Comenta aqui: sua área já está sentindo esse movimento?",
    "Me conta nos comentários: você já está usando IA no seu trabalho?",
    "Qual parte disso mais te assustou? Comenta abaixo.",
    "Comenta: você está preparado para essa mudança ou ainda está esperando?",
    "Me fala nos comentários: sua empresa já está tomando alguma ação?",
    "Qual foi o insight que mais te impactou? Comenta aqui.",
    "Comenta abaixo: isso já chegou na sua empresa ou ainda está chegando?",
    "Me conta: o que você vai fazer diferente depois de ler isso?",
    "Comenta aqui: você conhece alguém que precisa ver isso agora?",
    "Qual dessas mudanças mais te preocupa? Comenta abaixo.",
]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_carousel_content(topic: str = None, avoid_topics: list = None) -> dict:
    today   = datetime.now().strftime("%d/%m/%Y")
    weekday = datetime.now().strftime("%A")
    trending_context = fetch_trending()
    avoid_str = ""
    if avoid_topics:
        avoid_str = f"\n\nTÓPICOS JÁ USADOS (NÃO REPITA): {', '.join(avoid_topics)}"
    cta_comment = random.choice(_CTA_OPTIONS)

    if topic:
        topic_instruction = f'Tópico: "{topic}". Crie conteúdo extremamente atual sobre este tema.{avoid_str}'
    else:
        topic_instruction = f"""
Hoje é {today} ({weekday}). Com base nas notícias ABAIXO (fontes reais do dia), escolha O ÚNICO tema
com maior potencial viral para o Instagram brasileiro sobre IA Generativa.{avoid_str}

Critérios de escolha: impacto no mercado de trabalho, novidades de modelos, ferramentas disruptivas,
dados chocantes, mudanças que afetam diretamente profissionais brasileiros AGORA.

═══ NOTÍCIAS DO DIA (use estas como base do conteúdo) ═══
{trending_context}
═══════════════════════════════════════════════════════════

IMPORTANTE: O conteúdo DEVE ser baseado nestas notícias reais. Cite datas, empresas e dados específicos
das notícias acima. Não invente dados — use o que está nas notícias.
"""

    prompt = f"""Você é um jornalista e estrategista de conteúdo brasileiro que escreve sobre tecnologia há 12 anos.
Você não usa fórmulas prontas. Você pensa, analisa e escreve como um humano que realmente entende do assunto.
Seu conteúdo é reconhecido porque parece conversa de especialista, não de robô.

DATA: {today}

{topic_instruction}

════════════════════════════════════════════
COMO VOCÊ ESCREVE — LEIA COM ATENÇÃO
════════════════════════════════════════════

Você escreve como um analista que acabou de ler a notícia e quer explicar para um amigo inteligente.
Não resume. Não lista. Não usa bullet points com traço. Não usa "Passo 1:", "Passo 2:".
Escreve em parágrafos curtos, como texto jornalístico mesmo.

Sua voz tem:
- Opiniões próprias baseadas em dados reais
- Contexto histórico quando ajuda a entender ("isso não é novo — em 2023 já...")
- Comparações humanas ("é como se você fosse médico e o hospital passasse a usar IA para...")
- Ironia sutil quando cabe ("genial, né?", "surpresa de ninguém")
- Perguntas que o leitor faria ("mas e aí, quem paga essa conta?")
- Dados específicos com fonte e data ("segundo relatório da McKinsey de março de 2026...")

PROIBIDO ABSOLUTAMENTE:
- Traços no meio de frases como separador (— ou -)
- "Passo 1:", "Passo 2:", "Dica extra:", "Atenção:"
- "No cenário atual", "Vale ressaltar", "É fundamental", "Neste contexto"
- "Revolucionário", "Disruptivo", "Transformacional", "Ecossistema"
- Qualquer estrutura de lista com marcadores
- Frases que começam todas com a mesma estrutura
- Linguagem corporativa ou de relatório

════════════════════════════════════════════
ESTRUTURA NARRATIVA (storytelling obrigatório)
════════════════════════════════════════════

O carrossel conta UMA história do começo ao fim.
O leitor precisa sentir que está descobrindo algo junto com você.

SLIDE 1 — O CHOQUE INICIAL
Uma afirmação ou número que para qualquer pessoa no meio do scroll.
Não explique ainda. Apenas plante a dúvida ou o medo.
Headline em CAPS, máx 7 palavras. Subtítulo amplia sem revelar tudo.

SLIDE 2 — A PROVA
Aqui você mostra os dados que sustentam o slide 1.
Conte como um jornalista: quem fez, quando, qual foi o resultado, o que isso revela.
Não é uma lista de fatos. É uma análise com contexto.

SLIDE 3 — O QUE ESTÁ POR BAIXO
A camada que a maioria não viu. O dado que explica o dado.
Por que isso está acontecendo? Quem está ganhando? Quem está perdendo?

SLIDE 4 — O QUE VOCÊ PODE FAZER (parte 1)
Não é "dica". É uma postura, uma decisão estratégica.
Como alguém que já entendeu isso age diferente de quem não entendeu?

SLIDE 5 — O QUE VOCÊ PODE FAZER (parte 2)
Continua a narrativa do slide 4. Aprofunda.
Exemplo concreto de alguém ou empresa que já está fazendo isso.

SLIDE 6 — A VIRADA
O insight mais forte do carrossel. O que muda quando você entende isso de verdade.
Uma frase que o leitor vai querer mandar pra alguém.

SLIDE 7 — CTA QUE FAZ SENTIDO
Conectado diretamente com o que foi dito nos slides anteriores.
Não é genérico. É específico para quem acabou de ler tudo isso.
Varie entre: salvar, comentar, marcar alguém, compartilhar, testar algo.

════════════════════════════════════════════
REGRAS DO CORPO DE TEXTO (SAGRADAS — OBRIGATÓRIO)
════════════════════════════════════════════
OBRIGATÓRIO: cada campo "body" indica explicitamente quantos parágrafos escrever (2, 3 ou 4).
Siga EXATAMENTE a instrução de quantidade de parágrafos de cada slide — nunca escreva menos.
Os parágrafos DEVEM ser separados por \\n\\n. Nunca use \\n simples entre parágrafos.
Cada parágrafo: 1 a 2 frases curtas. Máximo 15 palavras por frase.
Sem listas. Sem traços. Sem dois pontos após rótulos. Texto corrido natural.
Cada parágrafo tem uma ideia própria e diferente dos demais.

Exemplo CORRETO com 3 parágrafos:
"A Klarna substituiu 700 atendentes por IA em março. O custo operacional caiu 40%.\\n\\nEsse movimento chegou nos bancos brasileiros sem manchete. Itaú e Bradesco reduziram equipes em 23% desde 2024.\\n\\nQuem ainda não mapeou quais funções do seu time são automatizáveis está ficando para trás."

Exemplo CORRETO com 2 parágrafos:
"O modelo GPT-4o agora processa vídeo em tempo real. Isso muda radicalmente o que é possível em automação.\\n\\nEmpresas que já usam isso estão entregando em horas o que antes levava semanas."

Exemplo ERRADO (jamais faça):
"Um único parágrafo longo sem quebra." ← PROIBIDO

════════════════════════════════════════════
left_box_text: OBRIGATÓRIO em todo slide de conteúdo
════════════════════════════════════════════
NUNCA use emoji em left_box_text — use apenas letras e números.
Para stat: número/dado principal (ex: "47%", "$2T", "700", "10x")
Para insight: palavra de impacto em caixa alta (ex: "VIRADA", "ALERTA", "CHOQUE", "REAL")
Para tip: número da dica (ex: "01", "02", "03")
Máx 2 palavras. Impacto visual máximo. Apenas texto simples, sem emoji.

Retorne APENAS o JSON (sem markdown, sem explicações):

{{
  "topic": "tema específico baseado nas notícias do dia",
  "hook_emoji": "emoji único e relevante",
  "handle": "stefanreiss.ia",
  "slides": [
    {{
      "slide_number": 1,
      "type": "hook",
      "headline": "afirmação que para o scroll (máx 7 palavras, sem caixa alta)",
      "subtitle": "contexto que amplifica sem revelar tudo (máx 12 palavras)",
      "cta_text": "deslize e entenda o que está acontecendo"
    }},
    {{
      "slide_number": 2,
      "type": "stat",
      "left_box_text": "número ou dado central",
      "left_box_sub": "contexto (máx 3 palavras)",
      "headline": "título analítico do slide (máx 6 palavras)",
      "body": "ESCREVA 4 PARÁGRAFOS separados por \\n\\n. Dado real com quem, quando e resultado.\\n\\nO que o número revela de não óbvio.\\n\\nQuem está ganhando e quem está perdendo.\\n\\nImpacto direto para quem está lendo agora.",
      "pexels_query": "2-3 palavras em inglês"
    }},
    {{
      "slide_number": 3,
      "type": "insight",
      "left_box_text": "palavra de impacto em CAPS",
      "left_box_sub": "subtag",
      "headline": "o que está por baixo disso (máx 6 palavras)",
      "body": "ESCREVA 2 PARÁGRAFOS separados por \\n\\n. A camada que a maioria não viu, com dado ou exemplo concreto.\\n\\nO que muda para quem entende isso antes dos outros.",
      "pexels_query": "2-3 palavras em inglês"
    }},
    {{
      "slide_number": 4,
      "type": "tip",
      "left_box_text": "01",
      "left_box_sub": "MOVE",
      "headline": "postura estratégica específica (máx 5 palavras)",
      "body": "ESCREVA 3 PARÁGRAFOS separados por \\n\\n. Como alguém que entendeu age diferente, com exemplo real.\\n\\nO resultado concreto dessa postura em números ou casos.\\n\\nO que separa quem faz de quem espera.",
      "pexels_query": "2-3 palavras em inglês"
    }},
    {{
      "slide_number": 5,
      "type": "tip",
      "left_box_text": "02",
      "left_box_sub": "MOVE",
      "headline": "segunda postura estratégica (máx 5 palavras)",
      "body": "ESCREVA 4 PARÁGRAFOS separados por \\n\\n. Nova perspectiva que aprofunda o slide anterior.\\n\\nDado ou referência real que valida o argumento.\\n\\nExemplo concreto de empresa ou profissional que já faz isso.\\n\\nA conclusão prática que o leitor pode aplicar hoje.",
      "pexels_query": "2-3 palavras em inglês"
    }},
    {{
      "slide_number": 6,
      "type": "insight",
      "left_box_text": "palavra de impacto em CAPS",
      "left_box_sub": "virada",
      "headline": "o insight que muda tudo (máx 5 palavras)",
      "body": "ESCREVA 2 PARÁGRAFOS separados por \\n\\n. O insight mais forte do carrossel com dado real que o sustenta.\\n\\nA pergunta que fica na cabeça de quem entendeu de verdade.",
      "pexels_query": "2-3 palavras em inglês"
    }},
    {{
      "slide_number": 7,
      "type": "cta",
      "closing": "FRASE DIRETA CONECTADA COM O SLIDE 1 (máx 7 palavras CAPS)",
      "cta_button": "ação específica e irresistível (máx 7 palavras)",
      "urgency": "o que muda para quem agir agora vs quem esperar (máx 12 palavras)",
      "secondary_cta": "Segue pra não perder o próximo → @stefanreiss.ia"
    }}
  ],
  "caption": "LEGENDA COMPLETA:\\n\\n[Reescreva o hook do slide 1 em 2 linhas, mais expandido]\\n\\nO que você vai entender nesse carrossel:\\n[ponto 1 sem traço, em forma de frase]\\n[ponto 2 sem traço, em forma de frase]\\n[ponto 3 sem traço, em forma de frase]\\n\\n[Parágrafo de contexto adicional escrito de forma jornalística]\\n\\nSalva esse post. Você vai querer reler isso quando esse assunto chegar na reunião da sua empresa.\\n\\n{cta_comment}\\n\\n#IAGenerativa #InteligenciaArtificial #FuturoDoTrabalho #IA2026 #ChatGPT #ClaudeAI #GeminiAI #Automacao #PromptEngineering #AIBrasil #Tecnologia #Inovacao #CarreiraIA #AITools #MachineLearning #ArtificialIntelligence"
}}"""

    def _fix_json_newlines(s: str) -> str:
        """Substitui quebras de linha literais dentro de strings JSON por \\n."""
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
            # Erro 529 = API sobrecarregada — aguarda e tenta de novo
            if "529" in str(e) or "overloaded" in str(e).lower():
                wait = 15 * (attempt + 1)
                print(f"  ⏳ API sobrecarregada. Aguardando {wait}s (tentativa {attempt+1}/5)...")
                time.sleep(wait)
            else:
                raise
    raise last_err
