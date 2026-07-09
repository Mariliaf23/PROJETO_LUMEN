"""
test_devolucao.py - Script para testar devolução de empréstimos
"""

import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_config import (
    listar_emprestimos_ativos, finalizar_emprestimo, gerar_multa,
    _conectar
)
from mysql.connector import Error

def diagnosticar_emprestimos():
    """Verifica os empréstimos ativos no banco"""
    print("=" * 60)
    print("DIAGNÓSTICO DE EMPRÉSTIMOS")
    print("=" * 60)
    
    emprestimos = listar_emprestimos_ativos()
    
    if not emprestimos:
        print("❌ Nenhum empréstimo ativo encontrado")
        return None
    
    print(f"✓ Encontrados {len(emprestimos)} empréstimos ativos\n")
    
    for emp in emprestimos:
        print(f"ID Empréstimo: {emp[0]}")
        print(f"  Aluno: {emp[1]}")
        print(f"  Exemplar: {emp[2]}")
        print(f"  Livro: {emp[3]}")
        print(f"  Data Empréstimo: {emp[4]}")
        print(f"  Data Prevista: {emp[5]}")
        print(f"  Status: {emp[6]}")
        print()
    
    return emprestimos[0] if emprestimos else None

def testar_devolucao(emp):
    """Testa o processo de devolução"""
    if not emp:
        print("Nenhum empréstimo para testar")
        return
    
    emp_id = emp[0]
    print("=" * 60)
    print(f"TESTANDO DEVOLUÇÃO - ID: {emp_id}")
    print("=" * 60)
    
    # Valida dados
    print(f"\n1. Validando dados do empréstimo...")
    print(f"   ID Exemplar esperado: {emp[2]}")
    
    conn = _conectar()
    cursor = conn.cursor()
    
    # Verifica exemplar no banco
    cursor.execute("SELECT id_exemplar FROM emprestimo WHERE id_emprestimo = %s", (emp_id,))
    resultado = cursor.fetchone()
    
    if resultado:
        id_exemplar = resultado[0]
        print(f"   ✓ ID Exemplar no BD: {id_exemplar}")
    else:
        print(f"   ❌ Empréstimo {emp_id} não encontrado!")
        conn.close()
        return
    
    # Verifica se exemplar existe
    cursor.execute("SELECT id_exemplar, status_exemplar FROM exemplar WHERE id_exemplar = %s", (id_exemplar,))
    ex_result = cursor.fetchone()
    
    if ex_result:
        print(f"   ✓ Exemplar existe: {ex_result}")
    else:
        print(f"   ❌ Exemplar {id_exemplar} não existe no BD!")
    
    conn.close()
    
    # Tenta finalizar
    print(f"\n2. Tentando finalizar empréstimo...")
    sucesso = finalizar_emprestimo(emp_id)
    
    if sucesso:
        print(f"   ✓ Devolução processada com sucesso!")
    else:
        print(f"   ❌ Erro ao processar devolução")
    
    print()

if __name__ == "__main__":
    emp = diagnosticar_emprestimos()
    testar_devolucao(emp)
