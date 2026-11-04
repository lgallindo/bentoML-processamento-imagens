# Dados e portas da demo (aula 022)

Quando `:3000` / `:9090` no Host estão ocupados por outros processos, use
esta demo **auxiliar**. Ela não substitui o BentoML canónico nem o
Prometheus do curso documentados em [`docs/ports.md`](../docs/ports.md).

| Papel | Porta | URL |
| :--- | ---: | :--- |
| Exporter sintético (métricas) | **8022** | <http://127.0.0.1:8022/metrics> |
| Prometheus da demo (UI Rules) | **9112** | <http://127.0.0.1:9112/rules> |

Régua do curso: exporter demo = `8000 + N`, Prometheus demo = `9090 + N`
(N = 22).

## Subida rápida (harness)

Na pasta desta aula:

~~~bash
cd 022_prometheus_rules_ui
bash scripts/capture_screenshots.sh
# CAPTURE_KEEP=1 bash scripts/capture_screenshots.sh   # mantém containers
~~~

O script sobe exporter + Prometheus em rede Docker, espera o job
`bentoml-imagens` em `UP`, grava fixtures JSON e regenera as capturas em
`illustrations/`. A UI fica em **9112** enquanto o harness corre.

Confirme:

~~~bash
curl -fsS http://127.0.0.1:9112/targets | head
curl -fsS 'http://127.0.0.1:9112/api/v1/rules' | python3 -m json.tool | head
~~~

Abra <http://127.0.0.1:9112/rules> e siga o ritual do README (grupo
`bentoml-response-time`, recording + alerting).

## Relação com o serviço real

| Aspecto | Real (`:3000` / `:9090`) | Demo (`:8022` / `:9112`) |
| :--- | :--- | :--- |
| Origem das durações | Inferência e I/O verdadeiros | Gerador da aula 010 |
| Objetivo | Operar o stack do curso | Ler `/rules` com sinal limpo |
| Job | `bentoml-imagens` → `127.0.0.1:3000` | `bentoml-imagens` → exporter demo |
| Evidência de desempenho do modelo | Não | Tampouco |
