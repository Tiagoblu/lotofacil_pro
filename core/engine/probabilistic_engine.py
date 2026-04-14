import random
from typing import Dict, List, Tuple, Any, Optional

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10
from core.statistics.score_v10 import detectar_ciclo


class ProbabilisticEngine:
    """
    Motor probabilístico V10 - Versão Comercial 1.1
    Inclui: Modo Híbrido V9 + Filtro de Fechamento de Ciclo. [cite: 8, 113, 197]
    """

    @staticmethod
    def identificar_dezenas_faltantes(concursos: List[Concurso]) -> List[int]:
        """Identifica quais dezenas ainda não saíram no ciclo atual."""
        todas_dezenas = set(range(1, 26))
        dezenas_sorteadas_no_ciclo = set()
        
        # Percorre do mais recente para o mais antigo para encontrar o início do ciclo
        for c in reversed(concursos):
            dezenas_sorteadas_no_ciclo.update(c.dezenas)
            if len(dezenas_sorteadas_no_ciclo) == 25:
                # O ciclo anterior fechou aqui. O ciclo atual começou no concurso seguinte.
                # Precisamos resetar e pegar apenas o que saiu DEPOIS desse fechamento.
                dezenas_sorteadas_no_ciclo = set()
                continue
        
        # Após o loop, o que sobrar em dezenas_sorteadas_no_ciclo é o progresso do ciclo ATUAL
        faltantes = list(todas_dezenas - dezenas_sorteadas_no_ciclo)
        return sorted(faltantes)

    @staticmethod
    def gerar_jogos(
        concursos: List[Concurso],
        quantidade: int = 5,
        candidatos: int = 300,
        modo: str = "BALANCEADO",
        jogos_base: Optional[List[List[int]]] = None,
        tamanho_nucleo_v9: int = 7
    ) -> Tuple[List[Tuple[Concurso, float, int]], Dict[str, Any]]:
        """
        Gera jogos usando o Motor V10 com priorização de fechamento de ciclo. [cite: 23, 121]
        """
        if not concursos:
            raise ValueError("Lista de concursos não pode ser vazia.")

        resultado_ciclo = detectar_ciclo(concursos)
        faltantes_ciclo = ProbabilisticEngine.identificar_dezenas_faltantes(concursos)

        info_ciclo: Dict[str, Any] = {
            "ciclo": resultado_ciclo.ciclo,
            "indice_volatilidade": resultado_ciclo.indice_volatilidade,
            "peso_recencia": resultado_ciclo.peso_recencia,
            "dezenas_faltantes": faltantes_ciclo
        }

        ultimo_concurso = concursos[-1]
        dezenas_ultimo = set(ultimo_concurso.dezenas)

        configuracoes = {
            "CONSERVADOR": {"max_repeticoes": 7},
            "BALANCEADO": {"max_repeticoes": 8},
            "AGRESSIVO": {"max_repeticoes": 9},
            "HIBRIDO_V9": {"max_repeticoes": 9},
        }

        modo_upper = modo.upper()
        config = configuracoes.get(modo_upper, configuracoes["BALANCEADO"])
        max_repeticoes = config["max_repeticoes"]

        jogos_avaliados: List[Tuple[Concurso, float, int]] = []
        usar_hibrido = (modo_upper == "HIBRIDO_V9" and jogos_base is not None and len(jogos_base) > 0)

        tentativas_maximas = candidatos * 10
        tentativas = 0

        while len(jogos_avaliados) < candidatos and tentativas < tentativas_maximas:
            tentativas += 1
            
            if usar_hibrido:
                jogo_molde = random.choice(jogos_base)
                nucleo = set(random.sample(jogo_molde, tamanho_nucleo_v9))
                vagas_restantes = 15 - tamanho_nucleo_v9
                
                # --- NOVO FILTRO DE CICLO ---
                # Tentamos colocar 2 dezenas faltantes do ciclo se elas não estiverem no núcleo
                faltantes_disponiveis = [d for d in faltantes_ciclo if d not in nucleo]
                dezenas_ciclo = []
                if len(faltantes_disponiveis) >= 2:
                    dezenas_ciclo = random.sample(faltantes_disponiveis, 2)
                
                complemento_aleatorio = vagas_restantes - len(dezenas_ciclo)
                dezenas_restantes = list(set(range(1, 26)) - nucleo - set(dezenas_ciclo))
                complemento = random.sample(dezenas_restantes, complemento_aleatorio)
                
                dezenas = sorted(list(nucleo) + dezenas_ciclo + complemento)
            else:
                dezenas = sorted(random.sample(range(1, 26), 15))

            repeticoes = len(set(dezenas) & dezenas_ultimo)
            if repeticoes > max_repeticoes:
                continue

            jogo = Concurso(numero=0, data="", dezenas=tuple(dezenas))
            resultado_v10 = calcular_score_v10(jogo, concursos)
            jogos_avaliados.append((jogo, resultado_v10.score_final, repeticoes))

        jogos_ordenados = sorted(jogos_avaliados, key=lambda x: x[1], reverse=True)
        return jogos_ordenados[:quantidade], info_ciclo