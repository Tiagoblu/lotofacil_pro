import tkinter as tk
from tkinter import messagebox, scrolledtext
from baixar import baixar_dados_novos, criar_banco
from analise import analisar_sem_baixar
from simulacao import gerar_simulacao
import sqlite3

DB_PATH = "lotofacil.db"

# ===========================
# Funções auxiliares
# ===========================

def log(msg):
    """Adiciona mensagem na área de log"""
    text_area.insert(tk.END, msg + "\n")
    text_area.see(tk.END)  # rolar para o final
    janela.update()

# ---------------------------
# Baixar concursos novos
# ---------------------------
def baixar():
    btn_baixar.config(state="disabled")
    log("Verificando concursos novos...")
    
    concursos = baixar_dados_novos()
    if not concursos:
        log("Nenhum concurso novo disponível.")
    else:
        log(f"{len(concursos)} concursos novos baixados:")
        for c in concursos:
            log(f"Concurso {c['numero']} - {', '.join(c['listaDezenas'])}")
    
    messagebox.showinfo("Download Concluído", "Processo de download finalizado!")
    btn_baixar.config(state="normal")

# ---------------------------
# Análise dos dados locais
# ---------------------------
def analisar():
    log("Iniciando análise dos dados locais...")
    analisar_sem_baixar()
    log("Análise concluída! Veja o terminal para detalhes.")
    messagebox.showinfo("Análise", "Análise concluída!")

# ---------------------------
# Simulação avançada
# ---------------------------
def simular():
    log("Iniciando simulação avançada...")
    gerar_simulacao()
    log("Simulação concluída! Veja o terminal para resultados.")
    messagebox.showinfo("Simulação", "Simulação concluída!")

# ---------------------------
# Mostrar todos concursos já baixados
# ---------------------------
def mostrar_concursos():
    log("Carregando todos concursos do banco...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT concurso, dezenas FROM concursos ORDER BY concurso")
    linhas = cursor.fetchall()
    conn.close()
    
    if not linhas:
        log("Nenhum concurso encontrado no banco.")
    else:
        log(f"Total de concursos: {len(linhas)}")
        for numero, dezenas in linhas:
            log(f"Concurso {numero} - {dezenas}")

# ===========================
# Criar janela principal
# ===========================
janela = tk.Tk()
janela.title("LOTOFÁCIL PRO - Atualizado")
janela.geometry("700x500")

# Título
titulo = tk.Label(janela, text="LOTOFÁCIL PRO", font=("Arial", 16))
titulo.pack(pady=10)

# Botões principais
btn_baixar = tk.Button(janela, text="Baixar Concursos Novos", width=30, command=baixar)
btn_baixar.pack(pady=5)

btn_analisar = tk.Button(janela, text="Analisar Dados Locais", width=30, command=analisar)
btn_analisar.pack(pady=5)

btn_simular = tk.Button(janela, text="Simulação Avançada", width=30, command=simular)
btn_simular.pack(pady=5)

btn_mostrar = tk.Button(janela, text="Ver Todos Concursos Baixados", width=30, command=mostrar_concursos)
btn_mostrar.pack(pady=5)

btn_sair = tk.Button(janela, text="Sair", width=30, command=janela.destroy)
btn_sair.pack(pady=10)

# Área de log / resultados
text_area = scrolledtext.ScrolledText(janela, width=85, height=20)
text_area.pack(padx=10, pady=10)

# Iniciar banco caso não exista
criar_banco()

# Iniciar janela
janela.mainloop()
