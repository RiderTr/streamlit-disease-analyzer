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
        # Заголовок PDF тепер теж залежатиме від мови (передаємо його ззовні)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial_Cyrillic', 'B', 12)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(4)

    def chapter_body(self, text):
        self.set_font('Arial_Cyrillic', '', 11)
        self.multi_cell(0, 10, text)
        self.ln()

st.set_page_config(page_title="CDI Analytics", layout="wide", page_icon="")

if 'lang' not in st.session_state:
    st.session_state.lang = 'UK'

st.sidebar.title("Language / Мова")
lang_choice = st.sidebar.radio("Оберіть мову / Select language:", ["🇺🇦 Українська", "🇬🇧 English"])
st.session_state.lang = 'UK' if 'Українська' in lang_choice else 'EN'

def _t(uk, en):
    return uk if st.session_state.lang == 'UK' else en

@st.cache_data
def get_data():
    return load_and_clean_data('U.S._Chronic_Disease_Indicators.csv')

with st.spinner(_t('Завантаження масиву даних... Це займе кілька секунд.', 'Loading dataset... This will take a few seconds.')):
    try:
        df = get_data()
    except Exception as e:
        st.error(f"{_t('Помилка завантаження файлу:', 'Error loading file:')} {e}")
        st.stop()

# 3. Бокове меню
st.sidebar.title(_t("Медична Аналітика США", "US Medical Analytics"))
st.sidebar.write(f"{_t('Даних у базі:', 'Records in database:')} **{len(df):,}**")

# Меню з перекладом
m_home = _t("Головна (Досьє хвороби)", "Home (Disease Profile)")
m_top = _t("Топ захворювань", "Top Diseases")
m_search = _t("Пошук хвороби", "Disease Search")
m_states = _t("Аналіз по штатах", "State Analysis")
m_trend = _t("Прогресія (Тренди)", "Progression (Trends)")
m_demo = _t("Вік та Стать", "Age & Gender")
m_compare = _t("Порівняння трендів", "Trend Comparison")

menu = [m_home, m_top, m_search, m_states, m_trend, m_demo, m_compare]
choice = st.sidebar.radio(_t("Оберіть розділ:", "Select section:"), menu)

lang = st.session_state.lang

if choice == m_home:
    st.title(_t("Швидке досьє по хворобі", "Quick Disease Profile"))
    topic = st.text_input(_t("Введіть назву хвороби (наприклад, Sleep, Asthma, Diabetes):", "Enter disease name (e.g., Sleep, Asthma, Diabetes):"), "Sleep")
    
    if topic:
        summary = get_disease_summary(df, topic)
        if summary:
            st.success(f"{_t('Досьє знайдено:', 'Profile found:')} **{topic}**")
            col1, col2 = st.columns(2)
            col1.metric(_t("Середній показник по США", "US Average Rate"), f"{summary['avg']}%")
            col2.metric(f"{_t('Найгірший штат', 'Worst State')} ({summary['worst_state']})", f"{summary['worst_val']}%")
            
            st.write("***")
            st.subheader(f"{_t('Динаміка захворюваності:', 'Disease Dynamics:')} {topic}")
            
            trend_df = get_time_progression(df, topic)
            if not trend_df.empty:
                st.plotly_chart(generate_trend_chart(trend_df, topic, lang), use_container_width=True)
            else:
                st.info(_t("Немає даних по роках для побудови графіка.", "No yearly data available for the chart."))

            st.write("---")
            st.subheader(_t("Прогноз та Звіти", "Forecast & Reports"))

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                if st.button(_t("Згенерувати прогноз на 5 років", "Generate 5-year forecast")):
                    future_data = predict_future_trend(trend_df, years_ahead=5)
                    if not future_data.empty:
                        st.write(_t("Очікувані показники:", "Expected metrics:"))
                        st.table(future_data[['YearStart', 'NumericValue']])
                    else:
                        st.error(_t("Недостатньо даних для прогнозу.", "Not enough data for forecast."))

            with col_f2:
                pdf = PDFReport()
                pdf.add_page()
                pdf.cell(0, 10, _t('Звіт з аналітики CDC', 'CDC Analytics Report'), ln=True, align='C')
                pdf.chapter_title(_t(f"Аналіз захворювання: {topic}", f"Disease Analysis: {topic}"))
                pdf.chapter_body(_t(f"Середній показник по країні: {summary['avg']}%", f"National average: {summary['avg']}%"))
                pdf.chapter_body(_t(f"Найгірша ситуація у штаті: {summary['worst_state']} ({summary['worst_val']}%)", f"Worst situation in state: {summary['worst_state']} ({summary['worst_val']}%)"))
                
                st.download_button(
                    label=_t("Скачати PDF звіт", "Download PDF Report"),
                    data=bytes(pdf.output()),
                    file_name=f"report_{topic}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning(_t("Даних не знайдено. Перевірте правильність написання.", "No data found. Please check the spelling."))

elif choice == m_top:
    st.title(_t("Найпоширеніші хронічні проблеми", "Most Common Chronic Issues"))
    top_n = st.slider(_t("Скільки хвороб показати?", "How many diseases to show?"), 3, 20, 5)
    
    top_list = find_top_diseases(df, top_n)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(_t("### Таблиця лідерів", "### Leaderboard"))
        c_name = _t("Хвороба", "Disease")
        c_val = _t("Відсоток (%)", "Percentage (%)")
        st.dataframe(pd.DataFrame(top_list, columns=[c_name, c_val]), use_container_width=True)
    with col2:
        st.write(_t("### Графічне порівняння", "### Graphical Comparison"))
        st.plotly_chart(generate_all_topics_chart(get_all_topics_avg(df).head(top_n), lang), use_container_width=True)

elif choice == m_search:
    st.title(_t("Пошук та Географія хвороби", "Disease Search & Geography"))
    kw = st.text_input(_t("Введіть ключове слово:", "Enter keyword:"), "")
    if kw:
        result = search_disease(df, kw)
        if result['found']:
            st.success(f"{_t('Знайдено унікальних тем:', 'Unique topics found:')} {len(result['topics_matched'])}")
            selected_topic = st.selectbox(_t("Оберіть конкретну тему:", "Select specific topic:"), result['topics_matched'])
            if selected_topic:
                states_map_df = get_state_data_for_topic(df, selected_topic, top_n=100)
                if not states_map_df.empty:
                    st.plotly_chart(generate_us_map(states_map_df, selected_topic, lang), use_container_width=True)
                else:
                    st.info(_t("Немає географічних даних.", "No geographic data available."))
        else:
            st.error(_t("За вашим запитом нічого не знайдено.", "Nothing found for your query."))

elif choice == m_states:
    st.title(_t("Топ штатів за хворобою", "Top States by Disease"))
    topic = st.text_input(_t("Введіть назву хвороби:", "Enter disease name:"), "Asthma")
    if topic:
        states_df = get_state_data_for_topic(df, topic)
        if not states_df.empty:
            st.plotly_chart(generate_bar_chart(states_df, topic, lang), use_container_width=True)
            with st.expander(_t("Показати сирі дані", "Show raw data")):
                st.dataframe(states_df)
                st.download_button("📥 CSV", states_df.to_csv(index=False), file_name=f"{topic}_states.csv")
        else:
            st.warning(_t("Даних немає.", "No data."))

elif choice == m_trend:
    st.title(_t("Зміна захворюваності по роках", "Disease Change Over Years"))
    topic = st.text_input(_t("Введіть назву хвороби:", "Enter disease name:"), "Diabetes")
    if topic:
        trend_df = get_time_progression(df, topic)
        if not trend_df.empty:
            st.plotly_chart(generate_trend_chart(trend_df, topic, lang), use_container_width=True)
        else:
            st.warning(_t("Немає даних по роках.", "No yearly data available."))

elif choice == m_demo:
    st.title(_t("Демографічний аналіз", "Demographic Analysis"))
    topic = st.text_input(_t("Введіть назву хвороби:", "Enter disease name:"), "Sleep")
    if topic:
        tab1, tab2 = st.tabs([_t("📊 Графіки", "📊 Charts"), _t("🗄️ Сирі дані", "🗄️ Raw Data")])
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(_t("Розподіл за віком", "Age Distribution"))
                age_df = get_age_distribution(df, topic)
                if not age_df.empty:
                    st.dataframe(age_df, use_container_width=True, hide_index=True)
                else:
                    st.info(_t("Даних по віку немає.", "No age data."))
            with col2:
                st.subheader(_t("Розподіл за статтю", "Gender Distribution"))
                gender_df = get_gender_distribution(df, topic)
                if not gender_df.empty:
                    st.plotly_chart(generate_gender_chart(gender_df, topic, lang), use_container_width=True)
                else:
                    st.info(_t("Даних по статі немає.", "No gender data."))
        with tab2:
            if not age_df.empty:
                st.download_button(_t("📥 Вікові дані (CSV)", "Age data (CSV)"), age_df.to_csv(index=False), f"{topic}_age.csv")

elif choice == m_compare:
    st.title(_t("Порівняння двох захворювань", "Comparison of Two Diseases"))
    col1, col2 = st.columns(2)
    with col1:
        topic1 = st.text_input(_t("Перша хвороба:", "First disease:"), "Obesity")
    with col2:
        topic2 = st.text_input(_t("Друга хвороба:", "Second disease:"), "Diabetes")
        
    if topic1 and topic2:
        trend1 = get_time_progression(df, topic1)
        trend2 = get_time_progression(df, topic2)
        if not trend1.empty and not trend2.empty:
            st.plotly_chart(generate_comparison_chart(trend1, topic1, trend2, topic2, lang), use_container_width=True)
        else:
            st.error(_t("Для однієї з хвороб відсутні дані.", "Data missing for one of the diseases."))
