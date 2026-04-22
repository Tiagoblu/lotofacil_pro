import random
from typing import Dict, List, Tuple, Any, Optional

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10
from core.statistics.score_v10 import detectar_ciclo


class ProbabilisticEngine:
    """
    Motor probabilístico V10 - Versão Comercial 1.2 (Otimizada)
    Melhoria: Lógica de Ciclo Progressiva e Inclusão Obrigatória de Reta Final.
    """

    @staticmethod
    def identificar_dezenas_faltantes(concursos: List[Concurso]) -> List[int]:
        """Identifica quais dezenas ainda não saíram no ciclo atual usando lógica progressiva."""
        todas_dezenas = set(range(1, 26))
        sorteadas_no_ciclo = set()
        
        # Processamento progressivo para garantir precisão no fecho
        for c in concursos:
            sorteadas_no_ciclo.update(c.dezenas)
            if len(sorteadas_no_ciclo) == 25:
                sorteadas_no_ciclo = set()
        
        faltantes = list(todas_dezenas - sorteadas_no_ciclo)
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
        max_repeticoes = 9 if modo.upper() == "HIBRIDO_V9" else 8

        jogos_avaliados: List[Tuple[Concurso, float, int]] = []
        usar_hibrido = (modo.upper() == "HIBRIDO_V9" and jogos_base is not None)

        tentativas_maximas = candidatos * 15
        tentativas = 0

        while len(jogos_avaliados) < candidatos and tentativas < tentativas_maximas:
            tentativas += 1
            
            if usar_hibrido:
                jogo_molde = random.choice(jogos_base)
                # Seleciona núcleo do V9
                nucleo = set(random.sample(jogo_molde, tamanho_nucleo_v9))
                
                # --- LÓGICA DE CICLO V1.2 (OBRIGATÓRIA) ---
                # Se restarem 3 ou menos, inclui todas. Se mais, sorteia 2.
                if len(faltantes_ciclo) <= 3 and len(faltantes_ciclo) > 0:
                    dezenas_ciclo = set(faltantes_ciclo)
                else:
                    faltantes_disponiveis = [d for d in faltantes_ciclo if d not in nucleo]
                    dezenas_ciclo = set(random.sample(faltantes_disponiveis, min(len(faltantes_disponiveis), 2)))
                
                # Montagem do jogo garantindo que não ultrapasse 15 dezenas
                dezenas_atuais = nucleo | dezenas_ciclo
                vagas_abertas = 15 - len(dezenas_atuais)
                
                if vagas_abertas < 0: # Caso o núcleo + ciclo passem de 15
                    dezenas_list = list(dezenas_atuais)
                    dezenas = sorted(random.sample(dezenas_list, 15))
                else:
                    possiveis = list(set(range(1, 26)) - dezenas_atuais)
                    complemento = random.sample(possiveis, vagas_abertas)
                    dezenas = sorted(list(dezenas_atuais) + complemento)
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