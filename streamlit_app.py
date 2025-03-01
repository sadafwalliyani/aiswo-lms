import pandas as pd
import streamlit as st
# from utils import issue_book, register_user, return_book, get_issued_books 

# Page configuration
st.set_page_config(page_title="AISWO LIBRARY MANAGEMENT SYSTEM", layout="wide")

# Custom CSS for Styling
st.markdown("""
<style>
.sidebar .sidebar-content {background-color: #079da4; color: white;}
h1, h2, h3, h4, h5, h6 {color: #079da4;}
.stButton button {background-color: #079da4; color: white; border-radius: 5px;}
.stButton button:hover {background-color: #057a7f;}
.stRadio label {color: black !important;}
</style>""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("Logo.png", width=150)
    st.title("AISWO LIBRARY MANAGEMENT SYSTEM")
    page = st.radio("Go to", ["Home", "Issue Book", "Registration"], key="nav_radio")

# 📌 Home Page - Display Issued Books
if page == "Home":
    st.title("📚 Currently Issued Books")

    # Fetch the latest issued books data
    issued_books = get_issued_books()

    if not issued_books.empty:
        st.write("Here are the books currently issued:")
        for index, row in issued_books.iterrows():
            book_id = row['BookID']
            with st.container():
                cols = st.columns([1, 3, 2, 2, 2])
                cols[0].write(f"**ID:** {book_id}")
                cols[1].write(f"**Title:** {row['Title']}")
                cols[2].write(f"**Issued To:** {row['IssuedTo']}")

                # Convert IssueDate to datetime for display
                issued_date = pd.to_datetime(row['IssueDate'], errors='coerce')
                cols[3].write(f"**Issued On:** {issued_date.date() if pd.notna(issued_date) else 'N/A'}")

                # Return Book Button
                with cols[4]:
                    if st.button("Return ⏎", key=f"ret_{book_id}_{index}"):
                        return_date = pd.to_datetime("today").date()
                        
                        if return_book(book_id, return_date):
                            st.success(f"Book {book_id} returned!")
                            st.rerun()  # 🔄 Immediately refresh UI after return
    else:
        st.write("No books are currently issued.")

# 📌 Issue Book Page
elif page == "Issue Book":
    st.title("📖 Issue New Book")

    with st.form("issue_form"):
        st.write("Fill in the details to issue a new book:")
        book_id = st.text_input("Book ID", key="book_id")
        title = st.text_input("Title", key="title")
        issued_to = st.text_input("Issued To", key="issued_to")
        issue_date = st.date_input("Issue Date", key="issue_date")

        if st.form_submit_button("Issue Book"):
            if issue_book(book_id, title, issued_to, issue_date):
                st.success("✅ Book issued successfully!")
            else:
                st.error("⚠ Error: Book ID already exists!")


# 📌 Registration
elif page == "Registration":
    st.title("📝 Register New User")
    st.write("Fill in the details to register a new user:")
    with st.form("reg_form"):  
        full_name = st.text_input("Full Name", key="full_name")
        classname = st.text_input("Class", key="classname")
        date_of_birth = st.date_input("Date of Birth", key="date_of_birth")
        address = st.text_input("Address", key="address")
        phone_number = st.text_input("Phone Number", key="phone_number")
        email = st.text_input("Email Address", key="email")

        if st.form_submit_button("Register"):
            if register_user(full_name, classname, date_of_birth, address, phone_number, email):
                st.success("✅ User registered successfully!")
            else:
                st.error("⚠ Error: User already exists!")
# utils code

# Define CSV file paths
CSV_FILE_LIBRARY = 'library_data.csv'
CSV_FILE_REGISTRATION = 'registration_newuser.csv'

# Library Data Functions
def load_library_data():
    """Load issued books data from CSV."""
    if os.path.exists(CSV_FILE_LIBRARY):
        try:
            df = pd.read_csv(CSV_FILE_LIBRARY, parse_dates=['IssueDate', 'ReturnDate'])
        except Exception as e:
            st.error(f"Error reading library CSV: {str(e)}")
            df = pd.DataFrame(columns=['BookID', 'Title', 'IssuedTo', 'IssueDate', 'ReturnDate'])
        
        df['ReturnDate'] = pd.to_datetime(df['ReturnDate'], errors='coerce')
        return df
    
    df = pd.DataFrame(columns=['BookID', 'Title', 'IssuedTo', 'IssueDate', 'ReturnDate'])
    df.to_csv(CSV_FILE_LIBRARY, index=False)
    return df

def save_library_data(df):
    """Save the updated book records to CSV."""
    df.to_csv(CSV_FILE_LIBRARY, index=False)

def issue_book(book_id, title, issued_to, issue_date):
    """Issue a new book, ensuring unique BookID."""
    df = load_library_data()
    if book_id in df['BookID'].astype(str).values:
        return False
    
    new_entry = pd.DataFrame([{
        'BookID': book_id,
        'Title': title,
        'IssuedTo': issued_to,
        'IssueDate': issue_date,
        'ReturnDate': pd.NaT
    }])
    
    df = pd.concat([df, new_entry], ignore_index=True)
    save_library_data(df)
    return True

def return_book(book_id, return_date):
    """Marks a book as returned and updates the CSV."""
    df = load_library_data()
    
    mask = df['BookID'].astype(str) == str(book_id)
    if mask.any():
        idx = df[mask].index[0]
        
        if pd.isna(df.at[idx, 'ReturnDate']):
            df.at[idx, 'ReturnDate'] = pd.to_datetime(return_date).strftime('%Y-%m-%d')
            save_library_data(df)
            return True
    
    return False

def get_issued_books():
    """Fetch books that are issued but not yet returned."""
    df = load_library_data()
    return df[(df['IssuedTo'].notna()) & (df['ReturnDate'].isna())]

# User Registration Functions
def load_registration_data():
    """Load user registration data from CSV."""
    if os.path.exists(CSV_FILE_REGISTRATION):
        try:
            df = pd.read_csv(CSV_FILE_REGISTRATION)
        except Exception as e:
            st.error(f"Error reading registration CSV: {str(e)}")
            df = pd.DataFrame(columns=['Full Name', 'Class', 'Date of Birth', 'Address', 'Phone Number', 'Email'])
        return df
    
    df = pd.DataFrame(columns=['Full Name', 'Class', 'Date of Birth', 'Address', 'Phone Number', 'Email'])
    df.to_csv(CSV_FILE_REGISTRATION, index=False)
    return df

def save_registration_data(df):
    """Save the updated user registration records to CSV."""
    df.to_csv(CSV_FILE_REGISTRATION, index=False)

def register_user(full_name, classname, date_of_birth, address, phone_number, email):
    """Register a new user."""
    df = load_registration_data()
    new_entry = pd.DataFrame([{
        'Full Name': full_name,
        'Class': classname,
        'Date of Birth': date_of_birth,
        'Address': address,
        'Phone Number': phone_number,
        'Email': email
    }])
    
    df = pd.concat([df, new_entry], ignore_index=True)
    save_registration_data(df)
    return True
