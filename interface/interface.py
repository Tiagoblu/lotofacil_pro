import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import csv

from services.geracao_service import GeracaoService
from infrastructure.downloader.baixar import baixar_dados_novos


def iniciar_interface():

    root = tk.Tk()
    root.title("Lotofácil PRO v2.3")
    root.geometry("1100x650")

    progresso_var = tk.DoubleVar()
    status_var = tk.StringVar(value="Inicializando...")
    eta_var = tk.StringVar(value="ETA: --")

    resultados_cache = []

    # =========================
    # ATUALIZAR BANCO AUTOMATICAMENTE
    # =========================
    def atualizar_banco():

        status_var.set("Atualizando concursos...")
        root.update()

        ok, msg = baixar_dados_novos()

        status_var.set(msg)

    # =========================
    # GERAR
    # =========================
    def gerar():

        btn_gerar.config(state="disabled")
        progress_bar["value"] = 0
        text_resultados.delete("1.0", tk.END)

        def atualizar_progresso(progresso, tempo_decorrido):
            def ui_update():
                progresso_var.set(progresso * 100)

                if progresso > 0:
                    tempo_total = tempo_decorrido / progresso
                    restante = tempo_total - tempo_decorrido
                    eta_var.set(f"ETA: {restante:.1f}s")

                status_var.set("Gerando jogos...")

            root.after(0, ui_update)

        def tarefa():
            nonlocal resultados_cache

            resultados = GeracaoService.gerar_simulacao(
                nivel="C",
                quantidade=10,
                callback=atualizar_progresso
            )

            resultados_cache = resultados

            def finalizar():
                jogos_unicos = set()

                for jogo, score in resultados:
                    tupla = tuple(jogo)

                    if tupla not in jogos_unicos:
                        jogos_unicos.add(tupla)
                        numeros = " ".join(f"{n:02d}" for n in jogo)
                        text_resultados.insert(
                            tk.END,
                            f"{numeros} | Score: {score}\n"
                        )

                atualizar_estatisticas()
                status_var.set("Concluído.")
                btn_gerar.config(state="normal")

            root.after(0, finalizar)

        threading.Thread(target=tarefa, daemon=True).start()

    # =========================
    # ESTATÍSTICAS
    # =========================
    def atualizar_estatisticas():

        if not resultados_cache:
            return

        scores = [s for _, s in resultados_cache]
        somas = [sum(j) for j, _ in resultados_cache]
        pares = [sum(1 for n in j if n % 2 == 0) for j, _ in resultados_cache]

        lbl_media_score.config(text=f"Média Score: {sum(scores)/len(scores):.2f}")
        lbl_melhor_score.config(text=f"Melhor Score: {max(scores):.2f}")
        lbl_pior_score.config(text=f"Pior Score: {min(scores):.2f}")
        lbl_media_soma.config(text=f"Média Soma: {sum(somas)/len(somas):.1f}")
        lbl_media_pares.config(text=f"Média Pares: {sum(pares)/len(pares):.1f}")

    # =========================
    # LIMPAR
    # =========================
    def limpar():
        text_resultados.delete("1.0", tk.END)

    # =========================
    # COPIAR
    # =========================
    def copiar():
        root.clipboard_clear()
        root.clipboard_append(text_resultados.get("1.0", tk.END))
        messagebox.showinfo("Copiado", "Resultados copiados!")

    # =========================
    # EXPORTAR
    # =========================
    def exportar():

        if not resultados_cache:
            messagebox.showwarning("Aviso", "Nenhum jogo para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Salvar como"
        )

        if not caminho:
            return

        with open(caminho, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Jogo", "Score"])

            for jogo, score in resultados_cache:
                writer.writerow([" ".join(map(str, jogo)), score])

        messagebox.showinfo("Exportado", "Arquivo salvo com sucesso!")

    # =========================
    # SAIR
    # =========================
    def sair():
        root.destroy()

    # =========================
    # LAYOUT
    # =========================

    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=5)

    btn_gerar = tk.Button(top_frame, text="Gerar", command=gerar)
    btn_gerar.pack(side="left", padx=5)

    tk.Button(top_frame, text="Limpar", command=limpar).pack(side="left", padx=5)
    tk.Button(top_frame, text="Copiar Tudo", command=copiar).pack(side="left", padx=5)
    tk.Button(top_frame, text="Exportar CSV", command=exportar).pack(side="left", padx=5)
    tk.Button(top_frame, text="Sair", command=sair).pack(side="right", padx=5)

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)

    text_resultados = tk.Text(main_frame)
    text_resultados.pack(side="left", fill="both", expand=True)

    painel = tk.Frame(main_frame, width=250)
    painel.pack(side="right", fill="y", padx=10)

    tk.Label(painel, text="Estatísticas", font=("Arial", 12, "bold")).pack(pady=10)

    lbl_media_score = tk.Label(painel, text="Média Score: -")
    lbl_media_score.pack(anchor="w")

    lbl_melhor_score = tk.Label(painel, text="Melhor Score: -")
    lbl_melhor_score.pack(anchor="w")

    lbl_pior_score = tk.Label(painel, text="Pior Score: -")
    lbl_pior_score.pack(anchor="w")

    lbl_media_soma = tk.Label(painel, text="Média Soma: -")
    lbl_media_soma.pack(anchor="w")

    lbl_media_pares = tk.Label(painel, text="Média Pares: -")
    lbl_media_pares.pack(anchor="w")

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(fill="x", padx=10, pady=5)

    progress_bar = ttk.Progressbar(bottom_frame, variable=progresso_var, maximum=100)
    progress_bar.pack(fill="x")

    tk.Label(bottom_frame, textvariable=eta_var).pack(anchor="w")
    tk.Label(bottom_frame, textvariable=status_var).pack(anchor="w")

    # 🔥 Atualiza banco automaticamente ao abrir
    threading.Thread(target=atualizar_banco, daemon=True).start()

    root.mainloop()