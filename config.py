import json
import os

# Salva o arquivo de configuração no diretório home do usuário
CONFIG_DIR = os.path.expanduser("~/.config/QuizApp")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def salvar_configuracao(tema, multiplicacoes, formulas, pesos_tabuadas, pontuacao_maxima_cronometrado=None):
    # Garante que o diretório de configuração exista
    os.makedirs(CONFIG_DIR, exist_ok=True)
    """
    Salva a configuração do usuário, incluindo a pontuação máxima do modo cronometrado.
    """
    try:
        # Primeiro, carrega os dados existentes para não sobrescrever a pontuação
        # se ela não for passada como argumento.
        config_existente = carregar_configuracao() if os.path.exists(CONFIG_FILE) else {}
        pontuacao_existente = config_existente.get("pontuacao_maxima_cronometrado", 0)


        config_data = {
            "tema_ativo_nome": tema,
            "multiplicacoes_data": multiplicacoes,
            "custom_formulas_data": formulas,
            "pesos_tabuadas": pesos_tabuadas,
            "pontuacao_maxima_cronometrado": pontuacao_maxima_cronometrado if pontuacao_maxima_cronometrado is not None else pontuacao_existente
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    except (IOError, TypeError) as e:
        print(f"Erro ao salvar a configuração em {CONFIG_FILE}: {e}")

def salvar_tema(tema):
    """
    Salva apenas a configuração do tema do usuário.
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config_existente = carregar_configuracao() if os.path.exists(CONFIG_FILE) else {}

        # Atualiza o tema na configuração existente
        config_existente["tema_ativo"] = tema

        # Salva o objeto de configuração completo de volta no arquivo
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            # Prepara os dados para salvar, garantindo que todas as chaves esperadas estejam presentes
            config_data_to_save = {
                "tema_ativo_nome": config_existente.get("tema_ativo"),
                "multiplicacoes_data": config_existente.get("multiplicacoes_data"),
                "custom_formulas_data": config_existente.get("custom_formulas_data"),
                "pesos_tabuadas": config_existente.get("pesos_tabuadas"),
                "pontuacao_maxima_cronometrado": config_existente.get("pontuacao_maxima_cronometrado")
            }
            json.dump(config_data_to_save, f, indent=4, ensure_ascii=False)
    except (IOError, TypeError) as e:
        print(f"Erro ao salvar o tema em {CONFIG_FILE}: {e}")

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
            "custom_formulas_data": [], # Começa com nenhuma fórmula personalizada
            "pesos_tabuadas": {str(i): 1.0 for i in range(1, 11)},
            "pontuacao_maxima_cronometrado": 0
        }
        # A função salvar_configuracao lida com a criação do diretório
        salvar_configuracao(
            config_padrao["tema_ativo_nome"],
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
            "tema_ativo": config_data.get("tema_ativo_nome"),
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
