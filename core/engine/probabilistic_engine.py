import random
import datetime
from typing import List, Tuple, Dict, Any

from core.domain.models import Concurso
from core.statistics.score_v10 import calcular as calcular_score_v10

class ProbabilisticEngine:
    """
    Motor Probabilístico V11 - High-Speed Elite Search
    Objetivo: Restaurar Scores 1.20+ com processamento instantâneo.
    """

    @staticmethod
    def identificar_dezenas_faltantes(concursos: List[Concurso]) -> List[int]:
        todas_dezenas = set(range(1, 26))
        sorteadas_no_ciclo = set()
        for c in concursos:
            sorteadas_no_ciclo.update(c.dezenas)
            if len(sorteadas_no_ciclo) == 25:
                sorteadas_no_ciclo = set()
        return sorted(list(todas_dezenas - sorteadas_no_ciclo))

    def gerar_jogos(self, concursos: List[Concurso], quantidade: int = 5):
        ultimo_concurso = concursos[-1]
        dezenas_ultimo = list(ultimo_concurso.dezenas)
        faltantes_ciclo = self.identificar_dezenas_faltantes(concursos)
        
        jogos_elite = []
        tentativas = 0
        # Aumentamos a amostragem para 100 mil para garantir o topo da curva
        max_tentativas = 100000 
        
        # Cache de busca para otimizar velocidade
        set_dezenas_ultimo = set(dezenas_ultimo)
        numeros_base = list(range(1, 26))

        while len(jogos_elite) < quantidade and tentativas < max_tentativas:
            tentativas += 1
            
            # Construção ultra-rápida do jogo
            nucleo = random.sample(dezenas_ultimo, 9)
            # Garante dezenas do ciclo (Janela de Ouro)
            jogo_set = set(nucleo) | set(faltantes_ciclo)
            
            vagas = 15 - len(jogo_set)
            if vagas > 0:
                possiveis = [n for n in numeros_base if n not in jogo_set]
                jogo_set.update(random.sample(possiveis, vagas))
            
            dezenas_finais = sorted(list(jogo_set))[:15]
            
            # Filtro de Repetição (8, 9 ou 10)
            rep = len(set(dezenas_finais) & set_dezenas_ultimo)
            if 8 <= rep <= 10:
                jogo_obj = Concurso(numero=0, data="", dezenas=tuple(dezenas_finais))
                resultado = calcular_score_v10(jogo_obj, concursos)
                score = resultado.score_final if hasattr(resultado, 'score_final') else resultado
                
                # SÓ CONSIDERA ELITE SE O SCORE FOR REALMENTE ALTO
                if score >= 1.15:
                    jogos_elite.append((jogo_obj, score, rep))
                    # Ordena e mantém apenas os melhores para não pesar a memória
                    jogos_elite.sort(key=lambda x: x[1], reverse=True)

        # Se após 100k tentativas não achar 5 de elite (raro), reduz o critério e tenta lote final
        if len(jogos_elite) < quantidade:
             # Busca de segurança para preencher a lista rapidamente
             for _ in range(5000):
                nucleo = random.sample(dezenas_ultimo, 9)
                jogo_set = set(nucleo) | set(faltantes_ciclo)
                vagas = 15 - len(jogo_set)
                if vagas > 0:
                    possiveis = [n for n in numeros_base if n not in jogo_set]
                    jogo_set.update(random.sample(possiveis, vagas))
                dezenas_finais = sorted(list(jogo_set))[:15]
                jogo_obj = Concurso(numero=0, data="", dezenas=tuple(dezenas_finais))
                resultado = calcular_score_v10(jogo_obj, concursos)
                score = resultado.score_final if hasattr(resultado, 'score_final') else resultado
                jogos_elite.append((jogo_obj, score, len(set(dezenas_finais) & set_dezenas_ultimo)))
             
             jogos_elite.sort(key=lambda x: x[1], reverse=True)

        return jogos_elite[:quantidade], {"dezenas_faltantes": faltantes_ciclo}

    def salvar_historico_v10(self, jogos, alvo):
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open("historico_v10.txt", "a", encoding="utf-8") as f:
                f.write("-" * 80 + "\n")
                f.write(f"Execução em: {timestamp}\n")
                f.write(f"Sugestões para o Concurso Alvo: {alvo}\n\n")
                for i, (jogo_obj, score, rep) in enumerate(jogos, 1):
                    dez_str = " ".join(f"{d:02d}" for d in sorted(jogo_obj.dezenas))
                    f.write(f"Jogo {i}: {dez_str}\n")
                    f.write(f"  Score V10             : {score:.6f}\n")
                    f.write(f"  Repetições Anteriores : {rep}\n\n")
        except Exception as e:
            print(f"[ERRO HISTÓRICO]: {e}")