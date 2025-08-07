# 🧾 Reconnaissance Optique des Factures Fournisseurs

Application Python avec interface graphique permettant d’extraire automatiquement les informations clés à partir d’une image de **facture fournisseur**.

---

## 🔍 Fonctionnalités principales

- Interface utilisateur simple avec **Tkinter**
- Chargement d’une **image de facture** (formats supportés : JPG, PNG, BMP…)
- Extraction automatique des champs importants via **OCR Tesseract**
- Export au format **JSON** des données extraites
- Aperçu de l’image affichée dans l’application

---

## 🧠 Champs extraits

- ✅ Nom du fournisseur
- ✅ Numéro de la facture
- ✅ Date de la facture
- ✅ Montant TTC
- ✅ Montant HT
- ✅ TVA
- ✅ Devise
- ✅ Numéro SIRET
- ✅ IBAN

---

## 📦 Technologies utilisées

- `Python 3.8+`
- `Tkinter` — pour l’interface graphique
- `Pillow` — gestion d’images
- `pytesseract` — OCR avec Tesseract
- `LayoutLMv3` — modèle de deep learning pour documents
- `transformers` — bibliothèque Hugging Face
- `torch` — framework PyTorch

---

## 🚀 Lancer l'application

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
