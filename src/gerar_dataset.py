"""
Gerador do dataset de telemetria da missao Aurora Siger.
Produz leituras de pre-decolagem cobrindo cenarios seguros e com anomalias.
Execucao: python3 gerar_dataset.py
Saida: data/telemetria_aurora.csv
"""
import csv
import os
import random

random.seed(42)

# Faixas seguras predefinidas (protocolo de pre-decolagem)
FAIXAS = {
    "temp_interna_c": (18.0, 27.0),
    "temp_externa_c": (-90.0, 60.0),
    "nivel_energia_pct": (85.0, 100.0),
    "pressao_tanque_bar": (190.0, 220.0),
}
MODULOS = ["mod_propulsao", "mod_navegacao", "mod_suporte_vida", "mod_comunicacao"]

CAMPOS = [
    "leitura_id", "janela", "temp_interna_c", "temp_externa_c",
    "integridade_estrutural", "nivel_energia_pct", "pressao_tanque_bar",
    "mod_propulsao", "mod_navegacao", "mod_suporte_vida", "mod_comunicacao",
]


def leitura_segura(lid, janela):
    return {
        "leitura_id": lid,
        "janela": janela,
        "temp_interna_c": round(random.uniform(19, 26), 1),
        "temp_externa_c": round(random.uniform(-85, 55), 1),
        "integridade_estrutural": 1,
        "nivel_energia_pct": round(random.uniform(86, 99), 1),
        "pressao_tanque_bar": round(random.uniform(192, 218), 1),
        "mod_propulsao": "OK",
        "mod_navegacao": "OK",
        "mod_suporte_vida": "OK",
        "mod_comunicacao": "OK",
    }


def gerar():
    linhas = []
    n = 1

    # 8 leituras totalmente seguras (esperado: PRONTO)
    for i in range(8):
        linhas.append(leitura_segura(f"L{n:03d}", f"T-{15 - i}min"))
        n += 1

    # Anomalias controladas (esperado: ABORTADA), uma variavel critica por vez
    anomalias = [
        {"nivel_energia_pct": 72.4},                       # energia abaixo do minimo
        {"integridade_estrutural": 0},                     # falha estrutural
        {"temp_interna_c": 31.8},                          # superaquecimento interno
        {"pressao_tanque_bar": 176.0},                     # pressao baixa nos tanques
        {"pressao_tanque_bar": 234.0},                     # sobrepressao nos tanques
        {"mod_propulsao": "FALHA"},                        # modulo critico em falha
        {"mod_suporte_vida": "FALHA"},                     # suporte de vida em falha
        {"temp_externa_c": 78.0, "temp_interna_c": 29.5},  # calor externo + interno
        {"nivel_energia_pct": 80.0, "mod_comunicacao": "FALHA"},  # multipla
    ]
    for i, override in enumerate(anomalias):
        base = leitura_segura(f"L{n:03d}", f"T-{7 - (i % 7)}min")
        base.update(override)
        linhas.append(base)
        n += 1

    # 3 leituras de borda (limite exato das faixas seguras -> PRONTO)
    borda = [
        {"nivel_energia_pct": 85.0},        # minimo exato de energia
        {"pressao_tanque_bar": 190.0},      # limite inferior de pressao
        {"temp_interna_c": 27.0, "pressao_tanque_bar": 220.0},  # limites superiores
    ]
    for override in borda:
        base = leitura_segura(f"L{n:03d}", "T-2min")
        base.update(override)
        linhas.append(base)
        n += 1

    return linhas


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    saida = os.path.join(aqui, "..", "data", "telemetria_aurora.csv")
    saida = os.path.abspath(saida)
    linhas = gerar()
    # contagem regressiva sequencial: T-20min ate T-1min
    for i, linha in enumerate(linhas):
        linha["janela"] = f"T-{len(linhas) - i}min"
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(linhas)
    print(f"Dataset gerado: {saida}")
    print(f"Total de leituras: {len(linhas)}")


if __name__ == "__main__":
    main()
