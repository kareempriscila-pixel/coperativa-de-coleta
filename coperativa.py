import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import datetime

# ==========================================
# 1. BANCO DE DADOS (Não precisa instalar nada)
# ==========================================
def init_db():
    conn = sqlite3.connect('reciclamais_local.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pesagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            catador TEXT,
            material TEXT,
            peso REAL,
            valor REAL,
            data TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. APLICATIVO PRINCIPAL E NAVEGAÇÃO
# ==========================================
class Aplicativo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("♻️ Recicla Mais - MVP")
        self.geometry("400x600")
        self.configure(bg="#f3f4f6")
        
        self.frames = {}
        # Cria as 3 telas e guarda na memória
        for F in (TelaLogin, TelaPesagem, TelaDashboard):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Inicia na tela de login
        self.mostrar_tela("TelaLogin")

    def mostrar_tela(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "TelaDashboard":
            frame.atualizar_lista()

# ==========================================
# TELA 1: LOGIN (Segurança de Acesso)
# ==========================================
class TelaLogin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        
        tk.Label(self, text="♻️ Recicla Mais", font=("Arial", 24, "bold"), fg="#166534", bg="#ffffff").pack(pady=40)
        tk.Label(self, text="Entrar no Sistema", font=("Arial", 16), bg="#ffffff").pack(pady=10)
        
        tk.Label(self, text="Seu E-mail:", bg="#ffffff", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.email = tk.Entry(self, font=("Arial", 14), bg="#f9fafb")
        self.email.insert(0, "coord@reciclamais.org.br")
        self.email.pack(fill="x", padx=40, pady=5)
        
        tk.Label(self, text="Senha:", bg="#ffffff", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.senha = tk.Entry(self, show="*", font=("Arial", 14), bg="#f9fafb")
        self.senha.insert(0, "123456") # Senha padrão
        self.senha.pack(fill="x", padx=40, pady=10)
        
        btn = tk.Button(self, text="Entrar", bg="#1e3a8a", fg="white", font=("Arial", 14, "bold"), 
                        command=self.validar_login, height=2)
        btn.pack(fill="x", padx=40, pady=30)

    def validar_login(self):
        # Validação simples
        if self.senha.get() == "123456":
            self.controller.mostrar_tela("TelaPesagem")
        else:
            messagebox.showerror("Erro de Acesso", "Senha inválida!")

# ==========================================
# TELA 2: REGISTRO E CÁLCULO (Funcionalidade Central)
# ==========================================
class TelaPesagem(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        self.precos = {"Papelão": 0.50, "Plástico": 2.00, "Vidro": 0.20, "Alumínio": 5.00}
        
        # Barra de Navegação
        nav = tk.Frame(self, bg="#166534")
        nav.pack(fill="x")
        tk.Button(nav, text="Registrar", bg="#166534", fg="white", bd=0, font=("Arial", 10, "bold")).pack(side="left", padx=15, pady=15)
        tk.Button(nav, text="Sincronizar", bg="#166534", fg="gray", bd=0, font=("Arial", 10), command=lambda: controller.mostrar_tela("TelaDashboard")).pack(side="left")
        tk.Button(nav, text="Sair", bg="#166534", fg="#fca5a5", bd=0, font=("Arial", 10), command=lambda: controller.mostrar_tela("TelaLogin")).pack(side="right", padx=15)
        
        tk.Label(self, text="Nova Pesagem", font=("Arial", 18, "bold"), bg="#ffffff").pack(pady=15)
        
        tk.Label(self, text="Catador(a):", bg="#ffffff", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.catador = ttk.Combobox(self, values=["João Santos", "Maria Silva", "José Pereira"], font=("Arial", 14), state="readonly")
        self.catador.current(0)
        self.catador.pack(fill="x", padx=40, pady=5)
        
        tk.Label(self, text="Material:", bg="#ffffff", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.material = ttk.Combobox(self, values=list(self.precos.keys()), font=("Arial", 14), state="readonly")
        self.material.current(0)
        self.material.bind("<<ComboboxSelected>>", self.calcular)
        self.material.pack(fill="x", padx=40, pady=5)
        
        tk.Label(self, text="Peso (Kg):", bg="#ffffff", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
        self.peso = tk.Entry(self, font=("Arial", 14), bg="#f9fafb")
        self.peso.bind("<KeyRelease>", self.calcular)
        self.peso.pack(fill="x", padx=40, pady=5)
        
        # Painel do Valor
        painel_valor = tk.Frame(self, bg="#f3f4f6", bd=1, relief="solid")
        painel_valor.pack(fill="x", padx=40, pady=20)
        self.lbl_valor = tk.Label(painel_valor, text="Valor a Pagar:\nR$ 0,00", font=("Arial", 18, "bold"), fg="#15803d", bg="#f3f4f6")
        self.lbl_valor.pack(pady=10)
        
        btn = tk.Button(self, text="Salvar Pesagem", bg="#15803d", fg="white", font=("Arial", 14, "bold"), command=self.salvar, height=2)
        btn.pack(fill="x", padx=40)

    def calcular(self, event=None):
        try:
            p = float(self.peso.get())
            m = self.material.get()
            v = p * self.precos[m]
            self.lbl_valor.config(text=f"Valor a Pagar:\nR$ {v:.2f}".replace(".", ","))
        except ValueError:
            self.lbl_valor.config(text="Valor a Pagar:\nR$ 0,00")

    def salvar(self):
        try:
            p = float(self.peso.get())
            if p <= 0: raise ValueError
            m = self.material.get()
            c = self.catador.get()
            v = p * self.precos[m]
            d = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Grava no SQLite local
            conn = sqlite3.connect('reciclamais_local.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pesagens (catador, material, peso, valor, data, status) VALUES (?,?,?,?,?,?)",
                           (c, m, p, v, d, "Pendente"))
            conn.commit()
            conn.close()
            
            self.peso.delete(0, tk.END)
            self.calcular()
            messagebox.showinfo("Sucesso", "✅ Pesagem salva localmente!")
        except ValueError:
            messagebox.showwarning("Atenção", "Por favor, insira um peso válido maior que zero.")

# ==========================================
# TELA 3: ALERTAS E SINCRONIZAÇÃO (Offline-First)
# ==========================================
class TelaDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        
        # Barra de Navegação
        nav = tk.Frame(self, bg="#166534")
        nav.pack(fill="x")
        tk.Button(nav, text="Registrar", bg="#166534", fg="gray", bd=0, font=("Arial", 10), command=lambda: controller.mostrar_tela("TelaPesagem")).pack(side="left", padx=15, pady=15)
        tk.Button(nav, text="Sincronizar", bg="#166534", fg="white", bd=0, font=("Arial", 10, "bold")).pack(side="left")
        tk.Button(nav, text="Sair", bg="#166534", fg="#fca5a5", bd=0, font=("Arial", 10), command=lambda: controller.mostrar_tela("TelaLogin")).pack(side="right", padx=15)
        
        self.lbl_banner = tk.Label(self, text="☁️ Modo Offline - 0 Pendentes", font=("Arial", 12, "bold"), bg="#fee2e2", fg="#991b1b", pady=10)
        self.lbl_banner.pack(fill="x")
        
        tk.Label(self, text="Registros Recentes", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10, anchor="w", padx=20)
        
        self.lista = tk.Listbox(self, font=("Arial", 12), bg="#f9fafb")
        self.lista.pack(fill="both", expand=True, padx=20, pady=5)
        
        btn = tk.Button(self, text="🔄 Sincronizar Agora", bg="#15803d", fg="white", font=("Arial", 14, "bold"), command=self.sincronizar, height=2)
        btn.pack(fill="x", padx=20, pady=20)

    def atualizar_lista(self):
        self.lista.delete(0, tk.END)
        conn = sqlite3.connect('reciclamais_local.db')
        cursor = conn.cursor()
        cursor.execute("SELECT catador, material, peso, valor, status FROM pesagens ORDER BY id DESC")
        registros = cursor.fetchall()
        conn.close()
        
        pendentes = sum(1 for r in registros if r[4] == "Pendente")
        
        if pendentes > 0:
            self.lbl_banner.config(text=f"☁️ Modo Offline - {pendentes} Pendentes", bg="#fee2e2", fg="#991b1b")
        else:
            self.lbl_banner.config(text="✅ Sistema Atualizado", bg="#dcfce7", fg="#166534")
        
        for r in registros:
            # Mostra alerta se estiver pendente
            aviso = "⚠️" if r[4] == "Pendente" else "✓"
            texto = f"{aviso} {r[0]} | {r[1]} | {r[2]}kg | R${r[3]:.2f}"
            self.lista.insert(tk.END, texto.replace(".", ","))

    def sincronizar(self):
        # Simula o envio alterando o status no banco local
        conn = sqlite3.connect('reciclamais_local.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE pesagens SET status='Sincronizado' WHERE status='Pendente'")
        conn.commit()
        conn.close()
        
        self.atualizar_lista()
        self.lbl_banner.config(text="✅ Sincronização Concluída!", bg="#dcfce7", fg="#166534")
        messagebox.showinfo("Sincronização", "Os dados foram enviados para a base central com sucesso!")

# Executa o aplicativo
if __name__ == "__main__":
    app = Aplicativo()
    app.mainloop()