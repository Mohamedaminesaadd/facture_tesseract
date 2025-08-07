import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Toplevel
from PIL import Image, ImageTk
import pytesseract
import os
import re
import json
from datetime import datetime
import requests
import io
from threading import Thread
from fuzzywuzzy import fuzz

# Vérifie que Tesseract est installé (chemin par défaut)
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if not os.path.exists(TESSERACT_PATH):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Tesseract non trouvé",
        "Le programme Tesseract-OCR n'est pas installé.\n\n"
        "Téléchargez-le ici :\nhttps://github.com/tesseract-ocr/tesseract\n\n"
        "Installez-le dans le chemin par défaut :\nC:\\Program Files\\Tesseract-OCR\\"
    )
    raise FileNotFoundError("Tesseract n'est pas installé.")

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Configuration de l'API météo
WEATHER_API_KEY = "66ac5e70deb304e75738fc9b6878554f"
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_ICON_MAP = {
    "Clear": "sun.png",
    "Clouds": "cloud.png",
    "Rain": "rain.png",
    "Snow": "snow.png",
    "Mist": "windy.png",
    "Haze": "windy.png",
    "Dust": "windy.png",
    "Fog": "windy.png"
}

# Mots-clés pour l'extraction des données
keywords = {
    "facture": [
        "facture", "Facture", "FACTURE", "fact ure", "fact.ure", "fact-ure", "factur", "factr", "factue", "factuer", 
        "facturee", "factrue", "fature", "fture", "facure", "fcture", "facutre", "faeture", "factuee", "fctre", 
        "fact", "facure", "facrure", "fac ture", "facturr", "fac ture", "fac-ture", "nº facture", "factura", 
        "f@cture", "facturr", "fct", "ftr", "factuure", "f-acture", "facture.", "facture:", "facture n", 
        "n°facture", "n° facture", "n facture", "n.facture", "num facture", "num.facture", "num facture.", "num facture:"
    ],
    "date": [
        "date", "Date", "DATE", "dte", "dat", "dt", "dare", "datte", "dalte", "daae", "dste", "dated", "d a t e", 
        "date:", "date d'émission", "dste", "date de", "d4te", "daté", "date du", "émission", "issue date", "date facturation",
        "date facture", "date emission", "date emmission", "date document", "document daté", "doc date", "date doc", "data", 
        "datr", "det", "dae", "date.", "date,", "date;", "date -", "date /", "date\\", "date n°", "date n", "date no"
    ],
    "total": [
        "total", "Total", "TOTAL", "totale", "montant total", "montant", "totl", "tota", "ttc", "tttal", "toal", "t0tal",
        "total général", "montant ttc", "net à payer", "prix total", "somme", "total à payer", "total dû", "somme due", 
        "montnt", "mnt", "mnt total", "montant à payer", "valeur totale", "net payable", "total net", "prix net", "prix à payer", 
        "payer", "net ttc", "montant net", "amont", "amnt", "ttal", "ttotal", "amont total", "somme totale", "total:", "total.", 
        "total,", "total;", "total -", "total /", "total\\", "total n°", "total n", "total no"
    ],
    "tva": [
        "tva", "TVA", "tVa", "tv4", "tva.", "valeur ajoutée", "tva%", "txa", "tma", "taxe", "tx", "taxe tva", 
        "tva applicable", "tva incluse", "taxe sur valeur", "tva 20%", "tva intracom", "tv@", "tv", "tvaa", 
        "tva intracommunautaire", "tax", "vat", "tva:", "t.v.a", "ta", "txe", "tav", "txv", "tax vat", "taxe %", 
        "t.v.a.", "tv a", "t v a", "t.v.a intracom", "t.v.a:", "tva.", "tva,", "tva;", "tva -", "tva /", "tva\\", "tva20%", 
        "tva 2 0 %", "tva 20 %", "tv@", "tva20 %"
    ],
    "fournisseur": [
        "fournisseur", "Fournisseur", "FOURNISSEUR", "fornisseur", "founiseur", "fourniseeur", "forniseur", "fourisseur", 
        "fournisur", "fournissur", "fourrisseur", "furnisseur", "fourni", "vendeur", "expéditeur", "expediteur", "societe", 
        "société", "sarl", "eurl", "sas", "sa", "snc", "entreprise", "societe xyz", "nom du fournisseur", "prestataire", 
        "compagnie", "propriétaire", "entreprsie", "société émettrice", "issuer", "from", "de", "exp", "émetteur", "facturé par", 
        "by", "payable to", "company", "supplier", "four nisseur", "four-nisseur", "four nissseur", "fournisseur.", "fournisseur,", 
        "fournisseur;", "fournisseur -", "fournisseur /", "fournisseur\\"
    ],
    "client": [
        "client", "Client", "CLIENT", "cliient", "clint", "clien", "cli ent", "cli@nt", "client final", "destinataire", 
        "nom du client", "acheteur", "achteur", "livré à", "livraison à", "bénéficiaire", "client n°", "id client", "client:", 
        "consommateur", "acheteur final", "to", "pour", "buyer", "payer", "customer", "recipient", "to:", "livré chez", "commande par", 
        "à l'attention de", "client id", "identifiant client", "client number", "nom client", "adresse client", "données client", 
        "clien t", "cli ent", "clien.", "client,", "client;", "client -", "client /", "client\\"
    ],
    "paiement": [
        "paiement", "mode de paiement", "payment", "payement", "moyen de paiement", "méthode de paiement", 
        "type de paiement", "conditions de paiement", "paiement par", "payé par", "règlement", "reglement", 
        "virement", "chèque", "cheque", "carte bancaire", "cb", "espèces", "especes", "prélèvement", 
        "prelevement", "mandat", "paypal", "transfert", "paiement:", "paiement.", "paiement -", "paiement /"
    ],
    "iban": [
        "iban", "IBAN", "i.b.a.n", "compte bancaire", "rib", "RIB", "r.i.b", "numéro de compte", "numero de compte", 
        "coordonnées bancaires", "coordonnees bancaires", "compte", "banque", "bic", "BIC", "swift", "SWIFT", 
        "code banque", "code guichet", "numéro compte", "numero compte", "clé rib", "cle rib", "domiciliation", 
        "titulaire du compte", "bank details", "account number", "bank account", "bank code", "iban:", "iban.", 
        "iban -", "iban /", "iban\\", "rib:", "rib.", "rib -", "rib /", "rib\\"
    ]
}

def is_similar(text, keywords_list, threshold=80):
    return any(fuzz.partial_ratio(text.lower(), kw.lower()) >= threshold for kw in keywords_list)

# Palette de couleurs modernes
COLORS = {
    'background': '#f5f6fa',
    'primary': '#3498db',
    'primary_dark': '#2980b9',
    'accent': '#2ecc71',
    'accent_dark': '#27ae60',
    'text': '#2c3e50',
    'text_light': '#7f8c8d',
    'white': '#ffffff',
    'panel': '#ecf0f1',
    'border': '#dfe6e9',
    'success': '#27ae60',
    'error': '#e74c3c'
}

class ModernButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = ttk.Style()
        self.style.configure('Modern.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=0,
                           relief='flat',
                           padding=8,
                           foreground=COLORS['white'],
                           background=COLORS['primary'],
                           bordercolor=COLORS['primary'])
        self.configure(style='Modern.TButton')

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Système Intelligent d'Extraction de Factures")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 800)
        self.style = ttk.Style()
        
        # Configuration du thème moderne
        self.root.configure(bg=COLORS['background'])
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.create_widgets()
        self.extracted_data = {}
        self.history = []
        self.update_clock()
        self.start_weather_updates("Paris")
        
    def configure_styles(self):
        # Configuration des styles
        self.style.configure('TFrame', background=COLORS['background'])
        self.style.configure('TLabel', background=COLORS['background'], font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground=COLORS['text'])
        self.style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), foreground=COLORS['text'])
        self.style.configure('Success.TLabel', foreground=COLORS['success'])
        self.style.configure('Error.TLabel', foreground=COLORS['error'])
        self.style.configure('Data.TLabel', font=('Consolas', 10), foreground=COLORS['text'])
        
        # Style des panneaux
        self.style.configure('Panel.TFrame', background=COLORS['white'], borderwidth=1, relief='solid', bordercolor=COLORS['border'])
        self.style.configure('Panel.TLabelframe', background=COLORS['white'], borderwidth=0)
        self.style.configure('Panel.TLabelframe.Label', background=COLORS['white'], font=('Segoe UI', 11, 'bold'), foreground=COLORS['text'])
        
        # Boutons modernes
        self.style.configure('Primary.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=0,
                           relief='flat',
                           padding=8,
                           foreground=COLORS['white'],
                           background=COLORS['primary'],
                           bordercolor=COLORS['primary'])
        self.style.map('Primary.TButton',
                      background=[('active', COLORS['primary_dark'])])
        
        self.style.configure('Accent.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=0,
                           relief='flat',
                           padding=8,
                           foreground=COLORS['white'],
                           background=COLORS['accent'],
                           bordercolor=COLORS['accent'])
        self.style.map('Accent.TButton',
                      background=[('active', COLORS['accent_dark'])])
        
        # Style de l'entrée
        self.style.configure('Modern.TEntry',
                           fieldbackground=COLORS['white'],
                           foreground=COLORS['text'],
                           padding=5,
                           bordercolor=COLORS['border'],
                           lightcolor=COLORS['border'],
                           darkcolor=COLORS['border'])
        
        # Style de l'arbre
        self.style.configure('Treeview', 
                           font=('Segoe UI', 9),
                           rowheight=25,
                           background=COLORS['white'],
                           fieldbackground=COLORS['white'],
                           foreground=COLORS['text'],
                           bordercolor=COLORS['border'],
                           borderwidth=0)
        self.style.configure('Treeview.Heading', 
                           font=('Segoe UI', 9, 'bold'),
                           background=COLORS['panel'],
                           foreground=COLORS['text'],
                           relief='flat')
        self.style.map('Treeview', 
                      background=[('selected', COLORS['primary'])],
                      foreground=[('selected', COLORS['white'])])

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style='Panel.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header
        header_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="Système Intelligent d'Extraction de Factures", 
                 style='Title.TLabel').pack(side=tk.LEFT, padx=10)
        
        # Time and weather frame
        info_frame = ttk.Frame(header_frame, style='Panel.TFrame')
        info_frame.pack(side=tk.RIGHT, padx=10)
        
        self.time_label = ttk.Label(info_frame, font=('Segoe UI', 9), style='Header.TLabel')
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        # Widget météo
        weather_frame = ttk.Frame(info_frame, style='Panel.TFrame')
        weather_frame.pack(side=tk.LEFT, padx=10)
        
        self.weather_icon_label = ttk.Label(weather_frame)
        self.weather_icon_label.pack(side=tk.LEFT, padx=2)
        
        self.weather_temp_label = ttk.Label(weather_frame, font=('Segoe UI', 9), style='Header.TLabel')
        self.weather_temp_label.pack(side=tk.LEFT, padx=2)
        
        self.weather_city_entry = ttk.Entry(weather_frame, width=12, font=('Segoe UI', 9), style='Modern.TEntry')
        self.weather_city_entry.insert(0, "Paris")
        self.weather_city_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(weather_frame, text="🔄", width=2, command=self.update_weather_city).pack(side=tk.LEFT)
        
        # Actions frame
        actions_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        ModernButton(actions_frame, text="Charger une facture", 
                   command=self.load_image, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ModernButton(actions_frame, text="Exporter en JSON", 
                   command=self.export_json, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ModernButton(actions_frame, text="Historique", 
                   command=self.show_history, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Image and data display
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Image panel
        image_panel = ttk.LabelFrame(display_frame, text="Aperçu de la facture", style='Panel.TLabelframe')
        image_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.image_label = ttk.Label(image_panel, background=COLORS['white'])
        self.image_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Data panel
        data_panel = ttk.LabelFrame(display_frame, text="Données extraites", style='Panel.TLabelframe')
        data_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.data_text = scrolledtext.ScrolledText(data_panel, wrap=tk.WORD, 
                                                 font=('Consolas', 10), 
                                                 padx=10, pady=10,
                                                 bg=COLORS['white'], fg=COLORS['text'],
                                                 insertbackground=COLORS['primary'],
                                                 selectbackground=COLORS['primary'],
                                                 selectforeground=COLORS['white'],
                                                 relief='flat',
                                                 borderwidth=1)
        self.data_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Prêt", relief='flat', 
                                  style='Header.TLabel', background=COLORS['panel'])
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def start_weather_updates(self, city="Paris", interval=120000):
        """Démarre les mises à jour périodiques de la météo"""
        self.fetch_weather(city)
        self.weather_update_job = self.root.after(interval, lambda: self.start_weather_updates(city, interval))

    def stop_weather_updates(self):
        """Arrête les mises à jour automatiques de la météo"""
        if self.weather_update_job:
            self.root.after_cancel(self.weather_update_job)
            self.weather_update_job = None

    def update_weather_city(self):
        city = self.weather_city_entry.get().strip()
        if city:
            self.stop_weather_updates()
            self.start_weather_updates(city)

    def fetch_weather(self, city):
        def thread_fetch():
            params = {
                "q": city,
                "units": "metric",
                "appid": WEATHER_API_KEY,
                "lang": "fr"
            }

            try:
                response = requests.get(WEATHER_BASE_URL, params=params)
                data = response.json()

                if response.status_code == 200:
                    temp = data["main"]["temp"]
                    weather_main = data["weather"][0]["main"]
                    weather_desc = data["weather"][0]["description"]

                    self.root.after(0, lambda: self.update_weather_ui(temp, weather_main, weather_desc))
                else:
                    print(f"Erreur API météo: {data.get('message', 'Unknown error')}")
            except Exception as e:
                print(f"Erreur connexion météo: {e}")

        Thread(target=thread_fetch, daemon=True).start()

    def update_weather_ui(self, temp, weather_main, weather_desc):
        self.weather_temp_label.config(text=f"{temp:.0f}°C - {weather_desc.capitalize()}")
        
        icon_url = WEATHER_ICON_MAP.get(weather_main, WEATHER_ICON_MAP["Clouds"])
        try:
            icon_response = requests.get(icon_url)
            img_data = icon_response.content
            img = Image.open(io.BytesIO(img_data)).resize((30, 30))
            icon = ImageTk.PhotoImage(img)
            self.weather_icon_label.config(image=icon)
            self.weather_icon_label.image = icon
        except Exception as e:
            print(f"Erreur chargement icône: {e}")

    def load_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff")])
        if not filepath:
            return

        self.status_bar.config(text=f"Traitement de l'image: {os.path.basename(filepath)}...")
        self.root.update()

        self.data_text.config(state=tk.NORMAL)
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, f"=== Facture: {os.path.basename(filepath)} ===\n\n", 'header')

        try:
            img = Image.open(filepath)
            img.thumbnail((500, 500))
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_image)

            self.run_ocr(filepath)
            self.status_bar.config(text=f"Terminé: {os.path.basename(filepath)}", style='Success.TLabel')
            
            self.add_to_history(filepath)
        except Exception as e:
            self.status_bar.config(text=f"Erreur: {str(e)}", style='Error.TLabel')
            messagebox.showerror("Erreur", f"Impossible de charger l'image:\n{e}")
        finally:
            self.data_text.config(state=tk.DISABLED)

    def add_to_history(self, filepath):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "file": os.path.basename(filepath),
            "path": filepath,
            "time": timestamp,
            "data": self.extracted_data.copy()
        })

    def show_history(self):
        history_window = Toplevel(self.root)
        history_window.title("Historique des factures")
        history_window.geometry("900x600")
        history_window.configure(bg=COLORS['background'])
        
        main_frame = ttk.Frame(history_window, style='Panel.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tree_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tree = ttk.Treeview(tree_frame, columns=('Date', 'Fichier', 'Numéro', 'Total'), show='headings')
        
        # Style des colonnes
        tree.heading('Date', text='Date/Heure', anchor=tk.W)
        tree.heading('Fichier', text='Fichier', anchor=tk.W)
        tree.heading('Numéro', text='Numéro Facture', anchor=tk.W)
        tree.heading('Total', text='Montant Total', anchor=tk.W)
        
        tree.column('Date', width=150)
        tree.column('Fichier', width=250)
        tree.column('Numéro', width=150)
        tree.column('Total', width=100)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        for item in reversed(self.history):
            tree.insert('', 'end', values=(
                item['time'],
                item['file'],
                item['data'].get('numero_facture', ''),
                item['data'].get('total', '')
            ))
        
        btn_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ModernButton(btn_frame, text="Voir les détails", 
                    command=lambda: self.show_history_details(tree), 
                    style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        ModernButton(btn_frame, text="Fermer", 
                    command=history_window.destroy,
                    style='Primary.TButton').pack(side=tk.RIGHT, padx=5)

    def show_history_details(self, tree):
        selected = tree.focus()
        if not selected:
            return
        item_data = tree.item(selected)
        index = len(self.history) - 1 - tree.index(selected)
        history_item = self.history[index]
        
        detail_window = Toplevel(self.root)
        detail_window.title(f"Détails: {history_item['file']}")
        detail_window.geometry("700x500")
        detail_window.configure(bg=COLORS['background'])
        
        main_frame = ttk.Frame(detail_window, style='Panel.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                       font=('Consolas', 10),
                                       bg=COLORS['white'], fg=COLORS['text'],
                                       padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        text.tag_configure('header', font=('Segoe UI', 11, 'bold'), foreground=COLORS['text'])
        text.tag_configure('bold', font=('Segoe UI', 10, 'bold'), foreground=COLORS['text'])
        text.tag_configure('data', font=('Consolas', 10), foreground=COLORS['text'])
        
        text.insert(tk.END, f"Fichier: {history_item['file']}\n", 'bold')
        text.insert(tk.END, f"Date de traitement: {history_item['time']}\n\n", 'bold')
        
        text.insert(tk.END, "Données extraites:\n", 'header')
        for key, value in history_item['data'].items():
            label = key.replace("_", " ").title() + ":"
            text.insert(tk.END, f"{label:<20}", 'bold')
            text.insert(tk.END, f"{value or 'Non trouvé(e)'}\n", 'data')
        
        text.config(state=tk.DISABLED)
        
        btn_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ModernButton(btn_frame, text="Fermer", 
                    command=detail_window.destroy,
                    style='Primary.TButton').pack(side=tk.RIGHT)

    def run_ocr(self, image_path):
        try:
            img = Image.open(image_path)
            raw_text = pytesseract.image_to_string(img, lang="fra")
            
            self.data_text.config(state=tk.NORMAL)
            self.data_text.insert(tk.END, "=== Texte brut extrait ===\n", 'header')
            self.data_text.insert(tk.END, raw_text + "\n\n", 'data')
            
            self.extract_fields(raw_text.split("\n"))
            self.data_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Erreur OCR", f"Erreur lors de l'extraction du texte:\n{e}")

    def extract_fields(self, lines):
        self.extracted_data = {
            "date": "",
            "total": "",
            "tva": "",
            "numero_facture": "",
            "fournisseur": "",
            "client": "",
            "mode_paiement": "",
            "iban_rib": ""
        }

        # Liste des mois en français (minuscules)
        mois_fr = [
            "janvier", "février", "fevrier", "mars", "avril", "mai", "juin", "juillet",
            "août", "aout", "septembre", "octobre", "novembre", "décembre", "decembre"
        ]

        # Dictionnaire pour convertir mois en numéro
        mois_to_num = {
            "janvier": "01", "février": "02", "fevrier": "02", "mars": "03", "avril": "04", "mai": "05", "juin": "06",
            "juillet": "07", "août": "08", "aout": "08", "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12", "decembre": "12"
        }

        for line in lines:
            line = re.sub(r'[^\w\s:/.-]', '', line.strip())
            if not line:
                continue
            line_lower = line.lower()

            # Extraction de la date
            if not self.extracted_data["date"]:
                # Test format numérique classique jj/mm/aaaa ou jj-mm-aaaa
                m = re.search(r"\b(\d{2}[/-]\d{2}[/-]\d{4})\b", line)
                if m:
                    self.extracted_data["date"] = m.group(1)
                else:
                    # Recherche format jj mois aaaa
                    # Exemple : 12 mai 2023
                    for mois in mois_fr:
                        # Pattern : jour (1 ou 2 chiffres) + espace + mois + espace + année 4 chiffres
                        pattern = rf"\b(\d{{1,2}})\s+{mois}\s+(\d{{4}})\b"
                        m2 = re.search(pattern, line_lower)
                        if m2:
                            jour = m2.group(1).zfill(2)  # complète avec 0 devant si nécessaire
                            mois_num = mois_to_num[mois]
                            annee = m2.group(2)
                            # Format standard jj/mm/aaaa
                            date_formatee = f"{jour}/{mois_num}/{annee}"
                            self.extracted_data["date"] = date_formatee
                            break  # on sort dès qu'on a trouvé une date

            # Extraction du numéro de facture
            if not self.extracted_data["numero_facture"] and is_similar(line_lower, keywords["facture"]):
                m = re.search(r"\b\d{4,}\b", line)
                if m:
                    self.extracted_data["numero_facture"] = m.group()

            # Extraction du montant total
            if not self.extracted_data["total"] and is_similar(line_lower, keywords["total"]):
                m = re.findall(r"\d+[.,]?\d*\s?(?:€|eur|dt|dhs)?", line)
                if m:
                    montant = re.findall(r"\d+[.,]?\d*", m[-1])
                    self.extracted_data["total"] = (montant[-1] if montant else "") + " €"

            # Extraction du taux de TVA
            if not self.extracted_data["tva"] and is_similar(line_lower, keywords["tva"]):
                m = re.search(r"\d{1,2}[.,]?\d{0,2}\s?%", line)
                if m:
                    self.extracted_data["tva"] = m.group()

            # Extraction du fournisseur
            if not self.extracted_data["fournisseur"] and is_similar(line_lower, keywords["fournisseur"]):
                self.extracted_data["fournisseur"] = line

            # Extraction du client
            if not self.extracted_data["client"] and is_similar(line_lower, keywords["client"]):
                self.extracted_data["client"] = line

            # Extraction du mode de paiement
            if not self.extracted_data["mode_paiement"] and is_similar(line_lower, keywords["paiement"]):
                # Recherche des modes de paiement courants
                paiement_mots = ["virement", "chèque", "cheque", "carte", "espèces", "especes", 
                               "prélèvement", "prelevement", "paypal", "mandat"]
                for mot in paiement_mots:
                    if mot in line_lower:
                        self.extracted_data["mode_paiement"] = mot.capitalize()
                        break

            # Extraction de l'IBAN/RIB
            if not self.extracted_data["iban_rib"] and is_similar(line_lower, keywords["iban"]):
                # Recherche d'un IBAN (FR76 XXXX XXXX XXXX XXXX XXXX XX)
                iban_pattern = r"\b[A-Z]{2}\d{2}\s?(?:\d{4}\s?){2,}\d{1,4}\b"
                m = re.search(iban_pattern, line.replace(" ", ""))
                if m:
                    self.extracted_data["iban_rib"] = m.group()
                else:
                    # Recherche d'un RIB français (XXXX XX XXX XXXXXXXXX XX)
                    rib_pattern = r"\b(?:\d{4}\s?\d{2}\s?\d{3}\s?\d{9}\s?\d{2})\b"
                    m = re.search(rib_pattern, line)
                    if m:
                        self.extracted_data["iban_rib"] = m.group()

        self.display_extracted_data()

    def display_extracted_data(self):
        self.data_text.config(state=tk.NORMAL)
        self.data_text.insert(tk.END, "=== Données structurées ===\n", 'header')
        
        for key, value in self.extracted_data.items():
            label = key.replace("_", " ").title() + ":"
            self.data_text.insert(tk.END, f"{label:<20}", 'bold')
            self.data_text.insert(tk.END, f"{value or 'Non trouvé(e)'}\n", 'data')
        
        self.data_text.insert(tk.END, "\n")
        self.data_text.config(state=tk.DISABLED)

    def export_json(self):
        if not self.extracted_data or not any(self.extracted_data.values()):
            messagebox.showwarning("Export", "Aucune donnée à exporter. Chargez d'abord une facture.")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Fichier JSON", "*.json")],
            initialfile=f"facture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
        if not filepath:
            return
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Export réussi", f"Données exportées avec succès dans:\n{filepath}")
            self.status_bar.config(text=f"Exporté: {os.path.basename(filepath)}", style='Success.TLabel')
        except Exception as e:
            messagebox.showerror("Erreur d'export", f"Erreur lors de l'export:\n{e}")
            self.status_bar.config(text=f"Erreur d'export: {str(e)}", style='Error.TLabel')

if __name__ == "__main__":
    root = tk.Tk()
    
    # Charger l'icône de l'application (si disponible)
    try:
        root.iconbitmap('favicon.ico')  # Remplacez par le chemin de votre icône
    except:
        pass
    
    app = OCRApp(root)
    
    # Configurer les balises de texte
    app.data_text.tag_configure('header', font=('Segoe UI', 11, 'bold'), foreground=COLORS['text'])
    app.data_text.tag_configure('bold', font=('Segoe UI', 10, 'bold'), foreground=COLORS['text'])
    app.data_text.tag_configure('data', font=('Consolas', 10), foreground=COLORS['text'])
    
    # Nettoyage à la fermeture
    def on_closing():
        app.stop_weather_updates()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
