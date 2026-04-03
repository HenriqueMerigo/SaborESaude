from database import conecta_db
import os

def localiza_tabela(tabela):

    match tabela:
        case 'cliente_categoria':
            print("Você escolheu a tabela cliente_categoria.")
            tabela = 'cliente_categoria'
        
        case 'cliente':
            print("Você escolheu a tabela cliente.")
            tabela = 'cliente'
        
        case 'forma_pagamento':
            print("Você escolheu a tabela forma_pagamento.")
            tabela = 'forma_pagamento'

        case 'pedido_status':
            print("Você escolheu a tabela pedido_status.")
            tabela = 'pedido_status'

        case 'pedido':
            print("Você escolheu a tabela pedido.")
            tabela = 'pedido'
        
        case 'produto_categoria':
            print("Você escolheu a tabela produto_categoria.")
            tabela = 'produto_categoria'

        case 'unidade_medida':
            print("Você escolheu a tabela unidade_medida.")
            tabela = 'unidade_medida'

        case 'produto':
            print("Você escolheu a tabela produto.")
            tabela = 'produto'

        case 'pedido_produto':
            print("Você escolheu a tabela pedido_produto.")
            tabela = 'pedido_produto'

        case _:
            print("Opção inválida (equivalente ao default).")



def __main__():
    conexao, cursor = conecta_db()
    tabela = input("Digite o nome da tabela que deseja acessar: ")
    localiza_tabela(tabela)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    __main__()