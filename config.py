import json
import os

# Salva o arquivo de configuração no diretório home do usuário
CONFIG_DIR = os.path.expanduser("~/.config/QuizApp")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def salvar_configuracao(tema, multiplicacoes, formulas):
    # Garante que o diretório de configuração exista
    os.makedirs(CONFIG_DIR, exist_ok=True)
    """
    Salva a configuração do usuário (tema, dados de multiplicação e fórmulas)
    em um arquivo JSON.
    """
    try:
        config_data = {
            "tema_ativo_nome": tema,
            "multiplicacoes_data": multiplicacoes,
            "custom_formulas_data": formulas
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except (IOError, TypeError) as e:
        print(f"Erro ao salvar a configuração em {CONFIG_FILE}: {e}")

def criar_configuracao_padrao():
    """
    Cria um arquivo de configuração padrão se ele não existir.
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"Arquivo de configuração não encontrado. Criando um novo em {CONFIG_FILE}")
        # Define uma configuração padrão mínima
        config_padrao = {
            "tema_ativo_nome": "colorido", # Um tema padrão
            "multiplicacoes_data": None, # Será inicializado no main.py se for None
            "custom_formulas_data": [] # Começa com nenhuma fórmula personalizada
        }
        # A função salvar_configuracao lida com a criação do diretório
        salvar_configuracao(
            config_padrao["tema_ativo_nome"],
            config_padrao["multiplicacoes_data"],
            config_padrao["custom_formulas_data"]
        )
        return True # Indica que um novo arquivo foi criado
    return False # Indica que o arquivo já existia

def carregar_configuracao():
    """
    Carrega a configuração do usuário a partir de um arquivo JSON.
    Se o arquivo não existir, ele cria um com valores padrão.
    """
    # Garante que um arquivo de configuração exista antes de tentar carregar
    criar_configuracao_padrao()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # Validação básica para garantir que as chaves esperadas estão presentes
        tema = config_data.get("tema_ativo_nome")
        multiplicacoes = config_data.get("multiplicacoes_data")
        formulas = config_data.get("custom_formulas_data")

        return tema, multiplicacoes, formulas

    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar ou decodificar {CONFIG_FILE}: {e}. Retornando configuração nula.")
        # Se o arquivo estiver corrompido, retornar None para que o main.py possa lidar com isso
        # (por exemplo, reinicializando os dados de multiplicação)
        return None, None, None
