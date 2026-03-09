# infrastructure/downloader/baixar.py

import requests
import time

from core.domain.models import Concurso
from infrastructure.database.repository import ConcursoRepository

URL_API = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"

cancelar_download = False


def solicitar_cancelamento():
    global cancelar_download
    cancelar_download = True


def obter_ultimo_numero():
    ultimo = ConcursoRepository.obter_ultimo()
    return ultimo.numero if ultimo else 0


def baixar_dados_novos(callback_progresso=None):

    global cancelar_download
    cancelar_download = False

    ultimo = obter_ultimo_numero()

    try:
        response = requests.get(URL_API, timeout=10)
        response.raise_for_status()
        total_atual = response.json()["numero"]
    except Exception:
        return False, "Erro ao conectar com API."

    if ultimo == total_atual:
        return True, "Banco já está atualizado."

    total_para_baixar = total_atual - ultimo
    baixados = 0

    for numero in range(ultimo + 1, total_atual + 1):

        if cancelar_download:
            return False, "Download cancelado pelo usuário."

        sucesso = False

        for tentativa in range(3):
            try:
                r = requests.get(f"{URL_API}/{numero}", timeout=10)
                r.raise_for_status()
                dados = r.json()

                concurso = Concurso(
                    numero=dados["numero"],
                    data=dados["dataApuracao"],
                    dezenas=tuple(int(d) for d in dados["listaDezenas"])
                )

                ConcursoRepository.salvar(concurso)

                sucesso = True
                break
            except Exception:
                time.sleep(1)

        if not sucesso:
            return False, f"Falha ao baixar concurso {numero}"

        baixados += 1
        percentual = int((baixados / total_para_baixar) * 100)

        if callback_progresso:
            callback_progresso(percentual, numero)

    return True, "Download concluído com sucesso."