import streamlit as st
import requests
from datetime import datetime
import pytz
import re

# Set page config
st.set_page_config(
    page_title="Content Request Form",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def get_current_utc_datetime():
    """Get current UTC datetime in YYYY-MM-DD HH:MM:SS format"""
    utc_now = datetime.now(pytz.UTC)
    return utc_now.strftime("%Y-%m-%d %H:%M:%S")

def is_valid_email(email):
    """Simple regex check for email validation"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Hardcoded webhook URL
WEBHOOK_URL = "https://lernoai.live/webhook/6dcf5935-5ace-4816-9d6a-7045bd8b64b6"

st.title("📝 Content Request Form")

# Main webhook form
with st.form("content_request_form"):
    st.subheader("📝 Content Request Parameters")

    # Topic/Title
    topic_title = st.text_input(
        "Topic/Title",
        placeholder="Enter the content topic or title",
        help="Main topic or title for the content"
    )

    # Primary Keyword
    primary_keyword = st.text_input(
        "Primary Keyword",
        placeholder="Enter the primary SEO keyword",
        help="Main keyword to focus on for SEO optimization"
    )
    
    # Email
    email = st.text_input(
        "Your Email Address",
        placeholder="Enter your email for notifications",
        help="The email address to receive notifications about the request"
    )

    # Target Word Count
    target_word_count = st.number_input(
        "Target Word Count",
        min_value=100,
        max_value=10000,
        value=1000,
        step=50,
        help="Desired number of words for the content"
    )

    # Client Name - Text input
    client_name = st.text_input(
        "Client Name",
        placeholder="Enter the client's name",
        help="The client requesting the content"
    )

    # Additional Details
    additional_details = st.text_area(
        "Additional Details",
        placeholder="Enter any additional requirements, style guidelines, references, or special instructions...",
        height=150,
        help="Any extra requirements, style preferences, tone, references, or special instructions"
    )

    # Submit button
    submitted = st.form_submit_button("🚀 Send Content Request", type="primary")

# Handle form submission
if submitted:
    # Validation
    errors = []
    if not topic_title:
        errors.append("Topic/Title is required")
    if not primary_keyword:
        errors.append("Primary Keyword is required")
    if not client_name:
        errors.append("Client Name is required")
    if not email:
        errors.append("Email address is required")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address")


    if errors:
        for error in errors:
            st.error(f"❌ {error}")
    else:
        # Get fresh timestamp for submission
        submission_time = get_current_utc_datetime()

        # Prepare the payload with all parameters
        payload = {
            "topic_title": topic_title,
            "primary_keyword": primary_keyword,
            "email": email,
            "target_word_count": target_word_count,
            "client_name": client_name,
            "additional_details": additional_details,
            "current_datetime_utc": submission_time,
            "request_type": "content_creation"
        }

        # Send the request
        with st.spinner("Sending content request..."):
            try:
                response = requests.post(
                    WEBHOOK_URL,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Streamlit-Content-Request-Client",
                        "X-Timestamp-UTC": submission_time,
                        "X-Request-Type": "content_creation",
                        "X-Client-Name": client_name
                    },
                    timeout=30
                )

                if response.status_code in [200, 201, 202]:
                    st.success("✅ Content request sent successfully!")
                else:
                    st.error(f"❌ Request failed with status code: {response.status_code}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The webhook might be slow to respond.")

            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Please check your internet connection.")

            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Request error: {str(e)}")

            except Exception as e:
                st.error(f"💥 Unexpected error: {str(e)}")
