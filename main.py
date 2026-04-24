import os
from datetime import datetime, timedelta

import altair as alt
import pandas as pd
import streamlit as st

COLUMNS = ["Data dormir", "Hora dormir", "Data acordar", "Hora acordar", "Horas dormidas"]
CSV_FILENAME = "registros_sono.csv"


def verifica_exist_csv(csv_filename):
    if not os.path.isfile(csv_filename):
        pd.DataFrame(columns=COLUMNS).to_csv(csv_filename, index=False)
        return

    df = pd.read_csv(csv_filename)
    missing_columns = [col for col in COLUMNS if col not in df.columns]
    if missing_columns:
        for col in missing_columns:
            df[col] = None
        df = df[COLUMNS]
        df.to_csv(csv_filename, index=False)


def ler_registros_csv(csv_filename):
    return pd.read_csv(csv_filename)


def formatar_duracao(total_minutos):
    horas = int(total_minutos // 60)
    minutos = int(total_minutos % 60)
    return f"{horas:02}:{minutos:02}"


def duracao_para_minutos(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()
    if not texto:
        return None

    partes = texto.split(":")
    try:
        if len(partes) == 2:
            horas, minutos = int(partes[0]), int(partes[1])
            return horas * 60 + minutos
        if len(partes) == 3:
            horas, minutos, segundos = int(partes[0]), int(partes[1]), int(partes[2])
            return horas * 60 + minutos + round(segundos / 60)
    except ValueError:
        return None

    return None


def adicionar_registro_csv(csv_filename, data_dormir, hora_dormir, data_acordar, hora_acordar, horas_dormidas):
    database = ler_registros_csv(csv_filename)
    novo_registro = pd.DataFrame(
        {
            "Data dormir": [data_dormir.strftime("%Y-%m-%d")],
            "Hora dormir": [hora_dormir.strftime("%H:%M:%S")],
            "Data acordar": [data_acordar.strftime("%Y-%m-%d")],
            "Hora acordar": [hora_acordar.strftime("%H:%M:%S")],
            "Horas dormidas": [horas_dormidas],
        }
    )
    database = pd.concat([database, novo_registro], ignore_index=True)
    database.to_csv(csv_filename, index=False)


def calcular_horas_dormidas(data_dormir, hora_dormir, data_acordar, hora_acordar):
    inicio_dt = datetime.combine(data_dormir, hora_dormir)
    fim_dt = datetime.combine(data_acordar, hora_acordar)

    if fim_dt < inicio_dt:
        fim_dt += timedelta(days=1)

    total_minutos = int((fim_dt - inicio_dt).total_seconds() // 60)
    return formatar_duracao(total_minutos), total_minutos


def preparar_dados(df):
    if df.empty:
        return df

    dados = df.copy()
    dados["Data dormir"] = pd.to_datetime(dados["Data dormir"], errors="coerce")
    dados["Data acordar"] = pd.to_datetime(dados["Data acordar"], errors="coerce")
    dados["Hora dormir dt"] = pd.to_datetime(dados["Hora dormir"], format="%H:%M:%S", errors="coerce")
    dados["Hora acordar dt"] = pd.to_datetime(dados["Hora acordar"], format="%H:%M:%S", errors="coerce")
    dados["Duracao minutos"] = dados["Horas dormidas"].apply(duracao_para_minutos)
    dados = dados.dropna(subset=["Data dormir", "Data acordar", "Duracao minutos", "Hora dormir dt", "Hora acordar dt"])

    dados["Duracao horas"] = dados["Duracao minutos"] / 60
    dados["Dia semana"] = dados["Data dormir"].dt.day_name()
    ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dados["Dia semana"] = pd.Categorical(dados["Dia semana"], categories=ordem_dias, ordered=True)

    dados["Horario dormir minutos"] = dados["Hora dormir dt"].dt.hour * 60 + dados["Hora dormir dt"].dt.minute
    dados["Horario acordar minutos"] = dados["Hora acordar dt"].dt.hour * 60 + dados["Hora acordar dt"].dt.minute

    dados = dados.sort_values("Data dormir")
    dados["Media movel 7 dias"] = dados["Duracao horas"].rolling(window=7, min_periods=1).mean()

    dados["Qualidade"] = pd.cut(
        dados["Duracao horas"],
        bins=[0, 6, 8, 24],
        labels=["Curta", "Ideal", "Longa"],
        include_lowest=True,
    )
    return dados


def exibir_metricas(dados, meta_horas):
    total_registros = int(len(dados))
    media_geral = dados["Duracao horas"].mean() if total_registros else 0

    hoje = pd.Timestamp.now().normalize()
    periodo_recente = dados[dados["Data dormir"] >= hoje - pd.Timedelta(days=7)]
    media_7_dias = periodo_recente["Duracao horas"].mean() if not periodo_recente.empty else 0

    aderencia = (
        ((dados["Duracao horas"] >= meta_horas - 0.5) & (dados["Duracao horas"] <= meta_horas + 0.5)).mean() * 100
        if total_registros
        else 0
    )

    if total_registros:
        ultimo_30_dias = dados[dados["Data dormir"] >= hoje - pd.Timedelta(days=30)]
        media_30 = ultimo_30_dias["Duracao horas"].mean() if not ultimo_30_dias.empty else media_geral
        tendencia = media_7_dias - media_30
        consistencia = dados["Horario dormir minutos"].std()
        consistencia = 0 if pd.isna(consistencia) else consistencia
        divida_sono = max(0, (meta_horas * total_registros) - dados["Duracao horas"].sum())
    else:
        tendencia = 0
        consistencia = 0
        divida_sono = 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Registros", f"{total_registros}")
    col2.metric("Media geral", f"{media_geral:.1f} h")
    col3.metric("Media ultimos 7 dias", f"{media_7_dias:.1f} h")
    col4.metric("Aderencia a meta", f"{aderencia:.0f}%")
    col5.metric("Tendencia (7d x 30d)", f"{tendencia:+.2f} h")
    col6.metric("Divida de sono", f"{divida_sono:.1f} h")

    if total_registros:
        st.caption(f"Consistencia de horario para dormir: desvio padrao de {consistencia:.0f} minutos.")


def exibir_graficos(dados, meta_horas):
    tabs = st.tabs(["Tendencia", "Padroes semanais", "Horario x duracao"])

    with tabs[0]:
        serie = dados[["Data dormir", "Duracao horas", "Media movel 7 dias"]].copy()
        base = alt.Chart(serie).encode(x=alt.X("Data dormir:T", title="Data"))

        linha_real = base.mark_line(point=True).encode(
            y=alt.Y("Duracao horas:Q", title="Horas dormidas"),
            color=alt.value("#22d3ee"),
            tooltip=["Data dormir:T", alt.Tooltip("Duracao horas:Q", format=".2f")],
        )

        linha_media = base.mark_line(strokeDash=[6, 4], size=3).encode(
            y=alt.Y("Media movel 7 dias:Q"),
            color=alt.value("#f59e0b"),
            tooltip=["Data dormir:T", alt.Tooltip("Media movel 7 dias:Q", format=".2f")],
        )

        meta_linha = pd.DataFrame({"Meta": [meta_horas]})
        regra_meta = alt.Chart(meta_linha).mark_rule(color="#10b981", strokeDash=[2, 2]).encode(y="Meta:Q")

        st.altair_chart((linha_real + linha_media + regra_meta).properties(height=320), use_container_width=True)

    with tabs[1]:
        media_semana = (
            dados.groupby("Dia semana", observed=True)["Duracao horas"]
            .mean()
            .reset_index()
            .dropna(subset=["Dia semana"])
        )
        grafico_semana = (
            alt.Chart(media_semana)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("Dia semana:N", sort=None, title="Dia da semana"),
                y=alt.Y("Duracao horas:Q", title="Media de horas"),
                color=alt.condition(
                    alt.datum["Duracao horas"] >= meta_horas,
                    alt.value("#34d399"),
                    alt.value("#fb7185"),
                ),
                tooltip=["Dia semana:N", alt.Tooltip("Duracao horas:Q", format=".2f")],
            )
            .properties(height=320)
        )
        st.altair_chart(grafico_semana, use_container_width=True)

    with tabs[2]:
        dispersao = (
            alt.Chart(dados)
            .mark_circle(size=100, opacity=0.75)
            .encode(
                x=alt.X("Horario dormir minutos:Q", title="Horario de dormir (minutos apos 00:00)"),
                y=alt.Y("Duracao horas:Q", title="Horas dormidas"),
                color=alt.Color("Qualidade:N", title="Qualidade"),
                tooltip=[
                    "Data dormir:T",
                    alt.Tooltip("Duracao horas:Q", format=".2f"),
                    "Qualidade:N",
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(dispersao, use_container_width=True)


def main():
    st.set_page_config(page_title="SleepWell Monitor", page_icon="😴", layout="wide")

    verifica_exist_csv(CSV_FILENAME)
    st.title("😴 SleepWell Monitor")
    st.caption("Registre, acompanhe e melhore sua rotina de sono.")

    st.subheader("Novo registro")
    col1_data_dormir, col2_hora_dormir = st.columns(2)
    with col1_data_dormir:
        data_dormir = st.date_input("Dia que foi dormir", key="data_dormir")
    with col2_hora_dormir:
        hora_dormir = st.time_input("Horario que foi dormir", key="hora_dormir")

    col1_data_acordar, col2_hora_acordar = st.columns(2)
    with col1_data_acordar:
        data_acordar = st.date_input("Dia que acordou", key="data_acordar")
    with col2_hora_acordar:
        hora_acordar = st.time_input("Horario que acordou", key="hora_acordar")

    horas, total_minutos = calcular_horas_dormidas(data_dormir, hora_dormir, data_acordar, hora_acordar)
    st.info(f"Duracao estimada do sono: {horas} h")

    if st.button("Salvar registro", type="primary"):
        if total_minutos <= 0:
            st.error("O horario de acordar precisa ser maior que o horario de dormir.")
        elif total_minutos > 24 * 60:
            st.error("Registro invalido: a duracao do sono nao pode ultrapassar 24 horas.")
        else:
            adicionar_registro_csv(CSV_FILENAME, data_dormir, hora_dormir, data_acordar, hora_acordar, horas)
            st.success(f"Registro salvo com sucesso! Voce dormiu {horas} h.")

    st.markdown("---")

    registros = ler_registros_csv(CSV_FILENAME)
    dados = preparar_dados(registros)

    st.subheader("Visao geral")
    meta_horas = st.slider("Meta de sono (horas)", min_value=5.0, max_value=10.0, value=8.0, step=0.5)
    exibir_metricas(dados, meta_horas)

    if not dados.empty:
        st.subheader("Analise visual")
        exibir_graficos(dados, meta_horas)

    st.subheader("Registros")
    tabela = registros.copy()
    if not tabela.empty:
        tabela["Data dormir"] = pd.to_datetime(tabela["Data dormir"], errors="coerce").dt.strftime("%d/%m/%Y")
        tabela["Data acordar"] = pd.to_datetime(tabela["Data acordar"], errors="coerce").dt.strftime("%d/%m/%Y")
    st.dataframe(tabela, use_container_width=True)

    csv_download = tabela.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar registros em CSV",
        data=csv_download,
        file_name="registros_sono_export.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
