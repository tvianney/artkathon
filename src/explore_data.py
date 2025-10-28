import pandas as pd

# Configurer pandas pour afficher toutes les lignes
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

df = pd.read_csv('IRIS.csv')

print(df)
