import customtkinter as ctk
import os
import json
import subprocess
import sys

from Core.fonctionsIMPR import listeImprimantes
from Core.fonctions import logMessage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.widgets = {}
        self.server_process = None

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

        self.load_configuration()
        
        # S'assurer que le serveur est arrêté à la fermeture de la fenêtre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.prefixeLog = "[APP]"

    #Haut de page Serveur
    def server_section(self):
        server_frame = ctk.CTkFrame(self.main_frame)
        server_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        server_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(server_frame, text=" Configuration du Serveur", compound="left", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")

        ctk.CTkLabel(server_frame, text="Adresse").grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")
        self.widgets['serveur_ip'] = ctk.CTkEntry(server_frame)
        self.widgets['serveur_ip'].grid(row=1, column=1, padx=20, pady=(5, 10), sticky="ew")
    
        ctk.CTkLabel(server_frame, text="Vitesse").grid(row=2, column=0, padx=20, pady=(5, 15), sticky="w")
        self.widgets['serveur_vitesse'] = ctk.CTkEntry(server_frame)
        self.widgets['serveur_vitesse'].grid(row=2, column=1, padx=20, pady=(5, 15), sticky="ew")

    # Menu des sections
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

        self.start_stop_button = ctk.CTkButton(action_frame, text="Lancer Serveur", command=self.toggle_server, fg_color="#28a745", hover_color="#218838")
        self.start_stop_button.grid(row=0, column=2, padx=5, sticky="e")

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
        content_frame = ctk.CTkFrame(tab)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)

        type_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        type_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=10)
        
        type_var = ctk.StringVar(value="Desactiver")
        self.widgets[key_prefix]['type'] = type_var

        ctk.CTkLabel(type_frame, text="État").pack(side="left", padx=(0, 20))
        
        config_options_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        config_options_frame.grid(row=1, column=0, sticky="nsew")
        config_options_frame.grid_columnconfigure(0, weight=1)
        
        def toggle_config_visibility():
            if type_var.get() == "Desactiver":
                config_options_frame.grid_remove()
            else:
                config_options_frame.grid()

        ctk.CTkRadioButton(type_frame, text="PDF", variable=type_var, value="pdf", command=toggle_config_visibility).pack(side="left", padx=5)
        ctk.CTkRadioButton(type_frame, text="Ticket", variable=type_var, value="txt", command=toggle_config_visibility).pack(side="left", padx=5)
        ctk.CTkRadioButton(type_frame, text="Désactiver", variable=type_var, value="Desactiver", command=toggle_config_visibility).pack(side="left", padx=5)

        ip_frame = ctk.CTkFrame(config_options_frame)
        ip_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=10)
        ip_frame.grid_columnconfigure(1, weight=1)

        ip_mode_var = ctk.StringVar(value="Auto IP")
        self.widgets[key_prefix]['ip_mode'] = ip_mode_var
        
        ctk.CTkLabel(ip_frame, text="Source").grid(row=0, column=0, padx=10, pady=5)
        
        manual_ip_entry = ctk.CTkEntry(ip_frame, placeholder_text="ex: 192.168.0.32")
        self.widgets[key_prefix]['manual_ip'] = manual_ip_entry

        def toggle_ip_entry():
            if ip_mode_var.get() == "Manuel":
                manual_ip_entry.grid(row=0, column=3, sticky="ew", padx=5)
            else:
                manual_ip_entry.grid_forget()

        ctk.CTkRadioButton(ip_frame, text="Auto IP", variable=ip_mode_var, value="Auto IP", command=toggle_ip_entry).grid(row=0, column=1, padx=5)
        ctk.CTkRadioButton(ip_frame, text="Manuel", variable=ip_mode_var, value="Manuel", command=toggle_ip_entry).grid(row=0, column=2, padx=5)
        ip_frame.grid_columnconfigure(3, weight=1)
        toggle_ip_entry()

        destination_frame = ctk.CTkFrame(config_options_frame)
        destination_frame.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
        destination_frame.grid_columnconfigure(0, weight=1)

        dest_mode_var = ctk.StringVar(value="Imprimantes")
        self.widgets[key_prefix]['dest_mode'] = dest_mode_var
        
        frame_windows_printers = ctk.CTkFrame(destination_frame, fg_color="transparent")
        frame_com_printer = ctk.CTkFrame(destination_frame, fg_color="transparent")
        frame_com_printer.grid_columnconfigure(1, weight=1)

        def toggle_destination_frames():
            if dest_mode_var.get() == "Imprimantes":
                frame_com_printer.grid_remove()
                frame_windows_printers.grid(row=1, column=0, sticky="ew", pady=5, padx=10)
            else:
                frame_windows_printers.grid_remove()
                frame_com_printer.grid(row=1, column=0, sticky="ew", pady=5, padx=10)

        ctk.CTkRadioButton(destination_frame, text="Imprimantes", variable=dest_mode_var, value="Imprimantes", command=toggle_destination_frames).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkRadioButton(destination_frame, text="Imprimante Série COM", variable=dest_mode_var, value="Série COM", command=toggle_destination_frames).grid(row=0, column=0, padx=(150, 10), pady=5, sticky="w")
        
        printers = listeImprimantes()
        self.widgets[key_prefix]['dest_imprimante_win'] = ctk.CTkComboBox(frame_windows_printers, values=printers)
        self.widgets[key_prefix]['dest_imprimante_win'].pack(fill="x", expand=True)

        ctk.CTkLabel(frame_com_printer, text="Port COM").grid(row=0, column=0, padx=5)
        self.widgets[key_prefix]['dest_port_com'] = ctk.CTkEntry(frame_com_printer, width=60)
        self.widgets[key_prefix]['dest_port_com'].grid(row=0, column=1, padx=5)
        ctk.CTkLabel(frame_com_printer, text="Vitesse").grid(row=0, column=2, padx=(20, 5))
        self.widgets[key_prefix]['dest_vitesse_com'] = ctk.CTkEntry(frame_com_printer)
        self.widgets[key_prefix]['dest_vitesse_com'].grid(row=0, column=3, padx=5, sticky="ew")
        frame_com_printer.grid_columnconfigure(3, weight=1)

        toggle_config_visibility()
        toggle_destination_frames()

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
    
    def tpe_content(self, tab, key_prefix):
        content_frame = self.generic_frame(tab, key_prefix)
        
        tpv_mode_var = ctk.StringVar(value="TPV IP")
        self.widgets[key_prefix]['tpv_mode'] = tpv_mode_var

        ip_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        ip_frame.grid_columnconfigure(1, weight=1)
        
        com_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        com_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(ip_frame, text="Adresse").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['ip_address'] = ctk.CTkEntry(ip_frame)
        self.widgets[key_prefix]['ip_address'].grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(ip_frame, text="Port").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.widgets[key_prefix]['ip_port'] = ctk.CTkEntry(ip_frame)
        self.widgets[key_prefix]['ip_port'].grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
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
        config_data = {}

        config_data['Serveur'] = {
            'url': self.widgets['serveur_ip'].get(),
            'vitesse_boucle': int(self.widgets['serveur_vitesse'].get() or 0)
        }

        config_data.update({f'Imprimante{i}': {} for i in range(1, 6)})
        for i in range(1, 6):
            key = f'imprimante_{i}'
            section_name = f'Imprimante{i}'
            if key in self.widgets:
                printer_type = self.widgets[key]['type'].get()
                printer_config = {'type': printer_type}

                if printer_type != 'Desactiver':
                    printer_config['source_mode'] = self.widgets[key]['ip_mode'].get()
                    printer_config['source_ip_manuelle'] = self.widgets[key]['manual_ip'].get() if self.widgets[key]['ip_mode'].get() == "Manuel" else "N.A."
                    
                    dest_mode = self.widgets[key]['dest_mode'].get()
                    printer_config['destination_mode'] = dest_mode
                    
                    if dest_mode == "Imprimantes":
                        printer_config['destination'] = self.widgets[key]['dest_imprimante_win'].get()
                    else: # Série COM
                        printer_config['destination'] = 'COM'
                        printer_config['port_com'] = self.widgets[key]['dest_port_com'].get()
                        printer_config['vitesse_com'] = self.widgets[key]['dest_vitesse_com'].get()
                
                config_data[section_name] = printer_config
        
        if 'lcd' in self.widgets:
            config_data['LCD'] = {
                'status': self.widgets['lcd']['status'].get(),
                'com_port': self.widgets['lcd']['com_port'].get(),
                'vitesse': self.widgets['lcd']['vitesse'].get(),
                'nb_caracteres': self.widgets['lcd']['nb_caracteres'].get()
            }

        if 'tpe' in self.widgets:
            tpe_config = {
                'status': self.widgets['tpe']['status'].get(),
                'mode': self.widgets['tpe']['tpv_mode'].get(),
                'test_mode': 'Activé' if self.widgets['tpe']['test_mode'].get() else 'Désactivé'
            }
            if self.widgets['tpe']['tpv_mode'].get() == "TPV IP":
                tpe_config['ip_address'] = self.widgets['tpe']['ip_address'].get()
                tpe_config['ip_port'] = self.widgets['tpe']['ip_port'].get()
            else:
                tpe_config['com_port'] = self.widgets['tpe']['com_port'].get()
                tpe_config['com_vitesse'] = self.widgets['tpe']['com_vitesse'].get()
                tpe_config['com_timeout'] = self.widgets['tpe']['com_timeout'].get()
            config_data['TPE'] = tpe_config

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "data", "config.json")
            
            with open(config_path, 'w', encoding='utf-8') as configfile:
                json.dump(config_data, configfile, ensure_ascii=False, indent=4)
                
            self.status_label.configure(text="✔️ Configuration sauvegardée", text_color="green")

        except Exception as e:
            logMessage(self.prefixeLog,f"Erreur pendant la sauvegarde de la configuration: {e}")
            self.status_label.configure(text=f"❌ Erreur: {e}", text_color="red")
        
        self.after(3000, lambda: self.status_label.configure(text="Prêt", text_color="gray"))

    def load_configuration(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "data", "config.json")

            if not os.path.exists(config_path):
                self.status_label.configure(text="Aucun fichier de configuration trouvé.", text_color="gray")
                self.after(4000, lambda: self.status_label.configure(text="Prêt", text_color="gray"))
                return

            with open(config_path, 'r', encoding='utf-8') as configfile:
                config_data = json.load(configfile)

            server_config = config_data.get('Serveur', {})
            self.widgets['serveur_ip'].insert(0, server_config.get('url', ''))
            self.widgets['serveur_vitesse'].insert(0, str(server_config.get('vitesse_boucle', '')))

            for i in range(1, 6):
                key = f'imprimante_{i}'
                section_name = f'Imprimante{i}'
                if key in self.widgets and section_name in config_data:
                    printer_config = config_data[section_name]
                    printer_type = printer_config.get('type', 'Desactiver')
                    self.widgets[key]['type'].set(printer_type)
                    
                    if printer_type != 'Desactiver':
                        ip_mode = printer_config.get('source_mode', 'Auto IP')
                        self.widgets[key]['ip_mode'].set(ip_mode)
                        if ip_mode == 'Manuel':
                            self.widgets[key]['manual_ip'].insert(0, printer_config.get('source_ip_manuelle', ''))
                        
                        dest_mode = printer_config.get('destination_mode', 'Imprimantes')
                        self.widgets[key]['dest_mode'].set(dest_mode)
                        
                        if dest_mode == 'Imprimantes':
                            self.widgets[key]['dest_imprimante_win'].set(printer_config.get('destination', ''))
                        else:
                            self.widgets[key]['dest_port_com'].insert(0, printer_config.get('port_com', ''))
                            self.widgets[key]['dest_vitesse_com'].insert(0, printer_config.get('vitesse_com', ''))

            if 'lcd' in self.widgets and 'LCD' in config_data:
                lcd_config = config_data.get('LCD', {})
                self.widgets['lcd']['status'].set(lcd_config.get('status', 'Activer'))
                self.widgets['lcd']['com_port'].insert(0, lcd_config.get('com_port', ''))
                self.widgets['lcd']['vitesse'].insert(0, lcd_config.get('vitesse', ''))
                self.widgets['lcd']['nb_caracteres'].insert(0, lcd_config.get('nb_caracteres', ''))

            if 'tpe' in self.widgets and 'TPE' in config_data:
                tpe_config = config_data.get('TPE', {})
                self.widgets['tpe']['status'].set(tpe_config.get('status', 'Activer'))
                mode = tpe_config.get('mode', 'TPV IP')
                self.widgets['tpe']['tpv_mode'].set(mode)
                
                if tpe_config.get('test_mode') == 'Activé':
                    self.widgets['tpe']['test_mode'].select()
                else:
                    self.widgets['tpe']['test_mode'].deselect()

                if mode == "TPV IP":
                    self.widgets['tpe']['ip_address'].insert(0, tpe_config.get('ip_address', ''))
                    self.widgets['tpe']['ip_port'].insert(0, tpe_config.get('ip_port', ''))
                else:
                    self.widgets['tpe']['com_port'].insert(0, tpe_config.get('com_port', ''))
                    self.widgets['tpe']['com_vitesse'].insert(0, tpe_config.get('com_vitesse', ''))
                    self.widgets['tpe']['com_timeout'].insert(0, tpe_config.get('com_timeout', ''))

            self.status_label.configure(text="Configuration chargée.", text_color="green")
            self.after(3000, lambda: self.status_label.configure(text="Prêt", text_color="gray"))

        except Exception as e:
            logMessage(self.prefixeLog, f"Erreur lors du chargement de la configuration: {e}")
            self.status_label.configure(text=f"❌ Erreur chargement: {e}", text_color="red")
            self.after(4000, lambda: self.status_label.configure(text="Prêt", text_color="gray"))

    def toggle_server(self):
        if self.server_process:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        self.status_label.configure(text="Lancement du serveur...", text_color="#28a745")
        try:
            python_executable = sys.executable

            self.server_process = subprocess.Popen([python_executable, "-m", "Core.serveur"])
            
            self.start_stop_button.configure(text="Arrêter Serveur", command=self.toggle_server, fg_color="#dc3545", hover_color="#c82333")
            self.status_label.configure(text="✔️ Serveur démarré", text_color="green")
            
        except Exception as e:
            logMessage(self.prefixeLog, f"Erreur lors du lancement du serveur: {e}")
            self.status_label.configure(text=f"❌ Erreur lancement: {e}", text_color="red")
            self.server_process = None

    def stop_server(self):
        if self.server_process:
            self.status_label.configure(text="Arrêt du serveur...", text_color="orange")
            self.server_process.terminate()  
            self.server_process.wait()       
            self.server_process = None
            self.start_stop_button.configure(text="Lancer Serveur", command=self.toggle_server, fg_color="#28a745", hover_color="#218838")
            self.status_label.configure(text="Serveur arrêté", text_color="gray")
    
    def on_closing(self):
        if self.server_process:
            self.stop_server()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()