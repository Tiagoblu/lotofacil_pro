import tkinter as tk
from tkinter import ttk, messagebox
import threading

from core.baixar import baixar_dados_novos
from core.simulacao import gerar_simulacao


def iniciar_interface():

    root = tk.Tk()
    root.title("Lotofácil PRO")
    root.geometry("1000x650")
    root.configure(bg="#eef1f5")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TProgressbar", thickness=8, background="#4a90e2")

    # ==============================
    # HEADER
    # ==============================

    header = tk.Frame(root, bg="#2c3e50", height=70)
    header.pack(fill="x")

    tk.Label(
        header,
        text="LOTOFÁCIL PRO",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(pady=15)

    # ==============================
    # CONTAINER
    # ==============================

    container = tk.Frame(root, bg="#eef1f5")
    container.pack(fill="both", expand=True, padx=20, pady=20)

    # ==============================
    # PAINEL ESQUERDO
    # ==============================

    painel = tk.Frame(container, bg="white", width=300)
    painel.pack(side="left", fill="y")
    painel.pack_propagate(False)

    tk.Label(
        painel,
        text="Configuração",
        bg="white",
        fg="#2c3e50",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=15)

    nivel_var = tk.StringVar(value="A")

    niveis = [
        ("A - Conservador", "A"),
        ("B - Equilibrado", "B"),
        ("C - Estratégico", "C"),
        ("D - Agressivo", "D")
    ]

    for texto, valor in niveis:
        tk.Radiobutton(
            painel,
            text=texto,
            variable=nivel_var,
            value=valor,
            bg="white",
            font=("Segoe UI", 10),
            anchor="w"
        ).pack(fill="x", padx=20)

    tk.Label(
        painel,
        text="\nQuantidade de Jogos",
        bg="white",
        font=("Segoe UI", 11)
    ).pack()

    qtd_entry = tk.Entry(painel, width=8, justify="center", font=("Segoe UI", 11))
    qtd_entry.insert(0, "1")
    qtd_entry.pack(pady=5)

    # ==============================
    # PAINEL DIREITO
    # ==============================

    area = tk.Frame(container, bg="white")
    area.pack(side="right", fill="both", expand=True, padx=(20, 0))

    tk.Label(
        area,
        text="Resultados",
        bg="white",
        fg="#2c3e50",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=10)

    contador_label = tk.Label(
        area,
        text="Nenhum jogo gerado.",
        bg="white",
        fg="#555",
        font=("Segoe UI", 10, "italic")
    )
    contador_label.pack(pady=(0, 5))

    text_frame = tk.Frame(area)
    text_frame.pack(fill="both", expand=True, padx=20)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    resultado_box = tk.Text(
        text_frame,
        font=("Consolas", 12),
        bg="#f8f9fb",
        bd=0,
        padx=15,
        pady=15,
        yscrollcommand=scrollbar.set
    )
    resultado_box.pack(fill="both", expand=True)

    scrollbar.config(command=resultado_box.yview)

    # ==============================
    # STATUS BAR
    # ==============================

    status_frame = tk.Frame(root, bg="#dde3ea", height=40)
    status_frame.pack(fill="x")

    label_status = tk.Label(
        status_frame,
        text="Sistema pronto.",
        bg="#dde3ea",
        font=("Segoe UI", 9)
    )
    label_status.pack(side="left", padx=15)

    progress = ttk.Progressbar(status_frame, mode="determinate")
    progress.pack(side="right", padx=15, fill="x", expand=True)

    # ==============================
    # FUNÇÕES
    # ==============================

    def gerar():

        try:
            nivel = nivel_var.get()
            quantidade = int(qtd_entry.get())

            if quantidade <= 0:
                raise ValueError

            btn_gerar.config(state="disabled")
            label_status.config(text="Gerando jogos...")
            resultado_box.delete("1.0", tk.END)
            root.update_idletasks()

            resultado = gerar_simulacao(nivel=nivel, quantidade=quantidade)

            texto_formatado = ""

            for i, jogo in enumerate(resultado, start=1):
                texto_formatado += f"JOGO {i:03d}\n"
                texto_formatado += "-" * 30 + "\n"
                texto_formatado += f"{jogo}\n\n"

            resultado_box.insert(tk.END, texto_formatado)
            resultado_box.see("1.0")

            contador_label.config(
                text=f"{quantidade} jogo(s) gerado(s)"
            )

            label_status.config(text="Geração concluída.")
            btn_gerar.config(state="normal")

        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser número positivo.")
            btn_gerar.config(state="normal")
            label_status.config(text="Erro.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            btn_gerar.config(state="normal")
            label_status.config(text="Erro.")

    def atualizar_barra(percentual, numero_atual):
        progress["value"] = percentual
        label_status.config(
            text=f"Atualizando concurso {numero_atual} - {percentual}%"
        )
        root.update_idletasks()

    def baixar():
        btn_baixar.config(state="disabled")
        sucesso, mensagem = baixar_dados_novos(callback_progresso=atualizar_barra)

        if sucesso:
            label_status.config(text="Atualização concluída.")
            messagebox.showinfo("Sucesso", mensagem)
        else:
            label_status.config(text="Erro na atualização.")
            messagebox.showerror("Erro", mensagem)

        btn_baixar.config(state="normal")

    def thread_baixar():
        threading.Thread(target=baixar).start()

    # ==============================
    # BOTÕES
    # ==============================

    btn_frame = tk.Frame(painel, bg="white")
    btn_frame.pack(pady=20)

    btn_gerar = tk.Button(
        btn_frame,
        text="Gerar Jogos",
        bg="#27ae60",
        fg="white",
        width=18,
        height=2,
        font=("Segoe UI", 10, "bold"),
        command=gerar
    )
    btn_gerar.pack(pady=5)

    btn_baixar = tk.Button(
        btn_frame,
        text="Atualizar Dados",
        bg="#3498db",
        fg="white",
        width=18,
        height=1,
        font=("Segoe UI", 10),
        command=thread_baixar
    )
    btn_baixar.pack(pady=5)

    btn_sair = tk.Button(
        btn_frame,
        text="Sair",
        bg="#e74c3c",
        fg="white",
        width=18,
        height=1,
        font=("Segoe UI", 10),
        command=root.destroy
    )
    btn_sair.pack(pady=5)

    root.mainloop()
