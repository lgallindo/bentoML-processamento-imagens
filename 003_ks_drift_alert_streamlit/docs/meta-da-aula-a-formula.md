# Meta da aula — da intenção à fórmula

Booklet completo (DevOps/MLOps → KS): [`booklet-devops-ate-ks.md`](booklet-devops-ate-ks.md).

## Intenção

Este serviço pode responder rápido e com HTTP 200 e, mesmo assim, trabalhar
sobre um mundo diferente do treino. A latência mede espera. Ela não mede se
os dados ainda combinam com a referência.

Nesta aula você mede essa combinação na forma da distribuição de luminância
**L**, resume o afastamento numa estatística **D** e produz um **alerta**
quando **D** cruza um limiar.

## Definições

- **L** — cinza do pixel após `convert("L")`, \(L \in \{0,\ldots,255\}\).
- **Histograma** — \(h_k\) = contagem na faixa \(k\); \(N=\sum h_k\).
- **CDF** — \(F_k=(1/N)\sum_{i\le k}h_i\).
- **δ** — \(\delta_k=|F_k-G_k|\) entre referência e lote.
- **D** — \(D=\max_k\delta_k\) (Kolmogorov–Smirnov).
- **Alerta** — INCONCLUSIVO / ALERTA se \(D\ge 0{,}10\) / TRANQUILO.

O valor-p assintótico existe no software, mas fica fora da regra de alerta
(complexidades de graus de liberdade / dependência entre pixels).

## Exemplo mínimo histograma → CDF

Contagens `[2, 1, 3]` → CDF `[2/6, 3/6, 6/6]`.
