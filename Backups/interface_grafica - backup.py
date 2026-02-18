from simulacao import gerar_simulacao

import tkinter as tk
from tkinter import messagebox

from baixar import baixar_dados
from analise import analisar_sem_baixar


def baixar():
    baixar_dados()
    messagebox.showinfo("Sucesso", "Dados baixados com sucesso!")


def analisar():
    analisar_sem_baixar()
    messagebox.showinfo("Análise", "Análise concluída! Veja o terminal.")


# Criar janela principal
janela = tk.Tk()
janela.title("LOTOFÁCIL PRO")
janela.geometry("300x250")

# Título
titulo = tk.Label(janela, text="LOTOFÁCIL PRO", font=("Arial", 16))
titulo.pack(pady=20)

# Botão baixar
botao_baixar = tk.Button(janela, text="Baixar Dados", width=25, command=baixar)
botao_baixar.pack(pady=5)

# Botão analisar
botao_analisar = tk.Button(janela, text="Analisar Dados Locais", width=25, command=analisar)
botao_analisar.pack(pady=5)

def simular():
    gerar_simulacao()
    messagebox.showinfo("Simulação", "Simulação concluída! Veja o terminal.")

# Botão simulação
botao_simular = tk.Button(janela, text="Simulação Avançada", width=25, command=simular)
botao_simular.pack(pady=5)

# Botão sair
botao_sair = tk.Button(janela, text="Sair", width=25, command=janela.destroy)
botao_sair.pack(pady=20)

# Iniciar janela
janela.mainloop()
