# Mapa — `01_workflow_l_to_alert.png`

Fonte canônica do código: [`../workflow_boxes.py`](../workflow_boxes.py).

| # | Rótulo na figura | Função | Módulo de produção |
| :---: | :--- | :--- | :--- |
| 1 | L (pixel) | `luminancia_L` | `histogram.extract_channel` / `convert("L")` |
| 2 | histograma h | `histograma_h` | `histogram.compute_histogram` |
| 3 | CDF F | `cdf_F` | `histogram.cumulative_distribution` |
| 4 | δ = \|F – G\| | `delta_FG` | (inline em plots / compare) |
| 5 | D = max δ | `D_max_delta` | `ks_compare.ks_statistic` |
| 6 | alerta em D | `alerta_em_D` | `alert_rule.alert_on_d` |

Antes desta nota (2026-10-28) o mapa existia só como figura + caption no
`app.py` / README — sem tabela nem módulo dedicado.
