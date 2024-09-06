import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os

# Função para verificar se o CSV existe; se não, criar com as colunas necessárias
def verifica_exist_csv(csv_filename):
    if not os.path.isfile(csv_filename):
        df = pd.DataFrame(columns=['Data dormir', 'Hora dormir', 'Data acordar', 'Hora acordar', 'Horas dormidas'])
        df.to_csv(csv_filename, index=False)

# Função para ler os registros de sono do arquivo CSV
def ler_registros_csv():
    return pd.read_csv(csv_filename)

# Função para adicionar um novo registro de sono ao arquivo CSV
def adicionar_registro_csv(data_dormir, hora_dormir, data_acordar, hora_acordar, horas_dormidas):
    database = ler_registros_csv()
    novo_registro = pd.DataFrame({
        'Data dormir': [data_dormir.strftime('%Y-%m-%d')],
        'Hora dormir': [hora_dormir.strftime('%H:%M:%S')],
        'Data acordar': [data_acordar.strftime('%Y-%m-%d')],
        'Hora acordar': [hora_acordar.strftime('%H:%M:%S')],
        'Horas dormidas': [horas_dormidas]
    })
    database = pd.concat([database, novo_registro], ignore_index=True)
    database.to_csv(csv_filename, index=False)

# Função para calcular as horas dormidas
def calcular_horas_dormidas(data_dormir, hora_dormir, data_acordar, hora_acordar):
    # Combinar data e hora em objetos datetime
    inicio_dt = datetime.combine(data_dormir, hora_dormir)
    fim_dt = datetime.combine(data_acordar, hora_acordar)
    
    # Se o horário de acordar for antes do de dormir, assumir que é no dia seguinte
    if fim_dt < inicio_dt:
        fim_dt += timedelta(days=1)
    
    # Calcular a diferença total em segundos
    total_segundos = (fim_dt - inicio_dt).total_seconds()
    
    # Converter para horas e minutos
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    
    # Retornar no formato "HH:MM"
    return f"{horas:02}:{minutos:02}"

# Função para exibir a data e hora selecionadas
def print_data_hora(data_sono, hora_sono, tipo='Sono'):
    if data_sono and hora_sono:
        data_hora_sono = datetime.combine(data_sono, hora_sono)
        data_hora_formatada = data_hora_sono.strftime('%d/%m/%Y %H:%M')
        st.write(f'Data e hora selecionadas ({tipo}): {data_hora_formatada}')
    else:
        st.write(f'Por favor, selecione tanto a data quanto a hora para {tipo}.')

if __name__ == '__main__':
    
    csv_filename = 'registros_sono.csv'
    verifica_exist_csv(csv_filename)

    _, col2_title_principal, _ = st.columns([1, 3, 1])
    col2_title_principal.title('Registro(s) de Sono')

    col1_data_dormir, col2_hora_dormir = st.columns(2)
    with col1_data_dormir:
        data_dormir = st.date_input('Dia que foi dormir', key='data_dormir')
    with col2_hora_dormir:
        hora_dormir = st.time_input('Horário que foi dormir', key='hora_dormir')
    print_data_hora(data_dormir, hora_dormir, tipo='Sono')

    st.markdown("---")

    col1_data_acordar, col2_hora_acordar = st.columns(2)
    with col1_data_acordar:
        data_acordar = st.date_input('Dia que acordou', key='data_acordar')
    with col2_hora_acordar:
        hora_acordar = st.time_input('Horário que acordou', key='hora_acordar')
    print_data_hora(data_acordar, hora_acordar, tipo='Acordar')

    # Botão para salvar o registro
    if st.button('Salvar registro'):
        horas = calcular_horas_dormidas(data_dormir, hora_dormir, data_acordar, hora_acordar)
        adicionar_registro_csv(data_dormir, hora_dormir, data_acordar, hora_acordar, horas)
        st.success(f'Registro salvo com sucesso! Você dormiu {horas} horas.')

    st.markdown("---")

    # Título secundário para exibir os registros
    _, col2_title_secondary, _ = st.columns([1, 3, 1])
    col2_title_secondary.title('Registro(s) de Sono')

    registros = ler_registros_csv()

    # Formatar as datas para exibição
    registros['Data dormir'] = pd.to_datetime(registros['Data dormir']).dt.strftime('%d/%m/%Y')
    registros['Data acordar'] = pd.to_datetime(registros['Data acordar']).dt.strftime('%d/%m/%Y')
    st.dataframe(registros)
