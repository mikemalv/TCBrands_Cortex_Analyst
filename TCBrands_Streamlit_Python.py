import _snowflake
import json
import streamlit as st
import time
from snowflake.snowpark.context import get_active_session

# Configure page and sidebar
st.set_page_config(
    page_title="Callaway Ai",
    page_icon="⛳",  # Can use emoji
    layout="wide"
)

# Debug mode (set to True to see session state)
debug = True

# Custom CSS (same as before)
st.markdown("""
    <style>
    /* Light mode styles */
    .stApp {
        color: black;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgb(5, 145, 254);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stDateInput label {
        color: white !important;
    }
    
    /* Button styling for both modes */
    .stButton > button {
        background-color: #003087 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
    }
    .stButton > button:hover {
        background-color: #004087 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Dark mode specific adjustments */
    [data-testid="stAppViewContainer"][data-theme="dark"] {
        color: white;
        background-color: #0E1117;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .streamlit-expanderContent {
        background-color: #262730 !important;
        color: white !important;
    }
    
    /* Light mode specific adjustments */
    [data-testid="stAppViewContainer"][data-theme="light"] {
        color: black;
        background-color: white;
    }
    
    [data-testid="stAppViewContainer"][data-theme="light"] .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
    }

    /* Headers styling for both modes */
    [data-testid="stAppViewContainer"][data-theme="light"] h1,
    [data-testid="stAppViewContainer"][data-theme="light"] h2,
    [data-testid="stAppViewContainer"][data-theme="light"] h3,
    [data-testid="stAppViewContainer"][data-theme="light"] h4,
    [data-testid="stAppViewContainer"][data-theme="light"] h5,
    [data-testid="stAppViewContainer"][data-theme="light"] h6 {
        color: black !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] h1,
    [data-testid="stAppViewContainer"][data-theme="dark"] h2,
    [data-testid="stAppViewContainer"][data-theme="dark"] h3,
    [data-testid="stAppViewContainer"][data-theme="dark"] h4,
    [data-testid="stAppViewContainer"][data-theme="dark"] h5,
    [data-testid="stAppViewContainer"][data-theme="dark"] h6 {
        color: white !important;
    }
    
    /* For Question Suggestions */
    .stButton > button {
        margin-bottom: 10px !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-align: left !important;
        padding: 10px 15px !important;
    }
    
    /* Hover effect for suggestion buttons */
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    /* Style for the welcome message */
    [data-testid="stMarkdown"] > div:first-child {
        font-size: 1.1em !important;
        margin-bottom: 20px !important;
    }
    
    
    
    
    
    </style>
""", unsafe_allow_html=True)

def refresh_snowflake_connection():
    """Refresh Snowflake connection and clear cached data"""
    try:
        # Clear session state
        for key in list(st.session_state.keys()):
            if key != 'theme_selector':  # Preserve theme selection
                del st.session_state[key]
        
        # Get fresh Snowflake session
        session = get_active_session()
        if session:
            session.clear_queries()  # Clear any cached queries
        
        # Reinitialize messages
        st.session_state.messages = []
        st.session_state.suggestions = []
        st.session_state.active_suggestion = None
        
        st.success("✅ Data connection refreshed successfully!")
        time.sleep(1)  # Give user time to see success message
        st.rerun()  # Rerun the app to reflect changes
        
    except Exception as e:
        st.error(f"❌ Error refreshing data: {str(e)}")

# Sidebar
with st.sidebar:
    # Move logo to top of sidebar
    col1, col2, col3 = st.columns([1, 2, 1])  # For center alignment
    with col2:
        st.image("https://swingfit.net/wp-content/uploads/2022/09/Callaway-Golf-Logo-596x343-1.png", width=150)
    st.divider()
    
    st.title("Select Option")
    selected_model = st.sidebar.selectbox(
    "Select Your Model:",
        (
            'snowflake-arctic', 'mistral-large', 'mistral-large2', 'reka-flash', 
            'reka-core', 'jamba-instruct', 'jamba-1.5-mini', 'jamba-1.5-large', 
            'mixtral-8x7b', 'llama2-70b-chat', 'llama3-8b', 'llama3-70b', 
            'llama3.1-8b', 'llama3.1-70b', 'llama3.1-405b', 'llama3.2-1b', 
            'llama3.2-3b', 'mistral-7b', 'gemma-7b'
        ),
        key="model_name"
    )

    analysis_type = st.selectbox(
        "Choose Analysis Type",
        ["Sales Analysis", "Option A", "Option B"]
    )
    date_range = st.date_input("Select Date Range", [])
    
    # Add Start Over and Refresh buttons
    if st.button("Start Over"):
        try:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Session cleared successfully!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing session state: {str(e)}")
    
    if st.button("Refresh Data", key="refresh_button"):
        refresh_snowflake_connection()
    
    # Add theme selector at bottom of sidebar
    st.divider()
    #theme = st.selectbox(
    #    "Choose Theme",
    #    ["Light", "Dark"],
    #    key="theme_selector"
    #)
    
    # Debug session state viewer
    if debug:
        with st.expander("Session State"):
            st.write(st.session_state)

# Constants
DATABASE    = "TCBRANDS"
SCHEMA      = "PUBLIC"
STAGE       = "TCBRANDS_STAGE"
FILE        = "TCBrands_Analyst_Model_v2.yaml"

# Main content area
# Remove logo from main area since it's now in sidebar
st.divider()
st.subheader("⛳ Callaway Ai")
st.divider()

def send_message(prompt: str) -> dict:
    """Calls the REST API and returns the response."""
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "semantic_model_file": f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}",
    }
    resp = _snowflake.send_snow_api_request(
        "POST",
        f"/api/v2/cortex/analyst/message",
        {},
        {},
        request_body,
        {},
        30000,
    )
    if resp["status"] < 400:
        return json.loads(resp["content"])
    else:
        raise Exception(
            f"Failed request with status {resp['status']}: {resp}"
        )

# Add this after the initializations but before the main chat loop:

def initialize_chat():
    """Initialize chat with welcome message and relevant suggestions"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.suggestions = []
        st.session_state.active_suggestion = None
        
        # Add initial welcome message with data-relevant suggestions
        welcome_message = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "👋 Welcome! I can help analyze your Callaway brands performance data. Here are some relevant questions you can ask:"
                },
                {
                    "type": "suggestions",
                    "suggestions": [
                        "Compare actual vs planned net sales across brands",
                        "Show me operating income by region",
                        "Which brand has the highest standard margin?",
                        "Compare EMEA vs LATAM performance",
                        "What are the sales trends for TravisMathew products?",
                        "Show me Big Bertha Driver performance across regions"
                    ]
                }
            ]
        }
        
        st.session_state.messages.append(welcome_message)

# Replace your existing initialization block with this:
if "messages" not in st.session_state:
    initialize_chat()

# The rest of your display logic remains the same, but add this right after your main content headers:
if len(st.session_state.messages) == 0:
    initialize_chat()

# Modify your display_content function to handle the welcome message:
def display_content(content: list, message_index: int = None) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            # Add some spacing for better appearance
            st.markdown("<br>", unsafe_allow_html=True)
            # Use columns for better suggestion layout
            cols = st.columns([1, 3, 1])
            with cols[1]:
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(
                        suggestion, 
                        key=f"{message_index}_{suggestion_index}",
                        use_container_width=True
                    ):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Running SQL..."):
                    session = get_active_session()
                    df = session.sql(item["statement"]).to_pandas()
                    if len(df.index) > 1:
                        data_tab, line_tab, bar_tab = st.tabs(
                            ["Data", "Line Chart", "Bar Chart"]
                        )
                        data_tab.dataframe(df)
                        if len(df.columns) > 1:
                            df = df.set_index(df.columns[0])
                        with line_tab:
                            st.line_chart(df)
                        with bar_tab:
                            st.bar_chart(df)
                    else:
                        st.dataframe(df)
                        
def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("user", avatar="🏌️"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            content = response["message"]["content"]
            display_content(content=content)
    st.session_state.messages.append({"role": "assistant", "content": content})

def display_content(content: list, message_index: int = None) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Running SQL..."):
                    session = get_active_session()
                    df = session.sql(item["statement"]).to_pandas()
                    if len(df.index) > 1:
                        data_tab, line_tab, bar_tab = st.tabs(
                            ["Data", "Line Chart", "Bar Chart"]
                        )
                        data_tab.dataframe(df)
                        if len(df.columns) > 1:
                            df = df.set_index(df.columns[0])
                        with line_tab:
                            st.line_chart(df)
                        with bar_tab:
                            st.bar_chart(df)
                    else:
                        st.dataframe(df)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.active_suggestion = None

for message_index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"], avatar="🏌️"):
        display_content(content=message["content"], message_index=message_index)

if user_input := st.chat_input("What questions do you have?"):
    process_message(prompt=user_input)

if st.session_state.active_suggestion:
    process_message(prompt=st.session_state.active_suggestion)
    st.session_state.active_suggestion = None