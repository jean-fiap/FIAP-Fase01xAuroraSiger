"""
Modulo central da missao Aurora Siger.
Contem as faixas seguras, as verificacoes de pre-decolagem e a analise energetica.
"""
import csv

# ---------------------------------------------------------------------------
# 1. Faixas seguras predefinidas (protocolo de pre-decolagem)
# ---------------------------------------------------------------------------
FAIXAS_SEGURAS = {
    "temp_interna_c": (18.0, 27.0, "Temperatura interna (C)"),
    "temp_externa_c": (-90.0, 60.0, "Temperatura externa (C)"),
    "nivel_energia_pct": (85.0, 100.0, "Nivel de energia (%)"),
    "pressao_tanque_bar": (190.0, 220.0, "Pressao dos tanques (bar)"),
}
MODULOS_CRITICOS = {
    "mod_propulsao": "Propulsao",
    "mod_navegacao": "Navegacao",
    "mod_suporte_vida": "Suporte de vida",
    "mod_comunicacao": "Comunicacao",
}

# ---------------------------------------------------------------------------
# 2. Especificacoes energeticas da nave Aurora
# ---------------------------------------------------------------------------
CAPACIDADE_TOTAL_KWH = 5000.0      # capacidade total do banco de baterias
CONSUMO_DECOLAGEM_KWH = 3200.0     # consumo estimado da fase de decolagem
PERDAS_PCT = 8.0                   # perdas (termicas, conversao, cabeamento)
CONSUMO_BASE_KW = 45.0             # consumo dos sistemas apos a decolagem
RESERVA_MINIMA_KWH = 500.0         # reserva exigida apos a decolagem

PRONTO = "PRONTO PARA DECOLAR"
ABORTADA = "DECOLAGEM ABORTADA"


def ler_telemetria(caminho):
    """Le o CSV de telemetria e converte os tipos numericos."""
    leituras = []
    with open(caminho, newline="", encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            for campo in FAIXAS_SEGURAS:
                linha[campo] = float(linha[campo])
            linha["integridade_estrutural"] = int(linha["integridade_estrutural"])
            leituras.append(linha)
    return leituras


def verificar_leitura(leitura):
    """Aplica todas as verificacoes e devolve (decisao, lista_de_falhas)."""
    falhas = []

    # Verificacao 1: integridade estrutural (valor booleano 0/1)
    if leitura["integridade_estrutural"] != 1:
        falhas.append("Integridade estrutural comprometida (0)")

    # Verificacao 2: faixas numericas
    for campo, (minimo, maximo, nome) in FAIXAS_SEGURAS.items():
        valor = leitura[campo]
        if valor < minimo:
            falhas.append(f"{nome} abaixo do minimo: {valor} < {minimo}")
        elif valor > maximo:
            falhas.append(f"{nome} acima do maximo: {valor} > {maximo}")

    # Verificacao 3: status dos modulos criticos
    for campo, nome in MODULOS_CRITICOS.items():
        if leitura[campo].strip().upper() != "OK":
            falhas.append(f"Modulo critico em falha: {nome}")

    # Verificacao 4: margem energetica para a decolagem
    energia = analise_energetica(leitura["nivel_energia_pct"])
    if energia["margem_kwh"] < RESERVA_MINIMA_KWH:
        falhas.append(
            f"Reserva energetica insuficiente: {energia['margem_kwh']:.1f} kWh "
            f"< {RESERVA_MINIMA_KWH:.0f} kWh"
        )

    decisao = PRONTO if not falhas else ABORTADA
    return decisao, falhas


def analise_energetica(carga_pct):
    """
    Autonomia inicial:
      energia_armazenada = capacidade_total * carga / 100
      energia_util       = energia_armazenada * (1 - perdas / 100)
      margem             = energia_util - consumo_decolagem
      autonomia_h        = margem / consumo_base
    """
    armazenada = CAPACIDADE_TOTAL_KWH * carga_pct / 100.0
    perdas = armazenada * PERDAS_PCT / 100.0
    util = armazenada - perdas
    margem = util - CONSUMO_DECOLAGEM_KWH
    autonomia_h = max(margem, 0.0) / CONSUMO_BASE_KW
    return {
        "carga_pct": carga_pct,
        "armazenada_kwh": round(armazenada, 1),
        "perdas_kwh": round(perdas, 1),
        "util_kwh": round(util, 1),
        "margem_kwh": round(margem, 1),
        "autonomia_h": round(autonomia_h, 2),
    }


def carga_minima_para_reserva():
    """Carga minima (%) que garante a reserva apos a decolagem."""
    necessaria = (CONSUMO_DECOLAGEM_KWH + RESERVA_MINIMA_KWH) / (1 - PERDAS_PCT / 100.0)
    return round(necessaria / CAPACIDADE_TOTAL_KWH * 100.0, 2)
