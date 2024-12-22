import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to send an email using Gmail SMTP
def send_email(recipient_email, subject, message):
    sender_email = "vijayawadaphpl@gmail.com"  # Replace with your Gmail email
    password = "qpgq vdfg gxqk mbxc"  # Replace with your Gmail password (consider using environment variables for security)
    
    try:
        # Setup the MIME
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # Establish connection to Gmail SMTP server (start TLS)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Encrypt the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        st.success(f"Email sent to {recipient_email}")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Initialize session state for tracking inventory and transactions
if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame(columns=["Item", "Stock", "Material Code", "Person Name"])

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = pd.DataFrame(columns=["Item", "Quantity", "Transaction Type", "Date", "Material Code", "Person Name"])

# Function to update inventory stock based on transactions
def update_inventory(item, quantity, transaction_type, material_code, person_name, additional_emails):
    # Check if the item exists in inventory, if not, create a new row
    if item not in st.session_state['inventory']['Item'].values:
        new_row = pd.DataFrame({
            "Item": [item], 
            "Stock": [0], 
            "Material Code": [material_code], 
            "Person Name": [person_name]
        })
        st.session_state['inventory'] = pd.concat([st.session_state['inventory'], new_row], ignore_index=True)
    
    # Update the stock based on the transaction type
    if transaction_type == "In":
        st.session_state['inventory'].loc[st.session_state['inventory']['Item'] == item, "Stock"] += quantity
    elif transaction_type == "Out":
        st.session_state['inventory'].loc[st.session_state['inventory']['Item'] == item, "Stock"] -= quantity
    
    # Always send an email for each transaction (In/Out)
    transaction_subject = f"Inventory Transaction: {transaction_type} for {item}"
    transaction_message = f"Dear {person_name},\n\nA transaction has been recorded for {item}.\nTransaction Type: {transaction_type}\nQuantity: {quantity}\nMaterial Code: {material_code}\n\nBest regards,\nInventory Management System"
    
    # Default email IDs (replace with your actual email addresses)
    default_email_ids = ["phplvjacr@indianoil.in.com"]  # List of default email addresses
    
    # Combine the default emails with additional emails entered by the user
    all_email_ids = default_email_ids + additional_emails
    
    # Send email to all email recipients about the current transaction
    for email in all_email_ids:
        send_email(email, transaction_subject, transaction_message)
    
    # Send transaction history via email
    send_transaction_history(all_email_ids)

    # Log transaction details
    log_transaction(item, quantity, transaction_type, material_code, person_name)

# Log transaction details to transaction history
def log_transaction(item, quantity, transaction_type, material_code, person_name):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_transaction = pd.DataFrame({
        "Item": [item], 
        "Quantity": [quantity], 
        "Transaction Type": [transaction_type], 
        "Date": [date], 
        "Material Code": [material_code], 
        "Person Name": [person_name]
    })
    
    st.session_state['transactions'] = pd.concat([st.session_state['transactions'], new_transaction], ignore_index=True)

# Function to send the transaction history
def send_transaction_history(all_email_ids):
    # Convert transaction history dataframe to a plain-text format
    history_message = "Transaction History:\n\n"
    history_message += st.session_state['transactions'].to_string(index=False)
    
    transaction_history_subject = "Inventory Transaction History"
    
    # Send transaction history to each email ID in the combined list
    for email in all_email_ids:
        send_email(email, transaction_history_subject, history_message)

# Set background color and other styling with image insertion
st.markdown("""
    <style>
    .reportview-container {
        background-color: #fafafa;  /* Light gray background */
    }
    .header {
        background-color: #4caf50;  /* Green header */
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
    }
    .footer {
        background-color: #333;  /* Dark footer */
        color: white;
        padding: 5px;
        text-align: center;
    }
    .main {
        background-color: #ffffff;  /* White content background */
        border-radius: 8px;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Display logo or image at the top
st.image("https://via.placeholder.com/800x200.png?text=Inventory+Management+System", width=800)

# Display title and inventory table
st.markdown("""
    <div class="header">
        SERPL Vijayawada<br>
        Online Material In & Out Register
    </div>
""", unsafe_allow_html=True)

st.subheader("Current Inventory")
st.dataframe(st.session_state['inventory'])

# Material entry form for in/out transactions
st.subheader("Enter Material In/Out")
transaction_type = st.selectbox("Transaction Type", ["In", "Out"])
item = st.text_input("Item Name")
material_code = st.text_input("Material Code")
person_name = st.text_input("Person Name")
quantity = st.number_input("Quantity", min_value=1)

# Add additional email addresses (comma separated)
additional_emails = st.text_area("Add Additional Email Recipients (comma separated)").split(',')

# Clean up any empty strings in the email list
additional_emails = [email.strip() for email in additional_emails if email.strip()]

# Transaction submission logic
if st.button("Submit Transaction"):
    if item and material_code and person_name and quantity > 0:
        # Process the transaction and log it
        update_inventory(item, quantity, transaction_type, material_code, person_name, additional_emails)
        st.success(f"{transaction_type} transaction for {quantity} of {item} has been recorded.")
    else:
        st.error("Please provide valid item name, material code, person name, and quantity.")

# Display transaction history
st.subheader("Transaction History")
if not st.session_state['transactions'].empty:
    st.dataframe(st.session_state['transactions'])
else:
    st.info("No transactions recorded yet.")

# Save current inventory and transactions to CSV (optional)
if st.button("Save Inventory and Transactions to CSV"):
    st.session_state['inventory'].to_csv('inventory.csv', index=False)
    st.session_state['transactions'].to_csv('transactions.csv', index=False)
    st.success("Inventory and transactions saved to CSV.")
