import customtkinter as ctk
import configparser 
import os
from Core.fonctions import *

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.widgets = {}

        # Fenêtre principale
        self.title("Configuration Serveur Impression")
        self.geometry("700x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.grid_columnconfigure(0, weight=1)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.server_section()
        self.tabs_section()
        self.ServeurAction()

    # Haut de page Serveur
    def server_section(self):
        server_frame = ctk.CTkFrame(self.main_frame)
        server_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        server_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(server_frame, text=" Configuration du Serveur", compound="left", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")

        ctk.CTkLabel(server_frame, text="Adresse IP").grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")
        self.widgets['serveur_ip'] = ctk.CTkEntry(server_frame)
        self.widgets['serveur_ip'].grid(row=1, column=1, padx=20, pady=(5, 10), sticky="ew")
    
        ctk.CTkLabel(server_frame, text="Vitesse").grid(row=2, column=0, padx=20, pady=(5, 15), sticky="w")
        self.widgets['serveur_vitesse'] = ctk.CTkEntry(server_frame)
        self.widgets['serveur_vitesse'].grid(row=2, column=1, padx=20, pady=(5, 15), sticky="ew")

    #Menu des sections
    def tabs_section(self):
        tab_view = ctk.CTkTabview(self.main_frame, anchor="w", segmented_button_selected_hover_color="#36719F")
        tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        tab_names = ["Imprimante 1","Imprimante 2","Imprimante 3","Imprimante 4","Imprimante 5","TPE","LCD"]
        
        for i, name in enumerate(tab_names):
            tab = tab_view.add(name)
            tab.grid_columnconfigure(0, weight=1)
            
            title_label = ctk.CTkLabel(tab, text=f" Paramètres de {name}", compound="left", font=ctk.CTkFont(size=14, weight="bold"))
            title_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
    
            widget_key_prefix = name.lower().replace(" ", "_")
            self.widgets[widget_key_prefix] = {}

            if name == "TPE":
                self.tpe_content(tab, widget_key_prefix)
            elif name == "LCD":
                self.lcd_content(tab, widget_key_prefix)
            else:
                self.printer_content(tab, widget_key_prefix)
    
    def ServeurAction(self):
        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        action_frame.grid_columnconfigure((0, 2), weight=1)

        self.status_label = ctk.CTkLabel(action_frame, text="Prêt.", text_color="gray")
        self.status_label.grid(row=0, column=0, padx=10, sticky="w")
        
        save_button = ctk.CTkButton(action_frame, text="Sauvegarder", command=self.save_configuration)
        save_button.grid(row=0, column=1, padx=5)

        start_button = ctk.CTkButton(action_frame, text="Démarrer Serveur", command=self.start_server, fg_color="#28a745", hover_color="#218838")
        start_button.grid(row=0, column=2, padx=5, sticky="e")

    def generic_frame(self, parent_tab, key_prefix):
        content_frame = ctk.CTkFrame(parent_tab)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        status_var = ctk.StringVar(value="Activer")
        self.widgets[key_prefix]['status'] = status_var

        status_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        status_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=10)
        ctk.CTkLabel(status_frame, text="État").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(status_frame, text="Activé", variable=status_var, value="Activer").pack(side="left", padx=5)
        ctk.CTkRadioButton(status_frame, text="Désactivé", variable=status_var, value="Desactiver").pack(side="left", padx=5)
        
        return content_frame

    def printer_content(self, tab, key_prefix):
        content_frame = self.generic_frame(tab, key_prefix)
        
        ip_mode_var = ctk.StringVar(value="Auto IP")
        self.widgets[key_prefix]['ip_mode'] = ip_mode_var

        ip_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ip_frame.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        ip_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(ip_frame, text="Configuration IP").grid(row=0, column=0, sticky="w", padx= 5)
        manual_ip_entry = ctk.CTkEntry(ip_frame, placeholder_text="ex: 192.165.0.32")
        self.widgets[key_prefix]['manual_ip'] = manual_ip_entry

        def toggle_ip_entry():
            if ip_mode_var.get() == "Manuel":
                manual_ip_entry.grid(row=0, column=2, sticky="ew", padx=5)
            else:
                manual_ip_entry.grid_forget()

        ctk.CTkRadioButton(ip_frame, text="Auto IP", variable=ip_mode_var, value="Auto IP", command=toggle_ip_entry).grid(row=0, column=1, padx=25, pady=(0, 5))
        ctk.CTkRadioButton(ip_frame, text="Manuel", variable=ip_mode_var, value="Manuel", command=toggle_ip_entry).grid(row=0, column=1, padx=(70, 5))
        toggle_ip_entry()

    # Contenu section LCD
    def lcd_content(self, tab, key_prefix):
        content_frame = self.generic_frame(tab, key_prefix)
        
        fields_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        fields_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fields_frame, text="LCD Série COM").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['com_port'] = ctk.CTkEntry(fields_frame)
        self.widgets[key_prefix]['com_port'].grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Vitesse").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['vitesse'] = ctk.CTkEntry(fields_frame)
        self.widgets[key_prefix]['vitesse'].grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(fields_frame, text="Nb caractères").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['nb_caracteres'] = ctk.CTkEntry(fields_frame)
        self.widgets[key_prefix]['nb_caracteres'].grid(row=2, column=1, sticky="ew", padx=10, pady=5)
    
    # Contenu section TPE
    def tpe_content(self, tab, key_prefix):
        content_frame = self.generic_frame(tab, key_prefix)
        
        tpv_mode_var = ctk.StringVar(value="TPV IP")
        self.widgets[key_prefix]['tpv_mode'] = tpv_mode_var

        ip_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ip_frame.grid_columnconfigure(1, weight=1)
        
        com_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        com_frame.grid_columnconfigure(1, weight=1)
        
        # IP 
        ctk.CTkLabel(ip_frame, text="Adresse IP").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['ip_address'] = ctk.CTkEntry(ip_frame)
        self.widgets[key_prefix]['ip_address'].grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(ip_frame, text="Port").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['ip_port'] = ctk.CTkEntry(ip_frame)
        self.widgets[key_prefix]['ip_port'].grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        # COM
        ctk.CTkLabel(com_frame, text="Port Série COM").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['com_port'] = ctk.CTkEntry(com_frame)
        self.widgets[key_prefix]['com_port'].grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(com_frame, text="Vitesse").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['com_vitesse'] = ctk.CTkEntry(com_frame)
        self.widgets[key_prefix]['com_vitesse'].grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(com_frame, text="Timeout (ms)").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['com_timeout'] = ctk.CTkEntry(com_frame)
        self.widgets[key_prefix]['com_timeout'].grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        def change_mode():
            if tpv_mode_var.get() == "TPV IP":
                com_frame.grid_forget()
                ip_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0))
            else:
                ip_frame.grid_forget()
                com_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0))

        radio_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        radio_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(radio_frame, text="Type Connexion:").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(radio_frame, text="IP", variable=tpv_mode_var, value="TPV IP", command=change_mode).pack(side="left", padx=5)
        ctk.CTkRadioButton(radio_frame, text="Série", variable=tpv_mode_var, value="TPV Série COM", command=change_mode).pack(side="left", padx=5)
        
        self.widgets[key_prefix]['test_mode'] = ctk.CTkCheckBox(content_frame, text="Activer le mode test TPE")
        self.widgets[key_prefix]['test_mode'].grid(row=3, column=0, padx=20, pady=15, sticky="w")
        change_mode()

    def save_configuration(self):
        config = configparser.ConfigParser()

        # Section Serveur
        config['Serveur'] = {
            'url': self.widgets['serveur_ip'].get(),
            'vitesse_boucle': self.widgets['serveur_vitesse'].get()
        }

        # Sections Imprimantes
        for i in range(1, 6):
            key = f'imprimante_{i}'
            section_name = f'Imprimante{i}'
            if key in self.widgets:
                config[section_name] = {
                    'status': self.widgets[key]['status'].get(),
                    'ip_mode': self.widgets[key]['ip_mode'].get(),
                    'manual_ip': self.widgets[key]['manual_ip'].get() if self.widgets[key]['ip_mode'].get() == "Manuel" else "N.A."
                }
        
        # Section LCD
        if 'lcd' in self.widgets:
            config['LCD'] = {
                'status': self.widgets['lcd']['status'].get(),
                'com_port': self.widgets['lcd']['com_port'].get(),
                'vitesse': self.widgets['lcd']['vitesse'].get(),
                'nb_caracteres': self.widgets['lcd']['nb_caracteres'].get()
            }

        # Section TPE
        if 'tpe' in self.widgets:
            config['TPE'] = {
                'status': self.widgets['tpe']['status'].get(),
                'mode': self.widgets['tpe']['tpv_mode'].get(),
                'test_mode': 'Activé' if self.widgets['tpe']['test_mode'].get() else 'Désactivé'
            }
            if self.widgets['tpe']['tpv_mode'].get() == "TPV IP":
                config['TPE']['ip_address'] = self.widgets['tpe']['ip_address'].get()
                config['TPE']['ip_port'] = self.widgets['tpe']['ip_port'].get()
            else:
                config['TPE']['com_port'] = self.widgets['tpe']['com_port'].get()
                config['TPE']['com_vitesse'] = self.widgets['tpe']['com_vitesse'].get()
                config['TPE']['com_timeout'] = self.widgets['tpe']['com_timeout'].get()


        # Écriture dans le fichier
        try:
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            print("Configuration sauvegardée dans config.ini")
            self.status_label.configure(text="✔️ Configuration sauvegardée", text_color="green")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            self.status_label.configure(text="❌ Erreur de sauvegarde", text_color="red")
        
        self.after(3000, lambda: self.status_label.configure(text="Prêt", text_color="gray"))


    def start_server(self):
        print("Démarrage du serveur...")
        self.status_label.configure(text="Démarrage du serveur...", text_color="#28a745")
        self.after(3000, lambda: self.status_label.configure(text="Serveur démarré", text_color="#28a745"))
        telecharger_fichier()

if __name__ == "__main__":
    app = App()
    app.mainloop()