# Notas de experimento — freeze, pixel vs média

Material de apoio ao handout da [aula 003](../README.md). Não substitui o
README; aprofunda **duas** decisões de desenho que o painel assume sem
repetir o arco DevOps→MLOps.

## 1. Por que 50 imagens se há 110 por tema

O repositório traz **110** praias e **110** florestas em `samples/`. O freeze
da aula usa **50** de cada lado de propósito:

| Papel | Fatia | Arquivo típico |
| :--- | :--- | :--- |
| Referência (treino) | `beaches[:50]` | `corpus_stats.json` |
| Controle (mesmo tema) | `beaches[50:100]` | `batch_stats/control.json` |
| Divergente | `forests[:50]` | `batch_stats/forests.json` |

Tamanhos **pareados** facilitam ler o alerta: mesmo \(n\) nos dois lados,
sem misturar “faltou imagem” com “mudou a forma de L”. Não é escassez de
dados; é o desenho do experimento.

Confirmação operacional (sem UI):

```bash
just verify-ks-alert control
just verify-ks-alert forests
```

Espera-se ordem de grandeza \(D \approx 0{,}05\) (TRANQUILO / QUIET na regra
D+p) no controle e \(D \approx 0{,}23\) nas florestas.

## 2. L por pixel versus média de L por imagem

Medido com o freeze `beaches[:50]` contra `forests[:50]` e contra
`beaches[50:100]`:

| Lente | beaches[:50] vs forests[:50] | beaches[:50] vs beaches[50:100] |
| :--- | :--- | :--- |
| **L por pixel** | D ≈ 0,23 → ALERTA | D ≈ 0,05 → TRANQUILO |
| **Média de L por imagem** | D ≈ 0,54 → ALERTA | D ≈ 0,18 → ALERTA |

### Por que a média falha no controle

Cada foto vira **um** número (brilho global). O KS passa a comparar duas
nuvens de 50 pontos em \(\mathbb{R}\). Variações inocentes de exposição entre
o primeiro e o segundo bloco de praias empurram as médias o bastante para
cruzar \(D \ge 0{,}10\) — **falso alerta** de drift de tema.

O histograma agregado de **pixels** preserva a **forma** da distribuição de
tons (quantos pixels escuros vs claros). Dois trechos do mesmo tema de praia
continuam parecidos na forma, mesmo que a média mude um pouco.

### Quando a média ainda aparece

A aula **008** (PSI) usa média de L por imagem de propósito (P2), com faixas
por quantis e limiares de crédito — outro aparelho, outra pergunta. Não
confunda com o eixo do alerta KS desta pasta.

## 3. Relação com o anti-vazamento de índices

Referência e controle **não** podem compartilhar arquivos. O módulo
`sample_sets.py` fixa `CORPUS_TAKE = 50` e `CONTROL_OFFSET = 50`. Miniaturas
do Streamlit usam essas fatias; ver também
`tests/test_sample_sets.py`.

## 4. Como regenerar os números

```bash
just extract-features
just build-corpus-stats
just build-demo-batches
just verify-ks-alert control
just verify-ks-alert forests
```

Se os valores divergirem materialmente do quadro acima, atualize esta nota
e a tabela do experimento no README **na mesma alteração**.
