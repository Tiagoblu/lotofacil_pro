from core.infrastructure.database.database import inicializar_banco
from core.infrastructure.database.repository import ConcursoRepository
from core.avaliacao.backtest_engine import BacktestEngine

inicializar_banco()
concursos = ConcursoRepository.obter_todos()
print(f"Total de concursos: {len(concursos)}")

resultados, resumo = BacktestEngine.executar(
    concursos,
    quantidade_concursos=500,
    jogos_por_concurso=10,
    candidatos_por_concurso=300,
    modo="BALANCEADO",
    salvar_csv=False,
)

print()
print("===== RESUMO BacktestEngine =====")
for k, v in resumo.items():
    print(f"  {k:15s}: {v}")