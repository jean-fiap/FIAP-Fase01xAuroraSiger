# Análise assistida por IA

**Ferramenta utilizada:** Claude (Anthropic), modelo de linguagem de uso geral.
**Entrada fornecida:** o arquivo `data/telemetria_aurora.csv` (20 leituras) e a tabela de faixas seguras do projeto.

## Prompt utilizado

> Você é um analista de controle de missão. Abaixo estão 20 leituras de telemetria de pré-decolagem da nave Aurora (CSV) e as faixas seguras do protocolo. Faça: (1) a classificação de cada leitura em NOMINAL, ATENÇÃO ou CRÍTICA, explicando o critério; (2) a identificação de anomalias, inclusive as que não violam nenhuma faixa mas parecem suspeitas; (3) sugestões de risco e de melhorias no protocolo de verificação. Responda em português, de forma objetiva.

## Resposta da IA (resumida e revisada pelo aluno)

### 1. Classificação dos dados

Critério adotado: **CRÍTICA** quando ao menos uma regra do protocolo é violada; **ATENÇÃO** quando todas as regras passam, mas alguma variável está exatamente no limite da faixa; **NOMINAL** nos demais casos.

| Classe | Leituras | Observação |
|---|---|---|
| NOMINAL | L001 a L008 | Todas as variáveis com folga confortável em relação aos limites. |
| ATENÇÃO | L018, L019, L020 | Aprovadas, mas no limite: energia em 85,0% (L018), pressão em 190,0 bar (L019), temperatura interna em 27,0 °C e pressão em 220,0 bar (L020). |
| CRÍTICA | L009 a L017 | Violam uma ou mais regras e resultam em DECOLAGEM ABORTADA. |

### 2. Anomalias identificadas

1. **Energia insuficiente (L009 e L017):** carga de 72,4% e 80,0%. Em L017 a margem pós-decolagem (480 kWh) fica apenas 20 kWh abaixo da reserva exigida, o que mostra que a regra de 85% é mais conservadora que o cálculo energético (80,43%).
2. **Falha estrutural (L010):** integridade = 0 com todos os demais sensores normais. É o tipo de falha que nenhum outro indicador antecipa, por isso deve ter prioridade máxima.
3. **Superaquecimento (L011 e L016):** em L016 a temperatura externa de 78 °C coincide com a interna de 29,5 °C, sugerindo transferência de calor do ambiente para a cabine (anomalias correlacionadas, não independentes).
4. **Pressão fora da faixa nos tanques (L012 e L013):** uma subpressão (176 bar, possível vazamento) e uma sobrepressão (234 bar, risco de ruptura) em janelas consecutivas. Uma oscilação dessa amplitude em 1 minuto é fisicamente improvável e pode indicar **falha do próprio sensor**.
5. **Módulos críticos (L014, L015, L017):** falhas de propulsão, suporte de vida e comunicação. A falha de suporte de vida (L015) é a mais grave para a tripulação.
6. **Anomalia sem violação de faixa:** a temperatura externa varia de forma abrupta entre leituras consecutivas (por exemplo, de valores próximos a -80 °C para valores positivos em 1 minuto). Todas estão dentro da faixa, mas uma variação dessas é incompatível com uma mesma plataforma de lançamento, o que aponta para ruído de sensor ou, neste projeto, para o caráter simulado dos dados.
7. **Instabilidade da sequência:** a nave alterna entre PRONTO e ABORTADA na contagem regressiva (T-13 aprovado, T-12 a T-4 abortados, T-3 a T-1 aprovados). Um protocolo real não deveria liberar a decolagem logo após nove abortos seguidos sem uma investigação.

### 3. Sugestões de risco e melhorias

- **Hierarquia de severidade:** integridade estrutural e suporte de vida devem abortar imediatamente (falha "go/no-go" absoluta); outras variáveis podem admitir nova leitura de confirmação.
- **Janela de estabilidade:** exigir que as últimas N leituras (por exemplo, 3 consecutivas) estejam aprovadas antes do status final PRONTO, evitando liberar a nave após uma sequência de falhas.
- **Faixa de alerta:** criar o estado ATENÇÃO no script para leituras no limite ou próximas dele (por exemplo, a menos de 5% da faixa), exigindo validação humana.
- **Redundância de sensores:** confirmar leituras extremas (como a variação de pressão em L012/L013) com um segundo sensor antes de concluir que há falha no tanque.
- **Taxa de variação:** além dos limites absolutos, verificar a variação entre leituras consecutivas para detectar sensores com defeito.
- **Energia:** manter o mínimo de 85% como margem operacional, já que ele cobre incertezas no consumo estimado da decolagem (3.200 kWh).

## Avaliação crítica do uso da IA

A IA acelerou a leitura dos dados e apontou padrões que as regras fixas do script não capturam (anomalias correlacionadas, variações abruptas e a instabilidade da sequência). Por outro lado, toda a resposta foi conferida contra o CSV e o resultado do script: a IA não substitui o algoritmo determinístico, que é auditável e sempre dá a mesma resposta para a mesma entrada. Em uma missão real, a IA atua como **apoio à decisão**, e a decisão de abortar continua sob responsabilidade da equipe humana.
