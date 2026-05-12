import streamlit as st
import pandas as pd
from data_loader import load_and_clean_data
from analytics import (
    find_top_diseases, search_disease, get_state_data_for_topic, 
    get_all_topics_avg, get_age_distribution, get_time_progression,
    get_gender_distribution, get_disease_summary, predict_future_trend
)
from report import (
    generate_bar_chart, generate_all_topics_chart, 
    generate_trend_chart, generate_gender_chart, generate_comparison_chart, generate_us_map
)
from fpdf import FPDF

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Arial_Cyrillic', '', r'C:\Windows\Fonts\arial.ttf')
        self.add_font('Arial_Cyrillic', 'B', r'C:\Windows\Fonts\arialbd.ttf')

    def header(self):
        self.set_font('Arial_Cyrillic', 'B', 15)
        self.cell(0, 10, 'Звіт з аналітики CDC', ln=True, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial_Cyrillic', 'B', 12)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial_Cyrillic', '', 11)
        self.multi_cell(0, 10, text)
        self.ln()

st.set_page_config(page_title="CDI Analytics", layout="wide", page_icon="📊")

@st.cache_data
def get_data():
    return load_and_clean_data('U.S._Chronic_Disease_Indicators.csv')

with st.spinner('Завантаження масиву даних... Це займе кілька секунд.'):
    try:
        df = get_data()
    except Exception as e:
        st.error(f"Помилка завантаження файлу: {e}")
        st.stop()

st.sidebar.title("Медична Аналітика США")
st.sidebar.write(f"Даних у базі: **{len(df):,}** рядків")

menu = [
    "Головна (Досьє хвороби)",
    "Топ захворювань",
    "Пошук хвороби",
    "Аналіз по штатах",
    "Прогресія (Тренди)",
    "Вік та Стать",
    "Порівняння трендів"
]
choice = st.sidebar.radio("Оберіть розділ:", menu)

if choice == "Головна (Досьє хвороби)":
    st.title("Швидке досьє по хворобі")
    
    topic = st.text_input("Введіть назву хвороби (наприклад, Sleep, Asthma, Diabetes):", "Sleep")
    
    if topic:
        summary = get_disease_summary(df, topic)
        if summary:
            st.success(f"Досьє знайдено: **{topic}**")
            col1, col2 = st.columns(2)
            col1.metric("Середній показник по США", f"{summary['avg']}%")
            col2.metric(f"Найгірший штат ({summary['worst_state']})", f"{summary['worst_val']}%")
            
            st.write("***")
            st.subheader(f"Динаміка захворюваності: {topic}")

            trend_df = get_time_progression(df, topic)
            
            if not trend_df.empty:
                st.plotly_chart(generate_trend_chart(trend_df, topic), use_container_width=True)
            else:
                st.info("Немає даних по роках для побудови графіка.")

            st.write("---")
            st.subheader("Прогноз та Звіти")

            col_f1, col_f2 = st.columns(2)

            with col_f1:
                if st.button("Згенерувати прогноз на 5 років"):
                    future_data = predict_future_trend(trend_df, years_ahead=5)
                    if not future_data.empty:
                        st.write("Очікувані показники:")
                        st.table(future_data[['YearStart', 'NumericValue']])
                    else:
                        st.error("Недостатньо даних для прогнозу.")

            with col_f2:
                pdf = PDFReport()
                pdf.add_page()
                pdf.chapter_title(f"Аналіз захворювання: {topic}")
                pdf.chapter_body(f"Середній показник по країні: {summary['avg']}%")
                pdf.chapter_body(f"Найгірша ситуація у штаті: {summary['worst_state']} ({summary['worst_val']}%)")

                pdf_bytes = bytes(pdf.output())

                st.download_button(
                    label="Скачати PDF звіт",
                    data=pdf_bytes,
                    file_name=f"report_{topic}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Даних не знайдено. Перевірте правильність написання.")

elif choice == "Топ захворювань":
    st.title("Найпоширеніші хронічні проблеми")
    top_n = st.slider("Скільки хвороб показати?", min_value=3, max_value=20, value=5)
    
    top_list = find_top_diseases(df, top_n)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("### Таблиця лідерів")
        st.dataframe(pd.DataFrame(top_list, columns=["Хвороба", "Відсоток (%)"]), use_container_width=True)
    
    with col2:
        st.write("### Графічне порівняння")
        topics_df = get_all_topics_avg(df)
        st.plotly_chart(generate_all_topics_chart(topics_df.head(top_n)), use_container_width=True)

elif choice == "Пошук хвороби":
    st.title("Пошук та Географія хвороби")
    st.write("Введіть ключове слово, оберіть точну тему та подивіться її розподіл на карті США.")
    
    kw = st.text_input("Введіть ключове слово (наприклад, Asthma, Cancer, Sleep):", "")
    
    if kw:
        result = search_disease(df, kw)
        if result['found']:
            st.success(f"Знайдено унікальних тем: {len(result['topics_matched'])}")

            selected_topic = st.selectbox("Оберіть конкретну тему для відображення на карті:", result['topics_matched'])
            
            if selected_topic:
                st.write("***")
                states_map_df = get_state_data_for_topic(df, selected_topic, top_n=100)
                
                if not states_map_df.empty:
                    st.plotly_chart(generate_us_map(states_map_df, selected_topic), use_container_width=True)

                    with st.expander("Показати географічні дані у вигляді таблиці"):
                        st.dataframe(states_map_df.sort_values(by='NumericValue', ascending=False).reset_index(drop=True), use_container_width=True)
                else:
                    st.info("Немає числових географічних даних для цієї теми")
        else:
            st.error("За вашим запитом нічого не знайдено")

elif choice == "Аналіз по штатах":
    st.title("Топ штатів за хворобою")
    topic = st.text_input("Введіть назву хвороби:", "Asthma")
    if topic:
        states_df = get_state_data_for_topic(df, topic)
        if not states_df.empty:
            st.plotly_chart(generate_bar_chart(states_df, topic), use_container_width=True)

            with st.expander("Показати сирі дані"):
                st.dataframe(states_df)
                st.download_button("Завантажити CSV", states_df.to_csv(index=False), file_name=f"{topic}_states.csv")
        else:
            st.warning("Даних немає")

elif choice == "Прогресія (Тренди)":
    st.title("Зміна захворюваності по роках")
    topic = st.text_input("Введіть назву хвороби:", "Diabetes")
    if topic:
        trend_df = get_time_progression(df, topic)
        if not trend_df.empty:
            st.plotly_chart(generate_trend_chart(trend_df, topic), use_container_width=True)
        else:
            st.warning("Немає даних по роках")

elif choice == "Вік та Стать":
    st.title("Демографічний аналіз")
    topic = st.text_input("Введіть назву хвороби:", "Sleep")
    
    if topic:
        tab1, tab2 = st.tabs(["Графіки", "Сирі дані"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Розподіл за віком")
                age_df = get_age_distribution(df, topic)
                if not age_df.empty:
                    st.dataframe(age_df, use_container_width=True, hide_index=True)
                else:
                    st.info("Даних по віку немає.")
                    
            with col2:
                st.subheader("Розподіл за статтю")
                gender_df = get_gender_distribution(df, topic)
                if not gender_df.empty:
                    st.plotly_chart(generate_gender_chart(gender_df, topic), use_container_width=True)
                else:
                    st.info("Даних по статі немає")
        
        with tab2:
            st.write("Тут можна переглянути або завантажити дані для власного аналізу")
            if not age_df.empty:
                st.download_button("📥 Завантажити вікові дані (CSV)", age_df.to_csv(index=False), f"{topic}_age.csv")
            if not gender_df.empty:
                st.download_button("📥 Завантажити гендерні дані (CSV)", gender_df.to_csv(index=False), f"{topic}_gender.csv")

elif choice == "Порівняння трендів":
    st.title("Порівняння двох захворювань")
    st.write("Введіть дві хвороби, щоб побачити їх графіки на одній шкалі")
    
    col1, col2 = st.columns(2)
    with col1:
        topic1 = st.text_input("Перша хвороба:", "Obesity")
    with col2:
        topic2 = st.text_input("Друга хвороба:", "Diabetes")
        
    if topic1 and topic2:
        trend1 = get_time_progression(df, topic1)
        trend2 = get_time_progression(df, topic2)
        
        if not trend1.empty and not trend2.empty:
            st.plotly_chart(generate_comparison_chart(trend1, topic1, trend2, topic2), use_container_width=True)
        else:
            st.error("Для однієї з хвороб відсутні дані по роках. Спробуйте інші")
