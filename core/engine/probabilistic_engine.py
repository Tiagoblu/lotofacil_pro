import random
from typing import Dict, List, Tuple, Any, Optional

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10
from core.statistics.score_v10 import detectar_ciclo


class ProbabilisticEngine:
    """
    Motor probabilístico de geração de jogos.

    Fluxo:
        - Detecta o ciclo atual do histórico via score_v10.detectar_ciclo().
        - Gera candidatos aleatórios ou híbridos com 15 dezenas.
        - Filtra candidatos pelo limite de repetições do modo escolhido.
        - Calcula o score V10 para cada candidato válido.
        - Retorna os melhores jogos ordenados por score.

    Modos disponíveis:
        - CONSERVADOR : max 7 repetições em relação ao último concurso
        - BALANCEADO  : max 8 repetições
        - AGRESSIVO   : max 9 repetições
        - HIBRIDO_V9  : max 9 repetições  ← Mescla núcleo forte do V9 com completude do V10
    """

    @staticmethod
    def gerar_jogos(
        concursos: List[Concurso],
        quantidade: int = 5,
        candidatos: int = 300,
        modo: str = "BALANCEADO",
        jogos_base: Optional[List[List[int]]] = None,
        tamanho_nucleo_v9: int = 7  # Parâmetro ajustado para dar mais liberdade ao V10
    ) -> Tuple[List[Tuple[Concurso, float, int]], Dict[str, Any]]:
        """
        Gera jogos avaliados pelo score V10.

        Args:
            concursos:  Lista de concursos históricos (mais antigos primeiro).
            quantidade: Quantos jogos finais retornar.
            candidatos: Quantos candidatos gerar antes do filtro por score.
            modo:       Modo estratégico ("CONSERVADOR", "BALANCEADO", "AGRESSIVO", "HIBRIDO_V9").
            jogos_base: Lista de jogos V9 fixos para servir de núcleo no modo HIBRIDO_V9.
            tamanho_nucleo_v9: Quantidade de dezenas extraídas do V9 (default 7).
        """
        if not concursos:
            raise ValueError("Lista de concursos não pode ser vazia.")

        # Detecta o ciclo uma única vez para todo o lote
        resultado_ciclo = detectar_ciclo(concursos)

        info_ciclo: Dict[str, Any] = {
            "ciclo"               : resultado_ciclo.ciclo,
            "indice_volatilidade" : resultado_ciclo.indice_volatilidade,
            "peso_recencia"       : resultado_ciclo.peso_recencia,
        }

        ultimo_concurso = concursos[-1]
        dezenas_ultimo  = set(ultimo_concurso.dezenas)

        configuracoes = {
            "CONSERVADOR": {"max_repeticoes": 7},
            "BALANCEADO" : {"max_repeticoes": 8},
            "AGRESSIVO"  : {"max_repeticoes": 9},
            "HIBRIDO_V9" : {"max_repeticoes": 9},
        }

        modo_upper = modo.upper()
        config         = configuracoes.get(modo_upper, configuracoes["BALANCEADO"])
        max_repeticoes = config["max_repeticoes"]

        jogos_avaliados: List[Tuple[Concurso, float, int]] = []
        
        usar_hibrido = (modo_upper == "HIBRIDO_V9" and jogos_base is not None and len(jogos_base) > 0)

        tentativas_maximas = candidatos * 4 
        tentativas = 0

        while len(jogos_avaliados) < candidatos and tentativas < tentativas_maximas:
            tentativas += 1
            
            if usar_hibrido:
                # 1. Escolhe um dos jogos base do V9
                jogo_molde = random.choice(jogos_base)
                # 2. Extrai um núcleo dinâmico (agora 7 dezenas, evitando engessamento)
                nucleo = set(random.sample(jogo_molde, tamanho_nucleo_v9))
                # 3. Descobre quais dezenas sobraram no volante
                dezenas_disponiveis = list(set(range(1, 26)) - nucleo)
                # 4. Preenche as vagas restantes aleatoriamente para o V10 avaliar
                vagas_restantes = 15 - tamanho_nucleo_v9
                complemento = random.sample(dezenas_disponiveis, vagas_restantes)
                # 5. Une e ordena
                dezenas = sorted(list(nucleo) + complemento)
            else:
                # Geração V10 Clássica
                dezenas = sorted(random.sample(range(1, 26), 15))

            repeticoes = len(set(dezenas) & dezenas_ultimo)

            if repeticoes > max_repeticoes:
                continue

            jogo = Concurso(
                numero=0,
                data="",
                dezenas=tuple(dezenas)
            )

            resultado_v10 = calcular_score_v10(jogo, concursos)
            score         = resultado_v10.score_final

            jogos_avaliados.append((jogo, score, repeticoes))

        jogos_ordenados = sorted(
            jogos_avaliados,
            key=lambda x: x[1],
            reverse=True
        )

        return jogos_ordenados[:quantidade], info_ciclo