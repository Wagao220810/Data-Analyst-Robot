import sys
import pandas as pd
import threading
try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    print("❌ ERRO: Instale o customtkinter rodando: pip install customtkinter")
    sys.exit(1)

from robo_analista_dados import RoboAnalistaDados

# Configuração visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppRoboGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Robô Analista de Dados - GUI")
        self.geometry("500x550")
        
        # Instancia o núcleo do nosso robô (O Model/Controller)
        self.robo = RoboAnalistaDados()
        
        # --- COMPONENTES DA INTERFACE ---
        self.label_titulo = ctk.CTkLabel(self, text="🤖 Robô Analista de Dados", font=("Arial", 24, "bold"))
        self.label_titulo.pack(pady=20)
        
        self.label_status = ctk.CTkLabel(self, text="Status: Aguardando dados...", text_color="orange")
        self.label_status.pack(pady=10)
        
        # Botões
        self.btn_carregar = ctk.CTkButton(self, text="📂 Escolher Arquivo", command=self.escolher_arquivo)
        self.btn_carregar.pack(pady=10, fill="x", padx=50)

        self.btn_graficos = ctk.CTkButton(self, text="📊 Gerar Gráficos", command=self.gerar_graficos, state="disabled")
        self.btn_graficos.pack(pady=10, fill="x", padx=50)
        
        self.btn_exportar = ctk.CTkButton(self, text="💾 Exportar para Power BI", command=self.exportar_dados, state="disabled", fg_color="#27ae60", hover_color="#1e8449")
        self.btn_exportar.pack(pady=10, fill="x", padx=50)

        self.btn_dashboard = ctk.CTkButton(self, text="🚀 Dashboard Interativo", command=self.gerar_dashboard, state="disabled")
        self.btn_dashboard.pack(pady=10, fill="x", padx=50)

        self.btn_ia = ctk.CTkButton(self, text="🤖 Auto-Pilot IA (Gemini)", command=self.auto_pilot, state="disabled", fg_color="#8E75B2", hover_color="#6c578c")
        self.btn_ia.pack(pady=10, fill="x", padx=50)

    def escolher_arquivo(self):
        """Abre a janela do Windows para selecionar o arquivo e injeta no Robô."""
        filepath = filedialog.askopenfilename(filetypes=[("Arquivos de Dados", "*.csv *.xlsx *.json")])
        if filepath:
            try:
                # Injeção Direta (Bypassando o terminal graças ao MVC)
                df = pd.read_csv(filepath) if filepath.endswith('.csv') else pd.read_excel(filepath)
                sucesso = self.robo._processar_novo_df(df)
                
                if sucesso:
                    self.label_status.configure(text=f"✅ {df.shape[0]} linhas carregadas!", text_color="#00FF00")
                    self.btn_graficos.configure(state="normal")
                    self.btn_dashboard.configure(state="normal")
                    self.btn_exportar.configure(state="normal")
                    self.btn_ia.configure(state="normal")
            except Exception as e:
                messagebox.showerror("Erro de Leitura", f"Não foi possível ler o arquivo:\n{e}")

    def gerar_graficos(self):
        self.robo.graficos()
        messagebox.showinfo("Sucesso", f"Gráficos salvos na pasta:\n{self.robo.output_dir}")

    def gerar_dashboard(self):
        self.robo.gerar_dashboard_html()

    def exportar_dados(self):
        """Abre a janela do Windows para o usuário escolher onde salvar os dados."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")],
            title="Salvar Dados Tratados"
        )
        if filepath:
            try:
                if filepath.endswith('.csv'):
                    self.robo.df.to_csv(filepath, index=False, sep=';')
                else:
                    self.robo.df.to_excel(filepath, index=False)
                messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exportar os dados:\n{e}")

    def auto_pilot(self):
        """Usa Multithreading para a IA pensar sem travar a interface gráfica."""
        self.label_status.configure(text="⏳ A IA está analisando seus dados...", text_color="yellow")
        self.btn_ia.configure(state="disabled") # Desativa o botão para evitar múltiplos cliques acidentais
        
        def tarefa_ia():
            self.robo.analise_automatizada_ia()
            # Atualiza a interface quando a IA terminar
            self.label_status.configure(text="✅ Relatório IA finalizado!", text_color="#00FF00")
            self.btn_ia.configure(state="normal")
            messagebox.showinfo("Sucesso", "Relatório Markdown gerado com sucesso!")

        # Dispara a IA em um "universo paralelo" (Thread 2) para a tela não congelar!
        threading.Thread(target=tarefa_ia, daemon=True).start()

if __name__ == "__main__":
    app = AppRoboGUI()
    app.mainloop()