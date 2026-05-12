import pandas as pd
import os

STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia', 'US': 'United States (Average)', 'PR': 'Puerto Rico', 'VI': 'Virgin Islands', 'GU': 'Guam', 'MP': 'Northern Mariana Islands',
    'AS': 'American Samoa', 'UM': 'United States Minor Outlying Islands'
}

def load_and_clean_data(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл {filepath} не найден.")
    
    df = pd.read_csv(filepath, low_memory=False)
    df['NumericValue'] = pd.to_numeric(df['DataValue'], errors='coerce')
    
    df['StateFullName'] = df['LocationAbbr'].map(STATE_NAMES).fillna(df['LocationAbbr'])
    return df

def get_unique_topics(df: pd.DataFrame) -> list:
    unique_topics = set(df['Topic'].dropna())
    return sorted(list(unique_topics))
