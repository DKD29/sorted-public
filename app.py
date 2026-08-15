import streamlit as st

import plotly.express as px

from datetime import datetime

from backend.transactions import (
    get_transactions,
    add_transaction,
    delete_transaction,
    edit_transaction
)

from backend.categories import CATEGORIES

from backend.auth import (
    create_user,
    authenticate,
    create_profile,
    get_profile
)

from backend.advisor import analyze_transactions

from Config import APP_MODE

from backend.budget import (
    get_budgets,
    set_budget,
    delete_budget,
    calculate_budget_status
)

import os

logo_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets",
    "images",
    "logo.png"
)

if os.path.exists(logo_path):
    st.image(
        logo_path,
        width=270
    )
else:
    st.error(
        f"Logo not found at: {logo_path}"
    )
# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SO₹TED",
    page_icon="₹",
    layout="wide"
)


# =========================================================
# SO₹TED UI THEME
# =========================================================

PRIMARY = "#004466"
TEXT = "#FFFFE4"
ACCENT = "#FACC62"
WARNING = "#8F0000"


st.markdown(
    f"""
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {{
        background-color: {PRIMARY};
    }}

    .stApp,
    .stApp p,
    .stApp label,
    .stApp span {{
        color: {TEXT};
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT} !important;
    }}


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY};
    }}

    section[data-testid="stSidebar"] * {{
        color: {TEXT} !important;
    }}


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {{
        background-color: {ACCENT};
        color: {PRIMARY} !important;
        border: 2px solid {ACCENT};
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s ease;
    }}

    .stButton > button p {{
        color: {PRIMARY} !important;
    }}

    .stButton > button:hover {{
        background-color: {TEXT};
        color: {PRIMARY} !important;
        border-color: {TEXT};
    }}

    .stButton > button:hover p {{
        color: {PRIMARY} !important;
    }}


    /* =====================================================
       INPUTS
       ===================================================== */

    input,
    textarea {{
        background-color: {TEXT} !important;
        color: {PRIMARY} !important;
        border-radius: 6px !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color: {PRIMARY} !important;
        opacity: 0.65;
    }}


    /* =====================================================
       SELECT BOXES
       ===================================================== */

    div[data-baseweb="select"] > div {{
        background-color: {TEXT} !important;
        color: {PRIMARY} !important;
        border-radius: 6px;
    }}

    div[data-baseweb="select"] span {{
        color: {PRIMARY} !important;
    }}

    div[data-baseweb="select"] input {{
        color: {PRIMARY} !important;
    }}


    /* =====================================================
       NUMBER INPUTS
       ===================================================== */

    div[data-testid="stNumberInput"] input {{
        background-color: {TEXT} !important;
        color: {PRIMARY} !important;
    }}

    div[data-testid="stNumberInput"] button {{
        background-color: {ACCENT} !important;
        color: {PRIMARY} !important;
        border-color: {ACCENT} !important;
    }}


    /* =====================================================
       CHECKBOXES / RADIO BUTTONS
       ===================================================== */

    div[data-testid="stCheckbox"] label p,
    div[data-testid="stRadio"] label p {{
        color: {TEXT} !important;
    }}


    /* =====================================================
       METRIC CARDS
       ===================================================== */

    div[data-testid="stMetric"] {{
        background-color: {PRIMARY};
        border: 2px solid {ACCENT};
        border-radius: 10px;
        padding: 15px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {TEXT} !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {ACCENT} !important;
    }}

    div[data-testid="stMetricDelta"] {{
        color: {TEXT} !important;
    }}


    /* =====================================================
       ALERTS / WARNINGS
       ===================================================== */

    

    /* =====================================================
       SUCCESS MESSAGES
       ===================================================== */

    div[data-testid="stAlert"][kind="success"] {{
        background-color: {ACCENT};
    }}

    div[data-testid="stAlert"][kind="success"] p {{
        color: {PRIMARY} !important;
    }}


    /* =====================================================
       INFO MESSAGES
       ===================================================== */

    div[data-testid="stAlert"][kind="info"] {{
        background-color: {PRIMARY};
        border: 2px solid {ACCENT};
    }}

    div[data-testid="stAlert"][kind="info"] p {{
        color: {TEXT} !important;
    }}


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {{
        border-color: {ACCENT} !important;
        opacity: 0.8;
    }}


    /* =====================================================
       EXPANDERS
       ===================================================== */

    details {{
        background-color: {PRIMARY};
        border: 1px solid {ACCENT};
        border-radius: 8px;
    }}

    details summary {{
        color: {TEXT} !important;
    }}


    /* =====================================================
       DATAFRAMES / TABLES
       ===================================================== */

    div[data-testid="stDataFrame"] {{
        border: 1px solid {ACCENT};
        border-radius: 8px;
    }}


    /* =====================================================
       LINKS
       ===================================================== */

    a {{
        color: {ACCENT} !important;
    }}


    /* =====================================================
       DELETE / DESTRUCTIVE BUTTONS
       ===================================================== */

    button[kind="secondary"] {{
        color: {PRIMARY};
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# TITLE
# =========================================================


st.subheader(
    "Your personal finance minister"
)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "editing_transaction" not in st.session_state:
    st.session_state.editing_transaction = None


# =========================================================
# LOGIN / SIGNUP
# =========================================================

if not st.session_state.logged_in:

    option = st.selectbox(
        "Choose option",
        [
            "Login",
            "Signup"
        ]
    )


    # =====================================================
    # SIGNUP
    # =====================================================

    if option == "Signup":

        st.header("Create Account")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        name = st.text_input(
            "Name"
        )

        age = st.number_input(
            "Age",
            min_value=5,
            max_value=100,
            value=13
        )

        user_type = st.selectbox(
            "User type",
            [
                "Student",
                "Working professional",
                "Self-employed",
                "Homemaker",
                "Retired",
                "Other"
            ]
        )

        goals = st.multiselect(
            "Financial goals",
            [
                "Save money",
                "Control spending",
                "Learn finance",
                "Track expenses",
                "Build saving habits",
                "Plan purchases"
            ]
        )

        detail_level = st.selectbox(
            "Detail level",
            [
                "Simple",
                "Balanced",
                "Detailed"
            ]
        )

        income_source = st.selectbox(
            "Income source",
            [
                "Pocket money",
                "Salary",
                "Business income",
                "Freelance income",
                "Pension",
                "Other"
            ]
        )

        if st.button("Create Account"):

            if create_user(
                username,
                password
            ):

                create_profile(
                    username,
                    name,
                    int(age),
                    user_type,
                    goals,
                    detail_level,
                    income_source
                )

                st.success(
                    "Account created. Please login."
                )

            else:

                st.error(
                    "Username already exists."
                )


    # =====================================================
    # LOGIN
    # =====================================================

    else:

        st.header("Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            if authenticate(
                username,
                password
            ):

                st.session_state.logged_in = True

                st.session_state.username = username

                st.success(
                    "Login successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password"
                )


# =========================================================
# DASHBOARD
# =========================================================

else:

    username = st.session_state.username

    header_col1, header_col2 = st.columns(
        [5, 1]
    )

    with header_col1:

        st.header(
            f"Welcome {username}"
        )

    with header_col2:

        if st.button(
            "Logout"
        ):

            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.editing_transaction = None

            st.rerun()


    profile = get_profile(
        username
    )

    transactions = get_transactions(
        username
    )

    if profile is None:

        st.error(
            "Your profile could not be loaded. Please create your profile again."
        )

        st.stop()


    st.divider()


    # =====================================================
    # DASHBOARD SUMMARY
    # =====================================================

    analysis = analyze_transactions(
        transactions
    )

    st.subheader(
        "Financial Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Spending",
            f"₹{analysis['total_spending']:.2f}"
        )

    with col2:

        st.metric(
            "Transactions",
            len(transactions)
        )

    with col3:

        largest_expense = analysis["largest_expense"]

        if largest_expense["merchant"] is not None:

            st.metric(
                "Largest Expense",
                f"₹{largest_expense['amount']:.2f}"
            )

        else:

            st.metric(
                "Largest Expense",
                "₹0.00"
            )

    with col4:

        st.metric(
            "Top Category",
            analysis["highest_category"]
            if analysis["highest_category"] is not None
            else "None"
        )


    st.divider()


    # =====================================================
    # SPENDING CHARTS
    # =====================================================

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.subheader(
            "Spending by Category"
        )

        if analysis["category_breakdown"]:

            chart_data = {
                "Category": list(analysis["category_breakdown"].keys()),
                "Amount": list(analysis["category_breakdown"].values())
            }

            fig = px.bar(
                chart_data,
                x="Category",
                y="Amount"
            )

            fig.update_traces(
                marker_color=ACCENT
            )

            fig.update_layout(
                paper_bgcolor=PRIMARY,
                plot_bgcolor=PRIMARY,
                font_color=TEXT,
                xaxis=dict(
                    title="Category",
                    color=TEXT,
                    gridcolor="#33667A"
                ),
                yaxis=dict(
                    title="Amount (₹)",
                    color=TEXT,
                    gridcolor="#33667A"
                ),
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Add transactions to see spending by category."
            )


    with chart_col2:

        st.subheader(
            "Daily Spending"
        )

        daily_spending = {}

        for transaction in transactions:

            dt = datetime.fromisoformat(
                transaction["timestamp"]
            )

            date_key = dt.strftime("%Y-%m-%d")
            date_display = dt.strftime("%d/%m/%Y")

            if date_key not in daily_spending:

                daily_spending[date_key] = {
                    "display": date_display,
                    "amount": 0
                }

            daily_spending[date_key]["amount"] += float(
                transaction["amount"]
            )

        if daily_spending:

            sorted_daily_spending = sorted(
                daily_spending.items()
            )

            chart_data = {
                item[1]["display"]: item[1]["amount"]
                for item in sorted_daily_spending
            }

            fig = px.line(
                x=list(chart_data.keys()),
                y=list(chart_data.values()),
                markers=True
            )

            fig.update_traces(
                line_color=ACCENT,
                marker_color=ACCENT
            )

            fig.update_layout(
                paper_bgcolor=PRIMARY,
                plot_bgcolor=PRIMARY,
                font_color=TEXT,
                xaxis=dict(
                    title="Date",
                    color=TEXT,
                    gridcolor="#33667A"
                ),
                yaxis=dict(
                    title="Amount (₹)",
                    color=TEXT,
                    gridcolor="#33667A"
                ),
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Add transactions to see daily spending."
            )


    st.divider()


    # =====================================================
    # BUDGET
    # =====================================================

    st.subheader(
        "Monthly Category Budget"
    )

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    budgets = get_budgets(
        username
    )

    category = st.selectbox(
        "Budget category",
        CATEGORIES,
        key="budget_category"
    )

    budget_amount = st.number_input(
        "Monthly budget",
        min_value=0.0,
        step=100.0,
        key="budget_amount"
    )

    if st.button(
        "Set Budget"
    ):

        if budget_amount <= 0:

            st.error(
                "Budget must be greater than ₹0."
            )

        else:

            set_budget(
                username,
                category,
                budget_amount,
                current_month
            )

            st.success(
                f"{category} budget set to ₹{budget_amount:.2f}."
            )

            st.rerun()


    st.divider()


    # =====================================================
    # BUDGET STATUS
    # =====================================================

    st.subheader(
        "Budget Status"
    )

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    budget_status = calculate_budget_status(
        username,
        transactions,
        current_month
    )

    if not budget_status:

        st.info(
            "No budget set for this month."
        )

    else:

        for category, data in budget_status.items():

            st.write(
                f"**{category}**"
            )

            st.write(
                f"Budget: ₹{data['budget']:.2f}"
            )

            st.write(
                f"Spent: ₹{data['spent']:.2f}"
            )

            st.write(
                f"Remaining: ₹{data['remaining']:.2f}"
            )

            if data["status"] == "Over budget":

                st.markdown(
                    f"""
                    <div style="
                        background-color: #8F0000;
                        color: #FFFFE4;
                        padding: 12px 16px;
                        border-radius: 8px;
                        border: 2px solid #8F0000;
                        margin: 8px 0;
                        font-weight: 600;	
                    ">
                        {category} is over budget by ₹{data['over_amount']:.2f}.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.success(
                    f"{category} is within budget."
                )

            if st.button(
                f"Delete {category} Budget",
                key=f"delete_budget_{category}"
            ):

                delete_budget(
                    username,
                    category,
                    current_month
                )

                st.success(
                    f"{category} budget deleted."
                )

                st.rerun()

    st.divider()


    # =====================================================
    # ADD TRANSACTION
    # =====================================================

    st.subheader(
        "Add Transaction"
    )

    merchant = st.text_input(
        "Merchant"
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0
    )

    category = st.selectbox(
        "Category",
        CATEGORIES
    )

    if st.button(
        "Add Transaction"
    ):

        add_transaction(
            username,
            merchant,
            amount,
            category
        )

        st.success(
            "Transaction added"
        )

        st.rerun()


    st.divider()

    # =====================================================
    # SO₹TED ADVISOR
    # =====================================================

    if APP_MODE == "local":

        st.subheader(
            "SO₹TED Advisor"
        )

        if len(transactions) == 0:

            st.info(
                "Add some transactions first so SO₹TED AI can analyze your spending."
            )

        else:

            if st.button(
                "Generate Financial Advice"
            ):

                from backend.advisor import generate_advice

                with st.spinner(
                    "SO₹TED AI is sorting..."
                ):

                    advice = generate_advice(
                        username,
                        profile,
                        transactions
                    )

                st.markdown(
                    advice
                )
        st.divider()
    
    # =====================================================
    # TRANSACTION HISTORY
    # =====================================================

    st.subheader(
        "Transaction History"
    )

    transactions = get_transactions(
        username
    )

    search_text = st.text_input(
        "Search transactions"
    )

    filter_category = st.selectbox(
        "Filter by category",
        ["All"] + CATEGORIES,
        key="transaction_filter"
    )

    sort_option = st.selectbox(
        "Sort by",
        [
            "Newest first",
            "Oldest first",
            "Highest amount",
            "Lowest amount"
        ],
        key="transaction_sort"
    )

    filtered_transactions = []


    # =====================================================
    # SEARCH + FILTER
    # =====================================================

    for index, transaction in enumerate(transactions):

        matches_search = (
            search_text.lower()
            in transaction["merchant"].lower()
            or
            search_text.lower()
            in transaction["category"].lower()
        )

        matches_category = (
            filter_category == "All"
            or
            transaction["category"] == filter_category
        )

        if matches_search and matches_category:

            filtered_transactions.append(
                (index, transaction)
            )


    # =====================================================
    # SORT
    # =====================================================

    if sort_option == "Newest first":

        filtered_transactions.sort(
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )

    elif sort_option == "Oldest first":

        filtered_transactions.sort(
            key=lambda x: x[1]["timestamp"]
        )

    elif sort_option == "Highest amount":

        filtered_transactions.sort(
            key=lambda x: float(
                x[1]["amount"]
            ),
            reverse=True
        )

    elif sort_option == "Lowest amount":

        filtered_transactions.sort(
            key=lambda x: float(
                x[1]["amount"]
            )
        )


    # =====================================================
    # DISPLAY TRANSACTIONS
    # =====================================================

    if len(transactions) == 0:

        st.info(
            "No transactions yet"
        )

    elif len(filtered_transactions) == 0:

        st.info(
            "No transactions match your search."
        )

    else:

        for index, transaction in filtered_transactions:

            dt = datetime.fromisoformat(
                transaction["timestamp"]
            )

            st.write(
                f"{dt.strftime('%d %b %Y %I:%M %p')} | "
                f"{transaction['merchant']} | "
                f"₹{transaction['amount']:.2f} | "
                f"{transaction['category']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Edit",
                    key=f"edit_{index}"
                ):

                    st.session_state.editing_transaction = index

                    st.rerun()

            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_{index}"
                ):

                    delete_transaction(
                        username,
                        index
                    )

                    st.session_state.editing_transaction = None

                    st.rerun()


    # =====================================================
    # EDIT TRANSACTION
    # =====================================================

    if st.session_state.editing_transaction is not None:

        index = st.session_state.editing_transaction

        if 0 <= index < len(transactions):

            transaction = transactions[index]

            st.divider()

            st.subheader(
                "Edit Transaction"
            )

            edit_merchant = st.text_input(
                "Merchant",
                value=transaction["merchant"],
                key=f"edit_merchant_{index}"
            )

            edit_amount = st.number_input(
                "Amount",
                value=float(transaction["amount"]),
                key=f"edit_amount_{index}"
            )

            edit_category = st.selectbox(
                "Category",
                CATEGORIES,
                index=CATEGORIES.index(
                    transaction["category"]
                ),
                key=f"edit_category_{index}"
            )

            if st.button(
                "Save Changes"
            ):

                edit_transaction(
                    username,
                    index,
                    edit_merchant,
                    edit_amount,
                    edit_category
                )

                st.session_state.editing_transaction = None

                st.success(
                    "Transaction updated"
                )

                st.rerun()

        else:

            st.session_state.editing_transaction = None
