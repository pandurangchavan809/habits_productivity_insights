import streamlit as st
from database import register_user, validate_user


def login_signup_ui():
    st.markdown("<h3 style='text-align:center;'>🔐 Login & Sign Up</h3>", unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑 Login", "🆕 Sign Up"])

    # LOGIN TAB

    with tab_login:
        st.subheader("Login to your account")

        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", use_container_width=True, key="login_btn"):
            if not login_username or not login_password:
                st.error("Please fill in both username and password.")
            else:
                user_id = validate_user(login_username, login_password)
                if user_id:
                    st.session_state["user_id"] = user_id
                    st.session_state["username"] = login_username
                    st.success("🎉 Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

   
    # SIGNUP TAB
    
    with tab_signup:
        st.subheader("Create a new account")

        signup_username = st.text_input("Choose a Username", key="signup_user")
        signup_password = st.text_input("Choose a Password", type="password", key="signup_pass")

        if st.button("Sign Up", use_container_width=True, key="signup_btn"):
            if not signup_username or not signup_password:
                st.error("Please fill in all fields.")
            else:
                created = register_user(signup_username, signup_password)
                if created:
                    st.success("🎉 Account created! You can now log in.")
                else:
                    st.error("Username already exists. Try another name.")


def logout_button():
    """Adds a logout button when the user is logged in."""
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
