import streamlit as st
import requests
import pandas as pd  # For reading CSV files

# Set backend URL here
BACKEND_URL = "http://foodbank-backend-alb-545677968.us-east-1.elb.amazonaws.com/api/process"  # Locally test first

# Load authentication data
auth_data = pd.read_csv("auth_data.csv")

def get_income_level(email):
    user_data = auth_data[auth_data['email_id'] == email]
    if not user_data.empty:
        return int(user_data['income'].values[0])
    return None

st.set_page_config(page_title="Food Bank Finder Chatbot", page_icon="🛒", layout="centered")

st.title("🛒 Food Bank Finder Chatbot")

email = st.text_input("Enter your email to access the chatbot:")
if email:
    income_level = get_income_level(email)
    if income_level is None:
        st.error("Email not found in the system. Access denied.")
        st.stop()
    elif income_level >= 10000:
        st.error("Your income level exceeds $10,000. Access denied.")
        st.stop()
    else:
        st.success("Access granted! You can now use the chatbot.")


st.markdown("""
Welcome!  
Type your location and needs, and I’ll recommend the best nearby food centers for you.
""")
st.info("ℹ️ Please enter a full address, including street, city, and zipcode for best results.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# User Input
if prompt := st.chat_input("Type your address and preferences here..."):
    # Save user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Make POST request to backend
        response = requests.post(
            BACKEND_URL,
            json={"input": prompt},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            if result.get("error"):
                if "ambiguous" in result["error"].lower() or "geocode" in result["error"].lower():
                    bot_reply = "🚫 I couldn't understand that address. Please provide a full address including **street name**, **city**, and **zipcode**."
                else:
                    bot_reply = f"❗ Error: {result['error']}\n\nDetails: {result.get('details', 'No details')}"
            else:
                # Show ONLY the final top recommendations (from LLM2 output)
                bot_reply = "### 🏠 Top Food Center Recommendations\n\n"
                bot_reply += f"{result['summary_llm_output']}"  # This should already be user-friendly with emojis etc.

        else:
            bot_reply = "❗ Error: Unable to connect to backend server."

    except Exception as e:
        bot_reply = f"❗ Exception occurred: {e}"

    # Display bot reply
    st.chat_message("assistant").markdown(bot_reply)
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
