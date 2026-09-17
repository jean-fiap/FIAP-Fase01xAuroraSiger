"""Gera os prints da execucao e o grafico energetico usados no README e no relatorio."""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aurora import (analise_energetica, ler_telemetria, verificar_leitura, PRONTO,  # noqa: E402
                    RESERVA_MINIMA_KWH, carga_minima_para_reserva)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(RAIZ, "assets")


def print_terminal(txt_path, png_path, titulo):
    linhas = open(txt_path, encoding="utf-8").read().rstrip("\n").split("\n")
    fonte = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    lh, pad, barra = 21, 22, 36
    w = max(fonte.getlength(l) for l in linhas) + pad * 2
    h = barra + pad * 2 + lh * len(linhas)
    img = Image.new("RGB", (int(w), int(h)), "#1E1F29")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, barra], fill="#2B2D3A")
    for i, c in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
        d.ellipse([14 + i * 22, 12, 26 + i * 22, 24], fill=c)
    d.text((90, 10), titulo, font=fb, fill="#B8BCCB")
    y = barra + pad
    for l in linhas:
        cor = "#E6E6E6"
        if "[OK]" in l or "PRONTO PARA DECOLAR" in l and "STATUS" in l:
            cor = "#7EE2A0"
        if "[X]" in l:
            cor = "#FF8A8A"
        if l.strip().startswith("- "):
            cor = "#F2C77B"
        if l.startswith("$"):
            cor = "#8AB4FF"
        d.text((pad, y), l, font=fonte, fill=cor)
        y += lh
    img.save(png_path)


def grafico_energia(png_path):
    leituras = ler_telemetria(os.path.join(RAIZ, "data", "telemetria_aurora.csv"))
    ids = [l["leitura_id"] for l in leituras]
    margens = [analise_energetica(l["nivel_energia_pct"])["margem_kwh"] for l in leituras]
    cores = ["#2E8B57" if verificar_leitura(l)[0] == PRONTO else "#C0392B" for l in leituras]
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=140)
    ax.bar(ids, margens, color=cores, width=0.65)
    ax.axhline(RESERVA_MINIMA_KWH, color="#333", ls="--", lw=1.2)
    ax.text(len(ids) - 0.5, RESERVA_MINIMA_KWH + 25, f"reserva minima {RESERVA_MINIMA_KWH:.0f} kWh",
            ha="right", fontsize=9, color="#333")
    ax.set_ylabel("Margem apos a decolagem (kWh)")
    ax.set_title("Margem energetica por leitura (verde: pronto | vermelho: abortada)", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close(fig)

    cargas = list(range(60, 101))
    marg = [analise_energetica(c)["margem_kwh"] for c in cargas]
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=140)
    ax.plot(cargas, marg, color="#2F5DA8", lw=2)
    ax.axhline(RESERVA_MINIMA_KWH, color="#333", ls="--", lw=1)
    ax.axvline(85, color="#C0392B", ls=":", lw=1.2)
    cm = carga_minima_para_reserva()
    ax.axvline(cm, color="#E67E22", ls=":", lw=1.2)
    ax.text(85.5, min(marg) + 50, "minimo operacional 85%", color="#C0392B", fontsize=8)
    ax.text(cm - 0.5, max(marg) - 150, f"minimo energetico {cm}%", color="#E67E22", fontsize=8, ha="right")
    ax.set_xlabel("Carga atual (%)")
    ax.set_ylabel("Margem apos a decolagem (kWh)")
    ax.set_title("Sensibilidade da margem energetica a carga das baterias", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS, "energia_sensibilidade.png"))
    plt.close(fig)


if __name__ == "__main__":
    txt = os.path.join(ASSETS, "saida_verificacao.txt")
    conteudo = open(txt, encoding="utf-8").read()
    with open(txt, "w", encoding="utf-8") as f:
        if not conteudo.startswith("$"):
            conteudo = "$ python3 src/verificacao.py\n" + conteudo
        f.write(conteudo)
    print_terminal(txt, os.path.join(ASSETS, "print_execucao.png"), "Terminal | aurora-siger")
    grafico_energia(os.path.join(ASSETS, "energia_margem.png"))
    print("Imagens geradas em assets/")
