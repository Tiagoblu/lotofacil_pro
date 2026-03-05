# core/config/score_config.py

class ScoreConfig:

    # ============================
    # Estatísticas calibradas
    # ============================

    MEDIA_SOMA = 195.1692
    DESVIO_SOMA = 17.8201

    MEDIA_PARES = 7.2007
    DESVIO_PARES = 1.2534

    # atraso médio aproximado (ajustável depois)
    MEDIA_ATRASO = 8
    DESVIO_ATRASO = 4

    # ============================
    # Pesos do modelo v3
    # ============================

    PESO_FREQUENCIA = 1.0
    PESO_SOMA = 1.0
    PESO_PARES = 1.0
    PESO_ATRASO = 0.6

    # ============================
    # Penalizações
    # ============================

    PENALIDADE_EXTREMO = 0.15