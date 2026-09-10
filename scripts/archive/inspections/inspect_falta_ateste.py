import pandas as pd

df_fa = pd.read_csv('pendencias_falta_ateste.csv', sep=';')
print(f"Total de pastas com Coletum sem Ateste: {len(df_fa)}")
print("\nPor Mês/Ano:")
print(df_fa['mes_ano'].value_counts())
print("\nPor Técnico:")
print(df_fa['tecnico'].value_counts())
print("\nPor Mês e Técnico:")
print(df_fa.groupby(['mes_ano', 'tecnico']).size().unstack(fill_value=0))
