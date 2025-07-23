import json
import os

# Salva o arquivo de configuração no diretório home do usuário
CONFIG_DIR = os.path.expanduser("~/.config/QuizApp")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def salvar_configuracao(tema, multiplicacoes, formulas, pesos_tabuadas, pontuacao_maxima_cronometrado):
    """
    Salva toda a configuração do usuário.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_data = {
        "tema_ativo": tema,
        "multiplicacoes_data": multiplicacoes,
        "custom_formulas_data": formulas,
        "pesos_tabuadas": pesos_tabuadas,
        "pontuacao_maxima_cronometrado": pontuacao_maxima_cronometrado
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except (IOError, TypeError) as e:
        print(f"Erro ao salvar a configuração em {CONFIG_FILE}: {e}")

def salvar_tema(tema):
    """
    Salva apenas a configuração do tema do usuário, preservando os outros dados.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    config_existente = carregar_configuracao()

    # Atualiza apenas o tema
    config_existente["tema_ativo"] = tema

    # Salva a configuração completa de volta
    salvar_configuracao(
        config_existente["tema_ativo"],
        config_existente["multiplicacoes_data"],
        config_existente["custom_formulas_data"],
        config_existente["pesos_tabuadas"],
        config_existente["pontuacao_maxima_cronometrado"]
    )

def criar_configuracao_padrao():
    """
    Cria um arquivo de configuração padrão se ele não existir.
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"Arquivo de configuração não encontrado. Criando um novo em {CONFIG_FILE}")
        # Define uma configuração padrão mínima
        config_padrao = {
            "tema_ativo": "colorido", # Um tema padrão
            "multiplicacoes_data": None, # Será inicializado no main.py se for None
            "custom_formulas_data": [], # Começa com nenhuma fórmula personalizada
            "pesos_tabuadas": {str(i): 1.0 for i in range(1, 11)},
            "pontuacao_maxima_cronometrado": 0
        }
        # A função salvar_configuracao lida com a criação do diretório
        salvar_configuracao(
            config_padrao["tema_ativo"],
            config_padrao["multiplicacoes_data"],
            config_padrao["custom_formulas_data"],
            config_padrao["pesos_tabuadas"],
            config_padrao["pontuacao_maxima_cronometrado"]
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
        return {
            "tema_ativo": config_data.get("tema_ativo"),
            "multiplicacoes_data": config_data.get("multiplicacoes_data"),
            "custom_formulas_data": config_data.get("custom_formulas_data"),
            "pesos_tabuadas": config_data.get("pesos_tabuadas", {str(i): 1.0 for i in range(1, 11)}),
            "pontuacao_maxima_cronometrado": config_data.get("pontuacao_maxima_cronometrado", 0)
        }

    except (IOError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar ou decodificar {CONFIG_FILE}: {e}. Retornando configuração nula.")
        # Se o arquivo estiver corrompido, retornar None para que o main.py possa lidar com isso
        # (por exemplo, reinicializando os dados de multiplicação)
        return {
            "tema_ativo": "colorido",
            "multiplicacoes_data": None,
            "custom_formulas_data": [],
            "pesos_tabuadas": {str(i): 1.0 for i in range(1, 11)},
            "pontuacao_maxima_cronometrado": 0
        }
