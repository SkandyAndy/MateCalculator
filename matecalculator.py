import tkinter as tk
from tkinter import messagebox
import datetime
import math

# --- KONSTANTEN (BASIEREND AUF ANNAHMEN) ---

# Annahme: 100 mg Koffein pro 0,5L Flasche (basierend auf 20mg/100ml)
KOFFEIN_PRO_MATE = 100  # in mg

# Empfohlene max. Tagesdosis für gesunde Erwachsene (Quelle: EFSA)
MAX_TAGESDOSIS = 400  # in mg

# Durchschnittliche Halbwertszeit von Koffein (kann stark variieren!)
KOFFEIN_HALBWERTSZEIT_STUNDEN = 5.0

# --- GLOBALE DATENBANK ---
# Speichert Tupel von (Zeitstempel des Konsums, Koffeinmenge)
getrunkene_mates_liste = []

# --- FUNKTIONEN ---

def add_mate():
    """
    Fügt eine Mate zur Liste hinzu, die "jetzt" getrunken wurde.
    """
    # Speichert den genauen Zeitpunkt und die Koffeinmenge
    jetzt = datetime.datetime.now()
    getrunkene_mates_liste.append((jetzt, KOFFEIN_PRO_MATE))
    
    # Aktualisiert sofort die Anzeige
    update_display()

def berechne_aktuelles_koffein_im_system():
    """
    Berechnet das geschätzte verbleibende Koffein im Körper
    basierend auf der Halbwertszeit.
    """
    jetzt = datetime.datetime.now()
    total_verbleibend = 0.0

    for zeit_getrunken, menge in getrunkene_mates_liste:
        # Berechne, wie viele Stunden seit dem Trinken vergangen sind
        stunden_vergangen = (jetzt - zeit_getrunken).total_seconds() / 3600.0
        
        # Formel für exponentiellen Zerfall: N(t) = N0 * (1/2)^(t / T_halb)
        halbwertszeiten_vergangen = stunden_vergangen / KOFFEIN_HALBWERTSZEIT_STUNDEN
        verbleibendes_koffein = menge * (0.5 ** halbwertszeiten_vergangen)
        
        total_verbleibend += verbleibendes_koffein
        
    return total_verbleibend

def berechne_heutige_gesamtaufnahme():
    """
    Berechnet die Gesamtmenge des Koffeins, das HEUTE konsumiert wurde.
    (Ignoriert den Zerfall, zählt nur die Aufnahme)
    """
    # Finde den Start des heutigen Tages (00:00 Uhr)
    heute_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_heute = 0
    
    for zeit_getrunken, menge in getrunkene_mates_liste:
        # Zähle nur Mates, die seit Mitternacht getrunken wurden
        if zeit_getrunken >= heute_start:
            total_heute += menge
    return total_heute

def update_display():
    """
    Aktualisiert alle Text-Labels in der GUI.
    """
    
    # 1. Gesamtaufnahme HEUTE berechnen
    total_heute_mg = berechne_heutige_gesamtaufnahme()
    lbl_total_heute_val.config(text=f"{total_heute_mg} mg")

    # 2. Verbleibend bis zum 400mg-Limit
    verbleibend_mg = MAX_TAGESDOSIS - total_heute_mg
    lbl_verbleibend_val.config(text=f"{verbleibend_mg} mg")

    # 3. Geschätztes Koffein AKTUELL im System (mit Zerfall)
    aktuell_im_system_mg = berechne_aktuelles_koffein_im_system()
    lbl_aktuell_system_val.config(text=f"{aktuell_im_system_mg:.1f} mg") # .1f = 1 Nachkommastelle

    # 4. Anzahl der Mates heute
    heute_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    mates_heute_anzahl = sum(1 for zeit, _ in getrunkene_mates_liste if zeit >= heute_start)
    lbl_mates_anzahl_val.config(text=f"{mates_heute_anzahl}")

    # --- Visuelle Warnungen ---
    # Setzt alle Farben zuerst auf normal zurück
    lbl_total_heute_val.config(fg="black")
    lbl_aktuell_system_val.config(fg="black")
    lbl_verbleibend_val.config(fg="green")
    lbl_warnung.config(text="")

    # Wenn das Limit (400mg) überschritten ist
    if total_heute_mg > MAX_TAGESDOSIS or aktuell_im_system_mg > MAX_TAGESDOSIS:
        lbl_warnung.config(text="WARNUNG: Empfohlene Tagesdosis überschritten!", fg="red")
        lbl_total_heute_val.config(fg="red")
        lbl_aktuell_system_val.config(fg="red")
        lbl_verbleibend_val.config(fg="red")
    
    # Wenn man sich dem Limit nähert (z.B. 80%)
    elif total_heute_mg > MAX_TAGESDOSIS * 0.8 or aktuell_im_system_mg > MAX_TAGESDOSIS * 0.8:
        lbl_warnung.config(text="Vorsicht: Du näherst dich dem Limit.", fg="orange")
        lbl_total_heute_val.config(fg="orange")
        lbl_aktuell_system_val.config(fg="orange")
        lbl_verbleibend_val.config(fg="orange")

def reset_day():
    """
    Setzt die Zähler für den heutigen Tag zurück.
    Behält aber Einträge von Vortagen (für die Zerfallsrechnung).
    """
    if messagebox.askyesno("Zurücksetzen", "Möchtest du wirklich alle Einträge von HEUTE löschen?"):
        global getrunkene_mates_liste
        heute_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Erstellt eine neue Liste, die nur Einträge enthält, die VOR heute waren
        getrunkene_mates_liste = [eintrag for eintrag in getrunkene_mates_liste if eintrag[0] < heute_start]
        
        update_display()

def auto_update():
    """
    Ruft alle 60 Sekunden update_display() auf, damit der Wert
    "Aktuell im System" automatisch sinkt.
    """
    update_display()
    # Ruft sich selbst alle 60000 ms (1 Minute) auf
    root.after(60000, auto_update)

# --- GUI ERSTELLUNG ---

root = tk.Tk()
root.title("Mate Koffein Tracker")
root.geometry("450x400") # Fenstergröße

main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# Titel
lbl_titel = tk.Label(main_frame, text="Lidl Mate Koffein Rechner", font=("Helvetica", 16, "bold"))
lbl_titel.pack(pady=(0, 10))

# Button zum Hinzufügen
btn_add = tk.Button(main_frame, text="(+) 1 Lidl Mate (0,5L) jetzt trinken", 
                    font=("Helvetica", 12), command=add_mate, bg="#4CAF50", fg="white", height=2)
btn_add.pack(pady=10, fill=tk.X)

# --- Anzeige-Frame (für die Werte) ---
display_frame = tk.Frame(main_frame, relief="sunken", borderwidth=2, padx=10, pady=10)
display_frame.pack(fill=tk.X, pady=10)

# Zeile 1: Mates heute
lbl_mates_anzahl = tk.Label(display_frame, text="Getrunkene Mates (heute):", font=("Helvetica", 10))
lbl_mates_anzahl.grid(row=0, column=0, sticky="w", pady=4)
lbl_mates_anzahl_val = tk.Label(display_frame, text="0", font=("Helvetica", 10, "bold"))
lbl_mates_anzahl_val.grid(row=0, column=1, sticky="e", pady=4)

# Zeile 2: Gesamtkoffein heute (Aufnahme)
lbl_total_heute = tk.Label(display_frame, text="Koffein-Aufnahme (heute):", font=("Helvetica", 10))
lbl_total_heute.grid(row=1, column=0, sticky="w", pady=4)
lbl_total_heute_val = tk.Label(display_frame, text="0 mg", font=("Helvetica", 10, "bold"))
lbl_total_heute_val.grid(row=1, column=1, sticky="e", pady=4)

# Zeile 3: Verbleibend bis 400mg
lbl_verbleibend = tk.Label(display_frame, text="Verbleibend bis 400mg-Limit:", font=("Helvetica", 10))
lbl_verbleibend.grid(row=2, column=0, sticky="w", pady=4)
lbl_verbleibend_val = tk.Label(display_frame, text=f"{MAX_TAGESDOSIS} mg", font=("Helvetica", 10, "bold"), fg="green")
lbl_verbleibend_val.grid(row=2, column=1, sticky="e", pady=4)

# Zeile 4: Aktuell im System (Zerfall)
lbl_aktuell_system = tk.Label(display_frame, text="Geschätzt aktuell im System:", font=("Helvetica", 11, "bold"))
lbl_aktuell_system.grid(row=3, column=0, sticky="w", pady=(10, 4))
lbl_aktuell_system_val = tk.Label(display_frame, text="0.0 mg", font=("Helvetica", 11, "bold"))
lbl_aktuell_system_val.grid(row=3, column=1, sticky="e", pady=(10, 4))

# Sorgt dafür, dass die Werte (Spalte 1) sich an den rechten Rand anpassen
display_frame.grid_columnconfigure(1, weight=1) 

# Warn-Label
lbl_warnung = tk.Label(main_frame, text="", font=("Helvetica", 10, "bold"), fg="red")
lbl_warnung.pack(pady=5)

# Reset Button
btn_reset = tk.Button(main_frame, text="Heutige Einträge zurücksetzen", command=reset_day)
btn_reset.pack(pady=5, side=tk.LEFT)

# --- Wichtiger Hinweis am Ende ---
hinweis_text = "HAFTUNGSAUSSCHLUSS: KEINE medizinische Beratung!\nNur eine Schätzung basierend auf Annahmen:\n100mg/Flasche, 400mg max. Dosis, 5h Halbwertszeit."
lbl_hinweis = tk.Label(root, text=hinweis_text, font=("Helvetica", 8), fg="gray", justify=tk.LEFT)
lbl_hinweis.pack(pady=10, padx=10, side=tk.BOTTOM, anchor="w")

# --- Start ---
# Zeigt die initialen Werte an (alles 0)
update_display()
# Startet den Timer, der die Zerfallsrechnung jede Minute aktualisiert
auto_update()
# Startet das GUI-Fenster
root.mainloop()