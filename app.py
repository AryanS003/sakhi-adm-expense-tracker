import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Establish connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_expenses():
    df = conn.read(worksheet="Sheet1")
    df = df.dropna(how="all")

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])

    return df

def add_expense(date, category, amount, note=""):
    """Add a new expense entry with optional transaction date."""
    df = conn.read(worksheet="Sheet1").dropna(how="all")

    # If no date is given, use today's date
    if date is None:
        date = datetime.now().date()

    # New row
    new_row = {
        "Date": date.strftime("%Y-%m-%d"),
        "Category": category,
        "Amount": amount,
        "Note": note,
    }

    # Append new row to DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Push updated DataFrame back to Google Sheets
    conn.update(worksheet="Sheet1", data=df)

def summary_df(df, period="daily"):
    if df.empty:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    if period == "daily":
        grouped = df.groupby(df["Date"].dt.date)["Amount"].sum().reset_index()
    elif period == "weekly":
        grouped = df.groupby(df["Date"].dt.to_period("W"))["Amount"].sum().reset_index()
    elif period == "monthly":
        grouped = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().reset_index()
    else:
        grouped = df

    return grouped

st.title("💰 Sakhi Expense Tracker")

# Add expense form
st.header("➕ Add Expense")
with st.form("expense_form"):
    txn_date = st.date_input("Transaction Date (optional)", value=None)  # 👈 allow blank
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0, step=1)
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Add Expense")
    if submitted and category and amount > 0:
        add_expense(txn_date, category, amount, note)
        if txn_date:
            st.success(f"Added: {txn_date} | {category} - {amount}")
        else:
            st.success(f"Added: {datetime.now().date()} | {category} - {amount}")

# Show expenses
st.header("📊 Expense Data")
df = get_expenses()
if not df.empty:
    st.subheader("📅 Daily Summary")
    st.dataframe(summary_df(df, "daily"))

    st.subheader("📆 Weekly Summary")
    st.dataframe(summary_df(df, "weekly"))

    st.subheader("📈 Monthly Summary")
    st.dataframe(summary_df(df, "monthly"))
    
    st.subheader("📜 Full Expense Log")
    st.dataframe(df)
else:
    st.info("No expenses yet. Add your first one above!")


