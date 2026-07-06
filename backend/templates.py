# backend/templates.py
# Estrutura para documentos LCA/LCC
# Cada tabela é um dicionário com chaves para cada processo

PROCESSOS = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]

LCA_LCC_TEMPLATE = {
    "lca": {
        "inputs": {p: [] for p in PROCESSOS},
        "processes": {p: [] for p in PROCESSOS},  # cada processo tem 3 linhas (Energy, Power, Time)
        "outputs": {p: [] for p in PROCESSOS}
    },
    "lcc": {
        "materials": {p: [] for p in PROCESSOS},
        "equipment": {p: [] for p in PROCESSOS},
        "labour": {p: [] for p in PROCESSOS},
        "outputs": {p: [] for p in PROCESSOS}
    }
}

DATASOURCE_OPTIONS = ["Medido", "Calculado", "Estimado", "Literatura"]