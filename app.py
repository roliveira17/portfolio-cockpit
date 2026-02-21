"""Portfolio Cockpit — Entry point Streamlit multipage."""

import streamlit as st

st.set_page_config(
    page_title="Portfolio Cockpit",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def check_auth() -> bool:
    """Autenticação simples por senha via st.secrets."""
    if st.session_state.get("authenticated"):
        return True

    password = st.secrets.get("auth", {}).get("password", "")
    if not password:
        return True

    st.markdown("## 🏦 Portfolio Cockpit")
    st.markdown("Digite a senha para acessar o dashboard.")
    entered = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if entered == password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    return False


def main():
    if not check_auth():
        st.stop()

    st.sidebar.markdown("## 🏦 Portfolio Cockpit")
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Family Office GARP Dashboard*")

    pages = [
        st.Page("pages/1_overview.py", title="Overview", icon="📊", default=True),
        st.Page("pages/2_positions.py", title="Positions", icon="💼"),
        st.Page("pages/3_risk_macro.py", title="Risk & Macro", icon="⚠️"),
        st.Page("pages/4_chat.py", title="Assessor", icon="💬"),
        st.Page("pages/5_knowledge_base.py", title="Knowledge Base", icon="📚"),
        st.Page("pages/6_simulator.py", title="Simulator", icon="🔬"),
    ]
    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()
