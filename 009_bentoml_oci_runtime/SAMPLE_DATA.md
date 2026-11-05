# Demo auxiliar — falhas típicas da ponte 009

[Voltar à aula 009](README.md).

Este texto não substitui o laboratório do README. Serve para destravar
erros comuns no Host.

## Variável `OCI_RUNTIME`

| Valor | Efeito |
| :--- | :--- |
| omitida ou em branco | `docker` (comportamento legado) |
| `docker` | `bentoml containerize --backend docker` e `docker run` no smoke |
| `podman` | `--backend podman` e `podman run` no smoke |
| outro | a receita falha de propósito |

```bash
OCI_RUNTIME=podman just containerize
OCI_RUNTIME=podman just oci-smoke "$IMAGE"
```

## Sintomas e causas

| Sintoma | Causa frequente | O que tentar |
| :--- | :--- | :--- |
| `Nenhum bento encontrado` | `just build` ainda não correu | `just build` na raiz |
| `backend` / binário não encontrado | Docker ou Podman fora do `PATH` | instalar o runtime ou mudar `OCI_RUNTIME` |
| `port is already allocated` / bind em 3000 | outro processo na porta canónica | parar o `just serve` ou o contêiner anterior |
| `/metrics` não responde a tempo | imagem a subir ou tag errada | esperar; confirmar `"$IMAGE"` com `docker images` / `podman images` |
| Grafana na 3000 | Host com stack alheio | este curso reserva **3000** ao BentoML — ver [`docs/ports.md`](../docs/ports.md) |

## O que esta pasta não sobe

Não há Prometheus, Grafana nem exporter sintético aqui. A prova da aula é
só o runtime OCI com `/metrics` na porta **3000**.
