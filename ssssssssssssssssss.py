import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from fpdf import FPDF
from io import BytesIO
import zipfile
import json
import re
import os
import pickle
import calendar
import hashlib
import base64

# ==============================
# SECURE AUTHENTICATION SYSTEM
# ==============================
def hash_password(password):
    """Hash a password using SHA-256 with a fixed salt"""
    salt = b"mobile_shop_salt_2024"
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return base64.b64encode(hashed).decode('utf-8')

def load_credentials():
    """Load credentials from secure storage"""
    try:
        if os.path.exists('auth_config.pkl'):
            with open('auth_config.pkl', 'rb') as f:
                auth_config = pickle.load(f)
                # Ensure all required keys exist
                if 'username' not in auth_config:
                    auth_config['username'] = "bond007"
                if 'password_hash' not in auth_config:
                    auth_config['password_hash'] = hash_password("bond007")
                if 'reset_code_hash' not in auth_config:
                    auth_config['reset_code_hash'] = hash_password("bond#")
                return auth_config
        else:
            # Create a new credentials file with fixed values
            auth_config = {
                'username': "bond007",
                'password_hash': hash_password("bond007"),
                'reset_code_hash': hash_password("bond#")
            }
            save_credentials(auth_config)
            
            # Display generated credentials in console
            print("=" * 50)
            print("SETUP COMPLETE: FIXED CREDENTIALS")
            print("=" * 50)
            print(f"USERNAME: bond007")
            print(f"PASSWORD: bond007") 
            print(f"RESET CODE: bond#")
            print("=" * 50)
            
            return auth_config
    except Exception as e:
        # If there's any error, create a new config with fixed values
        auth_config = {
            'username': "bond007",
            'password_hash': hash_password("bond007"),
            'reset_code_hash': hash_password("bond#")
        }
        save_credentials(auth_config)
        
        # Display generated credentials in console
        print("=" * 50)
        print("ERROR RECOVERY: USING FIXED CREDENTIALS")
        print("=" * 50)
        print(f"USERNAME: bond007")
        print(f"PASSWORD: bond007") 
        print(f"RESET CODE: bond#")
        print("=" * 50)
        
        return auth_config

def save_credentials(auth_config):
    """Save credentials to secure storage"""
    try:
        with open('auth_config.pkl', 'wb') as f:
            pickle.dump(auth_config, f)
    except Exception as e:
        st.error(f"Error saving credentials: {e}")

def check_credentials(username, password):
    """Check if username and password match stored credentials"""
    try:
        auth_config = load_credentials()
        hashed_input = hash_password(password)
        
        return username == auth_config['username'] and hashed_input == auth_config['password_hash']
    except KeyError:
        # If there's a KeyError, the auth config is corrupted, recreate it
        load_credentials()  # This will recreate the config
        return False

def check_reset_code(reset_code):
    """Check if reset code is correct"""
    try:
        auth_config = load_credentials()
        hashed_input = hash_password(reset_code)
        
        return hashed_input == auth_config['reset_code_hash']
    except KeyError:
        # If there's a KeyError, the auth config is corrupted, recreate it
        load_credentials()  # This will recreate the config
        return False

def update_password(new_password):
    """Update the password"""
    try:
        auth_config = load_credentials()
        auth_config['password_hash'] = hash_password(new_password)
        save_credentials(auth_config)
    except KeyError:
        # If there's a KeyError, the auth config is corrupted, recreate it
        auth_config = load_credentials()  # This will recreate the config
        auth_config['password_hash'] = hash_password(new_password)
        save_credentials(auth_config)

def login_section():
    """Display login form and handle authentication"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2.5rem;
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border-radius: 1rem;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .login-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(164, 66, 245, 0.1), transparent);
            transform: rotate(45deg);
            animation: shimmer 3s infinite;
            z-index: 0;
        }
        
        @keyframes shimmer {
            0% { transform: rotate(45deg) translateX(-100%); }
            100% { transform: rotate(45deg) translateX(100%); }
        }
        
        .login-content {
            position: relative;
            z-index: 1;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-header h2 {
            background: linear-gradient(90deg, #6a1b9a, #a442f5, #e0aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        
        .login-header p {
            color: #8c8c8c;
            font-size: 1rem;
        }
        
        .login-input {
            background-color: rgba(42, 42, 42, 0.8) !important;
            color: #f0f2f6 !important;
            border: 1px solid rgba(164, 66, 245, 0.3) !important;
            border-radius: 0.75rem !important;
            padding: 0.75rem 1rem !important;
            margin-bottom: 1.2rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px);
            width: 100%;
            box-sizing: border-box;
        }
        
        .login-input:focus {
            border-color: #a442f5 !important;
            box-shadow: 0 0 0 2px rgba(164, 66, 245, 0.3) !important;
        }
        
        .login-btn {
            background: linear-gradient(45deg, #6a1b9a, #8e24aa) !important;
            color: white !important;
            border: none !important;
            border-radius: 0.75rem !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(106, 27, 154, 0.3) !important;
            width: 100%;
            margin-top: 1rem;
        }
        
        .login-btn:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(106, 27, 154, 0.5) !important;
        }
        
        .reset-btn {
            background: transparent !important;
            color: #a442f5 !important;
            border: 1px solid #a442f5 !important;
            border-radius: 0.75rem !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100%;
        }
        
        .reset-btn:hover {
            background: rgba(164, 66, 245, 0.1) !important;
            transform: translateY(-2px) !important;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(164, 66, 245, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(164, 66, 245, 0); }
            100% { box-shadow: 0 0 0 0 rgba(164, 66, 245, 0); }
        }
        
        .shop-name-container {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border-radius: 0.75rem;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            text-align: center;
            border: 1px solid rgba(164, 66, 245, 0.3);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            width: 100%;
            box-sizing: border-box;
        }
        
        .shop-name {
            background: linear-gradient(90deg, #6a1b9a, #a442f5, #e0aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
        }
        
        .shop-tagline {
            color: #8c8c8c;
            font-size: 0.9rem;
            margin: 0.3rem 0 0 0;
        }
        
        .stTextInput>div>div>input {
            width: 100% !important;
            box-sizing: border-box !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if we're showing reset form
    if st.session_state.get('show_reset', False):
        reset_password_section()
        return False
    
    st.markdown("""
    <div class="login-container">
        <div class="login-content">
            <div class="shop-name-container">
                <h3 class="shop-name">AHSAN MOBILE,PRINT AND EASYPAISA SHOP.</h3>
                <p class="shop-tagline">Premium Mobile & Accessories Management System</p>
            </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("", placeholder="Enter username", key="username_input")
        password = st.text_input("", type="password", placeholder="Enter password", key="password_input")
        
        # Custom buttons with HTML
        st.markdown("""
        <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1.5rem;">
            <button type="submit" class="login-btn pulse">🔐 Login</button>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Reset Password", use_container_width=True):
                st.session_state.show_reset = True
                st.rerun()
        with col2:
            if st.form_submit_button("Login", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False
                    
                if check_credentials(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    return False
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    return False

def reset_password_section():
    """Password reset functionality"""
    auth_config = load_credentials()
    
    st.markdown("""
    <div class="login-container">
        <div class="login-content">
            <div class="login-header">
                <h2>Password Reset</h2>
                <p>Enter your reset code and new password</p>
            </div>
    """, unsafe_allow_html=True)
    
    with st.form("reset_password_form"):
        reset_code = st.text_input("", type="password", placeholder="Enter reset code", key="reset_code")
        new_password = st.text_input("", type="password", placeholder="Enter new password", key="new_password")
        confirm_password = st.text_input("", type="password", placeholder="Confirm new password", key="confirm_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Reset Password", use_container_width=True):
                if not all([reset_code, new_password, confirm_password]):
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not check_reset_code(reset_code):
                    st.error("Invalid reset code")
                else:
                    update_password(new_password)
                    st.success("Password reset successfully! You can now login with your new password.")
                    st.session_state.show_reset = False
                    st.rerun()
        with col2:
            if st.form_submit_button("Back to Login", use_container_width=True):
                st.session_state.show_reset = False
                st.rerun()

def logout_button():
    """Display logout button"""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.show_reset = False
        st.rerun()

# ==============================
# CUSTOM CSS STYLING - PROFESSIONAL & DYNAMIC
# ==============================
st.markdown("""
<style>
    /* Overall app styling with a dark, modern theme */
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    
    /* Main container styling */
    .main-container {
        padding: 2rem;
        border-radius: 1rem;
        background-color: #1a1a1a;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Header with a dynamic gradient and a strong presence */
    .header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #6a1b9a, #a442f5, #e0aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Tagline styling */
    .tagline {
        font-size: 1.1rem;
        text-align: center;
        color: #8c8c8c;
        margin-bottom: 2rem;
        font-style: italic;
    }

    /* Section titles with a more professional touch */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #a442f5;
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2a2a2a;
    }
    
    /* Button styling with a vibrant gradient and a more pronounced 3D effect on hover */
    .stButton>button {
        background: linear-gradient(45deg, #6a1b9a, #8e24aa);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(106, 27, 154, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 8px 25px rgba(106, 27, 154, 0.5);
    }
    
    /* Input field styling for a clean, cohesive look */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, 
    .stSelectbox>div>div, 
    .stTextArea>div>div>textarea {
        background-color: #2a2a2a;
        color: #f0f2f6;
        border: 1px solid #4a4a4a;
        border-radius: 0.75rem;
        padding: 0.75rem;
        transition: border-color 0.3s ease;
    }

    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus, 
    .stSelectbox>div>div:focus, 
    .stTextArea>div>div>textarea:focus {
        border-color: #a442f5;
        box-shadow: 0 0 0 1px #a442f5;
    }
    
    /* --- ENHANCED SIDEBAR NAVIGATION HOVER EFFECTS --- */
    .st-eb .st-cm {
        transition: all 0.3s ease-in-out;
        border-radius: 0.5rem;
    }
    
    .st-eb .st-cm:hover {
        background-color: #2a2a2a !important;
        color: #a442f5 !important;
        transform: scale(1.02);
        box-shadow: 0 0 10px rgba(164, 66, 245, 0.5);
    }
    
    .st-eb .st-cm:active, .st-eb .st-cm:focus {
        background-color: #2a2a2a !important;
        color: #a442f5 !important;
        border-left: 3px solid #a442f5;
    }
    /* --- END OF ENHANCED SIDEBAR EFFECTS --- */
    
    /* Metric cards with a subtle animation and soft glow on hover */
    .metric-card {
        background-color: #1a1a1a;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        border: 1px solid #2a2a2a;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(106, 27, 154, 0.4);
    }
    
    .metric-card h3 {
        color: #8c8c8c; 
        margin-bottom: 0.5rem;
    }
    
    /* Shop info container with a distinct border and gradient */
    .shop-info {
        background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #6a1b9a;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
        margin-top: 2rem;
        border-top: 1px solid #2a2a2a;
    }
    
    /* Warning styling for negative profit */
    .negative-profit {
        color: #F44336 !important;
        font-weight: bold;
    }
    
    /* Positive styling for profit */
    .positive-profit {
        color: #4CAF50 !important;
        font-weight: bold;
    }
    
    /* Customer balance styling */
    .balance-card {
        background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #a442f5;
    }
    
    /* Advance balance styling */
    .advance-card {
        background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #4CAF50;
    }

    /* Receipt styling */
    .receipt-container {
        background-color: white;
        color: black;
        padding: 20px;
        border-radius: 10px;
        font-family: monospace;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        max-width: 300px;
        margin: 0 auto;
    }
    
    .receipt-header {
        text-align: center;
        border-bottom: 2px dashed #ccc;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    .receipt-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    
    .receipt-total {
        border-top: 2px dashed #ccc;
        padding-top: 10px;
        margin-top: 15px;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    /* Data table styling */
    .dataframe {
        width: 100%;
        border-collapse: collapse;
    }
    
    .dataframe th {
        background-color: #2a2a2a;
        color: #a442f5;
        padding: 10px;
        text-align: left;
        border-bottom: 2px solid #4a4a4a;
    }
    
    .dataframe td {
        padding: 8px 10px;
        border-bottom: 1px solid #4a4a4a;
    }
    
    .dataframe tr:hover {
        background-color: #2a2a2a;
    }
    
    /* Custom PDF button styling */
    .pdf-button {
        background: linear-gradient(45deg, #d32f2f, #f44336) !important;
    }
    
    .pdf-button:hover {
        background: linear-gradient(45deg, #b71c1c, #d32f2f) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# DATA PERSISTENCE FUNCTIONS
# ==============================
def load_data():
    """Load data from persistent storage or initialize if not exists"""
    try:
        # Try to load from file first
        if os.path.exists('mobile_master_data.pkl'):
            with open('mobile_master_data.pkl', 'rb') as f:
                data = pickle.load(f)
            st.session_state.transactions = data.get('transactions', pd.DataFrame(columns=[
                'Date', 'Time', 'Type', 'Category', 'Model', 'Brand', 'Item', 
                'Color', 'Storage', 'Quantity', 'Selling_Price', 'Cost_Price', 
                'Profit', 'Paid_Amount', 'Left_Amount', 'Customer_Name',
                'Phone', 'CNIC', 'Address', 'Warranty', 'Compatible_With',
                'Transaction_ID', 'Status', 'Advance_Balance', 'IMEI'
            ]))
            st.session_state.expenditures = data.get('expenditures', pd.DataFrame(columns=[
                'Date', 'Time', 'Category', 'Amount', 'Description'
            ]))
            st.session_state.payments = data.get('payments', pd.DataFrame(columns=[
                'Date', 'Time', 'Customer_Name', 'Phone', 'CNIC', 
                'Amount', 'Transaction_ID', 'Payment_Type', 'Notes', 'Is_Advance'
            ]))
            st.session_state.customer_advances = data.get('customer_advances', pd.DataFrame(columns=[
                'Customer_Name', 'Phone', 'CNIC', 'Advance_Balance'
            ]))
        else:
            # Initialize empty DataFrames
            st.session_state.transactions = pd.DataFrame(columns=[
                'Date', 'Time', 'Type', 'Category', 'Model', 'Brand', 'Item', 
                'Color', 'Storage', 'Quantity', 'Selling_Price', 'Cost_Price', 
                'Profit', 'Paid_Amount', 'Left_Amount', 'Customer_Name',
                'Phone', 'CNIC', 'Address', 'Warranty', 'Compatible_With',
                'Transaction_ID', 'Status', 'Advance_Balance', 'IMEI'
            ])
            st.session_state.expenditures = pd.DataFrame(columns=[
                'Date', 'Time', 'Category', 'Amount', 'Description'
            ])
            st.session_state.payments = pd.DataFrame(columns=[
                'Date', 'Time', 'Customer_Name', 'Phone', 'CNIC', 
                'Amount', 'Transaction_ID', 'Payment_Type', 'Notes', 'Is_Advance'
            ])
            st.session_state.customer_advances = pd.DataFrame(columns=[
                'Customer_Name', 'Phone', 'CNIC', 'Advance_Balance'
            ])
        
        # Convert date columns to datetime for proper filtering - FIXED DATE HANDLING
        if not st.session_state.transactions.empty and 'Date' in st.session_state.transactions.columns:
            # Ensure dates are in proper format
            st.session_state.transactions['Date'] = pd.to_datetime(st.session_state.transactions['Date'], errors='coerce')
            # Remove any invalid dates
            st.session_state.transactions = st.session_state.transactions[st.session_state.transactions['Date'].notna()]
            
        if not st.session_state.expenditures.empty and 'Date' in st.session_state.expenditures.columns:
            st.session_state.expenditures['Date'] = pd.to_datetime(st.session_state.expenditures['Date'], errors='coerce')
            st.session_state.expenditures = st.session_state.expenditures[st.session_state.expenditures['Date'].notna()]
            
        if not st.session_state.payments.empty and 'Date' in st.session_state.payments.columns:
            st.session_state.payments['Date'] = pd.to_datetime(st.session_state.payments['Date'], errors='coerce')
            st.session_state.payments = st.session_state.payments[st.session_state.payments['Date'].notna()]
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Reset to empty DataFrames if there's an error
        st.session_state.transactions = pd.DataFrame(columns=[
            'Date', 'Time', 'Type', 'Category', 'Model', 'Brand', 'Item', 
            'Color', 'Storage', 'Quantity', 'Selling_Price', 'Cost_Price', 
            'Profit', 'Paid_Amount', 'Left_Amount', 'Customer_Name',
            'Phone', 'CNIC', 'Address', 'Warranty', 'Compatible_With',
            'Transaction_ID', 'Status', 'Advance_Balance', 'IMEI'
        ])
        st.session_state.expenditures = pd.DataFrame(columns=[
            'Date', 'Time', 'Category', 'Amount', 'Description'
        ])
        st.session_state.payments = pd.DataFrame(columns=[
            'Date', 'Time', 'Customer_Name', 'Phone', 'CNIC', 
            'Amount', 'Transaction_ID', 'Payment_Type', 'Notes', 'Is_Advance'
        ])
        st.session_state.customer_advances = pd.DataFrame(columns=[
            'Customer_Name', 'Phone', 'CNIC', 'Advance_Balance'
        ])

def save_data():
    """Save data to persistent storage"""
    try:
        # Ensure date columns are in proper format before saving
        if not st.session_state.transactions.empty and 'Date' in st.session_state.transactions.columns:
            st.session_state.transactions['Date'] = pd.to_datetime(st.session_state.transactions['Date'], errors='coerce')
            
        if not st.session_state.expenditures.empty and 'Date' in st.session_state.expenditures.columns:
            st.session_state.expenditures['Date'] = pd.to_datetime(st.session_state.expenditures['Date'], errors='coerce')
            
        if not st.session_state.payments.empty and 'Date' in st.session_state.payments.columns:
            st.session_state.payments['Date'] = pd.to_datetime(st.session_state.payments['Date'], errors='coerce')
            
        # Save all data to file
        data = {
            'transactions': st.session_state.transactions,
            'expenditures': st.session_state.expenditures,
            'payments': st.session_state.payments,
            'customer_advances': st.session_state.customer_advances
        }
        
        with open('mobile_master_data.pkl', 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ==============================
# SHOP INFORMATION
# ==============================
def shop_info_container():
    st.markdown("""
    <div class="shop-info">
        <h2 style="color: #a442f5; margin-bottom: 0.5rem;">AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI</h2>
        <p style="margin-bottom: 0.2rem; color: #8c8c8c;">Premium Mobile & Accessories Shop</p>
        <p style="margin-bottom: 0.2rem;"><strong>Proprietor:</strong> Ahsan khan </p>
        <p style="margin-bottom: 0.2rem;"><strong>Contact>:</strong> 03363617334</p>
        <p style="margin-bottom: 0.2rem;"><strong>Contact>:</strong> 03708635099</p>
        <p style="margin-bottom: 0;"><strong>Address:</strong> Jama Market, Loralai, Balochitan </p>
    </div>
    """, unsafe_allow_html=True)

# ==============================
# HELPER FUNCTIONS
# ==============================
def generate_transaction_id():
    """Generate a unique transaction ID"""
    if 'transactions' not in st.session_state or st.session_state.transactions.empty:
        return "TXN-00001"
    
    # Check if Transaction_ID column exists
    if 'Transaction_ID' not in st.session_state.transactions.columns:
        return "TXN-00001"
    
    # Get only valid transaction IDs (strings that match the pattern)
    valid_ids = st.session_state.transactions['Transaction_ID'].dropna()
    valid_ids = valid_ids[valid_ids.apply(lambda x: isinstance(x, str) and x.startswith('TXN-'))]
    
    if valid_ids.empty:
        return "TXN-00001"
    
    try:
        # Extract the numeric part and find the maximum
        nums = valid_ids.str.split('-').str[1].astype(int)
        max_num = nums.max()
        return f"TXN-{max_num + 1:05d}"
    except:
        # Fallback in case of any parsing error
        return f"TXN-{int(time.time())}"

def validate_phone(phone):
    """Validate Pakistani phone number format"""
    if not phone:
        return False
    pattern = r'^(\+92|0)[0-9]{10}$'
    return re.match(pattern, phone) is not None

def format_cnic(cnic):
    """Format CNIC to standard format (XXXXX-XXXXXXX-X)"""
    if not cnic:
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', cnic)
    
    # If we have 13 digits, format it properly
    if len(digits) == 13:
        return f"{digits[:5]}-{digits[5:12]}-{digits[12]}"
    else:
        # If not 13 digits, just return the cleaned version
        return digits

def validate_cnic(cnic):
    """Validate Pakistani CNIC format - accept any format but clean it"""
    if not cnic:  # CNIC is optional
        return True, ""
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', cnic)
    
    # If empty after cleaning, it's valid (optional)
    if not digits:
        return True, ""
    
    # If we have 13 digits, it's valid
    if len(digits) == 13:
        return True, f"{digits[:5]}-{digits[5:12]}-{digits[12]}"
    else:
        # Accept any number of digits but just return the cleaned version
        return True, digits

def get_customer_balance(customer_identifier):
    """Get customer balance based on phone, CNIC, or name"""
    if not st.session_state.transactions.empty:
        # Filter transactions for this customer
        customer_transactions = st.session_state.transactions[
            (st.session_state.transactions['Customer_Name'] == customer_identifier) |
            (st.session_state.transactions['Phone'] == customer_identifier) |
            (st.session_state.transactions['CNIC'] == customer_identifier)
        ]
        
        # Get advance balance if exists
        advance_balance = 0
        if not st.session_state.customer_advances.empty:
            customer_advance = st.session_state.customer_advances[
                (st.session_state.customer_advances['Customer_Name'] == customer_identifier) |
                (st.session_state.customer_advances['Phone'] == customer_identifier) |
                (st.session_state.customer_advances['CNIC'] == customer_identifier)
            ]
            if not customer_advance.empty:
                advance_balance = customer_advance['Advance_Balance'].sum()
        
        if not customer_transactions.empty:
            total_left = customer_transactions['Left_Amount'].sum()
            total_paid = customer_transactions['Paid_Amount'].sum()
            total_amount = customer_transactions['Selling_Price'].sum()
            
            # Get payment history
            if not st.session_state.payments.empty:
                customer_payments = st.session_state.payments[
                    (st.session_state.payments['Customer_Name'] == customer_identifier) |
                    (st.session_state.payments['Phone'] == customer_identifier) |
                    (st.session_state.payments['CNIC'] == customer_identifier)
                ]
                additional_payments = customer_payments['Amount'].sum()
                total_paid += additional_payments
                total_left -= additional_payments
            
            # Apply advance balance
            if advance_balance > 0:
                if total_left > 0:
                    if advance_balance >= total_left:
                        advance_balance -= total_left
                        total_left = 0
                        total_paid = total_amount
                    else:
                        total_left -= advance_balance
                        total_paid += advance_balance
                        advance_balance = 0
            
            return {
                'total_amount': total_amount,
                'total_paid': total_paid,
                'total_left': max(0, total_left),
                'advance_balance': advance_balance,
                'transactions': customer_transactions
            }
    
    # Check if customer has only advance balance
    if not st.session_state.customer_advances.empty:
        customer_advance = st.session_state.customer_advances[
            (st.session_state.customer_advances['Customer_Name'] == customer_identifier) |
            (st.session_state.customer_advances['Phone'] == customer_identifier) |
            (st.session_state.customer_advances['CNIC'] == customer_identifier)
        ]
        if not customer_advance.empty:
            advance_balance = customer_advance['Advance_Balance'].sum()
            return {
                'total_amount': 0,
                'total_paid': 0,
                'total_left': 0,
                'advance_balance': advance_balance,
                'transactions': pd.DataFrame()
            }
    
    return {'total_amount': 0, 'total_paid': 0, 'total_left': 0, 'advance_balance': 0, 'transactions': pd.DataFrame()}

def update_customer_advance(customer_name, phone, cnic, amount):
    """Update customer advance balance"""
    if not st.session_state.customer_advances.empty:
        # Check if customer already exists in advances
        customer_idx = st.session_state.customer_advances[
            (st.session_state.customer_advances['Customer_Name'] == customer_name) |
            (st.session_state.customer_advances['Phone'] == phone) |
            (st.session_state.customer_advances['CNIC'] == cnic)
        ].index
        
        if not customer_idx.empty:
            # Update existing customer advance
            st.session_state.customer_advances.loc[customer_idx, 'Advance_Balance'] += amount
        else:
            # Add new customer advance
            new_advance = {
                'Customer_Name': customer_name,
                'Phone': phone,
                'CNIC': cnic,
                'Advance_Balance': amount
            }
            st.session_state.customer_advances = pd.concat(
                [st.session_state.customer_advances, pd.DataFrame([new_advance])],
                ignore_index=True
            )
    else:
        # Add new customer advance
        new_advance = {
            'Customer_Name': customer_name,
            'Phone': phone,
            'CNIC': cnic,
            'Advance_Balance': amount
        }
        st.session_state.customer_advances = pd.concat(
            [st.session_state.customer_advances, pd.DataFrame([new_advance])],
            ignore_index=True
        )

# ==============================
# FIXED RECEIPT FUNCTIONS
# ==============================
def generate_receipt(transaction_data):
    """Generate a receipt for a transaction - FIXED FORMATTING"""
    # Format prices properly
    unit_price = transaction_data['Selling_Price'] / transaction_data['Quantity'] if transaction_data['Quantity'] > 0 else 0
    
    # Only show brand/model if they exist and are not None/empty
    brand_model = ""
    if transaction_data.get('Brand') and transaction_data.get('Model'):
        brand_model = f"{transaction_data['Brand']} {transaction_data['Model']}"
    elif transaction_data.get('Brand'):
        brand_model = transaction_data['Brand']
    elif transaction_data.get('Model'):
        brand_model = transaction_data['Model']
        
    # Only show color/storage if they exist and are not None/empty
    color_storage = ""
    if transaction_data.get('Color') and transaction_data.get('Storage'):
        color_storage = f"{transaction_data['Color']} {transaction_data['Storage']}"
    elif transaction_data.get('Color'):
        color_storage = transaction_data['Color']
    elif transaction_data.get('Storage'):
        color_storage = transaction_data['Storage']
    
    receipt_html = f"""
    <div class="receipt-container">
        <div class="receipt-header">
            <h2>AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI</h2>
            <p>Main Market, Loralai, Pakistan</p>
            <p>+92 300 1234567</p>
            <p>{transaction_data['Date']} {transaction_data['Time']}</p>
            <p>Transaction ID: {transaction_data['Transaction_ID']}</p>
        </div>
        
        <div style="margin-bottom: 15px;">
            <p><strong>Customer:</strong> {transaction_data['Customer_Name']}</p>
            <p><strong>Phone:</strong> {transaction_data['Phone']}</p>
        </div>
        
        <div style="border-bottom: 1px dashed #ccc; padding-bottom: 10px; margin-bottom: 10px;">
            <div class="receipt-item">
                <span>Item:</span>
                <span>{transaction_data['Item']}</span>
            </div>
            """
    
    # Only add brand/model line if it's not empty
    if brand_model:
        receipt_html += f"""
            <div class="receipt-item">
                <span>Brand/Model:</span>
                <span>{brand_model}</span>
            </div>
        """
    
    # Only add color/storage line if it's not empty
    if color_storage:
        receipt_html += f"""
            <div class="receipt-item">
                <span>Color/Storage:</span>
                <span>{color_storage}</span>
            </div>
        """
    
    # Add IMEI if available
    if transaction_data.get('IMEI'):
        receipt_html += f"""
            <div class="receipt-item">
                <span>IMEI:</span>
                <span>{transaction_data['IMEI']}</span>
            </div>
        """
    
    receipt_html += f"""
            <div class="receipt-item">
                <span>Quantity:</span>
                <span>{transaction_data['Quantity']}</span>
            </div>
            
            <div class="receipt-item">
                <span>Unit Price:</span>
                <span>{unit_price:,.0f} PKR</span>
            </div>
        </div>
        
        <div class="receipt-total">
            <span>TOTAL:</span>
            <span>{transaction_data['Selling_Price']:,.0f} PKR</span>
        </div>
        
        <div class="receipt-item">
            <span>Paid:</span>
            <span>{transaction_data['Paid_Amount']:,.0f} PKR</span>
        </div>
        
        <div class="receipt-item">
            <span>Balance:</span>
            <span>{transaction_data['Left_Amount']:,.0f} PKR</span>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <p>Thank you for your purchase!</p>
            {f"<p>Warranty: {transaction_data.get('Warranty', '')}</p>" if transaction_data.get('Warranty') else ""}
        </div>
    </div>
    """
    return receipt_html

def create_receipt_pdf(transaction_data):
    """Create a PDF receipt for a transaction - FIXED FORMATTING"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(74, 20, 140)
    pdf.cell(0, 10, "AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Main Market, Loralai, Pakistan", 0, 1, 'C')
    pdf.cell(0, 6, "+92 300 1234567", 0, 1, 'C')
    
    # Format date and time properly
    if isinstance(transaction_data['Date'], str):
        date_str = transaction_data['Date']
    else:
        date_str = transaction_data['Date'].strftime('%Y-%m-%d') if hasattr(transaction_data['Date'], 'strftime') else str(transaction_data['Date'])
    
    if isinstance(transaction_data['Time'], str):
        time_str = transaction_data['Time']
    else:
        time_str = transaction_data['Time'].strftime('%H:%M:%S') if hasattr(transaction_data['Time'], 'strftime') else str(transaction_data['Time'])
    
    pdf.cell(0, 6, f"{date_str} {time_str}", 0, 1, 'C')
    pdf.cell(0, 6, f"Transaction ID: {transaction_data['Transaction_ID']}", 0, 1, 'C')
    pdf.ln(5)
    
    # Customer info
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "CUSTOMER INFORMATION", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Name: {transaction_data['Customer_Name']}", 0, 1, 'L')
    pdf.cell(0, 6, f"Phone: {transaction_data['Phone']}", 0, 1, 'L')
    if transaction_data.get('CNIC'):
        pdf.cell(0, 6, f"CNIC: {transaction_data['CNIC']}", 0, 1, 'L')
    pdf.ln(5)
    
    # Item details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "ITEM DETAILS", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(50, 6, "Item:", 0, 0, 'L')
    pdf.cell(0, 6, f"{transaction_data['Item']}", 0, 1, 'L')
    
    # Only show brand/model if they exist and are not None/empty
    brand_model = ""
    if transaction_data.get('Brand') and transaction_data.get('Model'):
        brand_model = f"{transaction_data['Brand']} {transaction_data['Model']}"
    elif transaction_data.get('Brand'):
        brand_model = transaction_data['Brand']
    elif transaction_data.get('Model'):
        brand_model = transaction_data['Model']
        
    if brand_model:
        pdf.cell(50, 6, "Brand/Model:", 0, 0, 'L')
        pdf.cell(0, 6, f"{brand_model}", 0, 1, 'L')
    
    # Only show color/storage if they exist and are not None/empty
    color_storage = ""
    if transaction_data.get('Color') and transaction_data.get('Storage'):
        color_storage = f"{transaction_data['Color']} {transaction_data['Storage']}"
    elif transaction_data.get('Color'):
        color_storage = transaction_data['Color']
    elif transaction_data.get('Storage'):
        color_storage = transaction_data['Storage']
        
    if color_storage:
        pdf.cell(50, 6, "Color/Storage:", 0, 0, 'L')
        pdf.cell(0, 6, f"{color_storage}", 0, 1, 'L')
    
    # Add IMEI if available
    if transaction_data.get('IMEI'):
        pdf.cell(50, 6, "IMEI:", 0, 0, 'L')
        pdf.cell(0, 6, f"{transaction_data['IMEI']}", 0, 1, 'L')
    
    pdf.cell(50, 6, "Quantity:", 0, 0, 'L')
    pdf.cell(0, 6, f"{transaction_data['Quantity']}", 0, 1, 'L')
    
    unit_price = transaction_data['Selling_Price'] / transaction_data['Quantity'] if transaction_data['Quantity'] > 0 else 0
    pdf.cell(50, 6, "Unit Price:", 0, 0, 'L')
    pdf.cell(0, 6, f"{unit_price:,.0f} PKR", 0, 1, 'L')
    
    pdf.ln(5)
    
    # Financial details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 8, "Total Amount:", 0, 0, 'L')
    pdf.cell(0, 8, f"{transaction_data['Selling_Price']:,.0f} PKR", 0, 1, 'L')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(50, 6, "Amount Paid:", 0, 0, 'L')
    pdf.cell(0, 6, f"{transaction_data['Paid_Amount']:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(50, 6, "Balance Due:", 0, 0, 'L')
    pdf.cell(0, 6, f"{transaction_data['Left_Amount']:,.0f} PKR", 0, 1, 'L')
    
    pdf.ln(10)
    
    # Footer
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, "Thank you for your purchase!", 0, 1, 'C')
    if transaction_data.get('Warranty'):
        pdf.cell(0, 6, f"Warranty: {transaction_data['Warranty']}", 0, 1, 'C')
    else:
        pdf.cell(0, 6, "No warranty provided", 0, 1, 'C')
    
    # Add shop name in footer instead of "Mobile Master Pro System"
    pdf.cell(0, 6, " GN BY > AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin1')

def create_expenditure_pdf(expenditure_data):
    """Create a PDF for expenditure record"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(74, 20, 140)
    pdf.cell(0, 10, "AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Main Market, Loralai, Pakistan", 0, 1, 'C')
    pdf.cell(0, 6, "+92 300 1234567", 0, 1, 'C')
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "EXPENDITURE RECEIPT", 0, 1, 'C')
    pdf.ln(5)
    
    # Date and time
    if isinstance(expenditure_data['Date'], str):
        date_str = expenditure_data['Date']
    else:
        date_str = expenditure_data['Date'].strftime('%Y-%m-%d') if hasattr(expenditure_data['Date'], 'strftime') else str(expenditure_data['Date'])
    
    if isinstance(expenditure_data['Time'], str):
        time_str = expenditure_data['Time']
    else:
        time_str = expenditure_data['Time'].strftime('%H:%M:%S') if hasattr(expenditure_data['Time'], 'strftime') else str(expenditure_data['Time'])
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Date: {date_str} {time_str}", 0, 1, 'L')
    pdf.ln(5)
    
    # Expenditure details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "EXPENDITURE DETAILS", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(50, 6, "Category:", 0, 0, 'L')
    pdf.cell(0, 6, f"{expenditure_data['Category']}", 0, 1, 'L')
    
    pdf.cell(50, 6, "Amount:", 0, 0, 'L')
    pdf.cell(0, 6, f"{expenditure_data['Amount']:,.0f} PKR", 0, 1, 'L')
    
    pdf.ln(5)
    
    pdf.cell(50, 6, "Description:", 0, 0, 'L')
    pdf.multi_cell(0, 6, f"{expenditure_data['Description']}")
    
    pdf.ln(10)
    
    # Footer
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, "Expenditure recorded by AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin1')

def create_payment_pdf(payment_data):
    """Create a PDF for payment record"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(74, 20, 140)
    pdf.cell(0, 10, "AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Main Market, Loralai, Pakistan", 0, 1, 'C')
    pdf.cell(0, 6, "+92 300 1234567", 0, 1, 'C')
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "PAYMENT RECEIPT", 0, 1, 'C')
    pdf.ln(5)
    
    # Date and time
    if isinstance(payment_data['Date'], str):
        date_str = payment_data['Date']
    else:
        date_str = payment_data['Date'].strftime('%Y-%m-%d') if hasattr(payment_data['Date'], 'strftime') else str(payment_data['Date'])
    
    if isinstance(payment_data['Time'], str):
        time_str = payment_data['Time']
    else:
        time_str = payment_data['Time'].strftime('%H:%M:%S') if hasattr(payment_data['Time'], 'strftime') else str(payment_data['Time'])
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Date: {date_str} {time_str}", 0, 1, 'L')
    pdf.ln(5)
    
    # Payment details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "PAYMENT DETAILS", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(50, 6, "Customer Name:", 0, 0, 'L')
    pdf.cell(0, 6, f"{payment_data['Customer_Name']}", 0, 1, 'L')
    
    pdf.cell(50, 6, "Phone:", 0, 0, 'L')
    pdf.cell(0, 6, f"{payment_data['Phone']}", 0, 1, 'L')
    
    if payment_data.get('CNIC'):
        pdf.cell(50, 6, "CNIC:", 0, 0, 'L')
        pdf.cell(0, 6, f"{payment_data['CNIC']}", 0, 1, 'L')
    
    pdf.cell(50, 6, "Amount:", 0, 0, 'L')
    pdf.cell(0, 6, f"{payment_data['Amount']:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(50, 6, "Payment Type:", 0, 0, 'L')
    pdf.cell(0, 6, f"{payment_data['Payment_Type']}", 0, 1, 'L')
    
    if payment_data.get('Transaction_ID'):
        pdf.cell(50, 6, "Transaction ID:", 0, 0, 'L')
        pdf.cell(0, 6, f"{payment_data['Transaction_ID']}", 0, 1, 'L')
    
    pdf.ln(5)
    
    if payment_data.get('Notes'):
        pdf.cell(50, 6, "Notes:", 0, 0, 'L')
        pdf.multi_cell(0, 6, f"{payment_data['Notes']}")
    
    pdf.ln(10)
    
    # Footer
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, "Payment recorded in Mobile Master Pro System", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin1')

def create_dashboard_report(period='daily'):
    """Create a comprehensive dashboard report PDF with period filter"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(74, 20, 140)
    pdf.cell(0, 10, "AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, "Main Market, Loralai, Pakistan", 0, 1, 'C')
    pdf.cell(0, 6, "+92 300 1234567", 0, 1, 'C')
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"BUSINESS DASHBOARD REPORT - {period.upper()}", 0, 1, 'C')
    pdf.ln(5)
    
    # Report date
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'L')
    pdf.ln(5)
    
    # Calculate key metrics based on period
    transactions = st.session_state.transactions
    expenditures = st.session_state.expenditures
    
    today = datetime.now().date()
    
    # Filter data based on period
    if period == 'daily':
        filtered_transactions = transactions[transactions['Date'].dt.date == today]
        filtered_expenditures = expenditures[expenditures['Date'].dt.date == today]
        period_text = f"for {today.strftime('%Y-%m-%d')}"
    elif period == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        filtered_transactions = transactions[(transactions['Date'].dt.date >= start_of_week) & 
                                           (transactions['Date'].dt.date <= end_of_week)]
        filtered_expenditures = expenditures[(expenditures['Date'].dt.date >= start_of_week) & 
                                           (expenditures['Date'].dt.date <= end_of_week)]
        period_text = f"for week {start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}"
    elif period == 'monthly':
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        filtered_transactions = transactions[(transactions['Date'].dt.date >= start_of_month) & 
                                           (transactions['Date'].dt.date <= end_of_month)]
        filtered_expenditures = expenditures[(expenditures['Date'].dt.date >= start_of_month) & 
                                           (expenditures['Date'].dt.date <= end_of_month)]
        period_text = f"for {today.strftime('%B %Y')}"
    elif period == 'yearly':
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        filtered_transactions = transactions[(transactions['Date'].dt.date >= start_of_year) & 
                                           (transactions['Date'].dt.date <= end_of_year)]
        filtered_expenditures = expenditures[(expenditures['Date'].dt.date >= start_of_year) & 
                                           (expenditures['Date'].dt.date <= end_of_year)]
        period_text = f"for year {today.year}"
    else:
        # All time
        filtered_transactions = transactions
        filtered_expenditures = expenditures
        period_text = "for all time"
    
    # Today's metrics
    period_sales = filtered_transactions[filtered_transactions['Type'] == 'Sale']['Selling_Price'].sum()
    period_profit = filtered_transactions['Profit'].sum()
    period_expenditure = filtered_expenditures['Amount'].sum()
    
    # Overall metrics
    total_sales = transactions['Selling_Price'].sum()
    total_profit = transactions['Profit'].sum()
    total_expenditure = expenditures['Amount'].sum()
    pending_payments = transactions['Left_Amount'].sum()
    
    # Category breakdown
    mobile_sales = filtered_transactions[filtered_transactions['Category'] == 'Mobile']['Selling_Price'].sum()
    accessories_sales = filtered_transactions[filtered_transactions['Category'] == 'Accessories']['Selling_Price'].sum()
    service_sales = filtered_transactions[filtered_transactions['Category'] == 'Repair']['Selling_Price'].sum()
    
    # Period Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"{period.upper()} SUMMARY {period_text}", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(90, 6, f"{period.capitalize()} Sales:", 0, 0, 'L')
    pdf.cell(0, 6, f"{period_sales:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, f"{period.capitalize()} Profit:", 0, 0, 'L')
    pdf.cell(0, 6, f"{period_profit:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, f"{period.capitalize()} Expenditure:", 0, 0, 'L')
    pdf.cell(0, 6, f"{period_expenditure:,.0f} PKR", 0, 1, 'L')
    
    pdf.ln(5)
    
    # Overall Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "OVERALL SUMMARY", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(90, 6, "Total Sales:", 0, 0, 'L')
    pdf.cell(0, 6, f"{total_sales:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, "Total Profit:", 0, 0, 'L')
    pdf.cell(0, 6, f"{total_profit:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, "Total Expenditure:", 0, 0, 'L')
    pdf.cell(0, 6, f"{total_expenditure:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, "Pending Payments:", 0, 0, 'L')
    pdf.cell(0, 6, f"{pending_payments:,.0f} PKR", 0, 1, 'L')
    
    pdf.ln(5)
    
    # Category Breakdown
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"CATEGORY BREAKDOWN {period_text}", 0, 1, 'L')
    pdf.set_font("Arial", '', 10)
    
    pdf.cell(90, 6, "Mobile Sales:", 0, 0, 'L')
    pdf.cell(0, 6, f"{mobile_sales:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, "Accessories Sales:", 0, 0, 'L')
    pdf.cell(0, 6, f"{accessories_sales:,.0f} PKR", 0, 1, 'L')
    
    pdf.cell(90, 6, "Service Sales:", 0, 0, 'L')
    pdf.cell(0, 6, f"{service_sales:,.0f} PKR", 0, 1, 'L')
    
    pdf.ln(10)
    
    # Footer
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 6, "Report generated by AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin1')

# ==============================
# FORM FUNCTIONS
# ==============================
def add_mobile_sale_form():
    st.markdown('<div class="section-title">📱 Add New Mobile Sale</div>', unsafe_allow_html=True)
    
    # Initialize session state for receipt if not exists
    if 'last_transaction' not in st.session_state:
        st.session_state.last_transaction = None
    
    with st.form("add_mobile_sale_form", clear_on_submit=True):
        col_dt, col_t = st.columns(2)
        with col_dt:
            sale_date = st.date_input("Date*", datetime.now().date(), key="mobile_date")
        with col_t:
            sale_time = st.time_input("Time*", datetime.now().time(), key="mobile_time")

        st.subheader("Item Details")
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("Brand*", key="mobile_brand", placeholder="e.g., Samsung, Apple")
            color = st.text_input("Color*", key="mobile_color", placeholder="e.g., Black, Gold")
            quantity = st.number_input("Quantity*", min_value=1, step=1, key="mobile_qty", value=1)
        with col2:
            model = st.text_input("Model*", key="mobile_model", placeholder="e.g., S23 Ultra, iPhone 15")
            storage = st.text_input("Storage*", key="mobile_storage", placeholder="e.g., 128GB, 256GB")
            warranty = st.text_input("Warranty Details (Optional)", key="mobile_warranty")
        
        # IMEI field
        imei = st.text_input("IMEI Number (Optional)", key="mobile_imei", placeholder="Enter IMEI number(s)")
        
        st.subheader("Financial Details")
        col3, col4 = st.columns(2)
        with col3:
            cost_price = st.number_input("Cost Price (PKR)*", min_value=0, key="mobile_cost_price", value=0)
            paid_amount = st.number_input("Paid Amount (PKR)*", min_value=0, key="mobile_paid", value=0)
        with col4:
            selling_price = st.number_input("Selling Price (PKR)*", min_value=0, key="mobile_sell_price", value=0)
            
        # Validation for cost price and selling price
        if cost_price > 0 and selling_price > 0 and cost_price > selling_price:
            st.warning("⚠️ Cost price is higher than selling price. This will result in a loss.")
            
        if paid_amount > (selling_price * quantity):
            st.error("❌ Paid amount cannot be greater than total selling price.")
            
        st.subheader("Customer Details")
        customer_name = st.text_input("Customer Name*", key="mobile_customer", placeholder="Full name")
        phone = st.text_input("Phone Number*", key="mobile_phone", placeholder="03XX-XXXXXXX")
        cnic = st.text_input("CNIC (Optional)", key="mobile_cnic", placeholder="XXXXX-XXXXXXX-X or any format")
        address = st.text_area("Address (Optional)", key="mobile_address", placeholder="Customer address")
        
        submitted = st.form_submit_button("💾 Save Mobile Sale", use_container_width=True)
        if submitted:
            # Validate inputs
            if not all([brand, model, color, storage, customer_name, phone, selling_price > 0]):
                st.error("Please fill all required fields (marked with *). Selling Price must be greater than 0.")
            elif not validate_phone(phone):
                st.error("Please enter a valid Pakistani phone number (e.g., 03001234567 or +923001234567)")
            elif paid_amount > (selling_price * quantity):
                st.error("Paid Amount cannot be greater than Total Selling Price.")
            else:
                # Format CNIC
                cnic_valid, formatted_cnic = validate_cnic(cnic)
                if not cnic_valid:
                    st.error("Please enter a valid CNIC")
                    return
                
                total_selling_price = selling_price * quantity
                profit = total_selling_price - (cost_price * quantity)
                left_amount = total_selling_price - paid_amount
                transaction_id = generate_transaction_id()
                
                new_transaction = {
                    'Date': sale_date,
                    'Time': sale_time.strftime('%H:%M:%S'),
                    'Type': 'Sale',
                    'Category': 'Mobile',
                    'Model': model,
                    'Brand': brand,
                    'Item': f"{brand} {model} ({color}, {storage})", # Combines into one field for clarity
                    'Color': color,
                    'Storage': storage,
                    'Quantity': quantity,
                    'Selling_Price': total_selling_price,
                    'Cost_Price': cost_price,
                    'Profit': profit,
                    'Paid_Amount': paid_amount,
                    'Left_Amount': left_amount,
                    'Customer_Name': customer_name,
                    'Phone': phone,
                    'CNIC': formatted_cnic,
                    'Address': address,
                    'Warranty': warranty,
                    'Compatible_With': '', # Not applicable for mobiles
                    'Transaction_ID': transaction_id,
                    'Status': 'Completed' if left_amount == 0 else 'Pending',
                    'Advance_Balance': 0, # Not applicable for sales
                    'IMEI': imei
                }
                
                # Check for existing customer to update advance balance if paid more than due
                customer_result = get_customer_balance(phone)
                advance_applied = 0
                
                if customer_result['advance_balance'] > 0:
                    if customer_result['advance_balance'] >= left_amount:
                        advance_applied = left_amount
                        left_amount = 0
                    else:
                        advance_applied = customer_result['advance_balance']
                        left_amount -= advance_applied
                    
                    new_transaction['Left_Amount'] = left_amount
                    new_transaction['Paid_Amount'] = paid_amount + advance_applied
                    update_customer_advance(customer_name, phone, formatted_cnic, -advance_applied)

                # Add the new transaction
                new_row_df = pd.DataFrame([new_transaction])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_row_df], ignore_index=True)
                
                # Save data and display success message
                save_data()
                st.success("✅ Mobile sale recorded successfully!")
                
                # Store the last transaction for receipt generation
                st.session_state.last_transaction = new_transaction

def add_accessories_sale_form():
    st.markdown('<div class="section-title">🎧 Add New Accessories Sale</div>', unsafe_allow_html=True)
    
    # Initialize session state for receipt if not exists
    if 'last_transaction' not in st.session_state:
        st.session_state.last_transaction = None

    with st.form("add_accessories_sale_form", clear_on_submit=True):
        col_dt, col_t = st.columns(2)
        with col_dt:
            sale_date = st.date_input("Date*", datetime.now().date(), key="acc_date")
        with col_t:
            sale_time = st.time_input("Time*", datetime.now().time(), key="acc_time")

        st.subheader("Item Details")
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Name*", key="acc_item", placeholder="e.g., Screen Protector, Headphones")
            compatible_with = st.text_input("Compatible With (Optional)", key="acc_compatible", placeholder="e.g., iPhone 15, Samsung S23")
            quantity = st.number_input("Quantity*", min_value=1, step=1, key="acc_qty", value=1)
        with col2:
            brand = st.text_input("Brand (Optional)", key="acc_brand", placeholder="e.g., Anker, JBL")
            model = st.text_input("Model (Optional)", key="acc_model", placeholder="e.g., A2544, PureBass")
            
        st.subheader("Financial Details")
        col3, col4 = st.columns(2)
        with col3:
            cost_price = st.number_input("Cost Price (PKR)*", min_value=0, key="acc_cost_price", value=0)
            paid_amount = st.number_input("Paid Amount (PKR)*", min_value=0, key="acc_paid", value=0)
        with col4:
            selling_price = st.number_input("Selling Price (PKR)*", min_value=0, key="acc_sell_price", value=0)
            
        # Validation for cost price and selling price
        if cost_price > 0 and selling_price > 0 and cost_price > selling_price:
            st.warning("⚠️ Cost price is higher than selling price. This will result in a loss.")
        
        st.subheader("Customer Details")
        customer_name = st.text_input("Customer Name*", key="acc_customer", placeholder="Full name")
        phone = st.text_input("Phone Number*", key="acc_phone", placeholder="03XX-XXXXXXX")
        cnic = st.text_input("CNIC (Optional)", key="acc_cnic", placeholder="XXXXX-XXXXXXX-X")
        address = st.text_area("Address (Optional)", key="acc_address")
        
        submitted = st.form_submit_button("💾 Save Accessories Sale", use_container_width=True)
        if submitted:
            # Validate inputs
            if not all([item_name, customer_name, phone, selling_price > 0]):
                st.error("Please fill all required fields (marked with *). Selling Price must be greater than 0.")
            elif not validate_phone(phone):
                st.error("Please enter a valid Pakistani phone number.")
            elif paid_amount > (selling_price * quantity):
                st.error("Paid Amount cannot be greater than Total Selling Price.")
            else:
                cnic_valid, formatted_cnic = validate_cnic(cnic)
                if not cnic_valid:
                    st.error("Please enter a valid CNIC")
                    return
                
                total_selling_price = selling_price * quantity
                profit = total_selling_price - (cost_price * quantity)
                left_amount = total_selling_price - paid_amount
                transaction_id = generate_transaction_id()
                
                new_transaction = {
                    'Date': sale_date,
                    'Time': sale_time.strftime('%H:%M:%S'),
                    'Type': 'Sale',
                    'Category': 'Accessories',
                    'Model': model,
                    'Brand': brand,
                    'Item': item_name,
                    'Color': '',
                    'Storage': '',
                    'Quantity': quantity,
                    'Selling_Price': total_selling_price,
                    'Cost_Price': cost_price,
                    'Profit': profit,
                    'Paid_Amount': paid_amount,
                    'Left_Amount': left_amount,
                    'Customer_Name': customer_name,
                    'Phone': phone,
                    'CNIC': formatted_cnic,
                    'Address': address,
                    'Warranty': '',
                    'Compatible_With': compatible_with,
                    'Transaction_ID': transaction_id,
                    'Status': 'Completed' if left_amount == 0 else 'Pending',
                    'Advance_Balance': 0,
                    'IMEI': ''
                }
                
                customer_result = get_customer_balance(phone)
                advance_applied = 0
                if customer_result['advance_balance'] > 0:
                    if customer_result['advance_balance'] >= left_amount:
                        advance_applied = left_amount
                        left_amount = 0
                    else:
                        advance_applied = customer_result['advance_balance']
                        left_amount -= advance_applied
                    
                    new_transaction['Left_Amount'] = left_amount
                    new_transaction['Paid_Amount'] = paid_amount + advance_applied
                    update_customer_advance(customer_name, phone, formatted_cnic, -advance_applied)

                new_row_df = pd.DataFrame([new_transaction])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_row_df], ignore_index=True)
                save_data()
                st.success("✅ Accessories sale recorded successfully!")
                st.session_state.last_transaction = new_transaction

def add_repair_form():
    st.markdown('<div class="section-title">🔧 Add New Repair Service</div>', unsafe_allow_html=True)
    
    if 'last_transaction' not in st.session_state:
        st.session_state.last_transaction = None

    with st.form("add_repair_form", clear_on_submit=True):
        col_dt, col_t = st.columns(2)
        with col_dt:
            repair_date = st.date_input("Date*", datetime.now().date(), key="repair_date")
        with col_t:
            repair_time = st.time_input("Time*", datetime.now().time(), key="repair_time")
            
        st.subheader("Service Details")
        col1, col2 = st.columns(2)
        with col1:
            device_brand = st.text_input("Device Brand*", key="repair_brand", placeholder="e.g., iPhone, Samsung")
            service_description = st.text_area("Service Description*", key="repair_desc", placeholder="e.g., Screen replacement, battery repair")
        with col2:
            device_model = st.text_input("Device Model*", key="repair_model", placeholder="e.g., iPhone X, Samsung S20")
            
        st.subheader("Financial Details")
        col3, col4 = st.columns(2)
        with col3:
            service_cost = st.number_input("Service Cost (PKR)*", min_value=0, key="repair_cost", value=0)
            paid_amount = st.number_input("Paid Amount (PKR)*", min_value=0, key="repair_paid", value=0)
        with col4:
            selling_price = st.number_input("Selling Price (PKR)*", min_value=0, key="repair_sell_price", value=0)  # FIXED: Added missing quote
            
        if paid_amount > selling_price:
            st.error("❌ Paid amount cannot be greater than Total Selling Price.")
        
        st.subheader("Customer Details")
        customer_name = st.text_input("Customer Name*", key="repair_customer", placeholder="Full name")
        phone = st.text_input("Phone Number*", key="repair_phone", placeholder="03XX-XXXXXXX")
        cnic = st.text_input("CNIC (Optional)", key="repair_cnic", placeholder="XXXXX-XXXXXXX-X")
        
        submitted = st.form_submit_button("💾 Save Repair Service", use_container_width=True)
        if submitted:
            if not all([device_brand, device_model, service_description, customer_name, phone, selling_price > 0]):
                st.error("Please fill all required fields (marked with *). Selling Price must be greater than 0.")
            elif not validate_phone(phone):
                st.error("Please enter a valid Pakistani phone number.")
            elif paid_amount > selling_price:
                st.error("Paid Amount cannot be greater than Total Selling Price.")
            else:
                cnic_valid, formatted_cnic = validate_cnic(cnic)
                if not cnic_valid:
                    st.error("Please enter a valid CNIC")
                    return
                
                profit = selling_price - service_cost
                left_amount = selling_price - paid_amount
                transaction_id = generate_transaction_id()

                new_transaction = {
                    'Date': repair_date,
                    'Time': repair_time.strftime('%H:%M:%S'),
                    'Type': 'Service',
                    'Category': 'Repair',
                    'Model': device_model,
                    'Brand': device_brand,
                    'Item': service_description,
                    'Color': '',
                    'Storage': '',
                    'Quantity': 1,
                    'Selling_Price': selling_price,
                    'Cost_Price': service_cost,
                    'Profit': profit,
                    'Paid_Amount': paid_amount,
                    'Left_Amount': left_amount,
                    'Customer_Name': customer_name,
                    'Phone': phone,
                    'CNIC': formatted_cnic,
                    'Address': '',
                    'Warranty': '',
                    'Compatible_With': '',
                    'Transaction_ID': transaction_id,
                    'Status': 'Completed' if left_amount == 0 else 'Pending',
                    'Advance_Balance': 0,
                    'IMEI': ''
                }
                
                customer_result = get_customer_balance(phone)
                advance_applied = 0
                if customer_result['advance_balance'] > 0:
                    if customer_result['advance_balance'] >= left_amount:
                        advance_applied = left_amount
                        left_amount = 0
                    else:
                        advance_applied = customer_result['advance_balance']
                        left_amount -= advance_applied
                    
                    new_transaction['Left_Amount'] = left_amount
                    new_transaction['Paid_Amount'] = paid_amount + advance_applied
                    update_customer_advance(customer_name, phone, formatted_cnic, -advance_applied)

                new_row_df = pd.DataFrame([new_transaction])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_row_df], ignore_index=True)
                save_data()
                st.success("✅ Repair service recorded successfully!")
                st.session_state.last_transaction = new_transaction

def add_expenditure_form():
    st.markdown('<div class="section-title">💸 Add New Expenditure</div>', unsafe_allow_html=True)
    with st.form("add_expenditure_form", clear_on_submit=True):
        col_dt, col_t = st.columns(2)
        with col_dt:
            exp_date = st.date_input("Date*", datetime.now().date(), key="exp_date")
        with col_t:
            exp_time = st.time_input("Time*", datetime.now().time(), key="exp_time")
            
        exp_category = st.text_input("Category*", placeholder="e.g., Rent, Utilities, Salary", key="exp_cat")
        exp_amount = st.number_input("Amount (PKR)*", min_value=0.0, key="exp_amount", value=0.0)
        exp_description = st.text_area("Description*", key="exp_desc")
        
        submitted = st.form_submit_button("💾 Save Expenditure", use_container_width=True)
        if submitted:
            if not all([exp_category, exp_amount > 0, exp_description]):
                st.error("Please fill all required fields (marked with *). Amount must be greater than 0.")
            else:
                new_expenditure = {
                    'Date': exp_date,
                    'Time': exp_time.strftime('%H:%M:%S'),
                    'Category': exp_category,
                    'Amount': exp_amount,
                    'Description': exp_description
                }
                
                new_row_df = pd.DataFrame([new_expenditure])
                st.session_state.expenditures = pd.concat([st.session_state.expenditures, new_row_df], ignore_index=True)
                save_data()
                st.success("✅ Expenditure recorded successfully!")

def record_payment_form():
    st.markdown('<div class="section-title">💰 Record Customer Payment / Advance</div>', unsafe_allow_html=True)
    with st.form("record_payment_form", clear_on_submit=True):
        col_dt, col_t = st.columns(2)
        with col_dt:
            pay_date = st.date_input("Date*", datetime.now().date(), key="pay_date")
        with col_t:
            pay_time = st.time_input("Time*", datetime.now().time(), key="pay_time")  # FIXED: Added missing quote
            
        customer_name = st.text_input("Customer Name*", placeholder="Full name", key="pay_customer")
        phone = st.text_input("Phone Number*", placeholder="03XX-XXXXXXX", key="pay_phone")
        cnic = st.text_input("CNIC (Optional)", key="pay_cnic", placeholder="XXXXX-XXXXXXX-X")
        
        col1, col2 = st.columns(2)
        with col1:
            payment_amount = st.number_input("Amount Paid (PKR)*", min_value=0, key="pay_amount")
        with col2:
            payment_type = st.selectbox("Payment Type*", ['Cash', 'Bank Transfer', 'Online Payment'], key="pay_type")

        # Checkbox for advance payment
        is_advance = st.checkbox("This is a customer advance (not tied to a specific transaction)")
        
        notes = st.text_area("Notes (Optional)", key="pay_notes")
        
        submitted = st.form_submit_button("💾 Record Payment", use_container_width=True)
        if submitted:
            if not all([customer_name, phone, payment_amount > 0]):
                st.error("Please fill all required fields. Amount must be greater than 0.")
            elif not validate_phone(phone):
                st.error("Please enter a valid Pakistani phone number.")
            else:
                cnic_valid, formatted_cnic = validate_cnic(cnic)
                if not cnic_valid:
                    st.error("Please enter a valid CNIC")
                    return
                    
                if is_advance:
                    # Update customer advance balance
                    update_customer_advance(customer_name, phone, formatted_cnic, payment_amount)
                    st.success(f"✅ Advance of {payment_amount:,.0f} PKR recorded for {customer_name}.")
                else:
                    # Record as a payment towards a transaction
                    payment_data = {
                        'Date': pay_date,
                        'Time': pay_time.strftime('%H:%M:%S'),
                        'Customer_Name': customer_name,
                        'Phone': phone,
                        'CNIC': formatted_cnic,
                        'Amount': payment_amount,
                        'Transaction_ID': '', # To be updated later if needed
                        'Payment_Type': payment_type,
                        'Notes': notes,
                        'Is_Advance': is_advance
                    }
                    new_row_df = pd.DataFrame([payment_data])
                    st.session_state.payments = pd.concat([st.session_state.payments, new_row_df], ignore_index=True)
                    st.success(f"✅ Payment of {payment_amount:,.0f} PKR recorded for {customer_name}.")
                
                save_data()

# ==============================
# MAIN PAGES
# ==============================
def dashboard_page():
    st.markdown('<div class="section-title">📊 Dashboard Overview</div>', unsafe_allow_html=True)
    
    # Check if data exists
    if 'transactions' not in st.session_state:
        st.info("No data available to display. Please record some transactions.")
        return
        
    transactions = st.session_state.transactions
    expenditures = st.session_state.expenditures
    
    # Use today's date for daily calculations
    today = datetime.now().date()
    
    # Calculate key metrics
    today_sales = transactions[(transactions['Date'].dt.date == today) & (transactions['Type'] == 'Sale')]['Selling_Price'].sum()
    today_profit = transactions[(transactions['Date'].dt.date == today)]['Profit'].sum()
    today_expenditure = expenditures[expenditures['Date'].dt.date == today]['Amount'].sum()
    
    total_sales = transactions['Selling_Price'].sum()
    total_profit = transactions['Profit'].sum()
    total_expenditure = expenditures['Amount'].sum()
    
    # Calculate pending payments
    pending_payments = transactions['Left_Amount'].sum()
    
    # Calculate mobile vs accessories sales
    mobile_sales = transactions[transactions['Category'] == 'Mobile']['Selling_Price'].sum()
    accessories_sales = transactions[transactions['Category'] == 'Accessories']['Selling_Price'].sum()
    service_sales = transactions[transactions['Category'] == 'Repair']['Selling_Price'].sum()
    
    # Create metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Today's Sales</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #a442f5;">{today_sales:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        profit_style = "positive-profit" if today_profit >= 0 else "negative-profit"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Today's Profit</h3>
            <p class="{profit_style}" style="font-size: 1.5rem; font-weight: bold;">{today_profit:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Today's Expenditure</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #a442f5;">{today_expenditure:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Overall Business Performance")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Sales</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #a442f5;">{total_sales:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        profit_style = "positive-profit" if total_profit >= 0 else "negative-profit"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Profit</h3>
            <p class="{profit_style}" style="font-size: 1.5rem; font-weight: bold;">{total_profit:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Expenditure</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #a442f5;">{total_expenditure:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional metrics
    st.subheader("Additional Metrics")
    col7, col8, col9 = st.columns(3)
    with col7:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Pending Payments</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #FF9800;">{pending_payments:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    with col8:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Mobile Sales</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #a442f5;">{mobile_sales:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    with col9:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Accessories Sales</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #a442f5;">{accessories_sales:,.0f} PKR</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Sales Distribution")
    if total_sales > 0:
        sales_data = pd.DataFrame({
            'Category': ['Mobiles', 'Accessories', 'Services'],
            'Amount': [mobile_sales, accessories_sales, service_sales]
        })
        st.bar_chart(sales_data.set_index('Category'))
    
    st.subheader("Daily Profit & Loss Analysis")
    if not transactions.empty:
        daily_profit = transactions.groupby(transactions['Date'].dt.date)['Profit'].sum()
        st.line_chart(daily_profit)
    else:
        st.info("No sales data available for daily analysis.")
    
    # Add download report button
    st.markdown("---")
    st.subheader("Download Reports")
    
    # Period selection for reports
    report_period = st.selectbox(
        "Select Report Period",
        ["Daily", "Weekly", "Monthly", "Yearly", "All Time"],
        key="report_period"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        # Download dashboard report
        report_data = create_dashboard_report(period=report_period.lower().replace(" ", "_"))
        st.download_button(
            label=f"📄 Download {report_period} Report (PDF)",
            data=report_data,
            file_name=f"{report_period.lower().replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col2:
        # Download CSV data
        csv_data = transactions.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download All Data (CSV)",
            data=csv_data,
            file_name=f"business_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def customer_balance_page():
    st.markdown('<div class="section-title">👤 Customer Balances</div>', unsafe_allow_html=True)
    
    st.write("Search for a customer by Name, Phone, or CNIC to view their outstanding balance and payment history.")
    
    search_term = st.text_input("Search Customer", key="customer_search", placeholder="Enter Name, Phone or CNIC")
    
    if search_term:
        results = get_customer_balance(search_term)
        
        if results['total_amount'] > 0 or results['advance_balance'] > 0:
            st.markdown(f"""
            <div class="balance-card">
                <h3>Balance for {search_term}</h3>
                <div style="display: flex; justify-content: space-between; font-size: 1.1em;">
                    <p>Total Sales:</p>
                    <p>{results['total_amount']:,.0f} PKR</p>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 1.1em;">
                    <p>Total Paid:</p>
                    <p>{results['total_paid']:,.0f} PKR</p>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 1.5em; font-weight: bold; margin-top: 1rem; color: #4CAF50;">
                    <p>Balance Due:</p>
                    <p>{results['total_left']:,.0f} PKR</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if results['advance_balance'] > 0:
                st.markdown(f"""
                <div class="advance-card">
                    <h3>Customer Advance Balance</h3>
                    <div style="display: flex; justify-content: space-between; font-size: 1.5em; font-weight: bold; color: #a442f5;">
                        <p>Advance Remaining:</p>
                        <p>{results['advance_balance']:,.0f} PKR</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.subheader("Transaction History")
            if not results['transactions'].empty:
                # Display transactions with download buttons
                for idx, transaction in results['transactions'].iterrows():
                    with st.expander(f"Transaction {transaction['Transaction_ID']} - {transaction['Date'].strftime('%Y-%m-%d')}"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Item:** {transaction['Item']}")
                            st.write(f"**Amount:** {transaction['Selling_Price']:,.0f} PKR")
                            st.write(f"**Paid:** {transaction['Paid_Amount']:,.0f} PKR")
                            st.write(f"**Balance:** {transaction['Left_Amount']:,.0f} PKR")
                        with col2:
                            pdf_data = create_receipt_pdf(transaction.to_dict())
                            st.download_button(
                                label="📄 Download Receipt",
                                data=pdf_data,
                                file_name=f"receipt_{transaction['Transaction_ID']}.pdf",
                                mime="application/pdf",
                                key=f"receipt_{idx}"
                            )
            else:
                st.info("No transaction history found for this customer.")
        else:
            st.warning(f"No customer found with the identifier '{search_term}'.")

def data_view_page():
    st.markdown('<div class="section-title">🗃️ View & Download Data</div>', unsafe_allow_html=True)

    # Tabs for different data types
    tab1, tab2, tab3, tab4 = st.tabs(["Transactions", "Expenditures", "Payments", "Customer Advances"])

    with tab1:
        st.subheader("Sales & Service Transactions")
        transactions = st.session_state.transactions.sort_values(by='Date', ascending=False)
        
        # Add search and filter functionality
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("Search transactions", placeholder="Search by customer, item, ID...")
        with col_filter:
            filter_type = st.selectbox("Filter by type", ["All", "Sale", "Service"])
        
        # Apply filters
        filtered_transactions = transactions
        if search_query:
            filtered_transactions = filtered_transactions[
                filtered_transactions.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)
            ]
        if filter_type != "All":
            filtered_transactions = filtered_transactions[filtered_transactions['Type'] == filter_type]
        
        st.dataframe(filtered_transactions)
        
        if not filtered_transactions.empty:
            # Add download buttons for each transaction
            st.subheader("Download Receipts")
            for idx, transaction in filtered_transactions.iterrows():
                with st.expander(f"Transaction {transaction['Transaction_ID']} - {transaction['Date'].strftime('%Y-%m-%d') if hasattr(transaction['Date'], 'strftime') else transaction['Date']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Customer:** {transaction['Customer_Name']}")
                        st.write(f"**Item:** {transaction['Item']}")
                        st.write(f"**Amount:** {transaction['Selling_Price']:,.0f} PKR")
                    with col2:
                        pdf_data = create_receipt_pdf(transaction.to_dict())
                        st.download_button(
                            label="📄 Download Receipt",
                            data=pdf_data,
                            file_name=f"receipt_{transaction['Transaction_ID']}.pdf",
                            mime="application/pdf",
                            key=f"txn_receipt_{idx}",
                            use_container_width=True
                        )
            
            # Bulk download option
            st.subheader("Bulk Download Options")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Transactions CSV",
                    data=filtered_transactions.to_csv(index=False).encode('utf-8'),
                    file_name="transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                # Create a zip file with all receipts
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, transaction in filtered_transactions.iterrows():
                        pdf_data = create_receipt_pdf(transaction.to_dict())
                        zip_file.writestr(f"receipt_{transaction['Transaction_ID']}.pdf", pdf_data)
                
                zip_buffer.seek(0)
                st.download_button(
                    label="📦 Download All Receipts (ZIP)",
                    data=zip_buffer,
                    file_name="all_receipts.zip",
                    mime="application/zip",
                    use_container_width=True
                )

    with tab2:
        st.subheader("Expenditure Records")
        expenditures = st.session_state.expenditures.sort_values(by='Date', ascending=False)
        
        # Add search functionality
        exp_search = st.text_input("Search expenditures", placeholder="Search by category, description...")
        
        # Apply filters
        filtered_expenditures = expenditures
        if exp_search:
            filtered_expenditures = filtered_expenditures[
                filtered_expenditures.apply(lambda row: exp_search.lower() in str(row).lower(), axis=1)
            ]
        
        st.dataframe(filtered_expenditures)
        
        if not filtered_expenditures.empty:
            # Add download buttons for each expenditure
            st.subheader("Download Expenditure Records")
            for idx, expenditure in filtered_expenditures.iterrows():
                with st.expander(f"Expenditure - {expenditure['Date'].strftime('%Y-%m-%d') if hasattr(expenditure['Date'], 'strftime') else expenditure['Date']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Category:** {expenditure['Category']}")
                        st.write(f"**Amount:** {expenditure['Amount']:,.0f} PKR")
                        st.write(f"**Description:** {expenditure['Description']}")
                    with col2:
                        pdf_data = create_expenditure_pdf(expenditure.to_dict())
                        st.download_button(
                            label="📄 Download Record",
                            data=pdf_data,
                            file_name=f"expenditure_{expenditure['Date'].strftime('%Y%m%d')}_{idx}.pdf",
                            mime="application/pdf",
                            key=f"exp_{idx}",
                            use_container_width=True
                        )
            
            # Bulk download option
            st.subheader("Bulk Download Options")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Expenditures CSV",
                    data=filtered_expenditures.to_csv(index=False).encode('utf-8'),
                    file_name="expenditures.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                # Create a zip file with all expenditure records
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, expenditure in filtered_expenditures.iterrows():
                        pdf_data = create_expenditure_pdf(expenditure.to_dict())
                        zip_file.writestr(f"expenditure_{expenditure['Date'].strftime('%Y%m%d')}_{idx}.pdf", pdf_data)
                
                zip_buffer.seek(0)
                st.download_button(
                    label="📦 Download All Records (ZIP)",
                    data=zip_buffer,
                    file_name="all_expenditures.zip",
                    mime="application/zip",
                    use_container_width=True
                )

    with tab3:
        st.subheader("Payment Records")
        payments = st.session_state.payments.sort_values(by='Date', ascending=False)
        
        # Add search functionality
        pay_search = st.text_input("Search payments", placeholder="Search by customer, type...")
        
        # Apply filters
        filtered_payments = payments
        if pay_search:
            filtered_payments = filtered_payments[
                filtered_payments.apply(lambda row: pay_search.lower() in str(row).lower(), axis=1)
            ]
        
        st.dataframe(filtered_payments)
        
        if not filtered_payments.empty:
            # Add download buttons for each payment
            st.subheader("Download Payment Records")
            for idx, payment in filtered_payments.iterrows():
                with st.expander(f"Payment - {payment['Date'].strftime('%Y-%m-%d') if hasattr(payment['Date'], 'strftime') else payment['Date']}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Customer:** {payment['Customer_Name']}")
                        st.write(f"**Amount:** {payment['Amount']:,.0f} PKR")
                        st.write(f"**Type:** {payment['Payment_Type']}")
                        if payment.get('Notes'):
                            st.write(f"**Notes:** {payment['Notes']}")
                    with col2:
                        pdf_data = create_payment_pdf(payment.to_dict())
                        st.download_button(
                            label="📄 Download Receipt",
                            data=pdf_data,
                            file_name=f"payment_{payment['Date'].strftime('%Y%m%d')}_{idx}.pdf",
                            mime="application/pdf",
                            key=f"pay_{idx}",
                            use_container_width=True
                        )
            
            # Bulk download option
            st.subheader("Bulk Download Options")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Payments CSV",
                    data=filtered_payments.to_csv(index=False).encode('utf-8'),
                    file_name="payments.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                # Create a zip file with all payment records
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, payment in filtered_payments.iterrows():
                        pdf_data = create_payment_pdf(payment.to_dict())
                        zip_file.writestr(f"payment_{payment['Date'].strftime('%Y%m%d')}_{idx}.pdf", pdf_data)
                
                zip_buffer.seek(0)
                st.download_button(
                    label="📦 Download All Receipts (ZIP)",
                    data=zip_buffer,
                    file_name="all_payments.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            
    with tab4:
        st.subheader("Customer Advance Balances")
        customer_advances = st.session_state.customer_advances
        
        # Add search functionality
        adv_search = st.text_input("Search advances", placeholder="Search by customer name, phone...")
        
        # Apply filters
        filtered_advances = customer_advances
        if adv_search:
            filtered_advances = filtered_advances[
                filtered_advances.apply(lambda row: adv_search.lower() in str(row).lower(), axis=1)
            ]
        
        st.dataframe(filtered_advances)
        
        if not filtered_advances.empty:
            st.download_button(
                label="📥 Download Customer Advances CSV",
                data=filtered_advances.to_csv(index=False).encode('utf-8'),
                file_name="customer_advances.csv",
                mime="text/csv",
                use_container_width=True
            )

# ==============================
# MAIN APPLICATION LOGIC
# ==============================
def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    
    # Initialize authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'show_reset' not in st.session_state:
        st.session_state.show_reset = False

    # Check authentication
    if not st.session_state.authenticated:
        login_section()
        return

    # Load data on app start
    load_data()

    # Sidebar for navigation
    st.sidebar.markdown(f'<h1 style="text-align: center; color: #a442f5; font-size: 2rem;">AHSAN MOBILE SHOP</h1>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Display username and logout button
    st.sidebar.markdown(f'<p style="text-align: center; color: #8c8c8c;">Logged in as: <strong>{st.session_state.username}</strong></p>', unsafe_allow_html=True)
    
    # Navigation buttons
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.page = "Dashboard"
    if st.sidebar.button("📱 Mobile Sale"):
        st.session_state.page = "Mobile Sale"
    if st.sidebar.button("🎧 Accessories Sale"):
        st.session_state.page = "Accessories Sale"
    if st.sidebar.button("🔧 Repair Service"):
        st.session_state.page = "Repair Service"
    if st.sidebar.button("💸 Add Expenditure"):
        st.session_state.page = "Add Expenditure"
    if st.sidebar.button("💰 Record Payment"):
        st.session_state.page = "Record Payment"
    if st.sidebar.button("👤 Customer Balances"):
        st.session_state.page = "Customer Balances"
    if st.sidebar.button("🗃️ View & Download Data"):
        st.session_state.page = "Data View"
    
    st.sidebar.markdown("---")
    st.sidebar.button("🔄 Reload Data", on_click=load_data, use_container_width=True)
    
    # Logout button
    logout_button()
    
    # Main content area
    st.markdown('<h1 class="header">AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Your all-in-one solution for managing mobile shop operations.</p>', unsafe_allow_html=True)
    
    # Display shop info
    shop_info_container()
    
    # Display the current page based on session state
    if st.session_state.page == "Dashboard":
        dashboard_page()
    elif st.session_state.page == "Mobile Sale":
        add_mobile_sale_form()
    elif st.session_state.page == "Accessories Sale":
        add_accessories_sale_form()
    elif st.session_state.page == "Repair Service":
        add_repair_form()
    elif st.session_state.page == "Add Expenditure":
        add_expenditure_form()
    elif st.session_state.page == "Record Payment":
        record_payment_form()
    elif st.session_state.page == "Customer Balances":
        customer_balance_page()
    elif st.session_state.page == "Data View":
        data_view_page()
        
    st.markdown("---")
    
    # Display the receipt if a transaction was just submitted
    if st.session_state.get('last_transaction'):
        st.subheader("Transaction Receipt")
        receipt_data = st.session_state.last_transaction
        st.markdown(generate_receipt(receipt_data), unsafe_allow_html=True)
        
        pdf_data = create_receipt_pdf(receipt_data)
        st.download_button(
            label="📄 Download PDF Receipt",
            data=pdf_data,
            file_name=f"receipt_{receipt_data['Transaction_ID']}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    st.markdown('<div class="footer">Developed by DV>Z | A Project by AHSAN MOBILE SHOP AND EASYPAISA CENTER LORALAI</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()