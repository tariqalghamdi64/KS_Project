import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import chi2_contingency, f_oneway
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="🚀 Kickstarter Analytics Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stApp {
        background-color: #0e1117;
    }
    .css-1d391kg {
        background-color: #262730;
    }
    .stSelectbox > div > div {
        background-color: #262730;
        color: #fafafa;
    }
    .stSlider > div > div > div > div {
        background-color: #262730;
    }
    .metric-card {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #4a4a4a;
        margin: 0.5rem 0;
    }
    .success-metric {
        border-left: 4px solid #00ff88;
    }
    .warning-metric {
        border-left: 4px solid #ffaa00;
    }
    .info-metric {
        border-left: 4px solid #0088ff;
    }
    .danger-metric {
        border-left: 4px solid #ff4444;
    }
    h1, h2, h3 {
        color: #fafafa !important;
    }
    .stMarkdown {
        color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🚀 Kickstarter Analytics Dashboard")
st.markdown("### 📊 Comprehensive Analysis of Crowdfunding Projects")
st.markdown("---")

# Load data with progress indicator
@st.cache_data
def load_data():
    with st.spinner("🔄 Loading Kickstarter data from Google Drive..."):
        try:
            file_id = "1MwNbPlwLvO1J_K-rIQoztXi5ZuhhzQfL"
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
            df = pd.read_csv(url)
            st.success("✅ Data loaded successfully!")
            return df
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return None

# Load the data
kt_df = load_data()

if kt_df is not None:
    # Data preprocessing
    with st.spinner("🔄 Processing data..."):
        # Convert launched to datetime
        kt_df['launched_dt'] = pd.to_datetime(kt_df['launched'], errors='coerce')
        kt_df['year'] = kt_df['launched_dt'].dt.year
        kt_df['month'] = kt_df['launched_dt'].dt.month
        
        # Calculate success rate
        success_rate = (kt_df['state'] == 'successful').mean() * 100
        
        # Calculate total pledged and goal
        total_pledged = kt_df['pledged'].sum()
        total_goal = kt_df['goal'].sum()
        funding_ratio = (total_pledged / total_goal) * 100 if total_goal > 0 else 0

    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Year filter
    years = sorted(kt_df['year'].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "📅 Select Years:",
        years,
        default=years[-3:] if len(years) >= 3 else years
    )
    
    # Category filter
    categories = sorted(kt_df['main_category'].unique())
    selected_categories = st.sidebar.multiselect(
        "📂 Select Categories:",
        categories,
        default=categories[:5] if len(categories) >= 5 else categories
    )
    
    # State filter
    states = sorted(kt_df['state'].unique())
    selected_states = st.sidebar.multiselect(
        "🎯 Select Project States:",
        states,
        default=states
    )
    
    # Apply filters
    filtered_df = kt_df[
        (kt_df['year'].isin(selected_years) if selected_years else True) &
        (kt_df['main_category'].isin(selected_categories) if selected_categories else True) &
        (kt_df['state'].isin(selected_states) if selected_states else True)
    ]

    # Key Metrics Section
    st.header("📈 Key Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card success-metric">
            <h3>🎯 Success Rate</h3>
            <h2>{:.1f}%</h2>
        </div>
        """.format(success_rate), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card info-metric">
            <h3>📊 Total Projects</h3>
            <h2>{:,}</h2>
        </div>
        """.format(len(kt_df)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card warning-metric">
            <h3>💰 Total Pledged</h3>
            <h2>${:,.0f}M</h2>
        </div>
        """.format(total_pledged/1000000), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card danger-metric">
            <h3>🎯 Funding Ratio</h3>
            <h2>{:.1f}%</h2>
        </div>
        """.format(funding_ratio), unsafe_allow_html=True)

    st.markdown("---")

    # Charts Section
    st.header("📊 Interactive Visualizations")
    
    # Tab layout for different chart types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Project Success Analysis", 
        "📈 Trends Over Time", 
        "💰 Financial Analysis",
        "🌍 Geographic & Category Analysis",
        "📊 Statistical Insights"
    ])

    with tab1:
        st.subheader("🎯 Project Success Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Success rate by category
            success_by_cat = filtered_df.groupby('main_category')['state'].apply(
                lambda x: (x == 'successful').mean() * 100
            ).sort_values(ascending=False)
            
            fig = px.bar(
                x=success_by_cat.index,
                y=success_by_cat.values,
                title="🎯 Success Rate by Category",
                labels={'x': 'Category', 'y': 'Success Rate (%)'},
                color=success_by_cat.values,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **💡 Interpretation:** This chart shows which project categories have the highest success rates. 
            Categories with higher success rates are generally more appealing to backers or have better 
            project creators who know how to market their ideas effectively.
            """)

        with col2:
            # Project state distribution
            state_counts = filtered_df['state'].value_counts()
            fig = px.pie(
                values=state_counts.values,
                names=state_counts.index,
                title="📊 Project State Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **💡 Interpretation:** This pie chart shows the overall distribution of project outcomes. 
            It helps understand what percentage of projects succeed, fail, or get canceled, giving 
            a realistic view of crowdfunding success rates.
            """)

    with tab2:
        st.subheader("📈 Trends Over Time")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Projects per year
            projects_per_year = filtered_df['year'].value_counts().sort_index()
            fig = px.line(
                x=projects_per_year.index,
                y=projects_per_year.values,
                title="📈 Projects Launched per Year",
                labels={'x': 'Year', 'y': 'Number of Projects'},
                markers=True
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Success rate per year
            yearly_success = filtered_df.groupby('year')['state'].apply(
                lambda x: (x == 'successful').mean() * 100
            )
            fig = px.line(
                x=yearly_success.index,
                y=yearly_success.values,
                title="🎯 Success Rate Trend Over Years",
                labels={'x': 'Year', 'y': 'Success Rate (%)'},
                markers=True
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        # Monthly trends
        st.subheader("📅 Monthly Patterns")
        col1, col2 = st.columns(2)
        
        with col1:
            projects_per_month = filtered_df['month'].value_counts().sort_index()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            fig = px.bar(
                x=month_names,
                y=projects_per_month.reindex(range(1, 13), fill_value=0),
                title="📊 Projects by Month",
                labels={'x': 'Month', 'y': 'Number of Projects'}
            )
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            monthly_success = filtered_df.groupby('month')['state'].apply(
                lambda x: (x == 'successful').mean() * 100
            )
            fig = px.bar(
                x=month_names,
                y=monthly_success.reindex(range(1, 13), fill_value=0),
                title="🎯 Success Rate by Month",
                labels={'x': 'Month', 'y': 'Success Rate (%)'}
            )
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("💰 Financial Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pledged vs Goal scatter plot
            fig = px.scatter(
                filtered_df,
                x='goal',
                y='pledged',
                color='state',
                title="💰 Pledged vs Goal Amount",
                labels={'goal': 'Goal Amount (USD)', 'pledged': 'Amount Pledged (USD)'},
                log_x=True,
                log_y=True
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **💡 Interpretation:** This scatter plot shows the relationship between funding goals and 
            actual amounts pledged. Projects above the diagonal line exceeded their goals, while those 
            below fell short. The log scale helps visualize the wide range of funding amounts.
            """)

        with col2:
            # Backers vs Pledged
            fig = px.scatter(
                filtered_df,
                x='backers',
                y='pledged',
                color='state',
                title="👥 Backers vs Pledged Amount",
                labels={'backers': 'Number of Backers', 'pledged': 'Amount Pledged (USD)'},
                log_x=True,
                log_y=True
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **💡 Interpretation:** This chart shows how the number of backers relates to the total 
            amount pledged. Generally, more backers mean more money, but some projects get large 
            contributions from fewer backers.
            """)

        # Financial metrics by category
        st.subheader("💵 Financial Performance by Category")
        financial_by_cat = filtered_df.groupby('main_category').agg({
            'goal': 'mean',
            'pledged': 'mean',
            'backers': 'mean'
        }).round(2)
        
        fig = px.bar(
            financial_by_cat,
            title="💰 Average Financial Metrics by Category",
            labels={'value': 'Amount (USD)', 'variable': 'Metric'}
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("🌍 Geographic & Category Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top countries
            country_counts = filtered_df['country'].value_counts().head(10)
            fig = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                title="🌍 Top 10 Countries by Project Count",
                labels={'x': 'Country', 'y': 'Number of Projects'}
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Success rate by country
            success_by_country = filtered_df.groupby('country')['state'].apply(
                lambda x: (x == 'successful').mean() * 100
            ).sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=success_by_country.index,
                y=success_by_country.values,
                title="🎯 Success Rate by Country (Top 10)",
                labels={'x': 'Country', 'y': 'Success Rate (%)'}
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        # Category popularity
        st.subheader("📂 Category Analysis")
        category_analysis = filtered_df.groupby('main_category').agg({
            'state': 'count',
            'goal': 'mean',
            'pledged': 'mean'
        }).round(2)
        category_analysis.columns = ['Project Count', 'Avg Goal', 'Avg Pledged']
        
        fig = px.scatter(
            category_analysis,
            x='Project Count',
            y='Avg Pledged',
            size='Avg Goal',
            title="📊 Category Overview: Projects vs Funding",
            labels={'Project Count': 'Number of Projects', 'Avg Pledged': 'Average Amount Pledged (USD)'}
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.subheader("📊 Statistical Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plots for numerical variables
            fig = px.box(
                filtered_df,
                x='state',
                y='goal',
                title="📦 Funding Goal Distribution by State",
                labels={'state': 'Project State', 'goal': 'Funding Goal (USD)'}
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.box(
                filtered_df,
                x='state',
                y='backers',
                title="📦 Number of Backers by State",
                labels={'state': 'Project State', 'backers': 'Number of Backers'}
            )
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig, use_container_width=True)

        # Correlation analysis
        st.subheader("🔗 Correlation Analysis")
        
        # Calculate correlations for numerical variables
        numerical_cols = ['goal', 'pledged', 'backers']
        correlation_matrix = filtered_df[numerical_cols].corr()
        
        fig = px.imshow(
            correlation_matrix,
            title="🔗 Correlation Matrix of Numerical Variables",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **💡 Interpretation:** The correlation matrix shows how different numerical variables relate to each other. 
        Values closer to 1 indicate strong positive correlation, while values closer to -1 indicate strong 
        negative correlation. Values near 0 suggest little to no relationship.
        """)

    # Summary and insights
    st.markdown("---")
    st.header("💡 Key Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Success Factors:
        - **Category matters**: Some categories have much higher success rates
        - **Timing is key**: Certain months show better success rates
        - **Goal setting**: Realistic funding goals increase success chances
        - **Geographic location**: Some countries have higher success rates
        
        ### 📈 Trends:
        - Kickstarter popularity has grown over the years
        - Success rates vary significantly by category
        - Seasonal patterns exist in project launches
        """)
    
    with col2:
        st.markdown("""
        ### 💰 Financial Insights:
        - Most projects set goals under $10,000
        - Successful projects often exceed their goals
        - More backers generally mean more funding
        - Some categories require higher funding goals
        
        ### 🌟 Recommendations:
        - Choose categories with proven success rates
        - Launch during peak months for your category
        - Set realistic funding goals
        - Focus on building a strong backer community
        """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        🚀 <strong>Kickstarter Analytics Dashboard</strong> | 
        📊 Data-driven insights for crowdfunding success | 
        💡 Built with Streamlit & Plotly
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("❌ Failed to load data. Please check your internet connection and try again.") 