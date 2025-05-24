import pandas as pd
import numpy as np

# Charger le fichier CSV
df = pd.read_csv("base.csv")  # Remplace par le vrai nom de ton fichier

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip()

# Garder seulement les colonnes nécessaires
colonnes_a_garder = ['YEAR', 'MO', 'DY', 'T2M_MAX', 'T2M_MIN', 'PS', 'RH2M']
df = df[colonnes_a_garder]

# Ajouter la colonne moyenne de température
df['TEMPERATURE'] = (df['T2M_MAX'] + df['T2M_MIN']) / 2

# Convertir la pression en hPa
df['PS_hPa'] = df['PS'] * 10

# Supprimer les colonnes originales
df = df.drop(columns=['T2M_MAX', 'T2M_MIN', 'PS'])

# Fonction pour calculer le point de rosée
def calculer_point_rosee(Tin, RHin):
    gamma = np.log(RHin / 100) + (17.67 * Tin) / (243.5 + Tin)
    Trose = (243.5 * gamma) / (17.67 - gamma)
    return Trose

# Calculer le point de rosée et la température du condenseur
df['Trose'] = calculer_point_rosee(df['TEMPERATURE'], df['RH2M'])
df['Tout'] = df['Trose'] - 2

# Calcul des pressions de vapeur
df['Ps_in'] = 6.112 * np.exp((17.67 * df['TEMPERATURE']) / (df['TEMPERATURE'] + 243.5))
df['Pw_in'] = (df['RH2M'] / 100) * df['Ps_in']
df['Ps_out'] = 6.112 * np.exp((17.67 * df['Tout']) / (df['Tout'] + 243.5))
df['Pw_out'] = df['Ps_out']  # Pw_out ≈ Ps_out

# Calcul de l'humidité spécifique à l'entrée et à la sortie
df['win'] = 0.622 * df['Pw_in'] / (df['PS_hPa'] - df['Pw_in'])
df['wout'] = 0.622 * df['Pw_out'] / (df['PS_hPa'] - df['Pw_out'])

# Calcul de la différence d'humidité spécifique
df['delta_w'] = df['win'] - df['wout']

# Débit massique d'air supposé constant (1 kg/s) et durée (3600 s)
debit_air = 1.0  # kg/s
duree = 3600     # s

# Calcul de la masse d'eau condensée
df['meau'] = debit_air * df['delta_w'] * duree  # Masse d'eau condensée en kg

# Sauvegarder le nouveau fichier avec la colonne 'meau'
df.to_csv("dataset_final_avec_eau_condensee.csv", index=False)

print("✅ Fichier final sauvegardé sous 'dataset_final_avec_eau_condensee.csv'")
