import pandas as pd
import streamlit as st
import database as db

st.set_page_config(page_title="Oracle Admin Terminal", page_icon="🔑", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #05050a 0%, #0c0014 100%) !important;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔑 Oracle Terminal - Master Admin Directory")
st.caption("Authorized Node Operations Only")

# Admin Master Password Check
password_input = st.text_input("Enter Root Master Password", type="password")
if password_input == "oracleadmin2026":
    st.success("Root identity cleared! Extracting master user databases...")
    
    users_data = db.get_all_users()
    
    if users_data:
        # Convert to Pandas Dataframe for high-speed tabular audit
        df_users = pd.DataFrame(users_data, columns=["Database ID", "Username", "Email Address", "Hashed Password", "Account Access Tier"])
        
        st.subheader("👥 Registered Platform Nodes")
        st.dataframe(df_users, use_container_width=True)
        
        st.metric("Total Provisioned Users", len(df_users))
    else:
        st.info("No system nodes registered in database currently.")
else:
    st.error("Admin verification pending.")