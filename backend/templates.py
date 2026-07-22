# backend/templates.py
# Estrutura para documentos LCA/LCC
# Cada tabela é um dicionário com chaves para cada processo

# Processos padrão
PROCESSOS_PADRAO = ["Demagnetisation", "Crushing / Grinding", "Aqua regia microwave digestion", "ICP-OES/-MS"]

DATASOURCE_OPTIONS = ["Medido", "Calculado", "Estimado", "Literatura"]

def criar_estrutura_vazia():
    """Cria uma estrutura vazia para um novo documento."""
    return {
        "lca": {
            "inputs": {},
            "processes": {},
            "outputs": {}
        },
        "lcc": {
            "materials": {},
            "equipment": {},
            "labour": {},
            "outputs": {}
        }
    }

def criar_estrutura_com_processos(processos):
    """
    Cria uma estrutura de documento com os processos especificados.
    Cada campo (inputs, processes, outputs, etc.) terá uma lista vazia para cada processo.
    """
    estrutura = criar_estrutura_vazia()
    
    # Para cada seção, criar listas vazias para cada processo
    for secao in ["lca", "lcc"]:
        for campo in estrutura[secao].keys():
            estrutura[secao][campo] = {p: [] for p in processos}
    
    return estrutura

def ensure_new_structure(data, processos):
    """
    Garante que a estrutura do documento tem todos os campos e processos necessários.
    """
    if not data:
        return criar_estrutura_com_processos(processos)
    
    # Verificar se a estrutura tem todas as seções
    if "lca" in data and "lcc" in data:
        # Verificar se todos os campos existem
        for secao in ["lca", "lcc"]:
            for campo in ["inputs", "processes", "outputs"] if secao == "lca" else ["materials", "equipment", "labour", "outputs"]:
                if campo not in data[secao]:
                    data[secao][campo] = {}
                # Verificar se todos os processos existem neste campo
                for p in processos:
                    if p not in data[secao][campo]:
                        data[secao][campo][p] = []
        return data
    
    # Se a estrutura não estiver no formato correto, recriar
    return criar_estrutura_com_processos(processos)

def get_processos_from_data(data):
    """
    Obtém a lista de processos a partir dos dados do documento.
    Se não houver processos definidos, retorna os processos padrão.
    """
    if data and "lca" in data and "inputs" in data["lca"]:
        processos = list(data["lca"]["inputs"].keys())
        if processos:
            return processos
    return PROCESSOS_PADRAO