import streamlit as st
import pandas as pd

def main():
    st.title("Mainpage")
    st.divider()

    # Criando duas colunas
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Produtos"):
            st.switch_page("pages/app_produtos.py")

    with col2:
        if st.button('Mainpage'):
            st.switch_page("app.py")


if __name__ == "__main__":
    main()
