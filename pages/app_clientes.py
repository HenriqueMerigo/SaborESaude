import streamlit as st
import pandas as pd
import sqlite3
import re
from database import conecta_db

# Importações do CRUD de clientes
from crud_create import insert_cliente
from crud_update import update_cliente
from crud_delete import delete_cliente
from crud import cliente 

def formatar_telefone(tel):
    """
    Remove caracteres não numéricos e aplica a máscara (XX) XXXXX-XXXX
    """
    # Remove tudo que não for número
    numeros = re.sub(r'\D', '', tel)
    
    # Verifica se tem o tamanho esperado (DDD + 9 dígitos ou DDD + 8 dígitos)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    
    # Se não for um padrão reconhecido, retorna o que o usuário digitou limpo
    return tel

def get_categorias():
    """Busca as categorias de clientes para o Selectbox"""
    try:
        conn, cursor = conecta_db()
        df = pd.read_sql_query("SELECT id_cliente_categoria, ds_categoria FROM cliente_categoria", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame(columns=['id_cliente_categoria', 'ds_categoria'])

def main():
    # Inicialização de estados
    if 'mostrar_form_cliente' not in st.session_state:
        st.session_state.mostrar_form_cliente = False
    if 'modo_cliente' not in st.session_state:
        st.session_state.modo_cliente = None
    if 'cliente_selecionado' not in st.session_state:
        st.session_state.cliente_selecionado = None

    # --- CABEÇALHO ---
    col_titulo, col_voltar = st.columns([4, 2], vertical_alignment="bottom")
    with col_titulo:
        st.title("👥 Gestão de Clientes")
    with col_voltar:
        if st.button('🔙 Voltar ao Menu', use_container_width=True):
            st.switch_page("app.py")
    
    st.divider()

    # --- BUSCA E LISTAGEM ---
    df_clientes = pd.DataFrame()
    try:
        conn, cursor = conecta_db()
        c_busca, _ = st.columns([2, 1])
        with c_busca:
            busca = st.text_input("Filtrar clientes", placeholder="Nome do cliente...", label_visibility="collapsed")
        
        # Query com JOIN para mostrar o nome da categoria em vez de apenas o ID
        query = f"""
        SELECT 
            c.id_cliente AS 'ID',
            c.ds_cliente AS 'Nome',
            cat.ds_categoria AS 'Categoria',
            c.id_cliente_categoria,
            c.ds_telefone AS 'Telefone',
            c.ds_endereco AS 'Endereço'
        FROM cliente c
        LEFT JOIN cliente_categoria cat ON c.id_cliente_categoria = cat.id_cliente_categoria
        WHERE c.ds_cliente LIKE '%{busca}%'
        """
        df_clientes = pd.read_sql_query(query, conn)
        conn.close()

        if not df_clientes.empty:
            st.dataframe(df_clientes.drop(columns=['id_cliente_categoria']), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cliente cadastrado.")

    except Exception as e:
        st.error(f"Erro ao carregar lista: {e}")

    # --- BOTÕES DE AÇÃO ---
    st.write("")
    c1, c2, c3 = st.columns(3)
    
    if c1.button("➕ Novo Cliente", use_container_width=True):
        st.session_state.mostrar_form_cliente = True
        st.session_state.modo_cliente = 'inserir'
        st.session_state.cliente_selecionado = None
        st.rerun()

    if c2.button("📝 Editar Cliente", use_container_width=True):
        st.session_state.modo_cliente = 'pre-editar'
        st.session_state.mostrar_form_cliente = False
        st.rerun()

    if c3.button("🗑️ Excluir Cliente", use_container_width=True):
        st.session_state.modo_cliente = 'pre-excluir'
        st.session_state.mostrar_form_cliente = False
        st.rerun()

    # --- LÓGICA DE SELEÇÃO ---
    if not df_clientes.empty:
        if st.session_state.modo_cliente == 'pre-editar':
            with st.status("🔍 Selecionar Cliente", expanded=True):
                escolha = st.selectbox("Escolha:", options=df_clientes['Nome'].tolist())
                dados_c = df_clientes[df_clientes['Nome'] == escolha].iloc[0]
                
                if st.button("✅ Editar Selecionado", type="primary"):
                    st.session_state.cliente_selecionado = dados_c.to_dict()
                    st.session_state.modo_cliente = 'editar'
                    st.session_state.mostrar_form_cliente = True
                    st.rerun()

        elif st.session_state.modo_cliente == 'pre-excluir':
            with st.expander("⚠️ Confirmar Exclusão", expanded=True):
                escolha = st.selectbox("Remover:", options=df_clientes['Nome'].tolist())
                dados_c = df_clientes[df_clientes['Nome'] == escolha].iloc[0]
                if st.button(f"Confirmar Exclusão de {escolha}", type="primary"):
                    conn, cursor = conecta_db()
                    delete_cliente(conexao=conn, cursor=cursor, ds_cliente=escolha)
                    conn.close()
                    st.session_state.modo_cliente = None
                    st.rerun()

    # --- FORMULÁRIO ---
    if st.session_state.mostrar_form_cliente:
        st.divider()
        modo = st.session_state.modo_cliente
        item = st.session_state.cliente_selecionado
        df_cats = get_categorias()
        
        with st.form("form_cliente"):
            st.subheader("Cadastro/Edição de Cliente")
            
            nome = st.text_input("Nome do Cliente (ds_cliente)", value=item['Nome'] if item else "")
            
            # Selectbox para Categoria
            if not df_cats.empty:
                cat_options = df_cats['ds_categoria'].tolist()
                index_cat = 0
                if item and item['Categoria'] in cat_options:
                    index_cat = cat_options.index(item['Categoria'])
                
                cat_escolhida = st.selectbox("Categoria (id_cliente_categoria)", options=cat_options, index=index_cat)
                id_cat_final = int(df_cats[df_cats['ds_categoria'] == cat_escolhida]['id_cliente_categoria'].values[0])
            else:
                st.warning("Nenhuma categoria de cliente cadastrada!")
                id_cat_final = 0

            # Input de telefone com dica de formato
            tel_raw = st.text_input("Telefone (ds_telefone)", value=item['Telefone'] if item else "", help="Digite apenas números (Ex: 11999998888)")
            
            end = st.text_area("Endereço (ds_endereco)", value=item['Endereço'] if item else "")

            if st.form_submit_button("Salvar Registro", type="primary", use_container_width=True):
                try:
                    # Aplica a formatação antes de enviar para o objeto
                    tel_formatado = formatar_telefone(tel_raw)
                    
                    obj_c = cliente(
                        id_cliente = int(item['ID']) if modo == 'editar' else None,
                        ds_cliente = nome,
                        id_cliente_categoria = id_cat_final,
                        ds_telefone = tel_formatado,
                        ds_endereco = end
                    )
                    
                    conn, cursor = conecta_db()
                    if modo == 'inserir':
                        insert_cliente(obj_cliente=obj_c, conexao=conn, cursor=cursor)
                        st.success("Cliente cadastrado com sucesso!")
                    else:
                        update_cliente(conexao=conn, cursor=cursor, obj_cliente=obj_c)
                        st.success("Cliente atualizado com sucesso!")
                    conn.close()
                    
                    st.session_state.mostrar_form_cliente = False
                    st.session_state.modo_cliente = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        if st.button("Cancelar"):
            st.session_state.mostrar_form_cliente = False
            st.rerun()

if __name__ == "__main__":
    main()