import sys
sys.path.insert(0, "src")

import pandas as pd
from util.posicoes import preparar_posicoes
from regras.ordenacao import ordenar_posicoes


dados = pd.DataFrame({
    "posicao": [
        "EAM3W2", "EAM3W1", "EAM300", "EAM301", "EAM302",
        "EAE110", "EAE110A", "EAE111", "EAE-W01",
        "EAM0W1", "EAM0W2", "EAM001", "EAM002",
        "EAM1W1", "EAM101",
    ],
    "material": ["M1"] * 15,
    "lote": ["L1"] * 15,
    "tipo_deposito": ["DEP"] * 15,
    "estoque_atual": [10] * 15,
})

estoque = preparar_posicoes(dados)
estoque = ordenar_posicoes(estoque)

print(f"{'ordem':>5} | {'posicao':<10} | rua numero prioridade nivel sufixo")
print("-" * 65)
for i, row in estoque.iterrows():
    print(f"{i:5d} | {row['posicao']:<10} | "
          f"{row['rua']}    "
          f"{str(row['numero_posicao']):>4}   "
          f"{row['prioridade_posicao']}         "
          f"{str(row['nivel']):>4}  "
          f"{row['sufixo']!r}")

ordem_esperada = [
    "EAE-W01",
    "EAE110", "EAE110A", "EAE111",
    "EAM0W2", "EAM3W2",
    "EAM0W1", "EAM1W1", "EAM3W1",
    "EAM300",
    "EAM001", "EAM101", "EAM301",
    "EAM002", "EAM302",
]

resultado = list(estoque["posicao"])
if resultado == ordem_esperada:
    print("\n ORDENACAO CORRETA!")
else:
    print("\n ORDENACAO INCORRETA!")
    print(f"Esperada: {ordem_esperada}")
    print(f"Obtida:   {resultado}")
    sys.exit(1)
