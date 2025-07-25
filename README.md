
# GroupChat Analyzer

**Live Demo:** [https://groupchatanalyzer.streamlit.app/](https://groupchatanalyzer.streamlit.app/)

GroupChat Analyzer is a web application built with Streamlit to analyze and visualize data from group chat exports. The app allows users to upload chat data, visualize message statistics, analyze trends, and export the analyzed data.

## Tech Stack

- **Python:** The primary programming language used for the application.
- **Streamlit:** Framework for creating interactive web applications with Python.
- **Pandas:** Data manipulation and analysis library.
- **Matplotlib:** Plotting library for creating static, animated, and interactive visualizations.
- **Seaborn:** Statistical data visualization library based on Matplotlib.
- **NLTK (Natural Language Toolkit):** Library for working with human language data (text processing).
- **WordCloud:** Tool for generating word clouds.

## Features

- **Upload Chat Data:** Users can upload chat export files in text format.
- **Message Statistics:** View total messages, words, media shared, and links shared.
- **Timeline Analysis:** Visualize monthly and daily timelines of messages.
- **Activity Maps:** Analyze activity by day of the week and month.
- **Heatmaps:** Display weekly activity heatmaps.
- **User Analysis:** Identify the most active users and visualize their activities.
- **Word Cloud:** Generate and display a word cloud from chat messages.
- **Most Common Words:** List and visualize the most common words used in the chat.
- **Emoji Analysis:** Analyze and visualize the usage of emojis.
- **Export Data:** Option to download the analyzed data as a CSV file.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/groupchat-analyzer.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd groupchat-analyzer
   ```

3. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

5. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Streamlit app:**

   ```bash
   streamlit run app.py
   ```

2. **Open the app in your browser:** Navigate to `http://localhost:8501` to access the GroupChat Analyzer.

3. **Upload a chat file:** Use the file uploader in the sidebar to upload your group chat export file.

4. **Analyze Data:** Click the "Show Analysis" button to view various visualizations and statistics.

5. **Export Data:** Use the "Export Data" button to download the analyzed data as a CSV file.
