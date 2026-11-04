# Fixtures — série `ALERTS`

| Arquivo | Estado ilustrado |
| :--- | :--- |
| [`alerts_pending_example.json`](alerts_pending_example.json) | `alertstate=pending` |
| [`alerts_firing_example.json`](alerts_firing_example.json) | `alertstate=firing` |

Formato: resposta típica de
`GET /api/v1/query?query=ALERTS{alertname="BentoMLResponseTimeAnomaly"}`.

Para regenerar a partir de uma instância viva (demo `:9100` ou curso `:9090`
com job `bentoml-imagens`):

```bash
curl -fsS 'http://127.0.0.1:9100/api/v1/query?query=ALERTS' | python3 -m json.tool
```

As figuras em `illustrations/` são esquemas da página `/alerts` (regeneráveis
com `just generate-schematics`). Preferir capturas reais da UI quando o Host
tiver o Prometheus da aula a disparar — guarde scripts de captura em
`.local/021_prometheus_alerts_ui/` (não no README do aluno).
