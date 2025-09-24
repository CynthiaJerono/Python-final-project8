
# COVID-19 Three Pillars Analysis Dashboard
# Streamlit app for interactive exploration

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="COVID-19 Impact Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="@st.cache_data
def load_data():
    '''Load CSV from Google Drive and return DataFrame'''
    url = "https://drive.google.com/uc?id=1mqouGVQv_QThAGK8cN4N1vuXPQaRjNla"
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year  # same as before
    return df

# Load the data
df = load_data()
dt.year
    return df

# Load data
df = load_clean_data()

# Title and description
st.title("🏥 COVID-19: Three Pillars Impact Analysis")
st.markdown("""
**Interactive exploration of disease burden, healthcare system strain, and government response effectiveness**

**Follows the three-pillar framework: Burden | System Strain | Government Response**
""")

# Sidebar controls
st.sidebar.header("🎛️ Dashboard Controls")

# Country selection
countries = sorted(df['location'].unique())
selected_country = st.sidebar.selectbox(
    "Select Country:",
    countries,
    index=countries.index('United States') if 'United States' in countries else 0
)

# Year range slider
min_year = int(df['year'].min())
max_year = int(df['year'].max())
year_range = st.sidebar.slider(
    "Select Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Pillar selection
selected_pillar = st.sidebar.radio(
    "Focus Analysis Pillar:",
    ["Disease Burden", "Healthcare System Strain", "Government Response"]
)

# Filter data based on selections
filtered_df = df[
    (df['location'] == selected_country) & 
    (df['year'].between(year_range[0], year_range[1]))
]

# Main dashboard
st.header(f"📊 {selected_pillar} Analysis: {selected_country}")

if selected_pillar == "Disease Burden":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cases = filtered_df['total_cases'].max()
        st.metric("Total Cases", f"{total_cases:,.0f}")
    
    with col2:
        total_deaths = filtered_df['total_deaths'].max()
        st.metric("Total Deaths", f"{total_deaths:,.0f}")
    
    with col3:
        mortality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0
        st.metric("Mortality Rate", f"{mortality_rate:.2f}%")
    
    with col4:
        peak_cases = filtered_df['new_cases'].max()
        st.metric("Peak Daily Cases", f"{peak_cases:,.0f}")
    
    # Time series chart
    if not filtered_df.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(filtered_df['date'], filtered_df['new_cases_smoothed'], linewidth=2)
        ax.set_title(f'COVID-19 Cases in {selected_country}')
        ax.set_ylabel('Daily Cases (smoothed)')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters")

elif selected_pillar == "Healthcare System Strain":
    if not filtered_df.empty and filtered_df['hosp_patients'].notna().any():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            peak_hosp = filtered_df['hosp_patients'].max()
            st.metric("Peak Hospital Patients", f"{peak_hosp:,.0f}")
        
        with col2:
            beds_per_k = filtered_df['hospital_beds_per_thousand'].iloc[0] if not filtered_df['hospital_beds_per_thousand'].isna().all() else 0
            st.metric("Hospital Beds per 1000", f"{beds_per_k:.1f}")
        
        with col3:
            strain_ratio = (peak_hosp / (beds_per_k * 10)) if beds_per_k > 0 else 0
            st.metric("Peak Strain Ratio", f"{strain_ratio:.1f}x")
        
        # Hospitalization chart
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(filtered_df['date'], filtered_df['hosp_patients'], label='Hospital Patients', linewidth=2)
        if filtered_df['icu_patients'].notna().any():
            ax.plot(filtered_df['date'], filtered_df['icu_patients'], label='ICU Patients', linewidth=2)
        ax.set_title(f'Hospital System Strain in {selected_country}')
        ax.set_ylabel('Patients')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("Hospitalization data not available for selected country/time period")

else:  # Government Response
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_stringency = filtered_df['stringency_index'].mean()
            st.metric("Average Stringency", f"{avg_stringency:.1f}/100")
        
        with col2:
            max_vaccination = filtered_df['people_fully_vaccinated_per_hundred'].max()
            st.metric("Max Vaccination Rate", f"{max_vaccination:.1f}%")
        
        with col3:
            tests_per_case = filtered_df['tests_per_case'].mean() if 'tests_per_case' in filtered_df.columns else 0
            st.metric("Avg Tests per Case", f"{tests_per_case:.1f}")
        
        # Response metrics chart
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if filtered_df['stringency_index'].notna().any():
            ax.plot(filtered_df['date'], filtered_df['stringency_index'], label='Stringency Index', color='red', linewidth=2)
            ax.set_ylabel('Stringency Index', color='red')
            ax.tick_params(axis='y', labelcolor='red')
        
        if filtered_df['people_fully_vaccinated_per_hundred'].notna().any():
            ax2 = ax.twinx()
            ax2.plot(filtered_df['date'], filtered_df['people_fully_vaccinated_per_hundred'], 
                     label='Fully Vaccinated %', color='green', linewidth=2)
            ax2.set_ylabel('Vaccinated %', color='green')
            ax2.tick_params(axis='y', labelcolor='green')
        
        ax.set_title(f'Government Response in {selected_country}')
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters")

# Data sample display
with st.expander("🔍 View Data Sample"):
    if not filtered_df.empty:
        columns_to_show = ['date', 'new_cases', 'total_deaths']
        if 'hosp_patients' in filtered_df.columns:
            columns_to_show.append('hosp_patients')
        if 'stringency_index' in filtered_df.columns:
            columns_to_show.append('stringency_index')
            
        st.dataframe(filtered_df[columns_to_show].tail(10))
    else:
        st.write("No data available for the selected filters")

# Key insights sidebar
st.sidebar.markdown("---")
st.sidebar.header("💡 Key Insights")
st.sidebar.info("""
**Three Pillars Framework:**

- **Burden**: Case numbers, mortality rates, peak impacts
- **System Strain**: Hospital capacity, ICU utilization  
- **Government Response**: Restrictions, testing, vaccination
""")

st.sidebar.markdown("---")
st.sidebar.caption("Built following the step-by-step assignment structure")
