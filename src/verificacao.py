"""
Script de verificacao de pre-decolagem da nave Aurora (missao Aurora Siger).
Execucao (a partir da raiz do projeto): python3 src/verificacao.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aurora import (  # noqa: E402
    ABORTADA, PRONTO, analise_energetica, carga_minima_para_reserva,
    ler_telemetria, verificar_leitura, CAPACIDADE_TOTAL_KWH,
    CONSUMO_DECOLAGEM_KWH, PERDAS_PCT, RESERVA_MINIMA_KWH,
)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV = os.path.join(RAIZ, "data", "telemetria_aurora.csv")


def main():
    leituras = ler_telemetria(CSV)
    print("=" * 64)
    print(" MISSAO AURORA SIGER | VERIFICACAO DE PRE-DECOLAGEM")
    print("=" * 64)
    print(f"Leituras carregadas: {len(leituras)}\n")

    prontas, abortadas = 0, 0
    for leitura in leituras:
        decisao, falhas = verificar_leitura(leitura)
        e = analise_energetica(leitura["nivel_energia_pct"])
        simbolo = "[OK]" if decisao == PRONTO else "[X] "
        print(f"{simbolo} {leitura['leitura_id']} ({leitura['janela']:>8}) -> {decisao}"
              f" | margem {e['margem_kwh']:>7.1f} kWh")
        for f in falhas:
            print(f"       - {f}")
        if decisao == PRONTO:
            prontas += 1
        else:
            abortadas += 1

    print("\n" + "-" * 64)
    print(f"Resumo: {prontas} {PRONTO} | {abortadas} {ABORTADA}")
    print(f"Energia: capacidade {CAPACIDADE_TOTAL_KWH:.0f} kWh | consumo decolagem "
          f"{CONSUMO_DECOLAGEM_KWH:.0f} kWh | perdas {PERDAS_PCT:.0f}% | reserva "
          f"{RESERVA_MINIMA_KWH:.0f} kWh")
    print(f"Carga minima para decolar com reserva: {carga_minima_para_reserva()}%")

    ultima = leituras[-1]
    decisao_final, _ = verificar_leitura(ultima)
    print("-" * 64)
    print(f"STATUS FINAL (leitura mais recente {ultima['leitura_id']}): {decisao_final}")
    print("=" * 64)


if __name__ == "__main__":
    main()
