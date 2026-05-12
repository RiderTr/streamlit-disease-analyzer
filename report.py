import plotly.express as px
import pandas as pd

def generate_bar_chart(states_df: pd.DataFrame, topic: str):
    fig = px.bar(states_df, x='NumericValue', y='StateFullName', orientation='h',
                 title=f'Топ штатів за захворюванням: {topic}',
                 labels={'NumericValue': 'Середнє значення (%)', 'StateFullName': 'Штат'},
                 color='NumericValue', color_continuous_scale='Teal')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=40, b=0))
    return fig

def generate_all_topics_chart(topics_df: pd.DataFrame):
    n = len(topics_df) 
    
    fig = px.bar(topics_df, x='NumericValue', y='Topic', orientation='h',
                 title=f'Середній відсоток захворюваності: Топ-{n} тем', 
                 labels={'NumericValue': 'Середнє значення (%)', 'Topic': 'Хвороба'},
                 color='NumericValue', color_continuous_scale='Sunset')
    
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def generate_trend_chart(trend_df: pd.DataFrame, topic: str):
    fig = px.line(trend_df, x='YearStart', y='NumericValue', markers=True,
                  title=f'Динаміка захворюваності: {topic}',
                  labels={'YearStart': 'Рік', 'NumericValue': 'Середнє значення (%)'},
                  color_discrete_sequence=['purple'])
    fig.update_xaxes(dtick=1)
    return fig

def generate_gender_chart(gender_df: pd.DataFrame, topic: str):
    fig = px.pie(gender_df, values='NumericValue', names='Stratification1', hole=0.4,
                 title=f'Розподіл за статтю: {topic}',
                 color_discrete_sequence=['#3498db', '#e74c3c', '#95a5a6'])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def generate_comparison_chart(trend1: pd.DataFrame, topic1: str, trend2: pd.DataFrame, topic2: str):
    trend1['Хвороба'] = topic1
    trend2['Хвороба'] = topic2
    combined_df = pd.concat([trend1, trend2])
    
    fig = px.line(combined_df, x='YearStart', y='NumericValue', color='Хвороба', markers=True,
                  title='Порівняння прогресії двох захворювань',
                  labels={'YearStart': 'Рік', 'NumericValue': 'Середнє значення (%)'})
    fig.update_xaxes(dtick=1)
    return fig

def generate_us_map(states_df: pd.DataFrame, topic: str):
    fig = px.choropleth(
        states_df,
        locations='LocationAbbr',
        locationmode='USA-states',
        color='NumericValue',
        scope='usa',
        color_continuous_scale='Reds',
        title=f'Географічний розподіл захворюваності: {topic}',
        hover_name='StateFullName',
        labels={'NumericValue': 'Середнє значення (%)', 'LocationAbbr': 'Код штату'}
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig
