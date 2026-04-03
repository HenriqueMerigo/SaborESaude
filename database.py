import sqlite3

def conecta_db():
    conexao = sqlite3.connect('prd_saboresaude.db')
    cursor = conexao.cursor()
    print(f'Conexão com o banco de dados estabelecida com sucesso!\n')
    return conexao, cursor