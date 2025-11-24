# app.py
# Smart Habit & Productivity Tracker - Clean Professional Edition
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO

from config import ENABLE_AI, GEMINI_MODEL, GEMINI_API_KEY, ENABLE_PDF_EXPORT
from database import create_tables, insert_log, fetch_logs, export_csv, update_log, fetch_log_by_id
from data_processing import get_dataframe, weekly_summary, monthly_summary, activity_heatmap_data, compute_productivity_score
from ml_utils import get_clusters, train_regression, predict_next
from recommendations import get_gemini_reco
import export_utils

# Configuration
st.set_page_config(
    page_title="Smart Habit & Productivity Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()

# Helper Functions
def refresh_df():
    return get_dataframe()

def create_metric_card(label, value, delta=None, help_text=None):
    st.metric(label=label, value=value, delta=delta, help=help_text)

def create_gauge_chart(value, title, max_value=10):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': "#4F46E5"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, max_value*0.33], 'color': '#FEF3C7'},
                {'range': [max_value*0.33, max_value*0.66], 'color': '#DDD6FE'},
                {'range': [max_value*0.66, max_value], 'color': '#D1FAE5'}
            ],
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# Sidebar
with st.sidebar:
    st.title("Habit Tracker")
    st.caption("Personal Productivity Dashboard")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["Dashboard", "Log Activity", "Edit Logs", "Analytics", "AI Insights", "Export"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    df = refresh_df()
    if not df.empty:
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Logs", len(df))
            st.metric("Avg Sleep", f"{df['sleep_hours'].mean():.1f}h")
        with col2:
            st.metric("Avg Study", f"{df['study_hours'].mean():.1f}h")
            st.metric("Avg Score", f"{df['productivity_score'].mean():.1f}")
    
    st.divider()
    st.caption("Built with Streamlit + ML")
    st.caption("Version 2.0 Professional")

# Dashboard Page
if page == "Dashboard":
    st.title("Smart Habit & Productivity Dashboard")
    st.caption("Transform your daily habits into measurable success")
    
    df = refresh_df()
    
    if df.empty:
        st.info("Welcome! Start by logging your first activity in the Log Activity page.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("Track Daily Habits\n\nLog sleep, study hours, activities, and more")
        with col2:
            st.info("Visualize Progress\n\nSee trends and patterns in beautiful charts")
        with col3:
            st.info("Get AI Insights\n\nReceive personalized recommendations")
    else:
        # Key Metrics
        st.subheader("Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_sleep = df['sleep_hours'].mean()
            sleep_delta = df['sleep_hours'].iloc[-1] - avg_sleep if len(df) > 1 else None
            create_metric_card("Average Sleep", f"{avg_sleep:.1f}h", 
                             delta=f"{sleep_delta:+.1f}h" if sleep_delta else None)
        
        with col2:
            avg_study = df['study_hours'].mean()
            study_delta = df['study_hours'].iloc[-1] - avg_study if len(df) > 1 else None
            create_metric_card("Average Study", f"{avg_study:.1f}h",
                             delta=f"{study_delta:+.1f}h" if study_delta else None)
        
        with col3:
            create_metric_card("Total Logs", len(df))
        
        with col4:
            avg_prod = df['productivity_score'].mean()
            prod_delta = df['productivity_score'].iloc[-1] - avg_prod if len(df) > 1 else None
            create_metric_card("Productivity", f"{avg_prod:.1f}",
                             delta=f"{prod_delta:+.1f}" if prod_delta else None)
        
        st.divider()
        
        # Trend Charts
        st.subheader("7-Day Performance Trends")
        
        tab1, tab2, tab3 = st.tabs(["Sleep & Study", "Productivity Score", "Recent Activity"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                recent_df = df.tail(7)
                fig_sleep = go.Figure()
                fig_sleep.add_trace(go.Scatter(
                    x=recent_df['date'],
                    y=recent_df['sleep_hours'],
                    mode='lines+markers',
                    line=dict(color='#4F46E5', width=3),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(79, 70, 229, 0.1)',
                    name='Sleep Hours'
                ))
                fig_sleep.update_layout(
                    title='Sleep Hours Trend',
                    xaxis_title="Date",
                    yaxis_title="Hours",
                    hovermode='x unified',
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig_sleep, use_container_width=True)
            
            with col2:
                fig_study = go.Figure()
                fig_study.add_trace(go.Bar(
                    x=recent_df['date'],
                    y=recent_df['study_hours'],
                    marker=dict(
                        color=recent_df['study_hours'],
                        colorscale='Purples',
                        showscale=False
                    ),
                    name='Study Hours'
                ))
                fig_study.update_layout(
                    title='Study Hours Trend',
                    xaxis_title="Date",
                    yaxis_title="Hours",
                    height=350,
                    showlegend=False
                )
                st.plotly_chart(fig_study, use_container_width=True)
        
        with tab2:
            recent_df = df.tail(7)
            
            fig_prod = go.Figure()
            fig_prod.add_trace(go.Scatter(
                x=recent_df['date'],
                y=recent_df['productivity_score'],
                mode='lines+markers',
                line=dict(color='#10B981', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)',
                name='Productivity'
            ))
            fig_prod.update_layout(
                title='Productivity Score Trend',
                xaxis_title="Date",
                yaxis_title="Score",
                hovermode='x unified',
                height=350,
                showlegend=False
            )
            st.plotly_chart(fig_prod, use_container_width=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                current_score = df['productivity_score'].iloc[-1]
                gauge_fig = create_gauge_chart(current_score, "Current Productivity Score")
                st.plotly_chart(gauge_fig, use_container_width=True)
        
        with tab3:
            st.subheader("Recent Activity Log")
            display_df = df.tail(7)[['date', 'sleep_hours', 'study_hours', 'activities', 'mood']].copy()
            display_df.columns = ['Date', 'Sleep', 'Study', 'Activities', 'Mood']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

# Log Activity Page
elif page == "Log Activity":
    st.title("Log Your Daily Activity")
    st.caption("Track your habits to build a better routine")
    
    with st.form("log_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Basic Info")
            date = st.date_input("Date", value=datetime.today())
            mode = st.selectbox("Role", ["student", "employee"])
            mood = st.selectbox("Mood", ["", "happy", "good", "ok", "tired", "stressed"])
        
        with col2:
            st.subheader("Time Tracking")
            sleep_hours = st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, 
                                         step=0.5, value=7.0)
            study_hours = st.number_input("Study/Work Hours", min_value=0.0, max_value=24.0,
                                         step=0.5, value=2.0)
            screen_time = st.number_input("Screen Time (min)", min_value=0, max_value=1440,
                                         step=15, value=0)
        
        with col3:
            st.subheader("Health")
            water = st.number_input("Water Intake (L)", min_value=0.0, max_value=10.0,
                                   step=0.1, value=0.0)
            steps = st.number_input("Steps", min_value=0, max_value=100000, step=500, value=0)
        
        st.divider()
        
        activities = st.text_area("Activities (comma separated)", 
                                 placeholder="e.g., reading, coding, exercise, meditation")
        notes = st.text_area("Notes (optional)", max_chars=500, 
                            placeholder="Any additional thoughts or observations")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Save Activity Log", 
                                             use_container_width=True, type="primary")
        
        if submitted:
            timestamp = datetime.now().isoformat()
            tmp = {
                "sleep_hours": sleep_hours,
                "study_hours": study_hours,
                "mood": mood
            }
            prod_score = compute_productivity_score(tmp)
            
            insert_log(str(date), sleep_hours, study_hours, activities, timestamp,
                      mood=mood, notes=notes, mode=mode, water_intake=water, steps=steps,
                      screen_time_minutes=screen_time, productivity_score=prod_score)
            
            st.success(f"Activity logged successfully! Productivity Score: {prod_score}")
            st.balloons()
            st.rerun()

# Edit Logs Page
elif page == "Edit Logs":
    st.title("Edit & Manage Activity Logs")
    st.caption("Review and update your historical data")
    
    df = refresh_df()
    
    if df.empty:
        st.warning("No logs available to edit. Start by creating your first log!")
    else:
        st.subheader("Your Activity History")
        
        display_df = df[["id", "date", "sleep_hours", "study_hours", "mood", 
                        "productivity_score"]].tail(50).copy()
        display_df.columns = ["ID", "Date", "Sleep", "Study", "Mood", "Score"]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Edit Selected Log")
        
        log_id = st.number_input("Select Log ID to Edit", 
                                min_value=int(df["id"].min()), 
                                max_value=int(df["id"].max()), 
                                value=int(df["id"].max()))
        
        selected = fetch_log_by_id(int(log_id))
        
        if selected:
            _, date, sleep_hours, study_hours, activities, mood, notes, mode, timestamp, \
            water_intake, steps, screen_time, prod_score = selected
            
            st.info(f"Editing log from: {date} | Current Score: {prod_score}")
            
            with st.form("edit_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_sleep = st.number_input("Sleep Hours", value=float(sleep_hours))
                    new_mood = st.selectbox("Mood", ["", "happy", "good", "ok", "tired", "stressed"],
                                           index=["", "happy", "good", "ok", "tired", "stressed"].index(mood) if mood else 0)
                
                with col2:
                    new_study = st.number_input("Study Hours", value=float(study_hours))
                    new_mode = st.selectbox("Mode", ["student", "employee"],
                                           index=0 if mode=="student" else 1)
                
                with col3:
                    new_activities = st.text_area("Activities", value=str(activities))
                
                new_notes = st.text_area("Notes", value=str(notes) if notes else "")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    save = st.form_submit_button("Update Log", use_container_width=True, type="primary")
                
                if save:
                    new_prod_score = compute_productivity_score({
                        "sleep_hours": new_sleep,
                        "study_hours": new_study,
                        "mood": new_mood
                    })
                    
                    update_log(int(log_id),
                             sleep_hours=new_sleep,
                             study_hours=new_study,
                             activities=new_activities,
                             mood=new_mood,
                             notes=new_notes,
                             mode=new_mode,
                             productivity_score=new_prod_score)
                    
                    st.success(f"Log updated successfully! New Score: {new_prod_score}")
                    st.rerun()
        else:
            st.error("Selected log not found.")

# Analytics Page
elif page == "Analytics":
    st.title("Advanced Data Analytics")
    st.caption("Deep insights powered by machine learning")
    
    df = refresh_df()
    
    if df.empty:
        st.warning("Need data to generate analytics. Start logging your activities!")
    else:
        # Summary Statistics
        st.subheader("Statistical Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card("Average Sleep", f"{df['sleep_hours'].mean():.2f}h")
            create_metric_card("Sleep StdDev", f"{df['sleep_hours'].std():.2f}h")
        
        with col2:
            create_metric_card("Average Study", f"{df['study_hours'].mean():.2f}h")
            create_metric_card("Study StdDev", f"{df['study_hours'].std():.2f}h")
        
        with col3:
            create_metric_card("Avg Productivity", f"{df['productivity_score'].mean():.2f}")
            create_metric_card("Score StdDev", f"{df['productivity_score'].std():.2f}")
        
        with col4:
            create_metric_card("Total Days", len(df))
            if len(df) > 1:
                date_range = (pd.to_datetime(df['date'].iloc[-1]) - pd.to_datetime(df['date'].iloc[0])).days
                create_metric_card("Date Range", f"{date_range} days")
        
        st.divider()
        
        # Detailed Charts
        tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Distributions", "Correlations", "ML Insights"])
        
        with tab1:
            st.subheader("Long-term Trends")
            
            # Combined trend chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df['sleep_hours'],
                mode='lines+markers', 
                name='Sleep Hours',
                line=dict(color='#4F46E5', width=2),
                marker=dict(size=6)
            ))
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df['study_hours'],
                mode='lines+markers', 
                name='Study Hours',
                line=dict(color='#7C3AED', width=2),
                marker=dict(size=6)
            ))
            fig.add_trace(go.Scatter(
                x=df['date'], 
                y=df['productivity_score'],
                mode='lines+markers', 
                name='Productivity',
                line=dict(color='#10B981', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="All Metrics Over Time",
                xaxis_title="Date",
                yaxis_title="Value",
                hovermode='x unified',
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Moving averages
            col1, col2 = st.columns(2)
            with col1:
                window = st.slider("Moving Average Window", 3, 14, 7)
            
            df['sleep_ma'] = df['sleep_hours'].rolling(window=window).mean()
            df['study_ma'] = df['study_hours'].rolling(window=window).mean()
            
            fig_ma = go.Figure()
            fig_ma.add_trace(go.Scatter(
                x=df['date'], 
                y=df['sleep_ma'],
                mode='lines', 
                name=f'{window}-Day Avg Sleep',
                line=dict(color='#4F46E5', width=3)
            ))
            fig_ma.add_trace(go.Scatter(
                x=df['date'], 
                y=df['study_ma'],
                mode='lines', 
                name=f'{window}-Day Avg Study',
                line=dict(color='#7C3AED', width=3)
            ))
            
            fig_ma.update_layout(
                title=f"{window}-Day Moving Average",
                xaxis_title="Date",
                yaxis_title="Hours",
                height=350
            )
            st.plotly_chart(fig_ma, use_container_width=True)
        
        with tab2:
            st.subheader("Distribution Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_sleep_dist = go.Figure()
                fig_sleep_dist.add_trace(go.Histogram(
                    x=df['sleep_hours'],
                    nbinsx=20,
                    marker=dict(color='#4F46E5', line=dict(color='white', width=1)),
                    name='Sleep Hours'
                ))
                fig_sleep_dist.update_layout(
                    title='Sleep Hours Distribution',
                    xaxis_title="Sleep Hours",
                    yaxis_title="Frequency",
                    showlegend=False
                )
                st.plotly_chart(fig_sleep_dist, use_container_width=True)
            
            with col2:
                fig_study_dist = go.Figure()
                fig_study_dist.add_trace(go.Histogram(
                    x=df['study_hours'],
                    nbinsx=20,
                    marker=dict(color='#7C3AED', line=dict(color='white', width=1)),
                    name='Study Hours'
                ))
                fig_study_dist.update_layout(
                    title='Study Hours Distribution',
                    xaxis_title="Study Hours",
                    yaxis_title="Frequency",
                    showlegend=False
                )
                st.plotly_chart(fig_study_dist, use_container_width=True)
            
            # Box plots and Mood Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(y=df['sleep_hours'], name='Sleep', marker_color='#4F46E5'))
                fig_box.add_trace(go.Box(y=df['study_hours'], name='Study', marker_color='#7C3AED'))
                fig_box.add_trace(go.Box(y=df['productivity_score'], name='Productivity', marker_color='#10B981'))
                fig_box.update_layout(
                    title='Value Distributions (Box Plot)',
                    yaxis_title="Value",
                    showlegend=True
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            with col2:
                if 'mood' in df.columns and df['mood'].notna().any():
                    mood_counts = df['mood'].value_counts()
                    fig_mood = go.Figure()
                    fig_mood.add_trace(go.Pie(
                        labels=mood_counts.index,
                        values=mood_counts.values,
                        hole=0.4,
                        marker=dict(colors=['#10B981', '#4F46E5', '#F59E0B', '#EF4444', '#7C3AED'])
                    ))
                    fig_mood.update_layout(
                        title='Mood Distribution',
                        showlegend=True
                    )
                    st.plotly_chart(fig_mood, use_container_width=True)
        
        with tab3:
            st.subheader("Correlation Analysis")
            
            # Scatter plot
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=df['sleep_hours'],
                y=df['study_hours'],
                mode='markers',
                marker=dict(
                    size=df['productivity_score']*3,
                    color=df['productivity_score'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Productivity")
                ),
                text=df['date'],
                hovertemplate='<b>Date:</b> %{text}<br><b>Sleep:</b> %{x}h<br><b>Study:</b> %{y}h<extra></extra>'
            ))
            fig_scatter.update_layout(
                title='Sleep vs Study Hours (sized by Productivity)',
                xaxis_title="Sleep Hours",
                yaxis_title="Study Hours",
                height=400
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Correlation heatmap
            corr_cols = ['sleep_hours', 'study_hours', 'productivity_score']
            if 'water_intake' in df.columns:
                corr_cols.append('water_intake')
            if 'steps' in df.columns:
                corr_cols.append('steps')
            
            corr_matrix = df[corr_cols].corr()
            
            fig_heatmap = go.Figure()
            fig_heatmap.add_trace(go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu_r',
                zmid=0,
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            ))
            fig_heatmap.update_layout(
                title='Correlation Heatmap',
                height=400
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with tab4:
            st.subheader("Machine Learning Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### K-Means Clustering")
                with st.spinner("Running clustering algorithm..."):
                    clusters, km_model, cluster_err = get_clusters(df)
                
                if cluster_err:
                    st.warning(f"{cluster_err}")
                else:
                    df_cluster = df.copy()
                    df_cluster['Cluster'] = clusters
                    
                    fig_cluster = go.Figure()
                    
                    for cluster in df_cluster['Cluster'].unique():
                        cluster_data = df_cluster[df_cluster['Cluster'] == cluster]
                        fig_cluster.add_trace(go.Scatter(
                            x=cluster_data['sleep_hours'],
                            y=cluster_data['study_hours'],
                            mode='markers',
                            name=cluster,
                            marker=dict(
                                size=cluster_data['productivity_score']*2,
                                line=dict(width=1, color='white')
                            ),
                            text=cluster_data['date'],
                            hovertemplate='<b>Date:</b> %{text}<br><b>Pattern:</b> ' + cluster + '<extra></extra>'
                        ))
                    
                    fig_cluster.update_layout(
                        title='Productivity Patterns (K-Means)',
                        xaxis_title="Sleep Hours",
                        yaxis_title="Study Hours",
                        height=400
                    )
                    st.plotly_chart(fig_cluster, use_container_width=True)
                    
                    st.info(f"Identified {len(set(clusters))} distinct patterns in your habits")
            
            with col2:
                st.markdown("##### Predictive Analytics")
                models, reg_err = train_regression(df)
                
                if reg_err:
                    st.warning(f"{reg_err}")
                else:
                    exp_sleep = st.slider("Expected sleep hours tomorrow",
                                        min_value=0.0, max_value=12.0,
                                        value=7.0, step=0.5)
                    
                    if st.button("Generate Prediction", use_container_width=True):
                        with st.spinner("Calculating prediction..."):
                            last_study = float(df["study_hours"].iloc[-1]) if len(df) > 0 else 0.0
                            predicted_study, predicted_score = predict_next(models, exp_sleep, 
                                                                           study_hours=last_study)
                        
                        if predicted_study is not None:
                            st.success("Prediction Complete")
                            st.metric("Predicted Study Hours", f"{predicted_study:.1f}h")
                            st.metric("Predicted Productivity", f"{predicted_score:.1f}")
                            
                            gauge_fig = create_gauge_chart(predicted_score, "Predicted Productivity")
                            st.plotly_chart(gauge_fig, use_container_width=True)
                        else:
                            st.error("Prediction failed")
            
            # Activity heatmap
            st.divider()
            st.subheader("Activity Heatmap")
            heat = activity_heatmap_data(df)
            if heat.empty:
                st.info("No activity keywords found")
            else:
                st.dataframe(heat, use_container_width=True)

# AI Insights Page
elif page == "AI Insights":
    st.title("AI-Powered Recommendations")
    st.caption("Get personalized insights powered by Gemini AI")
    
    df = refresh_df()
    
    if df.empty:
        st.warning("AI needs data to generate recommendations. Start logging activities first!")
    else:
        if not ENABLE_AI:
            st.info("AI features are disabled. Enable ENABLE_AI in config.py to use this feature.")
        else:
            st.info("AI will analyze your habit patterns and provide personalized recommendations")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Generate AI Recommendations", use_container_width=True, type="primary"):
                    with st.spinner("AI is analyzing your data... This may take a moment"):
                        try:
                            reco = get_gemini_reco(df, mode="student")
                            
                            st.success("AI Analysis Complete!")
                            st.divider()
                            
                            st.subheader("Your Personalized Recommendations")
                            st.markdown(reco)
                            
                        except Exception as e:
                            st.error(f"AI Error: {e}")
                            st.info("Please check your API configuration in config.py")

# Export Page
elif page == "Export":
    st.title("Export & Reports")
    st.caption("Download your data and generate comprehensive reports")
    
    df = refresh_df()
    
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### CSV Export")
        st.write("Download your complete activity log as CSV")
        
        if st.button("Export to CSV", use_container_width=True, type="primary"):
            path = export_csv("habit_export.csv")
            with open(path, "rb") as f:
                st.download_button(
                    label="Download CSV File",
                    data=f,
                    file_name=f"habit_tracker_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col2:
        st.markdown("#### PDF Report")
        if ENABLE_PDF_EXPORT:
            st.write("Generate a comprehensive PDF report")
            
            if st.button("Generate PDF", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Generating PDF report..."):
                        pdf_path = export_utils.generate_pdf_report("habit_report.pdf")
                    
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Download PDF Report",
                            data=f,
                            file_name=f"habit_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
        else:
            st.warning("PDF export disabled. Enable in config.py")
    
    st.divider()
    
    # Data preview
    st.subheader("Data Preview")
    
    if df.empty:
        st.info("No data available")
    else:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Date Range", f"{(pd.to_datetime(df['date'].iloc[-1]) - pd.to_datetime(df['date'].iloc[0])).days} days")
        with col3:
            st.metric("Avg Productivity", f"{df['productivity_score'].mean():.1f}")
        with col4:
            st.metric("Data Completeness", f"{(df.notna().sum().sum() / df.size * 100):.0f}%")
        
        st.divider()
        
        # Full data table
        display_df = df[['date', 'sleep_hours', 'study_hours', 'productivity_score', 
                        'mood', 'activities']].copy()
        display_df.columns = ['Date', 'Sleep (h)', 'Study (h)', 'Score', 'Mood', 'Activities']
        
        st.dataframe(
            display_df.tail(50),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "Sleep (h)": st.column_config.NumberColumn("Sleep (h)", format="%.1f"),
                "Study (h)": st.column_config.NumberColumn("Study (h)", format="%.1f"),
                "Score": st.column_config.NumberColumn("Score", format="%.1f"),
            }
        )

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.caption("Smart Habit & Productivity Tracker v2.0")
    st.caption("Built with Streamlit, Plotly & Machine Learning")
    st.caption("© 2024 Student Project | Professional Edition")