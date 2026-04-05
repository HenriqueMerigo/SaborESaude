import streamlit as st
import pandas as pd

def main():
    st.title("Mainpage")
    st.divider()

    # Criando duas colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Pedidos", use_container_width=True):
            st.switch_page("pages/app_pedidos.py")

    with col2:
        if st.button('Produtos', use_container_width=True):
            st.switch_page("pages/app_produtos.py")

    with col3:
        if st.button('Clientes', use_container_width=True):
            st.switch_page("pages/app_clientes.py")


if __name__ == "__main__":
    main()
