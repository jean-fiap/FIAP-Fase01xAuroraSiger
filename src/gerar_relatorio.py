"""Monta docs/relatorio_aurora_siger.pdf (Markdown -> DOCX via pandoc -> PDF via LibreOffice)."""
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aurora  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GITHUB_URL = os.environ.get("GITHUB_URL", "https://github.com/SEU-USUARIO/aurora-siger")


def ler(rel):
    return open(os.path.join(RAIZ, rel), encoding="utf-8").read()


def sem_titulo(md):
    return "\n".join(l for l in md.split("\n") if not l.startswith("# "))


leituras = aurora.ler_telemetria(os.path.join(RAIZ, "data", "telemetria_aurora.csv"))
tab_tel = ["| ID | Janela | T.int | T.ext | Integr. | Energia | Pressão | Prop. | Nav. | S.vida | Com. |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
tab_en = ["| ID | Carga (%) | Armazenada | Perdas | Útil | Margem | Autonomia (h) | Decisão |",
          "|---|---|---|---|---|---|---|---|"]
for l in leituras:
    tab_tel.append(f"| {l['leitura_id']} | {l['janela']} | {l['temp_interna_c']} | {l['temp_externa_c']} | "
                   f"{l['integridade_estrutural']} | {l['nivel_energia_pct']} | {l['pressao_tanque_bar']} | "
                   f"{l['mod_propulsao']} | {l['mod_navegacao']} | {l['mod_suporte_vida']} | {l['mod_comunicacao']} |")
    e = aurora.analise_energetica(l["nivel_energia_pct"])
    d = "PRONTO" if aurora.verificar_leitura(l)[0] == aurora.PRONTO else "ABORTADA"
    tab_en.append(f"| {l['leitura_id']} | {e['carga_pct']} | {e['armazenada_kwh']} | {e['perdas_kwh']} | "
                  f"{e['util_kwh']} | {e['margem_kwh']} | {e['autonomia_h']} | {d} |")

md = f"""---
title: "Missão Aurora Siger: Relatório Operacional de Pré-Decolagem"
subtitle: "Atividade Integradora, Fase 1 | FIAP"
author: "Grupo 30: Jean Melo"
date: "Setembro de 2026"
---

# Introdução

Este relatório documenta a validação dos parâmetros técnicos da nave Aurora antes da decolagem na missão Aurora Siger. O trabalho reúne a organização da telemetria, um algoritmo de verificação, sua implementação em Python, a análise energética, uma análise assistida por IA e uma reflexão crítica.

**Repositório público no GitHub:** {GITHUB_URL}

# 1.1 Organização e descrição da telemetria

O dataset `data/telemetria_aurora.csv` contém 20 leituras simuladas na contagem regressiva (T-20min a T-1min), geradas de forma reproduzível pelo script `src/gerar_dataset.py` (seed fixa). Ele inclui leituras nominais, anomalias controladas (uma variável crítica por vez e casos múltiplos) e leituras exatamente nos limites das faixas.

| Variável | Descrição | Tipo / unidade | Faixa segura |
|---|---|---|---|
| temp_interna_c | Temperatura da cabine | °C | 18 a 27 |
| temp_externa_c | Temperatura do ambiente de lançamento | °C | -90 a 60 |
| integridade_estrutural | Integridade do casco | booleano 0/1 | 1 |
| nivel_energia_pct | Carga das baterias | % | 85 a 100 |
| pressao_tanque_bar | Pressão dos tanques de propelente | bar | 190 a 220 |
| mod_propulsao, mod_navegacao, mod_suporte_vida, mod_comunicacao | Status dos módulos críticos | OK / FALHA | OK |

Leituras completas:

{chr(10).join(tab_tel)}

# 1.2 Algoritmo de verificação

Cada leitura começa com uma lista de falhas vazia. Cada regra violada adiciona uma falha (o algoritmo não para na primeira, para informar todos os motivos). Ao final, lista vazia significa **PRONTO PARA DECOLAR**; caso contrário, **DECOLAGEM ABORTADA**.

![Fluxograma do algoritmo de verificação](assets/fluxograma.png){{ width=75% }}

**Pseudocódigo**

```
{ler("docs/algoritmo/pseudocodigo.txt")}
```

# 1.3 Script em Python

O código foi dividido em um módulo com as regras (`src/aurora.py`) e um script principal (`src/verificacao.py`), que lê os dados, executa as verificações e imprime o resultado.

**src/aurora.py**

```python
{ler("src/aurora.py")}
```

**src/verificacao.py**

```python
{ler("src/verificacao.py")}
```

**Resultado da execução**

![Execução do script de verificação](assets/print_execucao.png){{ width=95% }}

# 1.4 Análise energética

Parâmetros da nave: capacidade total de **5.000 kWh**, consumo estimado na decolagem de **3.200 kWh**, perdas energéticas de **8%**, consumo dos sistemas após a decolagem de **45 kW** e reserva mínima de **500 kWh**.

- Energia armazenada = capacidade × carga / 100
- Perdas = energia armazenada × 0,08
- Energia útil = energia armazenada − perdas
- Margem = energia útil − consumo na decolagem
- Autonomia (h) = margem / 45 kW

**Exemplo (L001, carga de 89,6%):** armazenada = 5000 × 0,896 = 4.480 kWh; perdas = 358,4 kWh; útil = 4.121,6 kWh; margem = 4.121,6 − 3.200 = 921,6 kWh; autonomia = 921,6 / 45 = 20,48 h.

**Carga mínima para manter a reserva:** (3.200 + 500) / 0,92 = 4.021,7 kWh, ou seja, **{aurora.carga_minima_para_reserva()}%** da capacidade. O protocolo adota 85% como margem operacional para absorver incertezas no consumo estimado.

{chr(10).join(tab_en)}

![Margem energética por leitura](assets/energia_margem.png){{ width=95% }}

![Sensibilidade da margem à carga](assets/energia_sensibilidade.png){{ width=75% }}

Conclusão energética: todas as leituras com carga de pelo menos 85% têm margem acima de 700 kWh (mais de 15 h de autonomia). As leituras L009 (72,4%) e L017 (80,0%) não garantem a reserva e são abortadas também por esse critério.

# 1.5 Análise assistida por IA

{sem_titulo(ler("docs/analise_ia.md"))}

# 1.6 Reflexão crítica

{sem_titulo(ler("docs/reflexao_critica.md"))}

# Conclusão

O algoritmo aprovou 11 leituras e abortou 9, sempre registrando o motivo de cada aborto. A leitura mais recente (L020, T-1min) está **PRONTA PARA DECOLAR**, resultado confirmado pela janela de estabilidade de 3 leituras sugerida pela análise de IA. O projeto completo (dataset, notebook, scripts e documentação) está no repositório indicado na introdução.
"""

def tabela_png(linhas_md, destino, larguras, abortadas):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cab = [c.strip() for c in linhas_md[0].strip("|").split("|")]
    corpo = [[c.strip() for c in l.strip("|").split("|")] for l in linhas_md[2:]]
    fig, ax = plt.subplots(figsize=(11, 0.32 * (len(corpo) + 1) + 0.2), dpi=160)
    ax.axis("off")
    t = ax.table(cellText=corpo, colLabels=cab, loc="center", cellLoc="center", colWidths=larguras)
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.25)
    for (r, c), cel in t.get_celld().items():
        cel.set_edgecolor("#C9CED8")
        if r == 0:
            cel.set_facecolor("#2F4A7A")
            cel.set_text_props(color="white", weight="bold")
        elif (r - 1) in abortadas:
            cel.set_facecolor("#FBE0E0" if "FALHA" not in corpo[r - 1][c] else "#F4B6B6")
    plt.tight_layout()
    plt.savefig(destino, bbox_inches="tight")
    plt.close(fig)


abortadas = {i for i, l in enumerate(leituras) if aurora.verificar_leitura(l)[0] == aurora.ABORTADA}
tabela_png(tab_tel, os.path.join(RAIZ, "assets", "tabela_telemetria.png"),
           [0.07, 0.09, 0.08, 0.08, 0.08, 0.09, 0.09, 0.09, 0.09, 0.09, 0.09], abortadas)
tabela_png(tab_en, os.path.join(RAIZ, "assets", "tabela_energia.png"),
           [0.09, 0.11, 0.13, 0.11, 0.12, 0.12, 0.14, 0.14], abortadas)
md = md.replace(chr(10).join(tab_tel), "![Leituras de telemetria (linhas em vermelho resultam em aborto)](assets/tabela_telemetria.png){ width=100% }")
md = md.replace(chr(10).join(tab_en), "![Análise energética por leitura](assets/tabela_energia.png){ width=100% }")

tmp = tempfile.mkdtemp()
md_path = os.path.join(tmp, "relatorio.md")
docx_path = os.path.join(tmp, "relatorio_aurora_siger.docx")
open(md_path, "w", encoding="utf-8").write(md)
subprocess.run(["pandoc", md_path, "-o", docx_path, "--resource-path", RAIZ, "--toc-depth=1"], check=True)
subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, docx_path],
               check=True, capture_output=True)
shutil.copyfile(os.path.join(tmp, "relatorio_aurora_siger.pdf"),
                os.path.join(RAIZ, "docs", "relatorio_aurora_siger.pdf"))
print("PDF gerado em docs/relatorio_aurora_siger.pdf")
