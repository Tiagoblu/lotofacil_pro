import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
from baixar import baixar_dados_novos, criar_banco
from analise import analisar_sem_baixar
from simulacao import gerar_simulacao
import sqlite3
import os
import csv

DB_PATH = "lotofacil.db"

# ===========================
# Funções auxiliares
# ===========================
def log(msg):
    """Adiciona mensagem na área de log"""
    text_area.insert(tk.END, msg + "\n")
    text_area.see(tk.END)
    janela.update()

# ---------------------------
# Baixar concursos novos
# ---------------------------
def baixar():
    btn_baixar.config(state="disabled")
    log("Verificando concursos novos...")
    try:
        concursos = baixar_dados_novos()
    except Exception as e:
        log(f"Erro ao baixar concursos: {e}")
        messagebox.showerror("Erro", "Falha ao baixar concursos.")
        btn_baixar.config(state="normal")
        return

    if not concursos:
        log("Nenhum concurso novo disponível.")
    else:
        log(f"{len(concursos)} concursos novos baixados:")
        for c in concursos:
            log(f"Concurso {c['numero']} - {', '.join(c['listaDezenas'])}")

    messagebox.showinfo("Download Concluído", "Processo de download finalizado!")
    btn_baixar.config(state="normal")
    atualizar_tabela_concursos()

# ---------------------------
# Análise dos dados locais
# ---------------------------
def analisar():
    log("Iniciando análise dos dados locais...")
    try:
        analisar_sem_baixar()
        log("Análise concluída!")
        messagebox.showinfo("Análise", "Análise concluída!")
    except Exception as e:
        log(f"Erro na análise: {e}")
        messagebox.showerror("Erro", "Falha na análise.")

# ---------------------------
# Simulação avançada
# ---------------------------
def simular():
    log("Iniciando simulação avançada...")
    try:
        resultados = gerar_simulacao()  # retorna lista de strings
        # Limpar tabela de simulação
        for i in tree_simulacao.get_children():
            tree_simulacao.delete(i)
        # Adicionar resultados na tabela e log
        for linha in resultados:
            tree_simulacao.insert("", tk.END, values=(linha,))
            log(linha)
        log("Simulação concluída!")
        messagebox.showinfo("Simulação", "Simulação concluída!")
    except Exception as e:
        log(f"Erro na simulação: {e}")
        messagebox.showerror("Erro", "Falha na simulação.")

# ---------------------------
# Atualizar tabela de concursos
# ---------------------------
def atualizar_tabela_concursos(filtro_num=None):
    for i in tree_concursos.get_children():
        tree_concursos.delete(i)

    if not os.path.exists(DB_PATH):
        log("Banco não encontrado.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concursos (
                concurso INTEGER PRIMARY KEY,
                data_sorteio TEXT,
                dezenas TEXT
            )
        """)
        conn.commit()

        if filtro_num:
            cursor.execute("SELECT concurso, dezenas FROM concursos WHERE concurso=? ORDER BY concurso", (filtro_num,))
        else:
            cursor.execute("SELECT concurso, dezenas FROM concursos ORDER BY concurso")
        linhas = cursor.fetchall()
        conn.close()

        for numero, dezenas in linhas:
            tree_concursos.insert("", tk.END, values=(numero, dezenas))
    except Exception as e:
        log(f"Erro ao carregar concursos: {e}")
        messagebox.showerror("Erro", "Falha ao carregar concursos.")

# ---------------------------
# Filtrar concurso por número
# ---------------------------
def filtrar_concurso():
    valor = filtro_entry.get()
    if valor.isdigit():
        atualizar_tabela_concursos(filtro_num=int(valor))
    else:
        messagebox.showwarning("Filtro", "Digite um número válido.")

# ---------------------------
# Exportar tabela para CSV
# ---------------------------
def exportar_csv(tabela):
    caminho = filedialog.asksaveasfilename(defaultextension=".csv",
                                           filetypes=[("CSV files", "*.csv")])
    if not caminho:
        return

    try:
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if tabela == "concursos":
                writer.writerow(["Concurso", "Dezenas"])
                for row in tree_concursos.get_children():
                    writer.writerow(tree_concursos.item(row)["values"])
            elif tabela == "simulacao":
                writer.writerow(["Resultado"])
                for row in tree_simulacao.get_children():
                    writer.writerow(tree_simulacao.item(row)["values"])
        messagebox.showinfo("Exportação", f"{tabela.capitalize()} exportado com sucesso!")
        log(f"{tabela.capitalize()} exportado para {caminho}")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao exportar CSV: {e}")

# ===========================
# Criar janela principal
# ===========================
janela = tk.Tk()
janela.title("LOTOFÁCIL PRO - Profissional")
janela.geometry("1000x650")

# Título
titulo = tk.Label(janela, text="LOTOFÁCIL PRO", font=("Arial", 16))
titulo.pack(pady=10)

# Botões principais
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=5)

btn_baixar = tk.Button(frame_botoes, text="Baixar Concursos Novos", width=25, command=baixar)
btn_baixar.grid(row=0, column=0, padx=5, pady=5)

btn_analisar = tk.Button(frame_botoes, text="Analisar Dados Locais", width=25, command=analisar)
btn_analisar.grid(row=0, column=1, padx=5, pady=5)

btn_simular = tk.Button(frame_botoes, text="Simulação Avançada", width=25, command=simular)
btn_simular.grid(row=1, column=0, padx=5, pady=5)

btn_sair = tk.Button(frame_botoes, text="Sair", width=25, command=janela.destroy)
btn_sair.grid(row=1, column=1, padx=5, pady=5)

# Filtro concurso
filtro_frame = tk.Frame(janela)
filtro_frame.pack(pady=5)
tk.Label(filtro_frame, text="Filtrar Concurso nº:").grid(row=0, column=0, padx=5)
filtro_entry = tk.Entry(filtro_frame, width=10)
filtro_entry.grid(row=0, column=1, padx=5)
tk.Button(filtro_frame, text="Filtrar", command=filtrar_concurso).grid(row=0, column=2, padx=5)
tk.Button(filtro_frame, text="Mostrar Todos", command=lambda: atualizar_tabela_concursos()).grid(row=0, column=3, padx=5)

# Área de log
text_area = scrolledtext.ScrolledText(janela, width=130, height=10)
text_area.pack(padx=10, pady=10)

# -------------------------
# Tabelas para concursos e simulação
# -------------------------
frame_tabelas = tk.Frame(janela)
frame_tabelas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Tabela concursos
tree_concursos = ttk.Treeview(frame_tabelas, columns=("Concurso", "Dezenas"), show="headings")
tree_concursos.heading("Concurso", text="Concurso")
tree_concursos.heading("Dezenas", text="Dezenas")
tree_concursos.column("Concurso", width=100, anchor="center")
tree_concursos.column("Dezenas", width=750)
tree_concursos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_concursos = tk.Scrollbar(frame_tabelas, orient="vertical", command=tree_concursos.yview)
tree_concursos.configure(yscroll=scrollbar_concursos.set)
scrollbar_concursos.pack(side=tk.LEFT, fill=tk.Y)

# Tabela simulação
tree_simulacao = ttk.Treeview(frame_tabelas, columns=("Resultado",), show="headings")
tree_simulacao.heading("Resultado", text="Simulação")
tree_simulacao.column("Resultado", width=750)
tree_simulacao.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_simulacao = tk.Scrollbar(frame_tabelas, orient="vertical", command=tree_simulacao.yview)
tree_simulacao.configure(yscroll=scrollbar_simulacao.set)
scrollbar_simulacao.pack(side=tk.LEFT, fill=tk.Y)

# -------------------------
# Botões Exportar CSV
# -------------------------
frame_export = tk.Frame(janela)
frame_export.pack(pady=5)
tk.Button(frame_export, text="Exportar Concursos CSV", command=lambda: exportar_csv("concursos")).grid(row=0, column=0, padx=5)
tk.Button(frame_export, text="Exportar Simulação CSV", command=lambda: exportar_csv("simulacao")).grid(row=0, column=1, padx=5)

# Iniciar banco e atualizar tabela
criar_banco()
atualizar_tabela_concursos()

# Iniciar interface
janela.mainloop()
