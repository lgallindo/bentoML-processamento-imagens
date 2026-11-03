"""Expõe métricas sintéticas: dois minutos estáveis, lentos e recuperados.

O relógio determina quantas observações existem. Visitar /metrics não gera
requisições fictícias adicionais. As três fases se repetem a cada seis minutos.
"""

from __future__ import annotations

import argparse
import math
import time
from http.server import BaseHTTPRequestHandler, HTTPServer


BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, math.inf)
OBSERVATIONS = {
    "/inference-grayscale": (0.004,) * 2 + (0.008,) * 3 + (0.02,) * 7
    + (0.04,) * 6 + (0.08,) * 2,
    "/inference-blur": (0.008,) + (0.02,) * 3 + (0.04,) * 4 + (0.08,) * 2,
    "/inference-resize": (0.004, 0.008, 0.02, 0.04, 0.08),
}
REQUESTS = "bentoml_service_request_total"
DURATION = "bentoml_service_request_duration_seconds"


def phase_seconds(elapsed: int, duration: int = 120) -> tuple[int, int]:
    """Segundos acumulados de latência normal e lenta; elapsed >= 0, duration > 0."""
    cycles, remainder = divmod(elapsed, 3 * duration)
    slow = cycles * duration + min(max(remainder - duration, 0), duration)
    return elapsed - slow, slow


def histogram(elapsed: int, endpoint: str, duration: int = 120) -> dict:
    """Contagens cumulativas e soma das durações sintéticas desde a partida."""
    normal_seconds, slow_seconds = phase_seconds(elapsed, duration)
    observations = OBSERVATIONS[endpoint]
    cumulative = [
        normal_seconds * sum(value <= upper for value in observations)
        + slow_seconds * sum(10 * value <= upper for value in observations)
        for upper in BUCKETS
    ]
    return {
        "cumulative": cumulative,
        "count": elapsed * len(observations),
        "sum": sum(observations) * (normal_seconds + 10 * slow_seconds),
    }


def render_metrics(elapsed: int, duration: int = 120) -> str:
    """Formato texto Prometheus 0.0.4; tempos são atribuídos pelo coletor."""
    lines = [
        f"# HELP {REQUESTS} Requisicoes sinteticas acumuladas desde a partida.",
        f"# TYPE {REQUESTS} counter",
    ]
    for endpoint, observations in OBSERVATIONS.items():
        lines.append(
            f'{REQUESTS}{{endpoint="{endpoint}",http_response_code="200"}} '
            f"{elapsed * len(observations)}"
        )
    lines.extend([
        f"# HELP {DURATION} Duracoes sinteticas em segundos.",
        f"# TYPE {DURATION} histogram",
    ])
    for endpoint in OBSERVATIONS:
        values = histogram(elapsed, endpoint, duration)
        for upper, count in zip(BUCKETS, values["cumulative"], strict=True):
            le = "+Inf" if math.isinf(upper) else str(upper)
            lines.append(f'{DURATION}_bucket{{endpoint="{endpoint}",le="{le}"}} {count}')
        lines.append(f'{DURATION}_count{{endpoint="{endpoint}"}} {values["count"]}')
        lines.append(f'{DURATION}_sum{{endpoint="{endpoint}"}} {values["sum"]:.9f}')
    lines.extend([
        "# HELP aula004_demo_phase Fase sintetica: 0 estavel, 1 lenta, 2 recuperacao.",
        "# TYPE aula004_demo_phase gauge",
        f"aula004_demo_phase {(elapsed // duration) % 3}",
        "# HELP aula004_demo_elapsed_seconds Tempo desde a partida do gerador.",
        "# TYPE aula004_demo_elapsed_seconds gauge",
        f"aula004_demo_elapsed_seconds {elapsed}",
    ])
    return "\n".join(lines) + "\n"


class MetricsHandler(BaseHTTPRequestHandler):
    started_at: float
    phase_duration: int

    def do_GET(self) -> None:
        if self.path != "/metrics":
            self.send_error(404, "Use /metrics")
            return
        elapsed = int(time.monotonic() - self.started_at)
        body = render_metrics(elapsed, self.phase_duration).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--phase-seconds", type=int, default=120,
                        help="Duração positiva de cada fase (padrão: 120 s).")
    args = parser.parse_args()
    MetricsHandler.started_at = time.monotonic()
    MetricsHandler.phase_duration = args.phase_seconds
    print(f"Dados sintéticos em http://127.0.0.1:{args.port}/metrics", flush=True)
    print(f"Fases de {args.phase_seconds} s: estável → lenta → recuperação.", flush=True)
    with HTTPServer(("127.0.0.1", args.port), MetricsHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
