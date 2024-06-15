import streamlit as st
import csv
import os

# Definir o nome do arquivo CSV para armazenar os registros de sono
csv_filename = 'registros_sono.csv'

# Verificar se o arquivo CSV já existe; se não, criar o arquivo e escrever o cabeçalho
if not os.path.isfile(csv_filename):
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Data', 'Duração (min)', 'Qualidade'])

# Função para ler os registros de sono do arquivo CSV
def ler_registros_csv():
    registros = []
    with open(csv_filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Pular o cabeçalho
        for row in reader:
            registros.append(row)
    return registros

# Função para adicionar um novo registro de sono ao arquivo CSV
def adicionar_registro_csv(data, duracao, qualidade):
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data, duracao, qualidade])

# Interface do Streamlit para inserir registros de sono
st.title('Inserir Registro de Sono')

data_sono = st.date_input('Data do sono')
duracao_sono = st.number_input('Duração do sono (em minutos)')
qualidade_sono = st.slider('Qualidade do sono (1-10)', min_value=1, max_value=10)

if st.button('Salvar Registro'):
    adicionar_registro_csv(data_sono, duracao_sono, qualidade_sono)
    st.success('Registro salvo com sucesso!')

# Mostrar registros existentes
st.title('Registros de Sono')
registros = ler_registros_csv()
for registro in registros:
    st.write(registro)
