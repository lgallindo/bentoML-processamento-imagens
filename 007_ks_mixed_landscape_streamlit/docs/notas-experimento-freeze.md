# Notas de experimento — freeze, pixel vs média

Material de apoio ao handout da lição 003. Não é o caminho principal da aula;
serve para quem quiser reproduzir os números e entender por que o eixo é L
por pixel.

## Por que 50 imagens se há 110 por tema

O repositório traz **110** praias e **110** florestas. O freeze da aula usa
**50** de cada lado de propósito: 50 praias como referência de treino, outras
50 praias (índices 51–100) como lote de controle, e 50 florestas como lote
divergente — tamanhos pareados para comparar o alerta. Não é escassez de
dados; é o desenho do experimento.

## L por pixel versus média de L por imagem

Medido neste host com o freeze `beaches[:50]` contra `forests[:50]` e contra
`beaches[50:100]`:

| Lente | beaches[:50] vs forests[:50] | beaches[:50] vs beaches[50:100] |
| :--- | :--- | :--- |
| **L por pixel** | D ≈ 0,23 → ALERTA | D ≈ 0,05 → TRANQUILO |
| **Média de L por imagem** | D ≈ 0,54 → ALERTA | D ≈ 0,18 → ALERTA |

A média comprime cada foto a um único número e reage sobretudo ao brilho
global. No controle (mesmo tema, outro trecho) isso cruza o limiar
\(D \ge 0{,}10\) e gera **falso alerta**. O histograma agregado de pixels
mantém o controle em TRANQUILO. Por isso a lição trabalha com L por pixel.
