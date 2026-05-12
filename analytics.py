import pandas as pd
import numpy as np

def find_top_diseases(df: pd.DataFrame, top_n: int = 5) -> list:
    subset = df[df['DataValueUnit'] == '%']
    topic_avg = subset.groupby('Topic')['NumericValue'].mean().sort_values(ascending=False)
    
    results = []
    for topic, val in topic_avg.head(top_n).items():
        results.append((topic, round(val, 2)))
    return results

def search_disease(df: pd.DataFrame, keyword: str) -> dict:
    matches = df[df['Topic'].str.contains(keyword, case=False, na=False)]
    
    if matches.empty:
        return {"keyword": keyword, "found": False, "count": 0}
        
    unique_topics = list(matches['Topic'].unique())
    
    return {
        "keyword": keyword,
        "found": True,
        "count": len(matches),
        "topics_matched": unique_topics
    }

def get_state_data_for_topic(df: pd.DataFrame, topic: str, top_n: int = 10) -> pd.DataFrame:
    subset = df[(df['Topic'] == topic) & (df['DataValueType'] == 'Crude Prevalence')]
    if subset.empty:
        return pd.DataFrame()
        
    state_avg = subset.groupby(['LocationAbbr', 'StateFullName'])['NumericValue'].mean().reset_index()
    state_avg = state_avg[state_avg['LocationAbbr'] != 'US']
    state_avg['NumericValue'] = state_avg['NumericValue'].round(2)
    
    return state_avg.sort_values(by='NumericValue', ascending=True).tail(top_n)

def get_all_topics_avg(df: pd.DataFrame) -> pd.DataFrame:
    subset = df[df['DataValueUnit'] == '%']
    avg_df = subset.groupby('Topic')['NumericValue'].mean().reset_index()
    avg_df['NumericValue'] = avg_df['NumericValue'].round(2)
    return avg_df.sort_values(by='NumericValue', ascending=False)

def get_age_distribution(df: pd.DataFrame, topic: str) -> pd.DataFrame:
    subset = df[(df['Topic'] == topic) & 
                (df['DataValueUnit'] == '%') &
                (df['StratificationCategory1'].str.contains('Age', case=False, na=False))]
    
    if subset.empty:
        return pd.DataFrame()
        
    age_avg = subset.groupby('Stratification1')['NumericValue'].mean().reset_index()
    
    age_avg['NumericValue'] = age_avg['NumericValue'].round(2)
    
    return age_avg.sort_values(by='Stratification1')

def get_time_progression(df: pd.DataFrame, topic: str) -> pd.DataFrame:
    subset = df[(df['Topic'] == topic) & (df['DataValueUnit'] == '%')]
    
    if subset.empty or 'YearStart' not in subset.columns:
        return pd.DataFrame()
        
    trend_avg = subset.groupby('YearStart')['NumericValue'].mean().reset_index()
    trend_avg['NumericValue'] = trend_avg['NumericValue'].round(2)
    return trend_avg.sort_values(by='YearStart')

def get_gender_distribution(df: pd.DataFrame, topic: str) -> pd.DataFrame:
    subset = df[(df['Topic'] == topic) & 
                (df['DataValueUnit'] == '%') &
                (df['StratificationCategory1'].str.contains('Gender', case=False, na=False))]
    
    if subset.empty:
        return pd.DataFrame()
        
    gender_avg = subset.groupby('Stratification1')['NumericValue'].mean().reset_index()
    gender_avg['NumericValue'] = gender_avg['NumericValue'].round(2)
    return gender_avg

def get_disease_summary(df: pd.DataFrame, topic: str) -> dict:
    subset = df[(df['Topic'] == topic) & (df['DataValueUnit'] == '%')]
    if subset.empty:
        return {}
        
    avg_val = round(subset['NumericValue'].mean(), 2)

    state_data = get_state_data_for_topic(df, topic, top_n=1)
    if not state_data.empty:
        worst_state = state_data.iloc[0]['StateFullName']
        worst_val = round(state_data.iloc[0]['NumericValue'], 2)
    else:
        worst_state, worst_val = "Невідомо", 0
        
    return {
        "topic": topic,
        "avg": avg_val,
        "worst_state": worst_state,
        "worst_val": worst_val
    }

def predict_future_trend(trend_df: pd.DataFrame, years_ahead: int = 5):
    if trend_df.empty or len(trend_df) < 2:
        return pd.DataFrame()

    x = trend_df['YearStart'].values
    y = trend_df['NumericValue'].values

    slope, intercept = np.polyfit(x, y, 1)

    last_year = int(x.max())
    future_years = np.array(range(last_year + 1, last_year + years_ahead + 1))

    future_values = slope * future_years + intercept

    future_df = pd.DataFrame({
        'YearStart': future_years,
        'NumericValue': np.round(future_values, 2),
        'Type': 'Прогноз'
    })
    
    return future_df
