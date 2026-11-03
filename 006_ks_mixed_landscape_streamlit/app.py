"""Streamlit: histograma → CDF → KS da luminância L; alerta sobre D (tráfego misto)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st
from PIL import Image

from alert_rule import alert_on_d
from corpus_stats import load_default_corpus_stats
from ks_compare import compare_stats
from plotting import (
    load_thumbnails,
    plot_cdf,
    plot_cdf_abs_diff,
    plot_dual_cdf,
    plot_histogram,
)
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"
ILLUSTRATIONS = ROOT / "illustrations"

ALERTA_PT = {
    "ALERT": "ALERTA",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}

ALGORITMO_CDF = """\
# Variáveis:
# contagens — histograma de L
# total — soma(contagens) = número de pixels
# acumulado, cdf, c

total ← soma(contagens)
acumulado ← 0
cdf ← lista vazia
para cada c em contagens:
    acumulado ← acumulado + c
    acrescentar (acumulado / total) em cdf
"""

ALGORITMO_DELTA = """\
# Variáveis:
# F_ref, F_lote — CDFs na mesma grade de L
# delta, D, i_star

delta ← lista vazia
para i de 0 até comprimento(F_ref) − 1:
    acrescentar |F_ref[i] − F_lote[i]| em delta
D ← máximo(delta)
i_star ← argmáximo(delta)
"""

LOTE_ROTULO = {
    "control": "Mesmo tema (outro trecho de praias)",
    "forests": "Florestas (tema puro)",
    "beaches": "Praias",
    "balls": "Bolas",
    "landscapes": "Mistura 25 praias + 25 florestas",
}

# Ordem preferida no seletor (os demais lotes, se existirem, vêm depois).
LOTE_ORDEM = ("control", "forests", "landscapes")

POC_L = '''from PIL import Image

img = Image.open("foto.jpg").convert("L")  # L ∈ {0, …, 255} por pixel
contagens = img.histogram()
'''


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def list_batches() -> list[str]:
    if not BATCH_STATS_DIR.is_dir():
        return []
    found = {p.stem for p in BATCH_STATS_DIR.glob("*.json")}
    ordered = [name for name in LOTE_ORDEM if name in found]
    rest = sorted(found - set(ordered))
    return ordered + rest


def rotulo_lote(name: str) -> str:
    if name in LOTE_ROTULO:
        return LOTE_ROTULO[name]
    if name.startswith("beaches+"):
        return "Mistura de temas"
    return name


def theme_paths_for_batch(name: str) -> list[Path]:
    root = repo_root() / "samples"
    beaches = sorted((root / "beaches").glob("*.jpg")) + sorted(
        (root / "beaches").glob("*.jpeg")
    )
    forests = sorted((root / "forests").glob("*.jpg")) + sorted(
        (root / "forests").glob("*.jpeg")
    )
    if name == "landscapes" or name.startswith("beaches+"):
        # Mesmo recorte do just build-demo-batches: praias[50:75] + florestas[:25]
        return beaches[50:75][:8] + forests[:25][:8]
    mapping = {
        "forests": root / "forests",
        "control": root / "beaches",
        "beaches": root / "beaches",
        "balls": root / "balls",
    }
    folder = mapping.get(name, root / name)
    if not folder.is_dir():
        return []
    paths = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
    if name == "control":
        return paths[50:100]
    return paths


def caminhos_referencia() -> list[Path]:
    root = repo_root() / "samples" / "beaches"
    paths = sorted(root.glob("*.jpg")) + sorted(root.glob("*.jpeg"))
    return paths[:50]


def mostrar_amostra(caminho: Path | None, legenda: str) -> None:
    if caminho is None or not caminho.is_file():
        st.caption("(sem imagem de amostra)")
        return
    st.image(Image.open(caminho), caption=legenda, width=220)


def fig(name: str) -> Path | None:
    path = ILLUSTRATIONS / name
    return path if path.is_file() else None


def d_do_lote(referencia: dict, nome: str, bins: int) -> float | None:
    path = BATCH_STATS_DIR / f"{nome}.json"
    if not path.is_file():
        return None
    lote = load_request_stats(path)
    return float(compare_stats(referencia, lote, channel="L", bins=bins)["statistic"])


st.set_page_config(page_title="KS — tráfego misto de paisagem", layout="wide")
st.title("KS — tráfego misto de paisagem")

st.header("Meta desta aula")
st.markdown(
    """
Tráfego real raramente é um tema puro. O serviço pode receber, na mesma
janela, pedidos que ainda “parecem” o treino e pedidos de outro mundo
visual. A pergunta desta aula: se **metade** das imagens ainda é praia
(fora do freeze de treino) e **metade** é floresta, o alerta sobre **D**
ainda dispara? Em que intensidade, frente a um controle de mesmo tema e a
um lote só de florestas?

Você mede a combinação na **forma** da distribuição de luminância **L**,
resume o afastamento numa estatística **D** (Kolmogorov–Smirnov) e produz
um **alerta** quando **D** cruza o limiar \(0{,}10\).
"""
)
fluxo = fig("01_workflow_l_to_alert.png")
if fluxo:
    st.image(str(fluxo), caption="Fluxo: L → histograma → CDF → δ → D → alerta")

st.header("Definições")

st.subheader("L — luminância do pixel")
st.markdown(
    r"""
Uma fotografia digital é uma grade de pontos — os **pixels**. Em cores, cada
pixel costuma carregar três canais. Para falar de “quão claro ou escuro” é o
ponto, convertemos a imagem para tons de cinza: preto num extremo, branco no
outro, e uma escada de cinzas no meio.

Na prática isso é `Image.convert("L")` no Pillow. Cada pixel passa a um
inteiro de **0** (preto) a **255** (branco). Chamamos esse valor de
**luminância** e o denotamos por **L**. Se \(I\) é a imagem e \((u,v)\) um
sítio na grade, \(L(u,v) \in \{0,1,\ldots,255\}\).

Tudo o que este app desenha e compara descreve a **distribuição de L sobre
os pixels** do conjunto. O eixo não é a média de L por foto: uma média por
imagem comprime demais a forma e, no controle de mesmo tema, pode disparar
alerta à toa (ver `docs/notas-experimento-freeze.md` no handout).
"""
)
st.code(POC_L, language="python")

st.subheader("Histograma")
st.markdown(
    r"""
Com L em mão, a pergunta seguinte é: *em cada degrau de cinza, quantos
pixels caíram?* Essa contagem, faixa a faixa, é o **histograma**.

Imagine baldes alinhados do preto ao branco. Cada pixel do conjunto cai num
balde. A altura do balde \(k\) é a contagem \(h_k\). O total de pixels é
\(N = \sum_k h_k\). Para várias imagens, some os histogramas imagem a
imagem: o resultado é o histograma do **conjunto**.
"""
)

st.subheader("CDF")
st.markdown(
    r"""
O histograma ainda fala em “quantos”. A **função de distribuição acumulada**
(CDF) fala em “até aqui, que fração do total?”. Você caminha dos baldes
escuros para os claros, vai somando as contagens e divide pelo total \(N\).
A curva começa perto de zero e termina em um: nunca desce.

$$
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i.
$$

**Exemplo mínimo.** Contagens `[2, 1, 3]` (\(N=6\)) → CDF
`[2/6, 3/6, 6/6]` — cerca de \(0{,}33\), \(0{,}50\) e \(1\).
"""
)
toy = fig("02_hist_to_cdf_toy.png")
if toy:
    st.image(str(toy), caption="Do histograma à CDF — exemplo mínimo")
st.code(ALGORITMO_CDF, language="text")

st.subheader("δ e D")
st.markdown(
    r"""
Agora você tem duas curvas na mesma grade de L: \(F\) na referência
(treino) e \(G\) no lote atual. Em cada faixa, a distância vertical entre
elas é \(\delta_k = \lvert F_k - G_k \rvert\). A estatística de
Kolmogorov–Smirnov de duas amostras é o **maior** desses afastamentos:

$$
D = \max_k \delta_k = \sup_x \lvert F(x) - G(x) \rvert.
$$

Se as formas de luminância forem parecidas, \(D\) fica pequeno. Se o lote
trouxer outro mundo visual, \(D\) sobe — e é sobre **esse** número que o
alerta dispara.

| Estado | Condição | Leitura |
| :--- | :--- | :--- |
| INCONCLUSIVO | \(n &lt; 8\) em qualquer lado | Janela / lote ainda fino |
| ALERTA | \(n \ge 8\) e \(D \ge 0{,}10\) | Formas de L divergem |
| TRANQUILO | \(n \ge 8\) e \(D &lt; 0{,}10\) | Compatível com a referência |

Em produção o lote é uma **caixa de tempo** (por exemplo pedidos dos
**últimos 30 dias**), não o histórico desde o dia zero. Sem esse fechamento
temporal, misturam-se regimes antigos e novos e o **D** deixa de responder
à pergunta *“o serviço ainda está adequado ao tráfego recente?”*.
"""
)

batches = list_batches()
if not batches:
    st.warning(
        "Não há arquivos em `batch_stats/`. "
        "Rode `just build-demo-batches` ou "
        "`just exercise-theme` + `just snapshot-batch`."
    )
    st.stop()

with st.sidebar:
    st.header("Parâmetros")
    batch_name = st.selectbox(
        "Lote atual",
        batches,
        format_func=rotulo_lote,
        index=batches.index("landscapes") if "landscapes" in batches else 0,
    )
    n_intervalos = st.slider(
        "Número de faixas do histograma de L",
        min_value=16,
        max_value=256,
        value=256,
        step=16,
    )

referencia = load_default_corpus_stats()
lote = load_request_stats(BATCH_STATS_DIR / f"{batch_name}.json")
payload = compare_stats(referencia, lote, channel="L", bins=n_intervalos)
estado = alert_on_d(
    payload["statistic"],
    payload["n_images_corpus"],
    payload["n_images_production"],
)

st.header("Alerta sobre D neste lote")
cores = {
    "ALERT": "#c62828",
    "QUIET": "#2e7d32",
    "INCONCLUSIVE": "#546e7a",
}
st.markdown(
    f"<div style='padding:1rem;border-radius:8px;background:{cores[estado]};"
    f"color:white;font-size:1.4rem;font-weight:600'>"
    f"{ALERTA_PT[estado]} — D = {payload['statistic']:.4f}</div>",
    unsafe_allow_html=True,
)
st.metric("D (Kolmogorov–Smirnov sobre L)", f"{payload['statistic']:.4f}")
st.caption(
    f"Nota: valor-p assintótico ≈ {payload['p_value']:.4g} "
    f"(n efetivo por imagens ≈ {payload['n_eff']:.2f}). "
    "Pixels da mesma foto não são independentes; o alerta responde só a "
    "**D**, não ao valor-p."
)

# Callout: D do misto tipicamente entre controle e florestas puras
d_control = d_do_lote(referencia, "control", n_intervalos)
d_forests = d_do_lote(referencia, "forests", n_intervalos)
d_landscapes = d_do_lote(referencia, "landscapes", n_intervalos)
if d_control is not None and d_forests is not None and d_landscapes is not None:
    st.info(
        f"**Comparação dos três lotes** (mesma referência, mesmas faixas): "
        f"controle D ≈ {d_control:.4f}; "
        f"paisagens mistas D ≈ {d_landscapes:.4f}; "
        f"florestas D ≈ {d_forests:.4f}. "
        "O D do tráfego 25+25 costuma ficar **entre** o controle (mesmo tema) "
        "e o lote só de florestas: metade do pedido ainda puxa a CDF para o "
        "lado do treino, mas a metade floresta já basta para D atravessar o "
        "limiar de alerta na maioria dos freezes."
    )

label_ref = "referência (praias de treino)"
label_lote = rotulo_lote(batch_name)
amostra_ref = caminhos_referencia()[:1]
amostra_lote = theme_paths_for_batch(batch_name)[:1]

st.header("1. Histograma de L em cada conjunto")
col_h1, col_h2 = st.columns(2)
with col_h1:
    mostrar_amostra(
        amostra_ref[0] if amostra_ref else None,
        "Amostra da referência",
    )
    st.pyplot(
        plot_histogram(
            payload["counts_corpus"],
            title="Histograma de L — referência",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with col_h2:
    mostrar_amostra(
        amostra_lote[0] if amostra_lote else None,
        "Amostra do lote",
    )
    st.pyplot(
        plot_histogram(
            payload["counts_production"],
            title="Histograma de L — lote atual",
            series_label=label_lote,
            color="#ef6c00",
        )
    )

st.header("2. CDF de L em cada conjunto")
st.markdown(r"Aplicamos \(F_k = (1/N)\sum_{i\le k} h_i\) a cada lado.")
col_c1, col_c2 = st.columns(2)
with col_c1:
    st.pyplot(
        plot_cdf(
            payload["cdf_corpus"],
            title="CDF de L — referência",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with col_c2:
    st.pyplot(
        plot_cdf(
            payload["cdf_production"],
            title="CDF de L — lote atual",
            series_label=label_lote,
            color="#ef6c00",
        )
    )

st.header("3. As duas CDFs e o segmento D")
st.markdown(
    "O segmento vermelho vertical é **D** = máximo de |F_ref − F_lote|."
)
st.pyplot(
    plot_dual_cdf(
        payload["cdf_corpus"],
        payload["cdf_production"],
        title=f"CDF de L — referência e {label_lote}",
        label_referencia=label_ref,
        label_lote=label_lote,
    )
)

st.header("4. Função δ e D = max δ")
st.code(ALGORITMO_DELTA, language="text")
st.pyplot(
    plot_cdf_abs_diff(
        payload["cdf_corpus"],
        payload["cdf_production"],
        title="δ(L) = |F_ref(L) − F_lote(L)|",
    )
)

st.header("Miniaturas")
box_treino, box_lote = st.columns(2)
with box_treino:
    with st.container(border=True):
        st.markdown("**Conjunto de treino (referência)**")
        thumbs = load_thumbnails(caminhos_referencia())
        if thumbs:
            st.image(thumbs, width=96)
with box_lote:
    with st.container(border=True):
        st.markdown(f"**Lote atual — {label_lote}**")
        thumbs = load_thumbnails(theme_paths_for_batch(batch_name))
        if thumbs:
            st.image(thumbs, width=96)

with st.expander("Detalhe numérico"):
    visivel = {
        k: v
        for k, v in payload.items()
        if not k.startswith("cdf") and not k.startswith("counts")
    }
    st.code(json.dumps(visivel, indent=2, ensure_ascii=False))
