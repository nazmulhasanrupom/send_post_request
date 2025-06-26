import streamlit as st
import requests
import json
from datetime import datetime
import pytz

# Set page config
st.set_page_config(
    page_title="Content Request Webhook Sender", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

def get_current_utc_datetime():
    """Get current UTC datetime in YYYY-MM-DD HH:MM:SS format"""
    utc_now = datetime.now(pytz.UTC)
    return utc_now.strftime("%Y-%m-%d %H:%M:%S")

# Initialize session state
if 'user_login' not in st.session_state:
    st.session_state.user_login = "nazmulhasanrupom"

# Initialize client list in session state
if 'client_list' not in st.session_state:
    st.session_state.client_list = [
        "koala",
        "technovation",
        "digitalmax", 
        "webcraft",
        "contentpro"
    ]

# Set current datetime (updates on each run)
current_datetime = get_current_utc_datetime()

st.title("📝 Content Request Webhook Sender")

# Display current info at the top - EXACT format as requested
st.markdown("### 📊 Current Session Info")
col1, col2 = st.columns(2)

with col1:
    st.info(f"**Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted):** {current_datetime}")

with col2:
    user_login = st.text_input(
        "Current User's Login:",
        value=st.session_state.user_login,
        key="user_input"
    )
    st.session_state.user_login = user_login

st.divider()

# Client Management Section
with st.expander("👥 Manage Client Names"):
    st.subheader("Add New Client")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_client = st.text_input(
            "New Client Name",
            placeholder="Enter new client name",
            key="new_client_input"
        )
    
    with col2:
        if st.button("➕ Add Client", type="secondary"):
            if new_client and new_client.strip():
                client_name_clean = new_client.strip().lower()
                if client_name_clean not in [client.lower() for client in st.session_state.client_list]:
                    st.session_state.client_list.append(new_client.strip())
                    st.success(f"✅ Added '{new_client.strip()}' to client list!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ '{new_client.strip()}' already exists in the list!")
            else:
                st.error("❌ Please enter a valid client name!")
    
    # Display current clients with option to remove
    if st.session_state.client_list:
        st.subheader("Current Clients")
        cols = st.columns(min(len(st.session_state.client_list), 4))
        
        for i, client in enumerate(st.session_state.client_list):
            with cols[i % 4]:
                col_inner1, col_inner2 = st.columns([3, 1])
                with col_inner1:
                    st.write(f"• {client}")
                with col_inner2:
                    if client.lower() != "koala":  # Protect the default client
                        if st.button("🗑️", key=f"remove_{i}", help=f"Remove {client}"):
                            st.session_state.client_list.remove(client)
                            st.rerun()

st.divider()

# Main webhook form
with st.form("content_request_form"):
    st.subheader("🔗 Webhook Configuration")
    
    webhook_url = st.text_input(
        "Webhook URL",
        placeholder="https://your-webhook-endpoint.com/webhook",
        help="Enter the complete webhook URL"
    )
    
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
    
    # Target Word Count
    target_word_count = st.number_input(
        "Target Word Count",
        min_value=100,
        max_value=10000,
        value=1000,
        step=50,
        help="Desired number of words for the content"
    )
    
    # Target Audience
    target_audience = st.selectbox(
        "Target Audience",
        options=[
            "General Public",
            "Business Professionals", 
            "Students",
            "Technical Professionals",
            "Marketing Professionals",
            "Small Business Owners",
            "Enterprise Decision Makers",
            "Content Creators",
            "Developers",
            "Other"
        ],
        help="Primary audience for this content"
    )
    
    # If "Other" is selected, show text input
    if target_audience == "Other":
        custom_audience = st.text_input(
            "Specify Target Audience",
            placeholder="Enter your specific target audience"
        )
        if custom_audience:
            target_audience = custom_audience
    
    # Client Name - Now as dropdown with koala as default
    client_name_index = 0  # Default to "koala" (first in list)
    if "koala" in st.session_state.client_list:
        client_name_index = st.session_state.client_list.index("koala")
    
    client_name = st.selectbox(
        "Client Name",
        options=st.session_state.client_list,
        index=client_name_index,
        help="Select the client requesting the content"
    )
    
    # Show selected client info
    st.info(f"🏢 Selected Client: **{client_name}**")
    
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
    if not webhook_url:
        errors.append("Webhook URL is required")
    if not topic_title:
        errors.append("Topic/Title is required")
    if not primary_keyword:
        errors.append("Primary Keyword is required")
    if not client_name:
        errors.append("Client Name is required")
    if not st.session_state.user_login:
        errors.append("User Login is required")
    
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
            "target_word_count": target_word_count,
            "target_audience": target_audience,
            "client_name": client_name,
            "additional_details": additional_details,
            "current_datetime_utc": submission_time,
            "current_user_login": st.session_state.user_login,
            "request_type": "content_creation"
        }
        
        # Show what we're sending
        with st.expander("📦 Payload Being Sent", expanded=True):
            st.json(payload)
        
        # Send the request
        with st.spinner("Sending content request..."):
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Streamlit-Content-Request-Client",
                        "X-Submitted-By": st.session_state.user_login,
                        "X-Timestamp-UTC": submission_time,
                        "X-Request-Type": "content_creation",
                        "X-Client-Name": client_name
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.success("✅ Content request sent successfully!")
                    
                    # Response details
                    st.subheader("📈 Response Details")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Status Code", response.status_code)
                    with col2:
                        st.metric("Response Time", f"{response.elapsed.total_seconds():.2f}s")
                    with col3:
                        st.metric("Client", client_name)
                    with col4:
                        st.metric("Word Count", target_word_count)
                    
                    # Show response content
                    if response.text:
                        st.subheader("📄 Response Content")
                        try:
                            response_json = response.json()
                            st.json(response_json)
                        except:
                            st.code(response.text)
                            
                elif response.status_code in [201, 202]:
                    st.success(f"✅ Content request accepted! Status: {response.status_code}")
                    if response.text:
                        try:
                            st.json(response.json())
                        except:
                            st.code(response.text)
                else:
                    st.error(f"❌ Request failed with status code: {response.status_code}")
                    if response.text:
                        st.code(response.text)
                        
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The webhook might be slow to respond.")
                
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Please check the webhook URL and your internet connection.")
                
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Request error: {str(e)}")
                
            except Exception as e:
                st.error(f"💥 Unexpected error: {str(e)}")

# Content request summary
if st.checkbox("📋 Show Current Request Summary"):
    st.subheader("📋 Current Request Summary")
    
    summary_data = {
        "Topic/Title": topic_title if 'topic_title' in locals() else "",
        "Primary Keyword": primary_keyword if 'primary_keyword' in locals() else "",
        "Target Word Count": target_word_count if 'target_word_count' in locals() else 1000,
        "Target Audience": target_audience if 'target_audience' in locals() else "General Public",
        "Client Name": client_name if 'client_name' in locals() else "koala",
        "Additional Details": additional_details if 'additional_details' in locals() else "",
        "Current Date Time (UTC - YYYY-MM-DD HH:MM:SS formatted)": current_datetime,
        "Current User Login": st.session_state.user_login
    }
    
    for key, value in summary_data.items():
        if value:
            st.write(f"**{key}:** {value}")

# Info section
with st.expander("ℹ️ How to use this Content Request App"):
    st.markdown(f"""
    ### Current Session Information:
    - **Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted):** {current_datetime}
    - **Current User's Login:** {st.session_state.user_login}
    
    ### Client Management:
    - **Default Client:** koala
    - **Add New Clients:** Use the "Manage Client Names" section above
    - **Remove Clients:** Click the 🗑️ button next to any client (except koala)
    - **Current Clients:** {', '.join(st.session_state.client_list)}
    
    ### Usage Instructions:
    1. **Manage Clients**: Add new clients using the expandable section above
    2. **Enter Webhook URL**: Provide your webhook endpoint URL
    3. **Fill Content Details**:
       - **Topic/Title**: Main subject or title for the content
       - **Primary Keyword**: Main SEO keyword to target
       - **Target Word Count**: Desired length of content (100-10,000 words)
       - **Target Audience**: Who will read this content
       - **Client Name**: Select from dropdown (defaults to "koala")
       - **Additional Details**: Any special requirements or guidelines
    4. **Submit**: Click "Send Content Request" to submit
    
    ### Payload Structure:
    ```json
    {{
        "topic_title": "Your Content Topic",
        "primary_keyword": "your-seo-keyword",
        "target_word_count": 1000,
        "target_audience": "Business Professionals",
        "client_name": "koala",
        "additional_details": "Special requirements...",
        "current_datetime_utc": "{current_datetime}",
        "current_user_login": "{st.session_state.user_login}",
        "request_type": "content_creation"
    }}
    ```
    """)

# Auto-refresh section
st.divider()
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.caption(f"Last updated: {current_datetime}")
with col2:
    st.caption(f"Active clients: {len(st.session_state.client_list)}")
with col3:
    if st.button("🔄 Refresh"):
        st.rerun()

# Export/Import clients section
with st.expander("⚙️ Advanced Client Management"):
    st.subheader("Export/Import Clients")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Export Client List**")
        client_list_json = json.dumps(st.session_state.client_list, indent=2)
        st.download_button(
            label="📥 Download Client List",
            data=client_list_json,
            file_name="client_list.json",
            mime="application/json"
        )
    
    with col2:
        st.markdown("**Import Client List**")
        uploaded_file = st.file_uploader(
            "Choose a client list JSON file",
            type="json",
            key="client_upload"
        )
        
        if uploaded_file is not None:
            try:
                client_data = json.load(uploaded_file)
                if isinstance(client_data, list):
                    # Merge with existing clients, avoiding duplicates
                    for client in client_data:
                        if client not in st.session_state.client_list:
                            st.session_state.client_list.append(client)
                    st.success(f"✅ Imported {len(client_data)} clients!")
                    st.rerun()
                else:
                    st.error("❌ Invalid file format. Expected a JSON array.")
            except Exception as e:
                st.error(f"❌ Error importing file: {str(e)}")
    
    # Bulk add clients
    st.subheader("Bulk Add Clients")
    bulk_clients = st.text_area(
        "Enter client names (one per line)",
        placeholder="client1\nclient2\nclient3",
        height=100
    )
    
    if st.button("📝 Add All Clients"):
        if bulk_clients:
            new_clients = [client.strip() for client in bulk_clients.split('\n') if client.strip()]
            added_count = 0
            for client in new_clients:
                if client not in st.session_state.client_list:
                    st.session_state.client_list.append(client)
                    added_count += 1
            
            if added_count > 0:
                st.success(f"✅ Added {added_count} new clients!")
                st.rerun()
            else:
                st.info("ℹ️ All clients already exist in the list.")