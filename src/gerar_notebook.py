"""Monta e executa o notebook notebook/aurora_siger.ipynb."""
import os
import nbformat as nbf
from nbclient import NotebookClient

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

cells = [
    md("# Missão Aurora Siger | Relatório Operacional de Pré-Decolagem\n\n"
       "Atividade Integradora, Fase 1 (FIAP). Grupo 30: Jean Melo.\n\n"
       "Este notebook lê a telemetria da nave Aurora, aplica o algoritmo de verificação, "
       "calcula a autonomia energética e decide entre **PRONTO PARA DECOLAR** e **DECOLAGEM ABORTADA**."),
    code("import sys, os\n"
         "sys.path.insert(0, os.path.abspath('../src'))\n"
         "import pandas as pd\n"
         "import matplotlib.pyplot as plt\n"
         "import aurora\n"
         "from aurora import ler_telemetria, verificar_leitura, analise_energetica, carga_minima_para_reserva\n"
         "CSV = '../data/telemetria_aurora.csv'"),
    md("## 1.1 Organização e descrição da telemetria\n\n"
       "| Coluna | Descrição | Unidade / tipo | Faixa segura |\n|---|---|---|---|\n"
       "| `leitura_id` | Identificador da leitura | texto | |\n"
       "| `janela` | Momento da contagem regressiva | T-min | |\n"
       "| `temp_interna_c` | Temperatura da cabine | °C | 18 a 27 |\n"
       "| `temp_externa_c` | Temperatura do ambiente de lançamento | °C | -90 a 60 |\n"
       "| `integridade_estrutural` | Integridade do casco (booleano) | 0/1 | 1 |\n"
       "| `nivel_energia_pct` | Carga das baterias | % | 85 a 100 |\n"
       "| `pressao_tanque_bar` | Pressão dos tanques de propelente | bar | 190 a 220 |\n"
       "| `mod_*` | Status dos 4 módulos críticos | OK/FALHA | OK |"),
    code("df = pd.read_csv(CSV)\nprint(df.shape)\ndf.head(10)"),
    code("df.describe().round(2)"),
    code("modulos = list(aurora.MODULOS_CRITICOS)\n"
         "df[modulos].apply(pd.Series.value_counts).fillna(0).astype(int)"),
    md("## 1.2 Algoritmo de verificação\n\n"
       "O fluxograma e o pseudocódigo completos estão em `docs/algoritmo/`. Resumo da lógica: "
       "cada leitura começa com uma lista de falhas vazia; cada regra violada adiciona uma falha; "
       "se a lista terminar vazia, a nave está **PRONTA**, caso contrário a decolagem é **ABORTADA**.\n\n"
       "![Fluxograma](../assets/fluxograma.png)"),
    md("## 1.3 Script em Python\n\nFaixas seguras usadas pelo módulo `src/aurora.py`:"),
    code("pd.DataFrame([(k, v[0], v[1]) for k, v in aurora.FAIXAS_SEGURAS.items()],\n"
         "             columns=['variavel', 'minimo', 'maximo'])"),
    code("leituras = ler_telemetria(CSV)\n"
         "resultados = []\n"
         "for l in leituras:\n"
         "    decisao, falhas = verificar_leitura(l)\n"
         "    resultados.append({'leitura_id': l['leitura_id'], 'janela': l['janela'],\n"
         "                       'decisao': decisao, 'falhas': '; '.join(falhas) or '-'})\n"
         "res = pd.DataFrame(resultados)\n"
         "res"),
    code("print(res['decisao'].value_counts().to_string())\n"
         "final = res.iloc[-1]\n"
         "print(f\"\\nSTATUS FINAL ({final['leitura_id']}, {final['janela']}): {final['decisao']}\")"),
    md("Execução do script completo pelo terminal (`python3 src/verificacao.py`):"),
    code("import subprocess\n"
         "print(subprocess.run([sys.executable, '../src/verificacao.py'], capture_output=True, text=True).stdout)"),
    md("## 1.4 Análise energética\n\n"
       "Parâmetros da nave: capacidade total **5.000 kWh**, consumo estimado na decolagem **3.200 kWh**, "
       "perdas energéticas **8%**, consumo dos sistemas após a decolagem **45 kW** e reserva mínima **500 kWh**.\n\n"
       "- energia armazenada = capacidade × carga / 100\n"
       "- perdas = armazenada × 8%\n"
       "- energia útil = armazenada − perdas\n"
       "- margem = energia útil − consumo na decolagem\n"
       "- autonomia (h) = margem / 45 kW\n\n"
       "**Exemplo (L001, carga 89,6%):** 5000 × 0,896 = 4480 kWh; perdas = 358,4 kWh; "
       "útil = 4121,6 kWh; margem = 921,6 kWh; autonomia = 20,48 h."),
    code("en = pd.DataFrame([{'leitura_id': l['leitura_id'], **analise_energetica(l['nivel_energia_pct'])}\n"
         "                   for l in leituras])\n"
         "en"),
    code("print('Carga minima para decolar mantendo a reserva:', carga_minima_para_reserva(), '%')\n"
         "print('Autonomia media apos a decolagem:', round(en['autonomia_h'].mean(), 2), 'h')"),
    code("cores = ['#2E8B57' if d == aurora.PRONTO else '#C0392B' for d in res['decisao']]\n"
         "fig, ax = plt.subplots(figsize=(11, 4))\n"
         "ax.bar(en['leitura_id'], en['margem_kwh'], color=cores)\n"
         "ax.axhline(aurora.RESERVA_MINIMA_KWH, ls='--', color='#333')\n"
         "ax.set_ylabel('Margem apos a decolagem (kWh)')\n"
         "ax.set_title('Margem energetica por leitura (verde: pronto | vermelho: abortada)')\n"
         "plt.xticks(rotation=45); plt.tight_layout(); plt.show()"),
    md("## 1.5 Análise assistida por IA\n\n"
       "O prompt e a resposta completa estão em `docs/analise_ia.md`. Abaixo, a classificação sugerida pela IA "
       "(NOMINAL, ATENÇÃO, CRÍTICA) reproduzida em código para conferência."),
    code("def classificar(l):\n"
         "    decisao, _ = verificar_leitura(l)\n"
         "    if decisao == aurora.ABORTADA:\n"
         "        return 'CRITICA'\n"
         "    no_limite = any(l[c] in (mn, mx) for c, (mn, mx, _) in aurora.FAIXAS_SEGURAS.items())\n"
         "    return 'ATENCAO' if no_limite else 'NOMINAL'\n\n"
         "res['classe_ia'] = [classificar(l) for l in leituras]\n"
         "res.groupby('classe_ia')['leitura_id'].apply(list)"),
    md("Principais anomalias apontadas: energia insuficiente (L009, L017), falha estrutural (L010), "
       "superaquecimento correlacionado com calor externo (L011, L016), oscilação improvável de pressão "
       "entre L012 e L013 (possível falha de sensor), falhas de módulos críticos (L014, L015, L017) e "
       "instabilidade da sequência (a nave volta a ficar PRONTA logo após nove abortos).\n\n"
       "Sugestões: hierarquia de severidade, janela de estabilidade de 3 leituras, estado de ATENÇÃO, "
       "redundância de sensores e verificação da taxa de variação."),
    code("# Sugestao da IA aplicada: janela de estabilidade (3 leituras aprovadas seguidas)\n"
         "ult = res['decisao'].tail(3).tolist()\n"
         "print('Ultimas 3 leituras:', ult)\n"
         "print('Liberacao com janela de estabilidade:', aurora.PRONTO if all(d == aurora.PRONTO for d in ult) else aurora.ABORTADA)"),
    md("## 1.6 Reflexão crítica\n\n"
       "O texto completo está em `docs/reflexao_critica.md` e aborda ética e responsabilidade, "
       "impacto social da exploração espacial e sustentabilidade tecnológica.\n\n"
       "## Conclusão\n\n"
       "O algoritmo aprovou 11 leituras e abortou 9, sempre informando o motivo. A leitura mais recente (L020) "
       "está **PRONTA PARA DECOLAR**, inclusive considerando a janela de estabilidade sugerida pela IA."),
]

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
destino = os.path.join(RAIZ, "notebook", "aurora_siger.ipynb")
NotebookClient(nb, timeout=120, kernel_name="python3",
               resources={"metadata": {"path": os.path.join(RAIZ, "notebook")}}).execute()
nbf.write(nb, destino)
print("Notebook executado:", destino)
