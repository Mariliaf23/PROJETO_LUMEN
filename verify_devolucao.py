"""
verify_devolucao.py - Verifica se a devolução foi registrada corretamente
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_config import _conectar

def verificar():
    conn = _conectar()
    cursor = conn.cursor()
    
    print("Verificando registro de devolução...\n")
    
    # Verifica empréstimo
    cursor.execute(
        """SELECT id_emprestimo, status, data_devolucao, data_prevista
           FROM emprestimo WHERE id_emprestimo = 1"""
    )
    emp = cursor.fetchone()
    
    if emp:
        print(f"✓ Empréstimo ID: {emp[0]}")
        print(f"  Status: {emp[1]}")
        print(f"  Data Devolução: {emp[2]}")
        print(f"  Data Prevista: {emp[3]}")
    
    print()
    
    # Verifica exemplar
    cursor.execute(
        """SELECT id_exemplar, status_exemplar FROM exemplar WHERE id_exemplar = 1"""
    )
    ex = cursor.fetchone()
    
    if ex:
        print(f"✓ Exemplar ID: {ex[0]}")
        print(f"  Status: {ex[1]}")
    
    print()
    
    # Verifica multa
    cursor.execute(
        """SELECT id_multa, valor, status_pagamento FROM multa 
           WHERE id_emprestimo = 1"""
    )
    multa = cursor.fetchone()
    
    if multa:
        print(f"✓ Multa gerada:")
        print(f"  ID: {multa[0]}")
        print(f"  Valor: R$ {multa[1]:.2f}")
        print(f"  Status: {multa[2]}")
    else:
        print("✓ Nenhuma multa gerada (devolução no prazo ou sem atraso)")
    
    conn.close()

if __name__ == "__main__":
    verificar()
