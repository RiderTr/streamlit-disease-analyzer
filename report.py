import plotly.express as px
import pandas as pd

def generate_bar_chart(states_df: pd.DataFrame, topic: str, lang: str = 'UK'):
    t_title = f'Топ штатів за захворюванням: {topic}' if lang == 'UK' else f'Top States for: {topic}'
    t_val = 'Середнє значення (%)' if lang == 'UK' else 'Average Value (%)'
    t_state = 'Штат' if lang == 'UK' else 'State'

    fig = px.bar(states_df, x='NumericValue', y='StateFullName', orientation='h',
                 title=t_title, labels={'NumericValue': t_val, 'StateFullName': t_state},
                 color='NumericValue', color_continuous_scale='Teal')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def generate_all_topics_chart(topics_df: pd.DataFrame, lang: str = 'UK'):
    n = len(topics_df)
    t_title = f'Середній відсоток: Топ-{n} тем' if lang == 'UK' else f'Average Percentage: Top {n} Topics'
    t_val = 'Середнє значення (%)' if lang == 'UK' else 'Average Value (%)'
    t_topic = 'Хвороба' if lang == 'UK' else 'Disease'

    fig = px.bar(topics_df, x='NumericValue', y='Topic', orientation='h',
                 title=t_title, labels={'NumericValue': t_val, 'Topic': t_topic},
                 color='NumericValue', color_continuous_scale='Sunset')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def generate_trend_chart(trend_df: pd.DataFrame, topic: str, lang: str = 'UK'):
    t_title = f'Динаміка захворюваності: {topic}' if lang == 'UK' else f'Disease Dynamics: {topic}'
    t_val = 'Середнє значення (%)' if lang == 'UK' else 'Average Value (%)'
    t_year = 'Рік' if lang == 'UK' else 'Year'

    fig = px.line(trend_df, x='YearStart', y='NumericValue', markers=True,
                  title=t_title, labels={'YearStart': t_year, 'NumericValue': t_val},
                  color_discrete_sequence=['purple'])
    fig.update_xaxes(dtick=1)
    return fig

def generate_gender_chart(gender_df: pd.DataFrame, topic: str, lang: str = 'UK'):
    t_title = f'Розподіл за статтю: {topic}' if lang == 'UK' else f'Gender Distribution: {topic}'
    
    fig = px.pie(gender_df, values='NumericValue', names='Stratification1', hole=0.4,
                 title=t_title, color_discrete_sequence=['#3498db', '#e74c3c', '#95a5a6'])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def generate_comparison_chart(trend1: pd.DataFrame, topic1: str, trend2: pd.DataFrame, topic2: str, lang: str = 'UK'):
    t_disease = 'Хвороба' if lang == 'UK' else 'Disease'
    t_title = 'Порівняння прогресії двох захворювань' if lang == 'UK' else 'Comparison of Two Diseases'
    t_val = 'Середнє значення (%)' if lang == 'UK' else 'Average Value (%)'
    t_year = 'Рік' if lang == 'UK' else 'Year'

    trend1[t_disease] = topic1
    trend2[t_disease] = topic2
    combined_df = pd.concat([trend1, trend2])
    
    fig = px.line(combined_df, x='YearStart', y='NumericValue', color=t_disease, markers=True,
                  title=t_title, labels={'YearStart': t_year, 'NumericValue': t_val})
    fig.update_xaxes(dtick=1)
    return fig

def generate_us_map(states_df: pd.DataFrame, topic: str, lang: str = 'UK'):
    t_title = f'Географічний розподіл: {topic}' if lang == 'UK' else f'Geographic Distribution: {topic}'
    t_val = 'Середнє значення (%)' if lang == 'UK' else 'Average Value (%)'
    t_code = 'Код штату' if lang == 'UK' else 'State Code'

    fig = px.choropleth(
        states_df, locations='LocationAbbr', locationmode='USA-states', color='NumericValue',
        scope='usa', color_continuous_scale='Reds', title=t_title, hover_name='StateFullName',
        labels={'NumericValue': t_val, 'LocationAbbr': t_code}
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig
