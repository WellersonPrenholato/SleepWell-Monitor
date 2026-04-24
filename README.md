# 😴 SleepWell Monitor

Aplicativo em **Streamlit** para registrar e acompanhar hábitos de sono com métricas e visualizações simples.

## ✨ Funcionalidades

- 📝 Registrar horário de dormir e acordar
- ⏱️ Cálculo automático da duração do sono
- ✅ Validação para evitar registros inválidos (ex.: mais de 24h)
- 📊 Painel com métricas de acompanhamento
- 📈 Gráficos avançados de tendência, padrões semanais e relação horário x duração
- 🧭 Classificação de qualidade do sono (Curta, Ideal, Longa)
- 🌙 Tema dark mode por padrão
- 📥 Exportação dos registros em CSV

## 🧰 Tecnologias

- Python 3.10+
- Streamlit
- Pandas

## 🚀 Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/WellersonPrenholato/SleepWell-Monitor.git
cd SleepWell-Monitor
```

### 2. Criar e ativar ambiente virtual (opcional, recomendado)

No Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar o app

```bash
streamlit run main.py
```

## 🗂️ Estrutura do projeto

```text
SleepWell-Monitor/
├── main.py
├── registros_sono.csv
└── README.md
```

## 📌 Observações

- O arquivo `registros_sono.csv` é criado automaticamente caso não exista.
- Os dados são armazenados localmente no CSV.

## 🤝 Contribuição

Sugestões e melhorias são bem-vindas. Abra uma issue ou envie um pull request.

## 📄 Licença

Projeto para fins educacionais.