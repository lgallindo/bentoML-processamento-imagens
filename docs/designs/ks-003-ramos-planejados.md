# Ramos planejados — lição 003 (KS / PSI / entrada×saída)

Estado: rascunho de planejamento (atualizado 2026-10-27).
Lição atual: referência `samples/beaches/` → lote homogêneo; KS sobre
**L por pixel** (não sobre a média por imagem).

---

## Ramo A — Lote de produção = praias + outro tema de paisagem

**Ideia.** Mesmo pipeline (histograma de L → CDF → δ → D → banner), mas o
lote junta **praias e florestas** num batch misto.

**Por quê.** Tráfego real raramente é um tema puro. O alerta ainda dispara
quando metade dos pedidos “parece” treino?

**Como (rascunho).**

1. Manter `corpus_stats.json` nas primeiras 50 praias.
2. Produção: N de `beaches/` (fora do freeze) + N de `forests/` (ex.: 25+25).
3. Gravar `batch_stats/beaches+forests.json` (ou `landscapes`).
4. Comparar D/banner com `forests` puro e `control` puro.

**Critério.** Tabela D + banner para misto vs puro.

---

## Ramo B — Population Stability Index (PSI)

**Ideia.** Análise equivalente em espírito (referência vs lote → número →
faixas de alerta), trocando KS por **PSI** nas mesmas faixas de uma variável
escolhida.

**Fórmula (rascunho).** Com as mesmas K faixas na referência e no lote,

```text
PSI = Σ_b (p_lote[b] − p_ref[b]) · ln(p_lote[b] / p_ref[b])
```

(com suavização se alguma massa for zero). Faixas clássicas de crédito:
&lt; 0,10 “estável”; 0,10–0,25 “investigar”; &gt; 0,25 “mudança forte”
(convenção Siddiqi / monitoração de scorecards — ver bibliografia da lição).

### Debate — qual variável monitorar? (propostas para grelha)

| # | Variável | Unidade | Prós | Contras |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | Histograma de **L por pixel** (igual à aula KS) | pixel | Comparável bit-a-bit com o D atual; mesma extração | Massas de pixel não são i.i.d.; PSI herda o mesmo enviesamento de “n enorme” |
| **P2** | **Média de L por imagem** | imagem | Uma observação = um pedido; alinhado ao PSI de scorecards; n = nº de imagens | Perde textura dentro da foto; sensível sobretudo a brilho global |
| **P3** | **Score / saída do serviço** (ex.: média de L da imagem **já em cinza** devolvida) | imagem (saída) | Monitora o que o modelo *emite*; detecta mudança de uso mesmo com entrada estável | Nesta aula a saída é determinística em L; pode espelhar demais a entrada |
| **P4** | Vetor curto (média L + desvio L + fração de pixels escuros) → PSI por coordenada ou na 1ª PC | imagem | Mais rico que um escalar | Explode o handout; precisa de escolha de bins por eixo |

**Recomendação provisória para a grelha de amanhã:** implementar **P2** como
caminho principal do ramo PSI (uma linha por imagem, bins por quantis da
referência) e manter **P1** como espelho didático do KS atual — a turma vê o
mesmo dado sob duas lentes. **P3** fica acoplado ao ramo C (entrada×saída).

**Perguntas para grelhar o dono do produto (amanhã):**

1. O alerta deve disparar quando muda o *tema visual* ou quando muda o
   *brilho médio do pedido*?
2. Preferimos falsos positivos altos (pixel/PSI-P1) ou sensibilidade a tema
   com n=imagens (média/PSI-P2)?
3. Em produção, o “score” a monitorar seria a saída do filtro ou um modelo
   downstream ainda inexistente nesta árvore?
4. Limiares 0,10 / 0,25 do crédito bancário fazem sentido para imagens, ou
   calibramos nos lotes `control` vs `forests` desta aula?

---

## Ramo C — KS na entrada **e** KS na saída

**Ideia.** Dois KSs no mesmo show:

1. **Entrada:** distribuição de L das imagens **submetidas** (treino vs lote).
2. **Saída:** distribuição de L das imagens **devolvidas** por
   `/inference-grayscale` (treino passado pelo serviço vs lote passado pelo
   serviço).

**Por quê.** Separar “os pedidos mudaram” de “o que o serviço emite mudou”.
Se a entrada diverge e a saída acompanha, o filtro está espelhando o drift.
Se a entrada for estável e a saída divergir, algo no caminho de inferência
mudou (ou o exercício forçou outro pré-processamento).

**Como (rascunho).**

1. Referência de entrada: freeze atual (`beaches[:50]` features).
2. Referência de saída: rodar as mesmas 50 pelo serviço (ou `Image.convert("L")`
   local espelhando o grayscale) → `corpus_stats_output.json`.
3. Lote de entrada: `batch_stats/forests.json` (já existe).
4. Lote de saída: após `exercise-theme`, agregar L das imagens salvas da
   resposta (ou re-extrair do PNG cinza).
5. Streamlit: dois banners lado a lado — “KS entrada” e “KS saída”.

**Critério.** Para `control`, ambos TRANQUILO; para `forests`, documentar se
entrada e saída contam a mesma história (esperado neste filtro determinístico).

---

## Ramo D — Histograma de L vs médias: falso alerta no controle

**Ideia.** Explicitar no show o contraste já medido: KS sobre **L por pixel**
vs KS sobre **média de L por imagem**, com ênfase no par **treino vs
controle** (mesmo tema).

**Números neste host (freeze 50×50):**

| Par | D (pixels) | Banner pixels | D (médias) | Banner médias (regra D≥0,10) |
| :--- | ---: | :--- | ---: | :--- |
| beaches[:50] vs forests[:50] | ≈0,23 | SINAL PARCIAL | ≈0,54 | ALERTA (D e p) |
| beaches[:50] vs beaches[50:100] | ≈0,05 | **TRANQUILO** | ≈0,18 | **SINAL PARCIAL** (falso alerta) |

**Por quê.** A média colapsa textura e oscila entre trechos do mesmo tema; o
limiar didático D ≥ 0,10 pega essa oscilação. O histograma agregado de pixels
mantém o controle quieto.

**Como (rascunho).**

1. Painel ou toggle no Streamlit: “unidade = pixel | unidade = média/imagem”.
2. Sempre mostrar o lote `control` ao lado de `forests`.
3. Texto fixo: “no controle, média ⇒ SINAL PARCIAL; pixels ⇒ TRANQUILO”.

**Critério.** A turma verbaliza o falso positivo antes de defender o freeze
em L por pixel.

---

## Nota — por que o freeze usa 50 e não as 110

Há **110** imagens por tema no repositório. O freeze didático usa **50** de
propósito: metade das praias como “treino”, outra fatia (51–100) como
controle de mesmo tema, e 50 florestas como lote divergente — tamanhos
pareados para a turma comparar. Não é limite do corpus; é desenho do
experimento. Expandir para 110×110 é um experimento à parte (ver números no
README).

---

## Ramo E — Anomalia (implementado como lição 005)

Ver `005_ks_anomaly_detection_streamlit/`: candidato ou janela temporal vs
referência; time boxing; reuso de L/CDF/D.
