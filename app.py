import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="WhatsApp GroupChat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def create_download_link(df, filename):
    """Create a download link for the DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
    return href

def main():
    st.markdown('<h1 class="main-header">💬 WhatsApp GroupChat Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📊 Analysis Options")
    st.sidebar.markdown("---")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Choose a WhatsApp chat file", 
        type=['txt'],
        help="Export your WhatsApp chat as a .txt file and upload it here"
    )
    
    if uploaded_file is not None:
        try:
            # Read and process the file
            with st.spinner("Processing chat data..."):
                bytes_data = uploaded_file.getvalue()
                data = bytes_data.decode("utf-8")
                df = preprocessor.preprocess(data)
            
            if df.empty:
                st.error("❌ No valid chat data found. Please check your file format.")
                return
            
            # Get user list
            user_list = df['user'].unique().tolist()
            if 'group_notification' in user_list:
                user_list.remove('group_notification')
            user_list.sort()
            user_list.insert(0, "Overall")
            
            # User selection
            selected_user = st.sidebar.selectbox(
                "👤 Select User for Analysis",
                user_list,
                help="Choose a specific user or 'Overall' for group analysis"
            )
            
            # Analysis options
            st.sidebar.markdown("---")
            st.sidebar.subheader("📈 Analysis Options")
            
            show_basic_stats = st.sidebar.checkbox("Basic Statistics", True)
            show_timeline = st.sidebar.checkbox("Timeline Analysis", True)
            show_activity = st.sidebar.checkbox("Activity Maps", True)
            show_wordcloud = st.sidebar.checkbox("Word Cloud", True)
            show_sentiment = st.sidebar.checkbox("Sentiment Analysis", True)
            show_emoji = st.sidebar.checkbox("Emoji Analysis", True)
            
            # Analysis button
            if st.sidebar.button("🔍 Show Analysis", type="primary"):
                analyze_chat(df, selected_user, {
                    'basic_stats': show_basic_stats,
                    'timeline': show_timeline,
                    'activity': show_activity,
                    'wordcloud': show_wordcloud,
                    'sentiment': show_sentiment,
                    'emoji': show_emoji
                })
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Please make sure you've uploaded a valid WhatsApp chat export file.")
    
    else:
        # Instructions
        st.info("👆 Please upload a WhatsApp chat file to begin analysis")
        
        with st.expander("📖 How to export WhatsApp chat"):
            st.markdown("""
            1. Open WhatsApp on your phone
            2. Go to the group chat you want to analyze
            3. Tap on the group name at the top
            4. Scroll down and tap "Export Chat"
            5. Choose "Without Media"
            6. Share the file and download it to your computer
            7. Upload the .txt file here
            """)

def analyze_chat(df, selected_user, options):
    """Main analysis function"""
    
    # Basic Statistics
    if options['basic_stats']:
        st.header("📊 Basic Statistics")
        
        try:
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Messages", f"{num_messages:,}")
            with col2:
                st.metric("Total Words", f"{words:,}")
            with col3:
                st.metric("Media Shared", f"{num_media_messages:,}")
            with col4:
                st.metric("Links Shared", f"{num_links:,}")
                
        except Exception as e:
            st.error(f"Error calculating basic stats: {str(e)}")
    
    # Timeline Analysis
    if options['timeline']:
        st.header("📈 Timeline Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Timeline")
            try:
                timeline = helper.monthly_timeline(selected_user, df)
                if not timeline.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(timeline['time'], timeline['message'], color='green', linewidth=2)
                    ax.set_xlabel('Month')
                    ax.set_ylabel('Number of Messages')
                    ax.set_title('Messages Over Time (Monthly)')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No data available for monthly timeline")
            except Exception as e:
                st.error(f"Error creating monthly timeline: {str(e)}")
        
        with col2:
            st.subheader("Daily Timeline")
            try:
                daily_timeline = helper.daily_timeline(selected_user, df)
                if not daily_timeline.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='blue', linewidth=1)
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Number of Messages')
                    ax.set_title('Messages Over Time (Daily)')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No data available for daily timeline")
            except Exception as e:
                st.error(f"Error creating daily timeline: {str(e)}")
    
    # Activity Maps
    if options['activity']:
        st.header("🗓️ Activity Maps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Most Busy Day")
            try:
                busy_day = helper.week_activity_map(selected_user, df)
                if not busy_day.empty:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    ax.set_xlabel('Day of Week')
                    ax.set_ylabel('Number of Messages')
                    ax.set_title('Activity by Day of Week')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No data available for day activity")
            except Exception as e:
                st.error(f"Error creating day activity map: {str(e)}")
        
        with col2:
            st.subheader("Most Busy Month")
            try:
                busy_month = helper.month_activity_map(selected_user, df)
                if not busy_month.empty:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    ax.set_xlabel('Month')
                    ax.set_ylabel('Number of Messages')
                    ax.set_title('Activity by Month')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No data available for month activity")
            except Exception as e:
                st.error(f"Error creating month activity map: {str(e)}")
        
        # Heatmap
        st.subheader("Weekly Activity Heatmap")
        try:
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if not user_heatmap.empty:
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(user_heatmap, annot=True, cmap='YlOrRd', fmt='g', ax=ax)
                ax.set_title('Activity Heatmap (Day vs Time Period)')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No data available for activity heatmap")
        except Exception as e:
            st.error(f"Error creating activity heatmap: {str(e)}")
    
    # Most Busy Users (only for Overall)
    if selected_user == 'Overall':
        st.header("👥 Most Active Users")
        try:
            x, new_df = helper.most_busy_users(df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.bar(x.index, x.values, color='red')
                ax.set_xlabel('Users')
                ax.set_ylabel('Number of Messages')
                ax.set_title('Most Active Users')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                st.subheader("User Activity Percentage")
                st.dataframe(new_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error analyzing user activity: {str(e)}")
    
    # Word Cloud
    if options['wordcloud']:
        st.header("☁️ Word Cloud")
        try:
            df_wc = helper.create_wordcloud(selected_user, df)
            if df_wc is not None:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.imshow(df_wc, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Word Cloud of Messages')
                st.pyplot(fig)
                
                # Most common words
                most_common_df = helper.most_common_words(selected_user, df)
                if not most_common_df.empty:
                    st.subheader("Most Common Words")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.barh(most_common_df[0], most_common_df[1])
                    ax.set_xlabel('Frequency')
                    ax.set_title('Top 20 Most Common Words')
                    plt.tight_layout()
                    st.pyplot(fig)
            else:
                st.info("No words available to generate word cloud")
        except Exception as e:
            st.error(f"Error creating word cloud: {str(e)}")
    
    # Emoji Analysis
    if options['emoji']:
        st.header("😊 Emoji Analysis")
        try:
            emoji_df = helper.emoji_helper(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Top Emojis")
                    st.dataframe(emoji_df.head(10), use_container_width=True)
                
                with col2:
                    st.subheader("Emoji Distribution")
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.pie(emoji_df[1].head(10), labels=emoji_df[0].head(10), autopct="%0.1f%%")
                    ax.set_title('Top 10 Emojis Distribution')
                    st.pyplot(fig)
            else:
                st.info("No emojis found in the selected messages")
        except Exception as e:
            st.error(f"Error analyzing emojis: {str(e)}")
    
    # Sentiment Analysis
    if options['sentiment']:
        st.header("🎭 Sentiment Analysis")
        try:
            with st.spinner("Analyzing sentiment..."):
                df['sentiment'] = df['message'].apply(helper.analyze_sentiment_wrapper)
                
                if selected_user != 'Overall':
                    sentiment_df = df[df['user'] == selected_user]
                else:
                    sentiment_df = df[df['user'] != 'group_notification']
                
                sentiment_counts = sentiment_df['sentiment'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig, ax = plt.subplots(figsize=(8, 8))
                    colors = ['green', 'red', 'gray']
                    ax.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct="%1.1f%%", 
                           startangle=90, colors=colors)
                    ax.set_title('Sentiment Distribution')
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("Sentiment Statistics")
                    st.dataframe(sentiment_counts.to_frame('Count'), use_container_width=True)
                    
                    # Calculate sentiment percentages
                    total_messages = sentiment_counts.sum()
                    for sentiment, count in sentiment_counts.items():
                        percentage = (count / total_messages) * 100
                        st.metric(f"{sentiment} Messages", f"{count:,} ({percentage:.1f}%)")
                        
        except Exception as e:
            st.error(f"Error analyzing sentiment: {str(e)}")
    
    # Export functionality
    st.header("💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Full Dataset"):
            filename = f"whatsapp_analysis_{selected_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            st.markdown(create_download_link(df, filename), unsafe_allow_html=True)
            st.success("✅ Download link generated!")
    
    with col2:
        if st.button("📊 Export Summary Stats"):
            try:
                summary_data = {
                    'Metric': ['Total Messages', 'Total Words', 'Media Shared', 'Links Shared'],
                    'Value': [
                        helper.fetch_stats(selected_user, df)[0],
                        helper.fetch_stats(selected_user, df)[1],
                        helper.fetch_stats(selected_user, df)[2],
                        helper.fetch_stats(selected_user, df)[3]
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                filename = f"whatsapp_summary_{selected_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                st.markdown(create_download_link(summary_df, filename), unsafe_allow_html=True)
                st.success("✅ Summary download link generated!")
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")

if __name__ == "__main__":
    main()