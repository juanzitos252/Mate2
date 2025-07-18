import flet as ft
from flet import (
    Page, Text, ElevatedButton, Row, Column, TextField, View, Container, Dropdown,
    MainAxisAlignment, CrossAxisAlignment, FontWeight, alignment,
    TextAlign, ScrollMode, padding, border, KeyboardType,
    Animation, AnimationCurve, ProgressBar, Icons, LinearGradient
)
import random
import time
import requests
from packaging import version
import subprocess
import threading
import os # Adicionado para manipulação de caminhos
import math # Adicionado para ceil e floor
from config import salvar_configuracao, carregar_configuracao

# --- Definições das Fórmulas Notáveis (Integrado de formula_definitions.py) ---

# --- Funções de Cálculo para Fórmulas Notáveis ---

def calc_quadrado_soma(a: int, b: int) -> int:
    """Calcula (a+b)^2."""
    return (a + b) ** 2

def calc_quadrado_diferenca(a: int, b: int) -> int:
    """Calcula (a-b)^2."""
    return (a - b) ** 2

def calc_produto_soma_diferenca(a: int, b: int) -> int:
    """Calcula a^2 - b^2."""
    return a**2 - b**2

def calc_raiz_soma_diferenca(a: int, b: int) -> int:
    """Calcula a - b, onde a e b são os números DENTRO das raízes na pergunta."""
    return a - b

# --- Definições da Lista de Fórmulas Notáveis ---
FORMULAS_NOTAVEIS = [
    {
        'id': "quadrado_soma",
        'display_name': "Quadrado da Soma: (a+b)^2",
        'variables': ['a', 'b'],
        'calculation_function': calc_quadrado_soma,
        'question_template': "Se a={a} e b={b}, qual o valor de (a+b)^2?",
        'reminder_template': "(x+y)^2 = x^2 + 2xy + y^2",
        'range_constraints': {},
        'variable_labels': {'a': "Valor de 'a'", 'b': "Valor de 'b'"}
    },
    {
        'id': "quadrado_diferenca",
        'display_name': "Quadrado da Diferença: (a-b)^2",
        'variables': ['a', 'b'],
        'calculation_function': calc_quadrado_diferenca,
        'question_template': "Se a={a} e b={b}, qual o valor de (a-b)^2?",
        'reminder_template': "(x-y)^2 = x^2 - 2xy + y^2",
        'range_constraints': {},
        'variable_labels': {'a': "Valor de 'a'", 'b': "Valor de 'b'"}
    },
    {
        'id': "produto_soma_diferenca",
        'display_name': "Produto da Soma pela Diferença: (a+b)(a-b)",
        'variables': ['a', 'b'],
        'calculation_function': calc_produto_soma_diferenca,
        'question_template': "Se a={a} e b={b}, qual o valor de (a+b)(a-b)?",
        'reminder_template': "(x+y)(x-y) = x^2 - y^2",
        'range_constraints': {'b': {'less_than_equal_a': True}},
        'variable_labels': {'a': "Valor de 'a'", 'b': "Valor de 'b' (b <= a)"}
    },
    {
        'id': "raiz_soma_diferenca",
        'display_name': "Diferença de Quadrados (Raízes): (sqrt(a)+sqrt(b))(sqrt(a)-sqrt(b))",
        'variables': ['a', 'b'],
        'calculation_function': calc_raiz_soma_diferenca,
        'question_template': "Qual o valor de (sqrt({a}) + sqrt({b})) * (sqrt({a}) - sqrt({b}))?",
        'reminder_template': "(sqrt(x) + sqrt(y))(sqrt(x) - sqrt(y)) = x - y",
        'range_constraints': {
            'a': {'min': 2},
            'b': {'less_than_a': True, 'min': 1}
        },
        'variable_labels': {
            'a': "Valor de 'a' (dentro da sqrt, a > b)",
            'b': "Valor de 'b' (dentro da sqrt, b < a)"
        }
    },
    {
        'id': "grandezas_diretamente_proporcionais",
        'display_name': "Grandezas Diretamente Proporcionais",
        'variables': ['valor_total', 'nome_irmao1', 'idade_irmao1', 'nome_irmao2', 'idade_irmao2'],
        'calculation_function': lambda **kwargs: f"{calc_divisao_diretamente_proporcional(kwargs['valor_total'], [(kwargs['nome_irmao1'], kwargs['idade_irmao1']), (kwargs['nome_irmao2'], kwargs['idade_irmao2'])])[kwargs['nome_irmao1']]},{calc_divisao_diretamente_proporcional(kwargs['valor_total'], [(kwargs['nome_irmao1'], kwargs['idade_irmao1']), (kwargs['nome_irmao2'], kwargs['idade_irmao2'])])[kwargs['nome_irmao2']]}",
        'question_template': "Maria precisa dividir R${valor_total} entre seus filhos, {nome_irmao1} de {idade_irmao1} anos e {nome_irmao2} de {idade_irmao2} anos, em partes diretamente proporcionais às suas idades. Quanto {nome_irmao1} receberá? E {nome_irmao2}?",
        'reminder_template': "Responda com os dois valores inteiros separados por vírgula (ex: 120,60), na ordem em que foram perguntados. Parte = (Idade / Soma das Idades) * Valor Total.",
        'range_constraints': {
            'valor_total': {'min': 20, 'max': 1000}, # Este range será um guia para o valor_total final
            'idade_irmao1': {'min': 1, 'max': 10},
            'idade_irmao2': {'min': 1, 'max': 10, 'not_equal_to_var': 'idade_irmao1'} # Para garantir idades diferentes e evitar divisão trivialmente igual
        },
        'variable_labels': {
            'valor_total': "Valor Total (R$) (será ajustado para divisão exata)",
            'nome_irmao1': "Nome Irmão(ã) 1", # Será preenchido aleatoriamente
            'idade_irmao1': "Idade Irmão(ã) 1 (1-10, inteiro)",
            'nome_irmao2': "Nome Irmão(ã) 2", # Será preenchido aleatoriamente
            'idade_irmao2': "Idade Irmão(ã) 2 (1-10, ≠ Idade 1, inteiro)"
        },
        'custom_variable_generators': {
            'nome_irmao1': lambda: random.choice(["Ana", "João", "Sofia"]),
            'nome_irmao2': lambda: random.choice(["Lucas", "Clara", "Pedro"])
        }
    },
    {
        'id': "grandezas_inversamente_proporcionais",
        'display_name': "Grandezas Inversamente Proporcionais",
        'variables': ['valor_total', 'nome_irmao1', 'idade_irmao1', 'nome_irmao2', 'idade_irmao2'],
        'calculation_function': lambda **kwargs: f"{calc_divisao_inversamente_proporcional(kwargs['valor_total'], [(kwargs['nome_irmao1'], kwargs['idade_irmao1']), (kwargs['nome_irmao2'], kwargs['idade_irmao2'])])[kwargs['nome_irmao1']]},{calc_divisao_inversamente_proporcional(kwargs['valor_total'], [(kwargs['nome_irmao1'], kwargs['idade_irmao1']), (kwargs['nome_irmao2'], kwargs['idade_irmao2'])])[kwargs['nome_irmao2']]}",
        'question_template': "Carlos quer dividir R${valor_total} entre seu filho {nome_irmao1} de {idade_irmao1} anos e sua filha {nome_irmao2} de {idade_irmao2} anos, em partes inversamente proporcionais às suas idades. Quanto {nome_irmao1} receberá? E {nome_irmao2}?",
        'reminder_template': "Responda com os dois valores inteiros separados por vírgula (ex: 60,120), na ordem em que foram perguntados. Parte = (Inverso da Idade Ajustado / Soma dos Inversos Ajustados) * Valor Total.",
        'range_constraints': {
            'valor_total': {'min': 20, 'max': 1000}, # Este range será um guia para o valor_total final
            'idade_irmao1': {'min': 1, 'max': 10}, # Idade não pode ser 0 para inversamente
            'idade_irmao2': {'min': 1, 'max': 10, 'not_equal_to_var': 'idade_irmao1'} # Idade não pode ser 0 e diferente da outra
        },
        'variable_labels': {
            'valor_total': "Valor Total (R$) (será ajustado para divisão exata)",
            'nome_irmao1': "Nome Filho(a) 1",
            'idade_irmao1': "Idade Filho(a) 1 (1-10, inteiro)",
            'nome_irmao2': "Nome Filho(a) 2",
            'idade_irmao2': "Idade Filho(a) 2 (1-10, ≠ Idade 1, inteiro)"
        },
        'custom_variable_generators': {
            'nome_irmao1': lambda: random.choice(["Bia", "Davi", "Laura"]),
            'nome_irmao2': lambda: random.choice(["Enzo", "Alice", "Miguel"])
        }
    },
]

def get_formula_definition(formula_id: str):
    for formula in FORMULAS_NOTAVEIS:
        if formula['id'] == formula_id:
            return formula
    return None

# --- Funções de Cálculo para Novas Fórmulas ---
def calc_divisao_diretamente_proporcional(valor_total: float, grandezas: list[tuple[str, float]]) -> dict[str, float]:
    """
    Calcula a divisão de um valor total de forma diretamente proporcional às grandezas fornecidas.
    Args:
        valor_total: O valor total a ser dividido.
        grandezas: Uma lista de tuplas, onde cada tupla contém o nome (str)
                   e o valor da grandeza (float). Ex: [("Manu", 4), ("Murilo", 2)]
    Returns:
        Um dicionário com o nome como chave e a parte correspondente como valor.
        Retorna um dicionário vazio se a soma das grandezas for zero para evitar divisão por zero.
    """
    soma_grandezas = sum(g[1] for g in grandezas)
    if soma_grandezas == 0:
        # Se a soma das grandezas é 0, e o valor_total não é 0, não é possível dividir.
        # Se valor_total também é 0, então cada parte é 0.
        # Para garantir inteiros, retornaremos 0 para todos se valor_total for 0,
        # ou um erro/dicionário vazio indicando impossibilidade.
        # Dado o contexto de idades, soma_grandezas > 0 é esperado.
        return {item[0]: 0 for item in grandezas}

    # Para garantir resultados inteiros, valor_total DEVE ser divisível pela soma_grandezas.
    # Esta função agora assume que os valores de entrada são tais que a divisão será inteira.
    # A lógica de garantir isso será movida para a geração da pergunta.
    if valor_total % soma_grandezas != 0:
        # Idealmente, isso não deveria acontecer se a geração da pergunta for correta.
        # Por ora, vamos forçar uma divisão inteira, mas isso pode levar a "perda" de valor.
        # A melhor abordagem é garantir que valor_total seja múltiplo de soma_grandezas.
        # Para este passo, vamos manter a expectativa de que a divisão será exata.
        # Se não for, o resultado não será "perfeitamente" proporcional em inteiros sem ajustes.
        # No entanto, a tarefa é que OS NÚMEROS APRESENTADOS sejam inteiros.
        # A função deve retornar inteiros.
        pass # A discussão sobre arredondamento ou ajuste de valor_total é para a geração.

    k = valor_total // soma_grandezas # Usar divisão inteira

    resultado = {}
    soma_distribuida = 0
    for i, (nome, grandeza_valor) in enumerate(grandezas):
        if i == len(grandezas) - 1: # Último item recebe o restante para garantir a soma exata
            parte = valor_total - soma_distribuida
        else:
            parte = grandeza_valor * k
        resultado[nome] = parte
        soma_distribuida += parte

    # Verificação final para garantir que a soma das partes é igual ao valor total
    if soma_distribuida != valor_total:
        # Este bloco pode ser alcançado se k não for inteiro e a lógica de distribuição acima
        # ainda assim não somar corretamente. A atribuição do restante ao último elemento visa evitar isso.
        # print(f"Alerta: Soma distribuída {soma_distribuida} != valor_total {valor_total}")
        # Ajuste simples: o último elemento recebe a diferença.
        # Isso já é feito no loop.
        pass

    return resultado

def mmc(a, b):
    """Calcula o Mínimo Múltiplo Comum de a e b."""
    if a == 0 or b == 0:
        return 0
    abs_a, abs_b = abs(a), abs(b)
    return abs(a*b) // mdc(a,b) if a !=0 and b != 0 else 0

def mdc(a, b):
    """Calcula o Máximo Divisor Comum de a e b."""
    while(b):
        a, b = b, a % b
    return a

def calc_divisao_inversamente_proporcional(valor_total: int, grandezas: list[tuple[str, int]]) -> dict[str, int]:
    """
    Calcula a divisão de um valor total de forma inversamente proporcional às grandezas fornecidas,
    garantindo resultados inteiros.
    Args:
        valor_total: O valor total a ser dividido (inteiro).
        grandezas: Uma lista de tuplas, onde cada tupla contém o nome (str)
                   e o valor da grandeza (inteiro > 0). Ex: [("Manu", 4), ("Murilo", 3)]
    Returns:
        Um dicionário com o nome como chave e a parte correspondente como valor (inteiro).
    """
    if not grandezas:
        return {}
    if any(g[1] <= 0 for g in grandezas):
        # Grandezas devem ser positivas para divisão inversa fazer sentido e evitar divisão por zero no cálculo do inverso.
        return {item[0]: 0 for item in grandezas} # Ou lançar erro

    # Passo 1: Encontrar o MMC de todas as grandezas (denominadores dos inversos)
    # Se grandezas são idades i1, i2, ..., in
    # Inversos: 1/i1, 1/i2, ..., 1/in
    # Para tornar proporcionais a inteiros, multiplicamos pelo MMC(i1, i2, ..., in)
    # Novas proporções: MMC/i1, MMC/i2, ..., MMC/in

    valores_grandezas = [g[1] for g in grandezas]

    if not valores_grandezas: return {}

    lcm = valores_grandezas[0]
    for i in range(1, len(valores_grandezas)):
        lcm = mmc(lcm, valores_grandezas[i])

    if lcm == 0: # Se alguma grandeza for 0, o mmc pode ser 0. Já tratado pela verificação g[1] <= 0
        return {item[0]: 0 for item in grandezas}

    proporcoes_inteiras = []
    soma_proporcoes_inteiras = 0
    for nome, val_g in grandezas:
        prop_inv_int = lcm // val_g # Esta será a "nova" grandeza para divisão direta
        proporcoes_inteiras.append({'nome': nome, 'prop': prop_inv_int, 'original_g': val_g})
        soma_proporcoes_inteiras += prop_inv_int

    if soma_proporcoes_inteiras == 0:
        # Isso aconteceria se todas as grandezas fossem extremamente grandes e lcm // val_g resultasse em 0 para todas.
        # Ou se houvesse um problema com o cálculo do MMC/proporções.
        # Com grandezas > 0, soma_proporcoes_inteiras deve ser > 0.
        return {item[0]: 0 for item in grandezas}

    # Agora, o problema é reduzido a uma divisão diretamente proporcional
    # usando as 'proporcoes_inteiras' e 'soma_proporcoes_inteiras'.
    # valor_total DEVE ser divisível por soma_proporcoes_inteiras para resultados perfeitamente inteiros.
    # Assim como no caso direto, essa garantia virá da geração da pergunta.

    # k = valor_total / soma_proporcoes_inteiras
    # Se k não for inteiro, a divisão não será "perfeita" em inteiros.
    # A função deve retornar inteiros.

    resultado = {}
    soma_distribuida = 0

    # Para garantir que a soma das partes seja exatamente valor_total,
    # distribuímos e ajustamos a última parte.
    for i, item_prop in enumerate(proporcoes_inteiras):
        if i == len(proporcoes_inteiras) - 1: # Último item
            parte = valor_total - soma_distribuida
        else:
            # A parte é (item_prop['prop'] / soma_proporcoes_inteiras) * valor_total
            # Para evitar float, e assumindo que valor_total é múltiplo de soma_proporcoes_inteiras:
            # parte = item_prop['prop'] * (valor_total // soma_proporcoes_inteiras)
            # Se não for múltiplo, a divisão não será exata.
            # A tarefa é que os números *apresentados* sejam inteiros.
            # A geração da pergunta deve garantir que `valor_total % soma_proporcoes_inteiras == 0`.
            # Por ora, se não for, haverá um "erro" de arredondamento implícito ou explícito.
            # Vamos usar a divisão inteira para k_inv e distribuir.
            if valor_total % soma_proporcoes_inteiras != 0:
                 # Sinaliza que a geração da pergunta precisa ser ajustada.
                 # print(f"Alerta Inverso: valor_total {valor_total} não é perfeitamente divisível por soma_proporcoes_inteiras {soma_proporcoes_inteiras}")
                 # Para fins de cálculo aqui, continuamos com a divisão inteira e ajustamos o último.
                 pass

            k_inv = valor_total // soma_proporcoes_inteiras # Constante de proporcionalidade (inteira ou não)
            parte = item_prop['prop'] * k_inv

        resultado[item_prop['nome']] = parte
        soma_distribuida += parte

    # Ajuste final se a soma não bater (principalmente se k_inv não fosse inteiro)
    # A lógica de atribuir o restante ao último item já cobre isso.
    if soma_distribuida != valor_total and len(proporcoes_inteiras) > 0:
        # Se houve um desvio e há itens para ajustar
        diff = valor_total - soma_distribuida
        # Adiciona a diferença ao último elemento que foi calculado (se houver)
        # Este ajuste é crucial para garantir que a soma das partes seja igual ao valor_total.
        # A última parte calculada no loop já é 'valor_total - soma_distribuida_anterior',
        # então este bloco pode ser redundante, mas é uma salvaguarda.
        ultimo_nome = proporcoes_inteiras[-1]['nome']
        resultado[ultimo_nome] += diff # Adiciona o que faltou/removeu o que excedeu

    return resultado

# --- Fim das Definições das Fórmulas Notáveis ---

# --- Lógica do Quiz ---
multiplicacoes_data = []
COOLDOWN_SEGUNDOS = 30

def inicializar_multiplicacoes():
    global multiplicacoes_data
    multiplicacoes_data = []
    for i in range(1, 11):
        for j in range(1, 11):
            multiplicacoes_data.append({
                'fator1': i, 'fator2': j, 'peso': 10.0, 'historico_erros': [],
                'vezes_apresentada': 0, 'vezes_correta': 0, 'ultima_vez_apresentada_ts': 0.0
            })

def selecionar_proxima_pergunta():
    global multiplicacoes_data
    agora_ts = time.time()
    perguntas_potenciais = [
        p for p in multiplicacoes_data if (agora_ts - p['ultima_vez_apresentada_ts']) > COOLDOWN_SEGUNDOS
    ]
    if not perguntas_potenciais:
        perguntas_potenciais = multiplicacoes_data
    if not perguntas_potenciais: return None
    perguntas_elegiveis_com_prioridade = []
    for pergunta_item in perguntas_potenciais:
        fator_peso = pergunta_item['peso']
        fator_erro_recente = 1.0
        if pergunta_item['historico_erros']:
            erros_recentes = sum(1 for erro in pergunta_item['historico_erros'] if erro)
            fator_erro_recente = 1 + (erros_recentes / len(pergunta_item['historico_erros']))
        fator_novidade = 1 / (1 + pergunta_item['vezes_apresentada'] * 0.05)
        prioridade = fator_peso * fator_erro_recente * fator_novidade
        perguntas_elegiveis_com_prioridade.append({'prioridade': prioridade, 'pergunta_original': pergunta_item})
    if not perguntas_elegiveis_com_prioridade:
        return random.choice(multiplicacoes_data) if multiplicacoes_data else None
    prioridades = [p['prioridade'] for p in perguntas_elegiveis_com_prioridade]
    perguntas_originais_refs = [p['pergunta_original'] for p in perguntas_elegiveis_com_prioridade]
    return random.choices(perguntas_originais_refs, weights=prioridades, k=1)[0]

def registrar_resposta(pergunta_selecionada_ref, acertou: bool):
    global tema_ativo_nome, multiplicacoes_data, custom_formulas_data
    if not pergunta_selecionada_ref: return
    pergunta_selecionada_ref['vezes_apresentada'] += 1
    pergunta_selecionada_ref['ultima_vez_apresentada_ts'] = time.time()
    pergunta_selecionada_ref['historico_erros'].append(not acertou)
    pergunta_selecionada_ref['historico_erros'] = pergunta_selecionada_ref['historico_erros'][-5:]
    if acertou:
        pergunta_selecionada_ref['vezes_correta'] += 1
        pergunta_selecionada_ref['peso'] = max(1.0, pergunta_selecionada_ref['peso'] * 0.7)
    else:
        pergunta_selecionada_ref['peso'] = min(100.0, pergunta_selecionada_ref['peso'] * 1.6)

    salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data)

def gerar_opcoes(fator1: int, fator2: int, todas_multiplicacoes_data_ref):
    resposta_correta = fator1 * fator2
    opcoes = {resposta_correta}
    tentativas_max = 30
    count_tentativas = 0
    while len(opcoes) < 4 and count_tentativas < tentativas_max:
        count_tentativas += 1
        tipo_variacao = random.choice(['fator_adjacente', 'resultado_proximo', 'aleatorio_da_lista'])
        nova_opcao = -1
        if tipo_variacao == 'fator_adjacente':
            fator_modificado = random.choice([1, 2])
            if fator_modificado == 1:
                f1_mod = max(1, fator1 + random.choice([-2, -1, 1, 2]))
                nova_opcao = f1_mod * fator2
            else:
                f2_mod = max(1, fator2 + random.choice([-2, -1, 1, 2]))
                nova_opcao = fator1 * f2_mod
        elif tipo_variacao == 'resultado_proximo':
            offset_options = [-1, 1, -2, 2, -3, 3]
            if fator1 > 1: offset_options.extend([-fator1 // 2, fator1 // 2])
            if fator2 > 1: offset_options.extend([-fator2 // 2, fator2 // 2])
            if not offset_options: offset_options = [-1, 1]
            offset = random.choice(offset_options)
            if offset == 0: offset = random.choice([-1, 1]) if offset_options != [-1, 1] else 1
            nova_opcao = resposta_correta + offset
        elif tipo_variacao == 'aleatorio_da_lista':
            if todas_multiplicacoes_data_ref:
                pergunta_aleatoria = random.choice(todas_multiplicacoes_data_ref)
                nova_opcao = pergunta_aleatoria['fator1'] * pergunta_aleatoria['fator2']
        if nova_opcao == resposta_correta: continue
        if nova_opcao > 0: opcoes.add(nova_opcao)
    idx = 1
    while len(opcoes) < 4:
        alternativa = resposta_correta + idx
        if alternativa not in opcoes and alternativa > 0: opcoes.add(alternativa)
        if len(opcoes) < 4:
            alternativa_neg = resposta_correta - idx
            if alternativa_neg > 0 and alternativa_neg not in opcoes: opcoes.add(alternativa_neg)
        idx += 1
        if idx > max(fator1, fator2, 10) + 20: break
    while len(opcoes) < 4:
        rand_num = random.randint(1, max(100, resposta_correta + 30))
        if rand_num > 0 and rand_num not in opcoes: opcoes.add(rand_num)
    lista_opcoes = list(opcoes)
    random.shuffle(lista_opcoes)
    return lista_opcoes

def gerar_opcoes_quiz_invertido(multiplicacao_base_ref, todas_multiplicacoes_data_ref):
    resposta_correta_valor = multiplicacao_base_ref['fator1'] * multiplicacao_base_ref['fator2']
    opcao_correta_obj = {'texto': f"{multiplicacao_base_ref['fator1']} x {multiplicacao_base_ref['fator2']}", 'original_ref': multiplicacao_base_ref, 'is_correct': True}
    opcoes_geradas = [opcao_correta_obj]
    candidatos_embaralhados = random.sample(todas_multiplicacoes_data_ref, len(todas_multiplicacoes_data_ref))
    for item_candidato in candidatos_embaralhados:
        if len(opcoes_geradas) >= 4: break
        if item_candidato['fator1'] == multiplicacao_base_ref['fator1'] and item_candidato['fator2'] == multiplicacao_base_ref['fator2']: continue
        if item_candidato['fator1'] * item_candidato['fator2'] == resposta_correta_valor: continue
        opcoes_geradas.append({'texto': f"{item_candidato['fator1']} x {item_candidato['fator2']}", 'original_ref': item_candidato, 'is_correct': False})
    tentativas_fallback = 0
    while len(opcoes_geradas) < 4 and tentativas_fallback < 50:
        tentativas_fallback += 1
        f1, f2 = random.randint(1, 10), random.randint(1, 10)
        if (f1 == multiplicacao_base_ref['fator1'] and f2 == multiplicacao_base_ref['fator2']) or (f1 * f2 == resposta_correta_valor): continue
        existe = any((op['original_ref']['fator1'] == f1 and op['original_ref']['fator2'] == f2) or \
                     (op['original_ref']['fator1'] == f2 and op['original_ref']['fator2'] == f1) for op in opcoes_geradas)
        if existe: continue
        dummy_ref = {'fator1': f1, 'fator2': f2, 'peso': 10.0, 'historico_erros': [], 'vezes_apresentada': 0, 'vezes_correta': 0, 'ultima_vez_apresentada_ts': 0.0}
        opcoes_geradas.append({'texto': f"{f1} x {f2}", 'original_ref': dummy_ref, 'is_correct': False})
    random.shuffle(opcoes_geradas)
    return opcoes_geradas[:4]

def sugerir_tabuada_para_treino():
    global multiplicacoes_data
    if not multiplicacoes_data: return random.randint(1,10)
    pesos_por_tabuada = {i: 0.0 for i in range(1, 11)}
    contagem_por_tabuada = {i: 0 for i in range(1, 11)}
    for item in multiplicacoes_data:
        fator1, fator2, peso = item['fator1'], item['fator2'], item['peso']
        if fator1 in pesos_por_tabuada:
            pesos_por_tabuada[fator1] += peso; contagem_por_tabuada[fator1] += 1
        if fator2 in pesos_por_tabuada and fator1 != fator2:
            pesos_por_tabuada[fator2] += peso; contagem_por_tabuada[fator2] += 1
    media_pesos = { tab: pesos_por_tabuada[tab] / contagem_por_tabuada[tab] if contagem_por_tabuada[tab] > 0 else 0 for tab in pesos_por_tabuada }
    if not any(v > 0 for v in media_pesos.values()): return random.randint(1,10) # Verifica se algum peso é maior que 0
    return max(media_pesos, key=media_pesos.get)

def calcular_estatisticas_gerais():
    global multiplicacoes_data
    if not multiplicacoes_data: return {'total_respondidas': 0, 'percentual_acertos_geral': 0, 'top_3_dificeis': []}
    total_respondidas = sum(item['vezes_apresentada'] for item in multiplicacoes_data)
    total_acertos = sum(item['vezes_correta'] for item in multiplicacoes_data)
    percentual_acertos_geral = (total_acertos / total_respondidas * 100) if total_respondidas > 0 else 0
    top_dificeis_completo = sorted(multiplicacoes_data, key=lambda x: (x['peso'], -x['vezes_correta'], x['vezes_apresentada']), reverse=True)
    top_3_dificeis_objs = [item for item in top_dificeis_completo if item['vezes_apresentada'] > 0][:3]
    top_3_dificeis_formatado = [f"{item['fator1']} x {item['fator2']}" for item in top_3_dificeis_objs]
    return {'total_respondidas': total_respondidas, 'percentual_acertos_geral': round(percentual_acertos_geral, 1), 'top_3_dificeis': top_3_dificeis_formatado}

def calcular_proficiencia_tabuadas():
    global multiplicacoes_data
    proficiencia_por_tabuada = {i: 0.0 for i in range(1, 11)}
    if not multiplicacoes_data: return proficiencia_por_tabuada

    for t in range(1, 11):
        itens_tabuada_t_apresentados, vistos_para_tabuada_t = [], set()
        for item_p in multiplicacoes_data:
            par_ordenado = tuple(sorted((item_p['fator1'], item_p['fator2'])))
            # Considerar apenas itens que foram apresentados
            if (item_p['fator1'] == t or item_p['fator2'] == t) and \
               par_ordenado not in vistos_para_tabuada_t and \
               item_p['vezes_apresentada'] > 0:
                itens_tabuada_t_apresentados.append(item_p)
                vistos_para_tabuada_t.add(par_ordenado)

        if not itens_tabuada_t_apresentados:
            # Se nenhum item da tabuada foi apresentado, a proficiência é 0
            proficiencia_por_tabuada[t] = 0.0
        else:
            # Calcular a média dos pesos apenas dos itens apresentados
            media_pesos = sum(it['peso'] for it in itens_tabuada_t_apresentados) / len(itens_tabuada_t_apresentados)
            # A fórmula de proficiência permanece a mesma, mas baseada em dados relevantes
            proficiencia_percentual = max(0, (100.0 - media_pesos) / (100.0 - 1.0)) * 100.0
            proficiencia_por_tabuada[t] = round(proficiencia_percentual, 1)

    return proficiencia_por_tabuada

def gerar_dados_heatmap():
    """
    Gera uma matriz 10x10 com a pontuação de dificuldade para cada multiplicação.
    A pontuação é baseada no 'peso' do item de multiplicação.
    Retorna a matriz e os pesos mínimo e máximo encontrados para normalização.
    """
    global multiplicacoes_data
    if not multiplicacoes_data:
        return [[0]*10 for _ in range(10)], 1.0, 10.0 # Retorna matriz de zeros se não houver dados

    # Inicializa a matriz do heatmap com um valor padrão (peso inicial)
    heatmap_data = [[10.0]*10 for _ in range(10)]
    min_peso, max_peso = float('inf'), float('-inf')

    # Cria um dicionário para acesso rápido aos itens de multiplicação
    data_dict = {(item['fator1'], item['fator2']): item for item in multiplicacoes_data}

    for i in range(1, 11):
        for j in range(1, 11):
            # Procura pelo item (i, j) ou (j, i)
            item = data_dict.get((i, j), data_dict.get((j, i)))
            if item:
                peso = item['peso']
                heatmap_data[i-1][j-1] = peso
                if peso < min_peso:
                    min_peso = peso
                if peso > max_peso:
                    max_peso = peso

    # Caso nenhum item tenha sido apresentado, min e max podem não ter sido atualizados
    if min_peso == float('inf'): min_peso = 1.0
    if max_peso == float('-inf'): max_peso = 10.0

    return heatmap_data, min_peso, max_peso

# A inicialização agora é feita dentro da função main, após carregar a configuração

# --- Armazenamento de Fórmulas Personalizadas ---
custom_formulas_data = [] # Lista para armazenar as fórmulas personalizadas
current_custom_formula_for_quiz = None # Armazena a fórmula selecionada para o quiz personalizado

# --- Constantes e Lógica de Atualização ---
# !!! IMPORTANTE: Substitua pelo seu URL do repositório GitHub !!!
GITHUB_REPO_URL_CONFIG = "https://api.github.com/repos/juanzitos252/Mate2/releases/latest"
APP_CURRENT_VERSION = "0.1.0" # Defina a versão atual do seu aplicativo

# Variáveis globais para status da atualização
update_available = False
latest_version_tag = ""
update_check_status_message = "Verificando atualizações..."

# --- Elementos Globais da UI para Atualização (Definidos antecipadamente) ---
# Estes são definidos aqui para estarem disponíveis globalmente quando as telas são construídas.
# Suas propriedades (cor, texto, visibilidade) serão atualizadas dinamicamente.

update_status_icon = ft.Icon(
    name=ft.Icons.SYNC_PROBLEM, # Ícone inicial
    # A cor será definida dinamicamente com base no tema e status
    tooltip="Verificando atualizações...",
    size=20
)
update_status_text = ft.Text(
    f"v{APP_CURRENT_VERSION}", # Texto inicial
    size=10,
    # A cor será definida dinamicamente
    opacity=0.7
)
update_action_button = ft.ElevatedButton(
    text="Atualizar Agora",
    icon=ft.Icons.UPDATE,
    visible=False, # Começa invisível
    # on_click será definido depois (show_update_dialog)
    # bgcolor e color serão definidos dinamicamente
)

# --- Diálogo de Confirmação e Lógica de Atualização (Definidos antecipadamente) ---
update_progress_indicator = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
update_dialog_content_text = Text("Uma nova versão do aplicativo está disponível. Deseja atualizar agora? O aplicativo precisará ser reiniciado.")

# Placeholder para o diálogo, será totalmente definido em `main` ou em uma função de setup se necessário
update_dialog = None # Será um ft.AlertDialog

def close_dialog(e, page_ref: ft.Page, dialog_ref: ft.AlertDialog):
    if dialog_ref:
        dialog_ref.open = False
    if page_ref: # Adicionada verificação para page_ref
        page_ref.update()

def perform_update_action(e, page_ref: ft.Page, dialog_ref: ft.AlertDialog):
    global update_check_status_message

    if not dialog_ref:
        return

    update_dialog_content_text.value = "Iniciando atualização..."
    dialog_ref.content = Column([
        update_dialog_content_text,
        Container(height=10),
        Row([update_progress_indicator, Text("Processando...")], alignment=MainAxisAlignment.CENTER)
    ])
    update_progress_indicator.visible = True
    dialog_ref.actions = [] # Remover botões durante o processo
    if page_ref: page_ref.update()

    try:
        if not os.path.exists(".git"):
            update_dialog_content_text.value = "ERRO: Este aplicativo não parece ser um repositório Git. A atualização automática não pode prosseguir."
            raise Exception("Não é um repositório Git.")

        update_dialog_content_text.value = "Salvando alterações locais (stash)..."
        if page_ref: page_ref.update()
        stash_result = subprocess.run(['git', 'stash', 'push', '-u', '-m', 'autostash_before_update'], capture_output=True, text=True)
        if stash_result.returncode != 0 and "No local changes to save" not in stash_result.stdout and "No local changes to save" not in stash_result.stderr:
            # Se houve um erro real no stash (não apenas "nada para salvar")
            print(f"Erro no git stash: {stash_result.stderr}")
            # Não necessariamente um erro fatal, pode prosseguir, mas registrar.
        print(f"Git stash push executado: {stash_result.stdout or stash_result.stderr}")


        update_dialog_content_text.value = "Buscando atualizações (fetch)..."
        if page_ref: page_ref.update()
        fetch_result = subprocess.run(['git', 'fetch'], check=True, capture_output=True, text=True)
        print(f"Git fetch executado: {fetch_result.stdout}")

        update_dialog_content_text.value = "Aplicando atualizações (git pull)..."
        if page_ref: page_ref.update()
        pull_result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        if pull_result.returncode != 0:
            # Verifica se o pull falhou devido a arquivos não rastreados que seriam sobrescritos
            if "Your local changes to the following files would be overwritten by merge" in pull_result.stderr or \
               "The following untracked working tree files would be overwritten by merge" in pull_result.stderr:
                update_dialog_content_text.value = (
                    "ERRO: A atualização falhou porque você tem alterações locais ou arquivos não rastreados "
                    "que entrariam em conflito com a atualização. Por favor, salve suas alterações (usando 'git stash' ou 'git commit') "
                    "e tente novamente. Se o problema persistir, use 'git pull' no terminal para resolver manualmente."
                )
            # Verifica se o pull falhou devido a um conflito de merge
            elif "CONFLICT" in pull_result.stdout or "Automatic merge failed" in pull_result.stderr:
                update_dialog_content_text.value = (
                    "ERRO: Ocorreu um conflito de merge durante a atualização. "
                    "Isso significa que suas alterações locais e as alterações remotas não puderam ser combinadas automaticamente. "
                    "Por favor, resolva os conflitos manualmente usando 'git status' e 'git mergetool' ou editando os arquivos, "
                    "e então finalize o merge com 'git commit'."
                )
                # O 'git pull' com conflito já deixa o repositório em um estado de merge,
                # então a melhor ação é informar o usuário. Tentar 'git stash pop' aqui seria problemático.
                # O stash original (se houve) permanece intacto.
            else:
                # Outros erros de git pull
                update_dialog_content_text.value = f"ERRO ao aplicar atualizações (git pull): {pull_result.stderr or pull_result.stdout}"

            # Em caso de falha no pull (exceto conflito de merge que requer ação manual), tentamos restaurar o stash.
            if "CONFLICT" not in pull_result.stdout:
                subprocess.run(['git', 'stash', 'pop'], capture_output=True, text=True) # Melhor esforço

            raise subprocess.CalledProcessError(pull_result.returncode, pull_result.args, output=pull_result.stdout, stderr=pull_result.stderr)
        print(f"Git pull executado: {pull_result.stdout}")

        update_dialog_content_text.value = "Restaurando alterações locais (stash pop)..."
        if page_ref: page_ref.update()
        pop_result = subprocess.run(['git', 'stash', 'pop'], capture_output=True, text=True)
        if pop_result.returncode != 0:
            # "No stash entries found." não é um erro crítico aqui.
            # Conflitos durante o pop são o principal problema.
            if "CONFLICT" in pop_result.stdout or "CONFLICT" in pop_result.stderr:
                update_dialog_content_text.value = (
                    "Atualização baixada, mas CONFLITOS ocorreram ao tentar restaurar suas alterações locais. "
                    "Suas alterações stashed (autostash_before_update) precisam ser resolvidas manualmente. "
                    "Reinicie o app. Para resolver, use 'git stash apply' e resolva os conflitos."
                )
                update_check_status_message = "Conflito no stash pop!"
            elif "No stash entries found." not in pop_result.stderr and "No stash found." not in pop_result.stdout : # Ignora se não havia stash
                update_dialog_content_text.value = (
                    f"Atualização baixada. Aviso ao restaurar stash: {pop_result.stderr or pop_result.stdout}. "
                    "Pode ser necessário verificar manualmente. Reinicie o app."
                )
            else: # Stash pop bem sucedido ou sem stash para aplicar
                update_dialog_content_text.value = "Atualização concluída com sucesso! Por favor, reinicie o aplicativo para aplicar as alterações."
                update_check_status_message = "Atualizado! Reinicie."
        else: # Stash pop bem sucedido
            update_dialog_content_text.value = "Atualização concluída com sucesso! Por favor, reinicie o aplicativo para aplicar as alterações."
            update_check_status_message = "Atualizado! Reinicie."
        print(f"Git stash pop tentado: {pop_result.stdout or pop_result.stderr}")


    except subprocess.CalledProcessError as err:
        error_details = f"{err.stderr or err.stdout or str(err)}".strip()
        # A mensagem já deve ter sido definida pelo bloco do pull
        if not ("ERRO: Não foi possível aplicar as atualizações" in update_dialog_content_text.value or "ERRO ao aplicar atualizações" in update_dialog_content_text.value) :
            update_dialog_content_text.value = f"ERRO no processo Git: {error_details}"
        print(f"Erro subprocess (pré-definido ou genérico): {error_details}")
        # Tentar garantir que o stash seja restaurado se o erro não foi no pull e o stash foi feito.
        if 'stash_result' in locals() and stash_result.returncode == 0 and "pull_result" in locals() and err.cmd != pull_result.args :
             # Se o stash foi bem sucedido e o erro não foi no pull, tentar pop.
             # Se o erro FOI no pull, o pop já foi tentado lá.
            subprocess.run(['git', 'stash', 'pop'], capture_output=True, text=True)

    except FileNotFoundError:
        update_dialog_content_text.value = "ERRO: Git não encontrado no sistema. A atualização automática não pode prosseguir. Por favor, instale o Git."
    except Exception as ex:
        # Se a mensagem já foi definida para um erro específico (como "Não é repo git"), não sobrescrever.
        if "ERRO:" not in update_dialog_content_text.value:
            update_dialog_content_text.value = f"ERRO inesperado durante a atualização: {str(ex)}"
        print(f"Erro Exception: {str(ex)}")

    update_progress_indicator.visible = False
    dialog_ref.actions = [ft.TextButton("OK, Entendido", on_click=lambda ev: close_dialog(ev, page_ref, dialog_ref))]
    if page_ref: page_ref.update()


def show_update_dialog(page_ref: ft.Page):
    global update_dialog # Acessa o update_dialog global
    if not page_ref or not update_dialog: # Adicionada verificação para page_ref e update_dialog
        print("Página ou diálogo de atualização não pronto para show_update_dialog")
        return

    # Certificar que o conteúdo e ações do diálogo estão corretos antes de mostrar
    update_dialog.content = update_dialog_content_text
    update_dialog.actions = [
            ft.TextButton("Sim, Atualizar", on_click=lambda e: perform_update_action(e, page_ref, update_dialog)),
            ft.TextButton("Agora Não", on_click=lambda e: close_dialog(e, page_ref, update_dialog)),
        ]
    update_dialog.title=Text("Confirmar Atualização")
    update_dialog.modal=True
    update_dialog.actions_alignment=ft.MainAxisAlignment.END

    page_ref.dialog = update_dialog
    update_dialog.open = True
    page_ref.update()

def get_local_git_commit_hash():
    """Obtém o hash do commit local."""
    try:
        # Verifica se é um repositório git
        if not os.path.exists(".git"):
            return "Não é um repositório git"

        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao obter hash do commit local: {e}")
        return "Erro ao obter commit"
    except FileNotFoundError:
        print("Git não encontrado. Certifique-se de que está instalado e no PATH.")
        return "Git não encontrado"

local_git_commit = get_local_git_commit_hash()

def check_for_updates():
    global update_available, latest_version_tag, update_check_status_message, APP_CURRENT_VERSION, GITHUB_REPO_URL_CONFIG
    update_check_status_message = "Verificando atualizações..." # Reset message before check
    try:
        response = requests.get(GITHUB_REPO_URL_CONFIG, timeout=10)
        response.raise_for_status()
        release_info = response.json()
        latest_version_tag = release_info['tag_name']

        # Remove 'v' prefixo se existir (ex: v1.0.1 -> 1.0.1)
        parsed_latest_version = latest_version_tag.lstrip('v')
        parsed_current_version = APP_CURRENT_VERSION.lstrip('v')

        if version.parse(parsed_latest_version) > version.parse(parsed_current_version):
            update_available = True
            update_check_status_message = f"Nova versão {latest_version_tag} disponível!"
            print(f"Atualização disponível: {latest_version_tag}")
        else:
            update_available = False
            update_check_status_message = "Você está na versão mais recente."
            print("Nenhuma atualização encontrada.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            update_check_status_message = "Erro: URL de atualização não encontrada (404)."
            print(f"Erro 404: A URL {GITHUB_REPO_URL_CONFIG} não foi encontrada. Verifique a configuração GITHUB_REPO_URL_CONFIG.")
        elif e.response.status_code == 403:
            update_check_status_message = "Erro: Acesso proibido à URL de atualização (403)."
            print(f"Erro 403: Acesso proibido à URL {GITHUB_REPO_URL_CONFIG}. Verifique as permissões do token ou do repositório.")
        else:
            update_check_status_message = f"Erro HTTP: {e.response.status_code} ao verificar atualizações."
            print(f"Erro HTTP {e.response.status_code} ao verificar atualizações: {e}")
    except requests.exceptions.ConnectionError:
        update_check_status_message = "Erro: Não foi possível conectar para verificar atualizações."
        print("Erro de conexão ao verificar atualizações. Verifique sua internet.")
    except requests.exceptions.Timeout:
        update_check_status_message = "Erro: Timeout ao verificar atualizações."
        print("Timeout ao verificar atualizações.")
    except Exception as e: # Captura outras exceções genéricas
        update_check_status_message = "Erro inesperado na verificação de atualizações."
        print(f"Erro inesperado ao verificar atualizações: {e}")


# --- Temas e Gerenciamento de Tema ---
TEMAS = {
    "colorido": {"fundo_pagina": ft.Colors.PURPLE_50, "texto_titulos": ft.Colors.DEEP_PURPLE_700, "texto_padrao": ft.Colors.BLACK87, "botao_principal_bg": ft.Colors.DEEP_PURPLE_400, "botao_principal_texto": ft.Colors.WHITE, "botao_opcao_quiz_bg": ft.Colors.BLUE_300, "botao_opcao_quiz_texto": ft.Colors.WHITE, "botao_destaque_bg": ft.Colors.PINK_ACCENT_200, "botao_destaque_texto": ft.Colors.BLACK87, "botao_tema_bg": ft.Colors.PINK_ACCENT_100, "botao_tema_texto": ft.Colors.BLACK, "feedback_acerto_texto": ft.Colors.GREEN_600, "feedback_erro_texto": ft.Colors.RED_500, "feedback_acerto_botao_bg": ft.Colors.GREEN_100, "feedback_erro_botao_bg": ft.Colors.RED_100, "container_treino_bg": ft.Colors.WHITE, "container_treino_borda": ft.Colors.DEEP_PURPLE_400, "textfield_border_color": ft.Colors.DEEP_PURPLE_400, "dropdown_border_color": ft.Colors.DEEP_PURPLE_400,"progressbar_cor": ft.Colors.DEEP_PURPLE_400, "progressbar_bg_cor": ft.Colors.PURPLE_100, "update_icon_color_available": ft.Colors.AMBER_700, "update_icon_color_uptodate": ft.Colors.GREEN_700, "update_icon_color_error": ft.Colors.RED_700},
    "claro": {"fundo_pagina": ft.Colors.GREY_100, "texto_titulos": ft.Colors.BLACK, "texto_padrao": ft.Colors.BLACK87, "botao_principal_bg": ft.Colors.BLUE_600, "botao_principal_texto": ft.Colors.WHITE, "botao_opcao_quiz_bg": ft.Colors.LIGHT_BLUE_200, "botao_opcao_quiz_texto": ft.Colors.BLACK87, "botao_destaque_bg": ft.Colors.CYAN_600, "botao_destaque_texto": ft.Colors.WHITE, "botao_tema_bg": ft.Colors.CYAN_200, "botao_tema_texto": ft.Colors.BLACK87,"feedback_acerto_texto": ft.Colors.GREEN_700, "feedback_erro_texto": ft.Colors.RED_700, "feedback_acerto_botao_bg": ft.Colors.GREEN_100, "feedback_erro_botao_bg": ft.Colors.RED_100, "container_treino_bg": ft.Colors.WHITE, "container_treino_borda": ft.Colors.BLUE_600, "textfield_border_color": ft.Colors.BLUE_600, "dropdown_border_color": ft.Colors.BLUE_600, "progressbar_cor": ft.Colors.BLUE_600, "progressbar_bg_cor": ft.Colors.BLUE_100, "update_icon_color_available": ft.Colors.ORANGE_ACCENT_700, "update_icon_color_uptodate": ft.Colors.GREEN_800, "update_icon_color_error": ft.Colors.RED_800},
    "escuro_moderno": {
        "fundo_pagina": ft.Colors.TEAL_900, # Fallback for page.bgcolor
        "gradient_page_bg": ft.LinearGradient(
            begin=alignment.top_center, # Changed from top_left
            end=alignment.bottom_center,  # Changed from bottom_right
            colors=[ft.Colors.INDIGO_900, ft.Colors.PURPLE_800, ft.Colors.TEAL_800], # Slightly adjusted shades for harmony
            stops=[0.1, 0.6, 1.0]
        ),
        "texto_titulos": ft.Colors.CYAN_ACCENT_200,
        "texto_padrao": ft.Colors.WHITE,
        "botao_principal_bg": ft.Colors.PINK_ACCENT_400,
        "botao_principal_texto": ft.Colors.WHITE,
        "botao_opcao_quiz_bg": ft.Colors.BLUE_GREY_700,
        "botao_opcao_quiz_texto": ft.Colors.WHITE,
        "botao_destaque_bg": ft.Colors.TEAL_ACCENT_400,
        "botao_destaque_texto": ft.Colors.WHITE,
        "botao_tema_bg": ft.Colors.with_opacity(0.2, ft.Colors.WHITE), # For theme selection buttons
        "botao_tema_texto": ft.Colors.CYAN_ACCENT_100,                 # For theme selection buttons text
        "feedback_acerto_texto": ft.Colors.GREEN_ACCENT_200,
        "feedback_erro_texto": ft.Colors.RED_ACCENT_100,
        "feedback_acerto_botao_bg": ft.Colors.with_opacity(0.3, ft.Colors.GREEN_ACCENT_100),
        "feedback_erro_botao_bg": ft.Colors.with_opacity(0.3, ft.Colors.RED_ACCENT_100),
        "container_treino_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE), # Slightly more subtle frosted glass
        "container_treino_borda": ft.Colors.CYAN_ACCENT_700,
        "textfield_border_color": ft.Colors.CYAN_ACCENT_700,
        "dropdown_border_color": ft.Colors.CYAN_ACCENT_700,
        "progressbar_cor": ft.Colors.CYAN_ACCENT_400,
        "progressbar_bg_cor": ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
        "update_icon_color_available": ft.Colors.YELLOW_ACCENT_400,
        "update_icon_color_uptodate": ft.Colors.GREEN_ACCENT_400,
        "update_icon_color_error": ft.Colors.RED_ACCENT_400
    },
    "dark": {
    "fundo_pagina": "#121212",
    "texto_titulos": "#FFFFFF",
    "texto_padrao": "#E0E0E0",
    "botao_principal_bg": "#BB86FC",
    "botao_principal_texto": "#000000",
    "botao_opcao_quiz_bg": "#03DAC6",
    "botao_opcao_quiz_texto": "#000000",
    "botao_destaque_bg": "#03DAC6",
    "botao_destaque_texto": "#000000",
    "botao_tema_bg": "#1F1F1F",
    "botao_tema_texto": "#FFFFFF",
    "feedback_acerto_texto": "#00C853",
    "feedback_erro_texto": "#FF4081",
    "feedback_acerto_botao_bg": "#33691E",
    "feedback_erro_botao_bg": "#D81B60",
    "container_treino_bg": "#1E1E1E",
    "container_treino_borda": "#BB86FC",
    "textfield_border_color": "#BB86FC",
    "dropdown_border_color": "#03DAC6",
    "progressbar_cor": "#BB86FC",
    "progressbar_bg_cor": "#3E3E3E",
    "update_icon_color_available": "#FFD600",
    "update_icon_color_uptodate": "#00E676",
    "update_icon_color_error": "#FF1744"
    }
}
tema_ativo_nome = "colorido" # Default theme
def obter_cor_do_tema_ativo(nome_cor_semantica: str, fallback_color=ft.Colors.BLACK): # Added fallback_color param
    # Se o tema ativo for o novo escuro e a cor pedida for 'gradient_page_bg', retorna o objeto Gradient.
    if tema_ativo_nome == "escuro_moderno" and nome_cor_semantica == "gradient_page_bg":
        return TEMAS["escuro_moderno"]["gradient_page_bg"]

    tema_atual = TEMAS.get(tema_ativo_nome, TEMAS["colorido"])
    return tema_atual.get(nome_cor_semantica, fallback_color) # Use provided fallback

# --- Constantes de UI (Dimensões e Animações) ---
BOTAO_LARGURA_PRINCIPAL = 220
BOTAO_ALTURA_PRINCIPAL = 50
BOTAO_LARGURA_OPCAO_QUIZ = 150
BOTAO_ALTURA_OPCAO_QUIZ = 50
PADDING_VIEW = padding.symmetric(horizontal=25, vertical=20)
ESPACAMENTO_COLUNA_GERAL = 15
ESPACAMENTO_BOTOES_APRESENTACAO = 10
ANIMACAO_FADE_IN_LENTO = Animation(400, AnimationCurve.EASE_IN)
ANIMACAO_APARICAO_TEXTO_BOTAO = Animation(250, AnimationCurve.EASE_OUT)
ANIMACAO_FEEDBACK_OPACIDADE = Animation(200, AnimationCurve.EASE_IN_OUT)
ANIMACAO_FEEDBACK_ESCALA = Animation(300, AnimationCurve.EASE_OUT_BACK)

# --- Funções de Construção de Tela ---
def mudar_tema(page: Page, novo_tema_nome: str):
    global tema_ativo_nome, multiplicacoes_data, custom_formulas_data
    if tema_ativo_nome == novo_tema_nome:
        return

    tema_ativo_nome = novo_tema_nome

    # Salva a configuração toda vez que o tema muda
    salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data)

    page.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")

    # Store current route
    current_route_val = page.route

    # Clear existing views
    page.views.clear()

    # Re-populate views directly, ensuring all build_... functions use the new theme.
    # This logic is similar to what's in route_change.

    # Base view (always present, typically the home screen)
    page.views.append(
        View(
            route="/",
            controls=[build_tela_apresentacao(page)],
            vertical_alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER
        )
    )

    # Append the specific view for the current_route_val if it's not the base view.
    # If current_route_val is "/", the base view is already the top view.
    if current_route_val == "/quiz":
        page.views.append(View("/quiz", [build_tela_quiz(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER))
    elif current_route_val == "/quiz_invertido":
        page.views.append(View("/quiz_invertido", [build_tela_quiz_invertido(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER))
    elif current_route_val == "/treino":
        page.views.append(View("/treino", [build_tela_treino(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER))
    elif current_route_val == "/estatisticas":
        page.views.append(View("/estatisticas", [build_tela_estatisticas(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER))
    elif current_route_val == "/formula_quiz_setup":
        page.views.append(View("/formula_quiz_setup", [build_tela_formula_quiz_setup(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER))
    elif current_route_val == "/custom_quiz":
        page.views.append(View("/custom_quiz", [build_tela_custom_quiz(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER))

    page.update()
    # We avoid calling page.go() here as we've manually rebuilt the view stack.
    # Calling page.go() would trigger route_change again, which is now redundant for this theme update.

# --- Funções Auxiliares para Fórmulas ---
# (parse_variable_ranges pode ser mantido se for útil para os ranges de 'a' e 'b' das fórmulas notáveis)
def parse_variable_ranges(range_str: str, default_min=1, default_max=10):
    """Converte uma string como '1-10' em {'min': 1, 'max': 10}. Limita ao intervalo 1-10."""
    try:
        parts = range_str.split('-')
        min_val = int(parts[0].strip())
        max_val = int(parts[1].strip())

        # Garante min <= max
        if min_val > max_val:
            min_val, max_val = max_val, min_val

        # Limita os valores para estar entre 1 e 10 (ou outro limite superior se necessário no futuro)
        # Para as variáveis base das fórmulas notáveis, vamos manter o limite de 1-10.
        min_val = max(1, min(min_val, 10))
        max_val = max(1, min(max_val, 10))

        # Garante min <= max novamente após o clipping
        if min_val > max_val:
            min_val = max_val # Se min_val era 11 e max_val era 5, ambos se tornam 10, depois min é ajustado.

        return {'min': min_val, 'max': max_val}
    except:
        # Retorna o padrão, mas também limitado
        return {'min': max(1, min(default_min, 10)), 'max': max(1, min(default_max, 10))}

# --- Tela de Configuração de Quiz com Fórmula Notável ---
def build_tela_formula_quiz_setup(page: Page):
    # Campo para nomear esta configuração de quiz (opcional, mas útil se salvarmos)
    quiz_config_name_field = TextField(
        label="Nome para esta Configuração de Quiz (Ex: Treino Quadrado da Soma)",
        width=350,
        color=obter_cor_do_tema_ativo("texto_padrao"),
        border_color=obter_cor_do_tema_ativo("textfield_border_color")
    )

    # Dropdown para selecionar o tipo de fórmula notável
    formula_type_dropdown_options = [
        ft.dropdown.Option(key=f['id'], text=f['display_name']) for f in FORMULAS_NOTAVEIS
    ]
    formula_type_dropdown = Dropdown(
        label="Selecione o Tipo de Fórmula",
        width=350,
        options=formula_type_dropdown_options,
        border_color=obter_cor_do_tema_ativo("dropdown_border_color"),
        color=obter_cor_do_tema_ativo("texto_padrao")
    )

    # Campos para os ranges das variáveis (inicialmente para 'a' e 'b')
    # Labels serão atualizados com base na fórmula selecionada
    var_a_range_field = TextField(
        label="Range para 'a' (1-10)", # Label genérico inicial
        width=170,
        color=obter_cor_do_tema_ativo("texto_padrao"),
        border_color=obter_cor_do_tema_ativo("textfield_border_color"),
        value="1-10" # Valor padrão
    )
    var_b_range_field = TextField(
        label="Range para 'b' (1-10)", # Label genérico inicial
        width=170,
        color=obter_cor_do_tema_ativo("texto_padrao"),
        border_color=obter_cor_do_tema_ativo("textfield_border_color"),
        value="1-10", # Valor padrão
        visible=True # A maioria das fórmulas usará 'b'
    )

    feedback_text = Text("", color=obter_cor_do_tema_ativo("texto_padrao"))

    # Dropdown para listar configurações de quiz salvas
    saved_quiz_configs_dropdown = Dropdown(
        label="Ou selecione uma configuração de quiz salva",
        width=350,
        options=[ft.dropdown.Option(key=cfg['name'], text=cfg['name']) for cfg in custom_formulas_data],
        border_color=obter_cor_do_tema_ativo("dropdown_border_color"),
        color=obter_cor_do_tema_ativo("texto_padrao")
    )

    def update_variable_fields(selected_formula_id: str):
        """Atualiza a visibilidade e labels dos campos de range das variáveis."""
        definition = get_formula_definition(selected_formula_id)
        if not definition:
            var_a_range_field.visible = False
            var_b_range_field.visible = False
        else:
            variables = definition.get('variables', [])
            labels = definition.get('variable_labels', {})

            if 'a' in variables:
                var_a_range_field.label = labels.get('a', "Range para 'a' (1-10)")
                var_a_range_field.visible = True
            else:
                var_a_range_field.visible = False

            if 'b' in variables:
                var_b_range_field.label = labels.get('b', "Range para 'b' (1-10)")
                var_b_range_field.visible = True
            else:
                var_b_range_field.visible = False
        page.update()

    def on_formula_type_change(e):
        if formula_type_dropdown.value:
            update_variable_fields(formula_type_dropdown.value)
        else: # Nenhum tipo selecionado, esconde campos de range
            var_a_range_field.visible = False
            var_b_range_field.visible = False
            page.update()

    formula_type_dropdown.on_change = on_formula_type_change
    var_a_range_field.visible = False
    var_b_range_field.visible = False

    # Definição da função movida para cima para que possa ser chamada antes do return
    def update_saved_quiz_configs_dropdown():
        saved_quiz_configs_dropdown.options = [
            ft.dropdown.Option(key=cfg['name'], text=cfg['name']) for cfg in custom_formulas_data
        ]
        current_selection = saved_quiz_configs_dropdown.value
        if custom_formulas_data:
            # Tenta manter a seleção atual se ela ainda for válida
            if not any(opt.key == current_selection for opt in saved_quiz_configs_dropdown.options):
                # Se não for válida (ex: item removido), seleciona o último ou nenhum
                saved_quiz_configs_dropdown.value = custom_formulas_data[-1]['name'] if custom_formulas_data else None
        else:
            saved_quiz_configs_dropdown.value = None

        # A verificação se o controle está na página antes de .update() é crucial.
        # No entanto, Flet pode lidar com isso internamente ou o erro ocorre se o controle
        # *nunca* foi adicionado. A movimentação da chamada inicial para o final da
        # construção da view é a principal correção.
        if saved_quiz_configs_dropdown.page: # Verifica se o controle já foi adicionado à página
            saved_quiz_configs_dropdown.update()
        # Se não estiver na página ainda (o que não deveria acontecer se chamada no final da build),
        # o .update() seria problemático. Flet pode ter proteções, mas a lógica é essa.

    def save_quiz_config_handler(e):
        global custom_formulas_data

        config_name = quiz_config_name_field.value.strip()
        selected_formula_id = formula_type_dropdown.value

        if not config_name:
            feedback_text.value = "Por favor, dê um nome para esta configuração de quiz."
            feedback_text.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()
            return

        if not selected_formula_id:
            feedback_text.value = "Por favor, selecione um tipo de fórmula."
            feedback_text.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()
            return

        if any(cfg['name'] == config_name for cfg in custom_formulas_data):
            feedback_text.value = f"Uma configuração de quiz com o nome '{config_name}' já existe."
            feedback_text.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()
            return

        ranges = {}
        definition = get_formula_definition(selected_formula_id)
        if definition:
            if 'a' in definition.get('variables', []):
                ranges['a'] = parse_variable_ranges(var_a_range_field.value)
            if 'b' in definition.get('variables', []):
                ranges['b'] = parse_variable_ranges(var_b_range_field.value)

        quiz_config_entry = {
            'name': config_name,
            'formula_id': selected_formula_id,
            'ranges': ranges
        }
        custom_formulas_data.append(quiz_config_entry)
        salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data)
        feedback_text.value = f"Configuração de Quiz '{config_name}' salva!"
        feedback_text.color = obter_cor_do_tema_ativo("feedback_acerto_texto")

        update_saved_quiz_configs_dropdown()
        quiz_config_name_field.value = ""
        formula_type_dropdown.value = None
        var_a_range_field.visible = False
        var_b_range_field.visible = False
        page.update()

    def start_quiz_with_saved_config_handler(e):
        global current_custom_formula_for_quiz

        selected_config_name = saved_quiz_configs_dropdown.value
        if not selected_config_name:
            feedback_text.value = "Nenhuma configuração de quiz salva selecionada."
            feedback_text.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()
            return

        quiz_config_to_run = next((cfg for cfg in custom_formulas_data if cfg['name'] == selected_config_name), None)

        if quiz_config_to_run:
            current_custom_formula_for_quiz = quiz_config_to_run
            page.go("/custom_quiz")
        else:
            feedback_text.value = f"Configuração de Quiz '{selected_config_name}' não encontrada."
            feedback_text.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()

    # A chamada inicial a update_saved_quiz_configs_dropdown() foi movida para o final da função,
    # antes de retornar view_container.

    save_button = ElevatedButton("Salvar Configuração do Quiz", on_click=save_quiz_config_handler, width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    start_quiz_button = ElevatedButton("Iniciar Quiz com Config. Salva", on_click=start_quiz_with_saved_config_handler, width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, bgcolor=obter_cor_do_tema_ativo("botao_destaque_bg"), color=obter_cor_do_tema_ativo("botao_destaque_texto"))
    back_button = ElevatedButton("Voltar ao Menu", on_click=lambda _: page.go("/"), width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))

    content = Column(
        controls=[
            Text("Configurar Quiz com Fórmula Notável", size=28, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos")),
            Container(height=10),
            Text("1. Configure um novo Quiz:", size=18, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao")),
            quiz_config_name_field,
            formula_type_dropdown,
            Container(height=5),
            Text("Defina os ranges para as variáveis (1-10):", color=obter_cor_do_tema_ativo("texto_padrao"), size=12),
            Row([var_a_range_field, var_b_range_field], spacing=10, alignment=MainAxisAlignment.CENTER),
            Container(height=10),
            save_button,
            Container(height=15, border=ft.border.only(bottom=ft.BorderSide(1, obter_cor_do_tema_ativo("texto_padrao"))), margin=ft.margin.symmetric(vertical=10)),
            Text("2. Ou inicie um Quiz com uma Configuração Salva:", size=18, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao")),
            saved_quiz_configs_dropdown,
            Container(height=10),
            start_quiz_button,
            Container(height=10),
            feedback_text,
            # Container(height=20, border=ft.border.only(bottom=ft.BorderSide(1, obter_cor_do_tema_ativo("texto_padrao"))), margin=ft.margin.symmetric(vertical=10)), # Linha divisória removida
            # Text("3. Ferramentas de Cálculo Adicionais:", size=18, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao")), # Removido
            # Container(height=10), # Removido
            # ElevatedButton( # Removido
            #     "Calculadora de Divisão Diretamente Proporcional",
            #     on_click=lambda _: page.go("/divisao_direta"),
            #     width=BOTAO_LARGURA_PRINCIPAL + 60,
            #     height=BOTAO_ALTURA_PRINCIPAL,
            #     bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"),
            #     color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
            # ),
            # Container(height=ESPACAMENTO_BOTOES_APRESENTACAO), # Removido
            # ElevatedButton( # Removido
            #     "Calculadora de Divisão Inversamente Proporcional",
            #     on_click=lambda _: page.go("/divisao_inversa"),
            #     width=BOTAO_LARGURA_PRINCIPAL + 60,
            #     height=BOTAO_ALTURA_PRINCIPAL,
            #     bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"),
            #     color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
            # ),
            Container(height=20), # Espaçamento antes do botão Voltar
            back_button,
        ],
        scroll=ScrollMode.AUTO,
        alignment=MainAxisAlignment.CENTER,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=ESPACAMENTO_COLUNA_GERAL
    )

    view_container = Container(content=content, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None

    # Chamada movida para aqui, após todos os controles da view estarem definidos e
    # antes da view_container ser retornada.
    update_saved_quiz_configs_dropdown()

    return view_container


def build_tela_apresentacao(page: Page):
    controles_botoes_tema = [
        Text("Escolha um Tema:", size=16, color=obter_cor_do_tema_ativo("texto_padrao")),
        Container(height=5),
        Row(
            [
                ElevatedButton(text="Colorido", on_click=lambda _: mudar_tema(page, "colorido"), width=BOTAO_LARGURA_PRINCIPAL/2 - 5, height=BOTAO_ALTURA_PRINCIPAL-10, bgcolor=obter_cor_do_tema_ativo("botao_tema_bg"), color=obter_cor_do_tema_ativo("botao_tema_texto")),
                ElevatedButton(text="Claro", on_click=lambda _: mudar_tema(page, "claro"), width=BOTAO_LARGURA_PRINCIPAL/2 - 5, height=BOTAO_ALTURA_PRINCIPAL-10, bgcolor=obter_cor_do_tema_ativo("botao_tema_bg"), color=obter_cor_do_tema_ativo("botao_tema_texto")),
                ElevatedButton(text="Escuro Moderno", on_click=lambda _: mudar_tema(page, "escuro_moderno"), width=BOTAO_LARGURA_PRINCIPAL/2 - 5, height=BOTAO_ALTURA_PRINCIPAL-10, bgcolor=obter_cor_do_tema_ativo("botao_tema_bg"), color=obter_cor_do_tema_ativo("botao_tema_texto")),
                ElevatedButton(text="Dark", on_click=lambda _: mudar_tema(page, "dark"), width=BOTAO_LARGURA_PRINCIPAL/2 - 5, height=BOTAO_ALTURA_PRINCIPAL-10, bgcolor=obter_cor_do_tema_ativo("botao_tema_bg"), color=obter_cor_do_tema_ativo("botao_tema_texto")),
            ],
            alignment=MainAxisAlignment.CENTER,
            spacing = 10
        )
    ]
    conteudo_apresentacao = Column(
        controls=[
            Text("Quiz Mestre da Tabuada", size=32, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_titulos")),
            Text("Aprenda e memorize a tabuada de forma divertida e adaptativa!", size=18, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_padrao")),
            Container(height=20),
            ElevatedButton("Iniciar Quiz", width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, on_click=lambda _: page.go("/quiz"), tooltip="Começar um novo quiz.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto")),
            Container(height=ESPACAMENTO_BOTOES_APRESENTACAO),
            ElevatedButton("Quiz Invertido", width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, on_click=lambda _: page.go("/quiz_invertido"), tooltip="Qual multiplicação resulta no número?", bgcolor=obter_cor_do_tema_ativo("botao_destaque_bg"), color=obter_cor_do_tema_ativo("botao_destaque_texto")),
            Container(height=ESPACAMENTO_BOTOES_APRESENTACAO),
            ElevatedButton("Modo Treino", width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, on_click=lambda _: page.go("/treino"), tooltip="Treinar uma tabuada.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto")),
            Container(height=ESPACAMENTO_BOTOES_APRESENTACAO),
            ElevatedButton("Estatísticas", width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, on_click=lambda _: page.go("/estatisticas"), tooltip="Veja seu progresso.", bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"), color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto")),
            Container(height=ESPACAMENTO_BOTOES_APRESENTACAO),
            ElevatedButton("Quiz com Fórmulas", width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, on_click=lambda _: page.go("/formula_quiz_setup"), tooltip="Crie ou selecione um quiz baseado em fórmulas notáveis ou acesse calculadoras.", bgcolor=obter_cor_do_tema_ativo("botao_destaque_bg"), color=obter_cor_do_tema_ativo("botao_destaque_texto")),
            Container(height=20, margin=ft.margin.only(top=10)), # Mantido para espaçamento antes dos botões de tema
        ] + controles_botoes_tema + [
            Container(height=10), # Mantido para espaçamento antes do botão de atualização
            update_action_button, # Adiciona o botão de "Atualizar Agora" se visível
            Container(height=5),
        ],
        alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=ESPACAMENTO_COLUNA_GERAL,
        scroll=ScrollMode.AUTO
    )

    view_container = Container(
        content=conteudo_apresentacao,
        alignment=alignment.center,
        expand=True,
        padding=PADDING_VIEW
    )

    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None

    return view_container

def build_tela_quiz(page: Page):
    texto_pergunta = Text(size=30, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_titulos"), opacity=0, animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO)
    botoes_opcoes = [ElevatedButton(text="", width=BOTAO_LARGURA_OPCAO_QUIZ, height=BOTAO_ALTURA_OPCAO_QUIZ, opacity=0, animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO) for _ in range(4)]
    texto_feedback = Text(size=18, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, opacity=0, scale=0.8, animate_opacity=ANIMACAO_FEEDBACK_OPACIDADE, animate_scale=ANIMACAO_FEEDBACK_ESCALA)
    def handle_resposta(e, botao_clicado_ref, todos_botoes_opcoes_ref, txt_feedback_ctrl_ref, btn_proxima_ctrl_ref):
        dados_botao = botao_clicado_ref.data
        era_correta = dados_botao['correta']
        pergunta_original_ref = dados_botao['pergunta_original']
        registrar_resposta(pergunta_original_ref, era_correta)
        if era_correta:
            txt_feedback_ctrl_ref.value = "Correto!"
            txt_feedback_ctrl_ref.color = obter_cor_do_tema_ativo("feedback_acerto_texto")
            botao_clicado_ref.bgcolor = obter_cor_do_tema_ativo("feedback_acerto_botao_bg")
        else:
            resposta_certa_valor = pergunta_original_ref['fator1'] * pergunta_original_ref['fator2']
            txt_feedback_ctrl_ref.value = f"Errado! A resposta era {resposta_certa_valor}"
            txt_feedback_ctrl_ref.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            botao_clicado_ref.bgcolor = obter_cor_do_tema_ativo("feedback_erro_botao_bg")
        for btn in todos_botoes_opcoes_ref: btn.disabled = True
        txt_feedback_ctrl_ref.opacity = 1; txt_feedback_ctrl_ref.scale = 1
        btn_proxima_ctrl_ref.visible = True; page.update()
    botao_proxima = ElevatedButton("Próxima Pergunta", on_click=None, visible=False, width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, tooltip="Carregar próxima pergunta.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    def carregar_nova_pergunta(page_ref, txt_pergunta_ctrl, btn_opcoes_ctrls, txt_feedback_ctrl, btn_proxima_ctrl):
        txt_feedback_ctrl.opacity = 0; txt_feedback_ctrl.scale = 0.8
        txt_pergunta_ctrl.opacity = 0
        for btn_opcao in btn_opcoes_ctrls: btn_opcao.opacity = 0
        pergunta_selecionada = selecionar_proxima_pergunta()
        if not pergunta_selecionada:
            txt_pergunta_ctrl.value = "Nenhuma pergunta disponível."; txt_pergunta_ctrl.opacity = 1
            for btn in btn_opcoes_ctrls: btn.visible = False
            txt_feedback_ctrl.value = ""; btn_proxima_ctrl.visible = False; page_ref.update(); return
        r_val = pergunta_selecionada['fator1'] * pergunta_selecionada['fator2']
        ops = gerar_opcoes(pergunta_selecionada['fator1'], pergunta_selecionada['fator2'], multiplicacoes_data)
        txt_pergunta_ctrl.value = f"{pergunta_selecionada['fator1']} x {pergunta_selecionada['fator2']} = ?"
        for i in range(4):
            btn_opcoes_ctrls[i].text = str(ops[i])
            btn_opcoes_ctrls[i].data = {'opcao': ops[i], 'correta': ops[i] == r_val, 'pergunta_original': pergunta_selecionada}
            btn_opcoes_ctrls[i].on_click = lambda e, btn=btn_opcoes_ctrls[i]: handle_resposta(page_ref, btn, btn_opcoes_ctrls, txt_feedback_ctrl, btn_proxima_ctrl)
            btn_opcoes_ctrls[i].bgcolor = obter_cor_do_tema_ativo("botao_opcao_quiz_bg")
            btn_opcoes_ctrls[i].color = obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
            btn_opcoes_ctrls[i].disabled = False; btn_opcoes_ctrls[i].visible = True
        txt_feedback_ctrl.value = ""; btn_proxima_ctrl.visible = False
        txt_pergunta_ctrl.opacity = 1
        for btn_opcao in btn_opcoes_ctrls: btn_opcao.opacity = 1
        page_ref.update()
    botao_proxima.on_click = lambda _: carregar_nova_pergunta(page, texto_pergunta, botoes_opcoes, texto_feedback, botao_proxima)
    carregar_nova_pergunta(page, texto_pergunta, botoes_opcoes, texto_feedback, botao_proxima)
    botao_voltar = ElevatedButton("Voltar ao Menu", on_click=lambda _: page.go("/"), width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, tooltip="Retornar à tela inicial.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    layout_botoes = Column([Row(botoes_opcoes[0:2], alignment=MainAxisAlignment.CENTER, spacing=15), Container(height=10), Row(botoes_opcoes[2:4], alignment=MainAxisAlignment.CENTER, spacing=15)], horizontal_alignment=CrossAxisAlignment.CENTER, spacing=10)
    conteudo_quiz = Column([texto_pergunta, Container(height=15), layout_botoes, Container(height=15), texto_feedback, Container(height=20), botao_proxima, Container(height=10), botao_voltar], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=ESPACAMENTO_COLUNA_GERAL, scroll=ScrollMode.AUTO)

    view_container = Container(content=conteudo_quiz, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

def build_tela_quiz_invertido(page: Page):
    texto_pergunta_invertida = Text(size=30, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_titulos"), opacity=0, animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO)
    botoes_opcoes_invertidas = [ElevatedButton(text="", width=BOTAO_LARGURA_OPCAO_QUIZ, height=BOTAO_ALTURA_OPCAO_QUIZ, opacity=0, animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO) for _ in range(4)]
    texto_feedback_invertido = Text(size=18, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, opacity=0, scale=0.8, animate_opacity=ANIMACAO_FEEDBACK_OPACIDADE, animate_scale=ANIMACAO_FEEDBACK_ESCALA)
    def handle_resposta_invertida(e, botao_clicado_ref, todos_botoes_opcoes_ref, txt_feedback_ctrl_ref, btn_proxima_ctrl_ref):
        dados_botao = botao_clicado_ref.data
        opcao_obj = dados_botao['opcao_obj']
        era_correta = opcao_obj['is_correct']
        pergunta_base_ref = dados_botao['pergunta_base_original_ref']
        registrar_resposta(pergunta_base_ref, era_correta)
        if era_correta:
            txt_feedback_ctrl_ref.value = "Correto!"
            txt_feedback_ctrl_ref.color = obter_cor_do_tema_ativo("feedback_acerto_texto")
            botao_clicado_ref.bgcolor = obter_cor_do_tema_ativo("feedback_acerto_botao_bg")
        else:
            resp_correta_txt = f"{pergunta_base_ref['fator1']} x {pergunta_base_ref['fator2']}"
            txt_feedback_ctrl_ref.value = f"Errado! A resposta era {resp_correta_txt}"
            txt_feedback_ctrl_ref.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            botao_clicado_ref.bgcolor = obter_cor_do_tema_ativo("feedback_erro_botao_bg")
            for btn_op in todos_botoes_opcoes_ref:
                if btn_op.data['opcao_obj']['is_correct']: btn_op.bgcolor = obter_cor_do_tema_ativo("feedback_acerto_botao_bg"); break
        for btn in todos_botoes_opcoes_ref: btn.disabled = True
        txt_feedback_ctrl_ref.opacity = 1; txt_feedback_ctrl_ref.scale = 1
        btn_proxima_ctrl_ref.visible = True; page.update()
    botao_proxima_invertido = ElevatedButton("Próxima Pergunta", on_click=None, visible=False, width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, tooltip="Carregar próxima pergunta.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    def carregar_nova_pergunta_invertida(page_ref, txt_pergunta_ctrl, btn_opcoes_ctrls, txt_feedback_ctrl, btn_proxima_ctrl):
        txt_feedback_ctrl.opacity = 0; txt_feedback_ctrl.scale = 0.8
        txt_pergunta_ctrl.opacity = 0
        for btn_opcao in btn_opcoes_ctrls: btn_opcao.opacity = 0
        multiplicacao_base = selecionar_proxima_pergunta()
        if not multiplicacao_base:
            txt_pergunta_ctrl.value = "Nenhuma pergunta base disponível."; txt_pergunta_ctrl.opacity = 1
            for btn in btn_opcoes_ctrls: btn.visible = False
            txt_feedback_ctrl.value = ""; btn_proxima_ctrl.visible = False; page_ref.update(); return
        resultado_alvo = multiplicacao_base['fator1'] * multiplicacao_base['fator2']
        txt_pergunta_ctrl.value = f"Qual operação resulta em {resultado_alvo}?"
        opcoes_objs_geradas = gerar_opcoes_quiz_invertido(multiplicacao_base, multiplicacoes_data)
        for i in range(len(opcoes_objs_geradas)):
            btn_opcoes_ctrls[i].text = opcoes_objs_geradas[i]['texto']
            btn_opcoes_ctrls[i].data = {'opcao_obj': opcoes_objs_geradas[i], 'pergunta_base_original_ref': multiplicacao_base}
            btn_opcoes_ctrls[i].on_click = lambda e, btn=btn_opcoes_ctrls[i]: handle_resposta_invertida(page_ref, btn, btn_opcoes_ctrls, txt_feedback_ctrl, btn_proxima_ctrl)
            btn_opcoes_ctrls[i].bgcolor = obter_cor_do_tema_ativo("botao_opcao_quiz_bg")
            btn_opcoes_ctrls[i].color = obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
            btn_opcoes_ctrls[i].disabled = False; btn_opcoes_ctrls[i].visible = True
        txt_feedback_ctrl.value = ""; btn_proxima_ctrl.visible = False
        txt_pergunta_ctrl.opacity = 1
        for btn_opcao in btn_opcoes_ctrls: btn_opcao.opacity = 1
        page_ref.update()
    botao_proxima_invertido.on_click = lambda _: carregar_nova_pergunta_invertida(page, texto_pergunta_invertida, botoes_opcoes_invertidas, texto_feedback_invertido, botao_proxima_invertido)
    carregar_nova_pergunta_invertida(page, texto_pergunta_invertida, botoes_opcoes_invertidas, texto_feedback_invertido, botao_proxima_invertido)
    botao_voltar_inv = ElevatedButton("Voltar ao Menu", on_click=lambda _: page.go("/"), width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, tooltip="Retornar à tela inicial.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    layout_botoes_inv = Column([Row(botoes_opcoes_invertidas[0:2], alignment=MainAxisAlignment.CENTER, spacing=15), Container(height=10), Row(botoes_opcoes_invertidas[2:4], alignment=MainAxisAlignment.CENTER, spacing=15)], horizontal_alignment=CrossAxisAlignment.CENTER, spacing=10)
    conteudo_quiz_inv = Column([texto_pergunta_invertida, Container(height=15), layout_botoes_inv, Container(height=15), texto_feedback_invertido, Container(height=20), botao_proxima_invertido, Container(height=10), botao_voltar_inv], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=ESPACAMENTO_COLUNA_GERAL, scroll=ScrollMode.AUTO)

    view_container = Container(content=conteudo_quiz_inv, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

def build_tela_treino(page: Page):
    tabuada_sugerida = sugerir_tabuada_para_treino()
    titulo_treino = Text(f"Treinando a Tabuada do {tabuada_sugerida}", size=28, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_titulos"))
    campos_tabuada_refs = []
    coluna_itens_tabuada = Column(spacing=10, scroll=ScrollMode.AUTO, expand=True, horizontal_alignment=CrossAxisAlignment.CENTER)
    for i in range(1, 11):
        r_correta_val = tabuada_sugerida * i
        txt_mult = Text(f"{tabuada_sugerida} x {i} = ", size=18, color=obter_cor_do_tema_ativo("texto_padrao"))
        campo_resp = TextField(width=100, text_align=TextAlign.CENTER, data={'fator1': tabuada_sugerida, 'fator2': i, 'resposta_correta': r_correta_val}, keyboard_type=KeyboardType.NUMBER)
        campos_tabuada_refs.append(campo_resp)
        coluna_itens_tabuada.controls.append(Row([txt_mult, campo_resp], alignment=MainAxisAlignment.CENTER, spacing=10))
    txt_resumo = Text(size=18, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_padrao"))
    btn_verificar = ElevatedButton("Verificar Respostas", width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, tooltip="Corrigir respostas.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    def handle_verificar_treino(e):
        global tema_ativo_nome, multiplicacoes_data, custom_formulas_data
        acertos = 0
        for campo in campos_tabuada_refs:
            dados = campo.data
            f1, f2, resp_esperada = dados['fator1'], dados['fator2'], dados['resposta_correta']
            acertou = False
            try:
                if int(campo.value) == resp_esperada: acertos += 1; acertou = True; campo.border_color = obter_cor_do_tema_ativo("feedback_acerto_texto")
                else: campo.border_color = obter_cor_do_tema_ativo("feedback_erro_texto")
            except ValueError: campo.border_color = obter_cor_do_tema_ativo("feedback_erro_texto")
            campo.disabled = True
            pergunta_ref = next((p for p in multiplicacoes_data if (p['fator1'] == f1 and p['fator2'] == f2) or (p['fator1'] == f2 and p['fator2'] == f1)), None)
            if pergunta_ref: registrar_resposta(pergunta_ref, acertou)
        txt_resumo.value = f"Você acertou {acertos} de {len(campos_tabuada_refs)}!"; btn_verificar.disabled = True
        salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data)
        page.update()
    btn_verificar.on_click = handle_verificar_treino
    btn_voltar = ElevatedButton("Voltar ao Menu", on_click=lambda _: page.go("/"), width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, tooltip="Retornar à tela inicial.", bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
    cont_tabuada = Container(content=coluna_itens_tabuada, border=border.all(2, obter_cor_do_tema_ativo("container_treino_borda")), border_radius=8, padding=padding.all(15), width=360, height=420, bgcolor=obter_cor_do_tema_ativo("container_treino_bg"))
    conteudo_treino = Column([titulo_treino, Container(height=10), cont_tabuada, Container(height=10), btn_verificar, Container(height=10), txt_resumo, Container(height=15), btn_voltar], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=ESPACAMENTO_COLUNA_GERAL, scroll=ScrollMode.AUTO)

    view_container = Container(content=conteudo_treino, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

def build_tela_estatisticas(page: Page):
    stats_gerais = calcular_estatisticas_gerais()
    proficiencia_tabuadas = calcular_proficiencia_tabuadas()
    heatmap_data, min_peso, max_peso = gerar_dados_heatmap()

    # --- Lógica de Cores para o Heatmap ---
    # --- Lógica de Cores para o Heatmap ---
    # Valores RGB para as cores do gradiente
    RGB_FACIL = (129, 199, 132)  # Cor correspondente a GREEN_300
    RGB_MEDIO = (255, 241, 118)  # Cor correspondente a YELLOW_300
    RGB_DIFICIL = (239, 83, 80)   # Cor correspondente a RED_400

    def interpolar_cor_rgb(valor, min_val, max_val, cor_inicio_rgb, cor_meio_rgb, cor_fim_rgb):
        """Interpola linearmente entre três cores usando seus valores RGB."""
        if min_val >= max_val: # Evita divisão por zero e normalização inválida
            return f"#{cor_meio_rgb[0]:02x}{cor_meio_rgb[1]:02x}{cor_meio_rgb[2]:02x}"

        percentual = (valor - min_val) / (max_val - min_val)
        percentual = max(0, min(1, percentual))

        if percentual < 0.5:
            p = percentual * 2
            r1, g1, b1 = cor_inicio_rgb
            r2, g2, b2 = cor_meio_rgb
        else:
            p = (percentual - 0.5) * 2
            r1, g1, b1 = cor_meio_rgb
            r2, g2, b2 = cor_fim_rgb

        r = int(r1 + p * (r2 - r1))
        g = int(g1 + p * (g2 - g1))
        b = int(b1 + p * (b2 - b1))

        return f"#{r:02x}{g:02x}{b:02x}"

    # Constantes de cor para a legenda (usando a API do Flet)
    COR_FACIL = ft.Colors.GREEN_300
    COR_MEDIO = ft.Colors.YELLOW_300
    COR_DIFICIL = ft.Colors.RED_400

    # --- Construção da Grade do Heatmap ---
    heatmap_grid = Column(spacing=2, horizontal_alignment=CrossAxisAlignment.CENTER)
    # Adiciona a linha de cabeçalho (números 1 a 10)
    header_row = Row(spacing=2)
    header_row.controls.append(Container(width=28, height=28)) # Canto vazio
    for j in range(1, 11):
        header_row.controls.append(
            Container(
                content=Text(str(j), size=12, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao")),
                width=28, height=28, alignment=alignment.center
            )
        )
    heatmap_grid.controls.append(header_row)


    for i in range(10): # Linhas 0-9 (representam 1-10)
        row = Row(spacing=2)
        # Adiciona o cabeçalho da linha (número da tabuada)
        row.controls.append(
            Container(
                content=Text(str(i + 1), size=12, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao")),
                width=28, height=28, alignment=alignment.center
            )
        )
        for j in range(10): # Colunas 0-9 (representam 1-10)
            peso = heatmap_data[i][j]
            # Normalização invertida: peso alto (difícil) tem cor "quente" (vermelho)
            cor_fundo = interpolar_cor_rgb(peso, min_peso, max_peso, RGB_FACIL, RGB_MEDIO, RGB_DIFICIL)
            celula = Container(
                width=28,
                height=28,
                bgcolor=cor_fundo,
                border_radius=3,
                tooltip=f"Dificuldade de {i+1} x {j+1}: {peso:.2f}",
                # Adiciona um leve brilho ao passar o mouse
                on_hover=lambda e: (
                    setattr(e.control.shadow, 'blur_radius', 15 if e.data == "true" else None),
                    setattr(e.control.shadow, 'color', ft.Colors.with_opacity(0.5, cor_fundo) if e.data == "true" else None),
                    e.control.update()
                ),
                shadow=ft.BoxShadow()
            )
            row.controls.append(celula)
        heatmap_grid.controls.append(row)

    # --- Legenda do Heatmap ---
    legenda_heatmap = Row(
        controls=[
            Text("Fácil", color=COR_FACIL),
            Container(
                width=150, height=10,
                gradient=ft.LinearGradient(
                    begin=alignment.center_left,
                    end=alignment.center_right,
                    colors=[COR_FACIL, COR_MEDIO, COR_DIFICIL]
                ),
                border_radius=5
            ),
            Text("Difícil", color=COR_DIFICIL)
        ],
        spacing=10, alignment=MainAxisAlignment.CENTER
    )

    lista_proficiencia_controls = []
    for t in range(1, 11):
        progresso = proficiencia_tabuadas.get(t, 0) / 100.0
        cor_barra_semantica = "feedback_acerto_texto" # Default to green (high proficiency)
        if progresso < 0.4: # Low proficiency
            cor_barra_semantica = "feedback_erro_texto" # Red
        elif progresso < 0.7: # Medium proficiency
            cor_barra_semantica = "progressbar_cor" # Theme's progress bar color (e.g., purple/blue)

        cor_barra_dinamica = obter_cor_do_tema_ativo(cor_barra_semantica)
        progressbar_bg_color_dinamica = obter_cor_do_tema_ativo("progressbar_bg_cor")

        lista_proficiencia_controls.append(
            Row(
                [
                    Text(f"Tabuada do {t}: ", size=16, color=obter_cor_do_tema_ativo("texto_padrao"), width=130),
                    ProgressBar(value=progresso, width=150, color=cor_barra_dinamica, bgcolor=progressbar_bg_color_dinamica),
                    Text(f"{proficiencia_tabuadas.get(t, 0):.1f}%", size=16, color=obter_cor_do_tema_ativo("texto_padrao"), width=60, text_align=TextAlign.RIGHT)
                ],
                alignment=MainAxisAlignment.CENTER
            )
        )

    col_prof = Column(controls=lista_proficiencia_controls, spacing=8, horizontal_alignment=CrossAxisAlignment.CENTER)

    top_3_txt = [Text(item, size=16, color=obter_cor_do_tema_ativo("texto_padrao")) for item in stats_gerais['top_3_dificeis']]
    if not top_3_txt:
        top_3_txt = [Text("Nenhuma dificuldade registrada ainda!", size=16, color=obter_cor_do_tema_ativo("texto_padrao"))]

    col_dificuldades = Column(controls=top_3_txt, spacing=5, horizontal_alignment=CrossAxisAlignment.CENTER)

    conteudo_stats = Column(
        controls=[
            Text("Suas Estatísticas", size=32, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos"), text_align=TextAlign.CENTER),
            Container(height=15),
            Text(f"Total de Perguntas Respondidas: {stats_gerais['total_respondidas']}", size=18, color=obter_cor_do_tema_ativo("texto_padrao")),
            Text(f"Percentual de Acertos Geral: {stats_gerais['percentual_acertos_geral']:.1f}%", size=18, color=obter_cor_do_tema_ativo("texto_padrao")),

            Container(
                content=Column([
                    Text("Mapa de Calor da Tabuada", size=22, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos")),
                    Text(
                        "Esta grade mostra a dificuldade de cada multiplicação. As cores variam de verde (fácil) a vermelho (difícil).",
                        size=14,
                        color=obter_cor_do_tema_ativo("texto_padrao"),
                        text_align=TextAlign.CENTER,
                        italic=True
                    ),
                ]),
                margin=ft.margin.only(top=20, bottom=10)
            ),
            heatmap_grid,
            Container(height=5),
            legenda_heatmap,

            Container(
                Text("Proficiência por Tabuada:", size=22, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos")),
                margin=ft.margin.only(top=20, bottom=10)
            ),
            col_prof,
            Container(height=10),
            Container(
                Text("Maiores Dificuldades Atuais:", size=22, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos")),
                margin=ft.margin.only(top=20, bottom=10)
            ),
            col_dificuldades,
            Container(height=25),
            ElevatedButton(
                "Voltar ao Menu",
                width=BOTAO_LARGURA_PRINCIPAL,
                height=BOTAO_ALTURA_PRINCIPAL,
                on_click=lambda _: page.go("/"),
                tooltip="Retornar à tela inicial.",
                bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"),
                color=obter_cor_do_tema_ativo("botao_principal_texto")
            ),
        ],
        scroll=ScrollMode.AUTO,
        alignment=MainAxisAlignment.CENTER,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=ESPACAMENTO_COLUNA_GERAL
    )
    view_container = Container(content=conteudo_stats, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

# --- Tela de Quiz com Fórmula Personalizada ---
def build_tela_custom_quiz(page: Page):
    global current_custom_formula_for_quiz

    if current_custom_formula_for_quiz is None:
        error_content = Column([
            Text("Erro: Nenhuma fórmula personalizada selecionada.", color=obter_cor_do_tema_ativo("feedback_erro_texto"), size=20),
            ElevatedButton("Voltar para Seleção", on_click=lambda _: page.go("/custom_formula_setup"), bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))
        ], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, spacing=20)
        return Container(content=error_content, alignment=alignment.center, expand=True, padding=PADDING_VIEW)

    formula_obj = current_custom_formula_for_quiz
    texto_pergunta = Text(size=24, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, color=obter_cor_do_tema_ativo("texto_titulos"), opacity=0, animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO)
    botoes_opcoes = [ElevatedButton(text="", width=BOTAO_LARGURA_OPCAO_QUIZ, height=BOTAO_ALTURA_OPCAO_QUIZ, opacity=0, animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO) for _ in range(4)]
    texto_feedback = Text(size=18, weight=FontWeight.BOLD, text_align=TextAlign.CENTER, opacity=0, scale=0.8, animate_opacity=ANIMACAO_FEEDBACK_OPACIDADE, animate_scale=ANIMACAO_FEEDBACK_ESCALA)

    def generate_notable_formula_question_data(quiz_config):
        formula_id = quiz_config.get('formula_id')
        user_ranges = quiz_config.get('ranges', {})

        formula_definition = get_formula_definition(formula_id)
        if not formula_definition:
            print(f"Erro: Definição da fórmula não encontrada para ID: {formula_id}")
            return None

        variables_defs = formula_definition.get('variables', [])
        calculation_func = formula_definition.get('calculation_function')
        question_template = formula_definition.get('question_template')
        reminder_template = formula_definition.get('reminder_template')
        range_constraints = formula_definition.get('range_constraints', {}) # Constraints gerais da fórmula
        user_range_overrides = quiz_config.get('ranges', {}) # Ranges específicos do usuário para esta config de quiz

        if not all([variables_defs, calculation_func, question_template, reminder_template]):
            print(f"Erro: Definição da fórmula incompleta para ID: {formula_id}")
            return None

        local_vars_values = {}

        # Gerar idades primeiro, pois valor_total pode depender delas
        idade_var_names = [v for v in variables_defs if 'idade' in v]
        other_var_names = [v for v in variables_defs if 'idade' not in v and v != 'valor_total']

        # Processar idades
        for var_name in idade_var_names:
            # User overrides para ranges de 'a' e 'b' (que são mapeados para idades aqui)
            # Se a config do quiz tem ranges específicos para 'a' ou 'b', e estamos processando 'idade_irmao1' (mapeado de 'a')
            # ou 'idade_irmao2' (mapeado de 'b'), usamos esses ranges.
            # Nota: Esta lógica de mapeamento 'a'/'b' para idades é um pouco implícita.
            # Seria melhor se os user_ranges usassem os nomes das variáveis diretamente.
            # Por ora, vamos assumir que 'a' corresponde à primeira idade, 'b' à segunda.

            current_user_range_for_var = user_range_overrides.get(var_name, {}) # Tenta pegar pelo nome exato primeiro
            if not current_user_range_for_var: # Fallback para mapeamento a/b se existir
                if var_name == 'idade_irmao1' and 'a' in user_range_overrides:
                    current_user_range_for_var = user_range_overrides['a']
                elif var_name == 'idade_irmao2' and 'b' in user_range_overrides:
                    current_user_range_for_var = user_range_overrides['b']

            formula_constraints_for_var = range_constraints.get(var_name, {})

            default_min_val = 1
            default_max_val = 10 # Default para idades

            min_val = current_user_range_for_var.get('min', formula_constraints_for_var.get('min', default_min_val))
            max_val = current_user_range_for_var.get('max', formula_constraints_for_var.get('max', default_max_val))

            if min_val > max_val: min_val = max_val

            not_equal_to_var_name = formula_constraints_for_var.get('not_equal_to_var')
            val_candidate = -1
            if not_equal_to_var_name and not_equal_to_var_name in local_vars_values:
                forbidden_value = local_vars_values[not_equal_to_var_name]
                attempts = 0
                while attempts < 20:
                    val_candidate = random.randint(min_val, max_val)
                    if val_candidate != forbidden_value: break
                    attempts += 1
                else: # Se não conseguiu gerar diferente, usa o último candidato
                    pass # val_candidate já tem um valor
            else:
                val_candidate = random.randint(min_val, max_val)
            local_vars_values[var_name] = val_candidate

        # Gerar valor_total de forma coordenada para fórmulas de grandezas
        if formula_id.startswith("grandezas_"):
            idade1 = local_vars_values.get('idade_irmao1')
            idade2 = local_vars_values.get('idade_irmao2')

            if idade1 is None or idade2 is None:
                print(f"Erro: Idades não geradas corretamente para {formula_id}")
                return None # Não pode prosseguir

            # Usar os ranges de valor_total da definição da fórmula como guia
            vt_constraints = range_constraints.get('valor_total', {})
            min_vt_desejado = vt_constraints.get('min', 20)
            max_vt_desejado = vt_constraints.get('max', 1000)

            novo_valor_total = -1

            if formula_id == "grandezas_diretamente_proporcionais":
                soma_idades = idade1 + idade2
                if soma_idades == 0: return None # Evita divisão por zero

                min_k = math.ceil(min_vt_desejado / soma_idades)
                max_k = math.floor(max_vt_desejado / soma_idades)

                k_multiplicador = random.randint(max(1, min_k), max(1, max_k)) if max_k >= min_k and max_k > 0 else random.randint(2,10)
                novo_valor_total = soma_idades * k_multiplicador

            elif formula_id == "grandezas_inversamente_proporcionais":
                if idade1 == 0 or idade2 == 0: return None # Evita divisão por zero

                l = mmc(idade1, idade2)
                prop1 = l // idade1
                prop2 = l // idade2
                soma_proporcoes_inteiras = prop1 + prop2
                if soma_proporcoes_inteiras == 0: return None

                min_k = math.ceil(min_vt_desejado / soma_proporcoes_inteiras)
                max_k = math.floor(max_vt_desejado / soma_proporcoes_inteiras)

                k_multiplicador = random.randint(max(1, min_k), max(1, max_k)) if max_k >= min_k and max_k > 0 else random.randint(2,10)
                novo_valor_total = soma_proporcoes_inteiras * k_multiplicador

            local_vars_values['valor_total'] = novo_valor_total

        # Processar outras variáveis (nomes, 'a', 'b' para fórmulas não-grandezas, e valor_total para não-grandezas)
        vars_to_process_generically = other_var_names
        if not formula_id.startswith("grandezas_"): # Se não for grandeza, valor_total é gerado genericamente
            vars_to_process_generically.append('valor_total')

        for var_name in vars_to_process_generically:
            if var_name not in variables_defs: continue # Skip if var_name (like 'valor_total') isn't in this formula's defs
            if var_name in local_vars_values: continue # Já processado (ex: valor_total para grandezas)

            custom_generator = formula_definition.get('custom_variable_generators', {}).get(var_name)
            if custom_generator:
                local_vars_values[var_name] = custom_generator()
                continue

            current_user_range_for_var = user_range_overrides.get(var_name, {})
            formula_constraints_for_var = range_constraints.get(var_name, {})

            default_min = 1; default_max = 10 # Default genérico
            if var_name == 'valor_total': # Default específico para valor_total (não-grandezas)
                default_min = 20; default_max = 1000
            elif var_name == 'a' or var_name == 'b': # Default para 'a' e 'b' de outras fórmulas
                 default_min = formula_constraints_for_var.get('min', 1)
                 default_max = formula_constraints_for_var.get('max', 10)


            min_val = current_user_range_for_var.get('min', formula_constraints_for_var.get('min', default_min))
            max_val = current_user_range_for_var.get('max', formula_constraints_for_var.get('max', default_max))

            if min_val > max_val: min_val = max_val

            # Constraints como less_than_a, etc. para 'a' e 'b'
            # Esta lógica precisa ser robusta para diferentes tipos de constraints
            # Exemplo: 'b' < 'a' ou 'b' <= 'a'
            # Para simplificar, a lógica de not_equal_to_var já foi tratada para idades.
            # Para 'a' e 'b' de outras fórmulas, constraints mais complexas podem precisar de ajuste aqui.
            # A lógica atual de gerar 'a' e 'b' independentemente e depois validar pode não ser ideal.
            # Por ora, vamos focar na geração simples por range.
            local_vars_values[var_name] = random.randint(min_val, max_val)

        # Validação final e chamada da função de cálculo
        # Garantir que todas as chaves necessárias para calculation_func estejam presentes
        # As chaves para calculation_func são as listadas em formula_definition['variables']

        # Preencher com nomes de irmãos se ainda não estiverem (caso não use custom_generator)
        if 'nome_irmao1' in variables_defs and 'nome_irmao1' not in local_vars_values:
            local_vars_values['nome_irmao1'] = random.choice(["Ana", "João", "Sofia"])
        if 'nome_irmao2' in variables_defs and 'nome_irmao2' not in local_vars_values:
            local_vars_values['nome_irmao2'] = random.choice(["Lucas", "Clara", "Pedro"])


        # Verificar se todas as variáveis necessárias para a função de cálculo estão presentes
        calculation_args = {}
        for var_key in variables_defs: # Iterar sobre as chaves que a função de cálculo espera
            if var_key not in local_vars_values:
                # Tentar gerar se for uma variável simples que faltou e não tem custom generator
                # Isso é um fallback, idealmente todas deveriam ser geradas acima.
                if var_key not in formula_definition.get('custom_variable_generators', {}):
                    f_constr = range_constraints.get(var_key, {})
                    u_constr = user_range_overrides.get(var_key, {})
                    min_v = u_constr.get('min', f_constr.get('min', 1))
                    max_v = u_constr.get('max', f_constr.get('max', 10))
                    if min_v > max_v: min_v = max_v
                    local_vars_values[var_key] = random.randint(min_v, max_v)
                    print(f"Aviso: Variável '{var_key}' gerada no fallback para {formula_id}.")

            if var_key in local_vars_values:
                 calculation_args[var_key] = local_vars_values[var_key]
            else:
                print(f"Erro Crítico: Chave '{var_key}' esperada pela função de cálculo não encontrada em local_vars_values para {formula_id} nem gerada no fallback. Valores: {local_vars_values}")
                return None


        try:
            # Passar apenas os argumentos que a função de cálculo espera
            correct_answer = calculation_func(**calculation_args)
        except KeyError as ke:
            print(f"Erro de Chave ao calcular fórmula '{formula_id}' com args {calculation_args}. Chave ausente: {ke}. Esperadas: {variables_defs}")
            return None
        except Exception as e:
            print(f"Erro ao calcular fórmula '{formula_id}' com args {calculation_args}. Erro: {e}. Esperadas: {variables_defs}")
            return None

        # Formatar a string da pergunta com todos os valores em local_vars_values
        # (nomes dos irmãos, idades, valor_total etc.)
        try:
            full_question_text = question_template.format(**local_vars_values)
        except KeyError as ke:
            print(f"Erro de Chave ao formatar question_template para '{formula_id}' com local_vars_values {local_vars_values}. Chave ausente: {ke}.")
            return None

        # Para as fórmulas de grandezas, a `calculation_function` agora retorna uma string "valor1,valor2".
        # A `correct_answer` será essa string.
        # As opções devem ser strings no formato "valor1,valor2".

        options_set = set()
        final_options = []

        if formula_id.startswith("grandezas_"):
            options_set.add(correct_answer) # correct_answer já é a string "v1,v2"

            # Gerar opções incorretas para grandezas
            val_total = local_vars_values.get('valor_total', 200) # Default para evitar erro se não existir
            parts_correct = [int(p) for p in correct_answer.split(',')]

            attempts = 0
            while len(options_set) < 4 and attempts < 50:
                attempts += 1
                type_error = random.choice(['swap', 'one_off', 'both_off', 'sum_differs'])

                p1, p2 = parts_correct[0], parts_correct[1]

                if type_error == 'swap':
                    if p1 != p2: # Só faz sentido se os valores forem diferentes
                        new_opt_str = f"{p2},{p1}"
                    else: # Se forem iguais, tenta outra estratégia
                        offset = random.randint(5, 20) * random.choice([-1,1])
                        new_opt_str = f"{max(0, p1 + offset)},{max(0, p2 - offset)}" # Mantém a soma
                        if new_opt_str == correct_answer: # Evita adicionar a correta de novo
                            new_opt_str = f"{max(0, p1 - offset)},{max(0, p2 + offset)}"


                elif type_error == 'one_off':
                    offset = random.randint(max(1, int(p1 * 0.1)), max(5, int(p1 * 0.25))) * random.choice([-1, 1])
                    if random.choice([True, False]):
                        new_p1 = max(0, p1 + offset)
                        new_p2 = p2
                        # Ajustar new_p2 para que a soma ainda seja val_total, se possível, ou próximo
                        # new_p2 = val_total - new_p1 # Isso faria a soma ser sempre correta, o que não queremos para todas as opções.
                        # Para 'one_off', a outra parte pode ficar igual ou ser levemente ajustada para não bater a soma exata.
                        if abs(new_p1 + new_p2 - val_total) > val_total * 0.05 : # Se a soma ficou muito distante
                             new_p2 = max(0, val_total - new_p1) if (val_total - new_p1) > 0 else p2 # Tenta ajustar
                    else:
                        new_p1 = p1
                        new_p2 = max(0, p2 + offset)
                        if abs(new_p1 + new_p2 - val_total) > val_total * 0.05 :
                             new_p1 = max(0, val_total - new_p2) if (val_total - new_p2) > 0 else p1


                    new_opt_str = f"{int(round(new_p1))},{int(round(new_p2))}"

                elif type_error == 'both_off':
                    offset1 = random.randint(max(1, int(p1 * 0.1)), max(5, int(p1 * 0.2))) * random.choice([-1, 1])
                    offset2 = random.randint(max(1, int(p2 * 0.1)), max(5, int(p2 * 0.2))) * random.choice([-1, 1])
                    new_p1 = max(0, p1 + offset1)
                    new_p2 = max(0, p2 + offset2)
                    new_opt_str = f"{int(round(new_p1))},{int(round(new_p2))}"

                else: # sum_differs (ou fallback)
                    # Gera duas partes que somam algo diferente do valor_total
                    new_p1 = max(0, p1 + random.randint(-int(val_total*0.15), int(val_total*0.15)))
                    new_p2 = max(0, val_total - new_p1 + random.randint(-int(val_total*0.1), int(val_total*0.1)) * random.choice([-1,1,1])) # Garante que a soma não seja exatamente val_total
                    if new_p1 == p1 and new_p2 == p2: # Evita adicionar a correta
                        new_p2 += random.randint(5,15) * random.choice([-1,1])
                        new_p2 = max(0, new_p2)

                    new_opt_str = f"{int(round(new_p1))},{int(round(new_p2))}"

                if new_opt_str not in options_set:
                    options_set.add(new_opt_str)

            final_options = list(options_set)
            while len(final_options) < 4: # Fallback se não gerou 4 opções
                fb_p1 = random.randint(0, int(round(val_total)))
                fb_p2 = max(0, int(round(val_total - fb_p1 + random.randint(-20,20)))) # Soma próxima, mas não exata
                fb_opt_str = f"{fb_p1},{fb_p2}"
                if fb_opt_str not in final_options:
                    final_options.append(fb_opt_str)
                else: # Evita duplicatas no fallback
                    final_options.append(f"{fb_p1+1},{max(0,fb_p2-1)}")


            random.shuffle(final_options)

        else: # Lógica original para outras fórmulas que retornam int/float
            options_set_num = {int(round(float(correct_answer)))} # Converte para float primeiro em caso de erro
            attempts = 0
            # Gerar opções incorretas
            ca_num = float(correct_answer)
            possible_offsets = [-10, -5, -2, -1, 1, 2, 5, 10]
            if abs(ca_num) > 50:
                possible_offsets.extend([int(round(ca_num * 0.1)), int(round(ca_num * -0.1))])
                possible_offsets.extend([int(round(ca_num * 0.05)), int(round(ca_num * -0.05))])
            possible_offsets = sorted(list(set(o for o in possible_offsets if o != 0)))

            while len(options_set_num) < 4 and attempts < 50:
                offset_val = random.choice(possible_offsets) if possible_offsets else random.randint(-5,5)
                new_opt_candidate = ca_num + offset_val
                new_opt = int(round(new_opt_candidate))
                if new_opt not in options_set_num: options_set_num.add(new_opt)
                attempts += 1

            idx_fallback = 1
            while len(options_set_num) < 4 and idx_fallback < 20:
                alt_opt_positive = int(round(ca_num + idx_fallback * (random.randint(1,3))))
                alt_opt_negative = int(round(ca_num - idx_fallback * (random.randint(1,3))))
                if alt_opt_positive not in options_set_num: options_set_num.add(alt_opt_positive)
                if len(options_set_num) < 4 and alt_opt_negative not in options_set_num: options_set_num.add(alt_opt_negative)
                idx_fallback += 1

            while len(options_set_num) < 4:
                random_fill_opt = random.randint(int(round(ca_num-20)), int(round(ca_num+20)))
                if random_fill_opt not in options_set_num: options_set_num.add(random_fill_opt)

            final_options = [str(opt) for opt in list(options_set_num)] # Converte para string
            random.shuffle(final_options)


        # A pergunta do quiz já está completa no question_template para grandezas.
        # Para outras, 'full_question_text' é usado.
        # A 'correct_answer' agora é uma string para grandezas, ou int/float convertido para string para outras.

        full_question_text_quiz = full_question_text # Para fórmulas não-grandezas
        if formula_id.startswith("grandezas_"):
             # A full_question_text já é a pergunta completa para grandezas.
             # Não precisa do f-string de antes que focava só no primeiro.
             full_question_text_quiz = full_question_text

        return {
            'full_question': full_question_text_quiz,
            'options': final_options[:4],
            'correct_answer': str(correct_answer), # Garante que a resposta correta seja string
            'reminder_template': reminder_template,
            'original_question_template_for_display': full_question_text
        }

    botao_proxima = ElevatedButton("Próxima Pergunta", on_click=None, visible=False, width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))

    current_question_data_ref = {}

    texto_lembrete_formula = Text(
        "",
        size=16,
        color=obter_cor_do_tema_ativo("texto_padrao"),
        text_align=TextAlign.CENTER,
        opacity=0,
        animate_opacity=ANIMACAO_APARICAO_TEXTO_BOTAO
    )

    def handle_custom_answer(e, botao_clicado_ref, todos_botoes_opcoes_ref, txt_feedback_ctrl_ref, txt_lembrete_ctrl_ref, btn_proxima_ctrl_ref, question_data_ref, formula_config_ref):
        selected_option = botao_clicado_ref.data['option']
        correct_answer = question_data_ref['correct_answer']
        reminder_text = question_data_ref.get('reminder_template', "")

        is_correct = (selected_option == correct_answer)

        if is_correct:
            txt_feedback_ctrl_ref.value = "Correto!"
            txt_feedback_ctrl_ref.color = obter_cor_do_tema_ativo("feedback_acerto_texto")
            botao_clicado_ref.bgcolor = obter_cor_do_tema_ativo("feedback_acerto_botao_bg")
        else:
            txt_feedback_ctrl_ref.value = f"Errado! A resposta era {correct_answer}"
            txt_feedback_ctrl_ref.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            botao_clicado_ref.bgcolor = obter_cor_do_tema_ativo("feedback_erro_botao_bg")
            for btn_op in todos_botoes_opcoes_ref:
                if btn_op.data['option'] == correct_answer:
                    btn_op.bgcolor = obter_cor_do_tema_ativo("feedback_acerto_botao_bg")
                    break

        for btn in todos_botoes_opcoes_ref: btn.disabled = True
        txt_feedback_ctrl_ref.opacity = 1; txt_feedback_ctrl_ref.scale = 1

        # Exibe o lembrete que pode ser a pergunta original mais completa
        original_question_template = question_data_ref.get('original_question_template_for_display')
        actual_reminder = question_data_ref.get('reminder_template', "")

        if formula_config_ref.get('formula_id',"").startswith("grandezas_") and original_question_template:
             # Para grandezas, o "lembrete" principal é a pergunta completa sobre ambos os irmãos
            txt_lembrete_ctrl_ref.value = f"Detalhe: {original_question_template}\nLembrete Fórmula: {actual_reminder}"
        elif actual_reminder:
            txt_lembrete_ctrl_ref.value = f"Lembrete: {actual_reminder}"
        else:
            txt_lembrete_ctrl_ref.value = "" # Limpa se não houver lembrete

        if txt_lembrete_ctrl_ref.value:
            txt_lembrete_ctrl_ref.opacity = 1
        else:
            txt_lembrete_ctrl_ref.opacity = 0


        btn_proxima_ctrl_ref.visible = True; page.update()

    def carregar_nova_pergunta_custom(page_ref, formula_config_ref, txt_pergunta_ctrl, btn_opcoes_ctrls, txt_feedback_ctrl, txt_lembrete_ctrl, btn_proxima_ctrl, question_data_storage):
        txt_feedback_ctrl.opacity = 0; txt_feedback_ctrl.scale = 0.8
        txt_lembrete_ctrl.opacity = 0
        txt_pergunta_ctrl.opacity = 0
        for btn_opcao in btn_opcoes_ctrls: btn_opcao.opacity = 0

        question_data = generate_notable_formula_question_data(formula_config_ref)

        if not question_data:
            txt_pergunta_ctrl.value = "Erro ao gerar pergunta para esta configuração."; txt_pergunta_ctrl.opacity = 1
            for btn in btn_opcoes_ctrls: btn.visible = False
            txt_feedback_ctrl.value = ""; btn_proxima_ctrl.visible = False
            btn_proxima_ctrl.text = "Voltar para Configuração"
            btn_proxima_ctrl.on_click = lambda _: page.go("/formula_quiz_setup")
            btn_proxima_ctrl.visible = True
            page_ref.update(); return

        question_data_storage.clear()
        question_data_storage.update(question_data)

        # 'full_question' já está adaptada para o quiz (focando no primeiro irmão para grandezas)
        txt_pergunta_ctrl.value = question_data['full_question']

        for i in range(4):
            if i < len(question_data['options']):
                op_val_str = str(question_data['options'][i]) # Options are now always strings

                # Para grandezas, as opções são "valor1,valor2" e não devem ter "R$" prefixo.
                # Para outras fórmulas, as opções são números (convertidos para string) e podem ter "R$" se apropriado (mas a lógica atual não adiciona R$ para elas de forma genérica aqui).
                # A decisão de adicionar "R$" foi removida para simplificar, pois o formato da opção já é o display.
                btn_opcoes_ctrls[i].text = op_val_str
                btn_opcoes_ctrls[i].data = {'option': op_val_str} # op_val_str é a string da opção
                btn_opcoes_ctrls[i].on_click = lambda e, btn=btn_opcoes_ctrls[i]: handle_custom_answer(e, btn, btn_opcoes_ctrls, txt_feedback_ctrl, txt_lembrete_ctrl, btn_proxima_ctrl, question_data_storage, formula_config_ref)
                btn_opcoes_ctrls[i].bgcolor = obter_cor_do_tema_ativo("botao_opcao_quiz_bg")
                btn_opcoes_ctrls[i].color = obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
                btn_opcoes_ctrls[i].disabled = False; btn_opcoes_ctrls[i].visible = True
            else:
                btn_opcoes_ctrls[i].visible = False

        txt_feedback_ctrl.value = ""; btn_proxima_ctrl.visible = False
        btn_proxima_ctrl.text = "Próxima Pergunta"
        btn_proxima_ctrl.on_click = lambda _: carregar_nova_pergunta_custom(page_ref, formula_config_ref, txt_pergunta_ctrl, btn_opcoes_ctrls, txt_feedback_ctrl, txt_lembrete_ctrl, btn_proxima_ctrl, question_data_storage)

        txt_pergunta_ctrl.opacity = 1
        for btn_opcao in btn_opcoes_ctrls:
            if btn_opcao.visible: btn_opcao.opacity = 1
        page_ref.update()

    botao_proxima.on_click = lambda _: carregar_nova_pergunta_custom(page, formula_obj, texto_pergunta, botoes_opcoes, texto_feedback, texto_lembrete_formula, botao_proxima, current_question_data_ref)
    carregar_nova_pergunta_custom(page, formula_obj, texto_pergunta, botoes_opcoes, texto_feedback, texto_lembrete_formula, botao_proxima, current_question_data_ref)

    botao_voltar_setup = ElevatedButton("Mudar Config. / Menu", on_click=lambda _: page.go("/formula_quiz_setup"), width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL, bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto"))

    layout_botoes = Column([Row(botoes_opcoes[0:2], alignment=MainAxisAlignment.CENTER, spacing=15), Container(height=10), Row(botoes_opcoes[2:4], alignment=MainAxisAlignment.CENTER, spacing=15)], horizontal_alignment=CrossAxisAlignment.CENTER, spacing=10)

    conteudo_quiz = Column(
        [
            Text(f"Quiz Fórmula: {formula_obj['name']}", size=20, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos"), text_align=TextAlign.CENTER),
            Container(height=5),
            texto_pergunta,
            Container(height=15),
            layout_botoes,
            Container(height=15),
            texto_feedback,
            Container(height=10),
            texto_lembrete_formula,
            Container(height=20),
            botao_proxima,
            Container(height=10),
            botao_voltar_setup
        ],
        alignment=MainAxisAlignment.CENTER,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=ESPACAMENTO_COLUNA_GERAL,
        scroll=ScrollMode.AUTO
    )

    view_container = Container(content=conteudo_quiz, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

# --- Tela para Divisão Diretamente Proporcional ---
def build_tela_divisao_diretamente_proporcional(page: Page):
    valor_total_field = TextField(
        label="Valor Total a ser Dividido (V)",
        width=350,
        keyboard_type=KeyboardType.NUMBER,
        color=obter_cor_do_tema_ativo("texto_padrao"),
        border_color=obter_cor_do_tema_ativo("textfield_border_color")
    )

    grandezas_column = Column(spacing=10, scroll=ScrollMode.AUTO, height=200)
    resultados_column = Column(spacing=5, scroll=ScrollMode.AUTO, height=150)
    feedback_text_divisao = Text("", color=obter_cor_do_tema_ativo("texto_padrao"), size=16)

    def adicionar_campo_grandeza(e=None):
        if len(grandezas_column.controls) >= 10: # Limite de 10 grandezas
            feedback_text_divisao.value = "Limite de 10 grandezas atingido."
            feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()
            return

        novo_nome_field = TextField(
            label=f"Nome da Parte {len(grandezas_column.controls) + 1}",
            width=160,
            color=obter_cor_do_tema_ativo("texto_padrao"),
            border_color=obter_cor_do_tema_ativo("textfield_border_color")
        )
        nova_grandeza_field = TextField(
            label=f"Valor da Grandeza {len(grandezas_column.controls) + 1}",
            width=160,
            keyboard_type=KeyboardType.NUMBER,
            color=obter_cor_do_tema_ativo("texto_padrao"),
            border_color=obter_cor_do_tema_ativo("textfield_border_color")
        )
        grandezas_column.controls.append(
            Row([novo_nome_field, nova_grandeza_field], spacing=10, alignment=MainAxisAlignment.CENTER)
        )
        feedback_text_divisao.value = "" # Limpa feedback anterior
        page.update()

    def calcular_divisao_handler(e):
        resultados_column.controls.clear()
        try:
            valor_total_str = valor_total_field.value
            if not valor_total_str:
                feedback_text_divisao.value = "Por favor, insira o Valor Total."
                feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                page.update()
                return

            valor_total = float(valor_total_str)
            if valor_total <= 0:
                feedback_text_divisao.value = "O Valor Total deve ser positivo."
                feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                page.update()
                return

            grandezas_input = []
            for i, row_control in enumerate(grandezas_column.controls):
                if isinstance(row_control, Row) and len(row_control.controls) == 2:
                    nome_field = row_control.controls[0]
                    grandeza_val_field = row_control.controls[1]

                    nome = nome_field.value.strip()
                    grandeza_str = grandeza_val_field.value

                    if not nome:
                        feedback_text_divisao.value = f"Por favor, insira o Nome da Parte {i+1}."
                        feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                        page.update()
                        return
                    if not grandeza_str:
                        feedback_text_divisao.value = f"Por favor, insira o Valor da Grandeza {i+1}."
                        feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                        page.update()
                        return

                    grandeza_valor = float(grandeza_str)
                    if grandeza_valor <= 0:
                        feedback_text_divisao.value = f"O Valor da Grandeza {i+1} ('{nome}') deve ser positivo."
                        feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                        page.update()
                        return
                    grandezas_input.append((nome, grandeza_valor))

            if not grandezas_input:
                feedback_text_divisao.value = "Adicione pelo menos uma grandeza."
                feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                page.update()
                return

            resultado_calculo = calc_divisao_diretamente_proporcional(valor_total, grandezas_input)

            if not resultado_calculo: # Caso de soma das grandezas ser zero
                 feedback_text_divisao.value = "A soma das grandezas não pode ser zero."
                 feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            else:
                resultados_column.controls.append(
                    Text("Resultados da Divisão:", weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos"))
                )
                soma_partes = 0
                for nome, parte in resultado_calculo.items():
                    resultados_column.controls.append(
                        Text(f"{nome}: {parte:.2f}", color=obter_cor_do_tema_ativo("texto_padrao"))
                    )
                    soma_partes += parte
                resultados_column.controls.append(
                    Text(f"Soma das Partes: {soma_partes:.2f} (Original: {valor_total:.2f})", weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao"))
                )
                feedback_text_divisao.value = "Cálculo realizado com sucesso!"
                feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_acerto_texto")

        except ValueError:
            feedback_text_divisao.value = "Erro: Verifique se todos os valores numéricos são válidos."
            feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
        except Exception as ex:
            feedback_text_divisao.value = f"Erro inesperado: {str(ex)}"
            feedback_text_divisao.color = obter_cor_do_tema_ativo("feedback_erro_texto")
        page.update()

    # Adicionar campos iniciais para duas grandezas
    adicionar_campo_grandeza()
    adicionar_campo_grandeza()

    add_grandeza_button = ElevatedButton(
        "Adicionar Grandeza",
        icon=Icons.ADD_CIRCLE_OUTLINE,
        on_click=adicionar_campo_grandeza,
        width=BOTAO_LARGURA_PRINCIPAL - 80, height=BOTAO_ALTURA_PRINCIPAL -10,
        bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"),
        color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
    )

    remove_grandeza_button = ElevatedButton(
        "Remover Última",
        icon=Icons.REMOVE_CIRCLE_OUTLINE,
        on_click=lambda _: (
            grandezas_column.controls.pop() if len(grandezas_column.controls) > 1 else None,
            page.update()
        ),
        width=BOTAO_LARGURA_PRINCIPAL - 80, height=BOTAO_ALTURA_PRINCIPAL -10,
        bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"),
        color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto"),
        disabled=len(grandezas_column.controls) <= 1
    )


    calcular_button = ElevatedButton(
        "Calcular Divisão",
        on_click=calcular_divisao_handler,
        width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL,
        bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"),
        color=obter_cor_do_tema_ativo("botao_principal_texto")
    )
    back_button = ElevatedButton(
        "Voltar ao Menu",
        on_click=lambda _: page.go("/"),
        width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL,
        bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"),
        color=obter_cor_do_tema_ativo("botao_principal_texto")
    )

    content = Column(
        controls=[
            Text("Divisão Diretamente Proporcional", size=28, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos")),
            Container(height=10),
            valor_total_field,
            Container(height=10),
            Text("Insira as Partes e suas Grandezas:", size=18, color=obter_cor_do_tema_ativo("texto_padrao")),
            Container(
                content=grandezas_column,
                border=border.all(1, obter_cor_do_tema_ativo("textfield_border_color")),
                border_radius=5,
                padding=10,
                margin=ft.margin.symmetric(vertical=5)
            ),
            Row([add_grandeza_button, remove_grandeza_button], alignment=MainAxisAlignment.CENTER, spacing=10),
            Container(height=15),
            calcular_button,
            Container(height=10),
            feedback_text_divisao,
            Container(height=10),
            Container(
                content=resultados_column,
                border=border.all(1, obter_cor_do_tema_ativo("textfield_border_color")),
                border_radius=5,
                padding=10,
                margin=margin.symmetric(vertical=5),
                visible= True # Sempre visível, mas conteúdo é dinâmico
            ),
            Container(height=15),
            back_button,
        ],
        scroll=ScrollMode.AUTO,
        alignment=MainAxisAlignment.START, # Alinhar ao topo para melhor visualização com scroll
        horizontal_alignment=CrossAxisAlignment.CENTER,
        spacing=ESPACAMENTO_COLUNA_GERAL
    )

    # Atualizar estado do botão de remover
    def update_remove_button_state():
        remove_grandeza_button.disabled = len(grandezas_column.controls) <= 1
        page.update()

    grandezas_column.on_change = lambda _: update_remove_button_state() # Atualiza se a coluna mudar (adicionar/remover)
    update_remove_button_state() # Estado inicial


    view_container = Container(content=content, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

# --- Tela para Divisão Inversamente Proporcional ---
def build_tela_divisao_inversamente_proporcional(page: Page):
    valor_total_field_inv = TextField(
        label="Valor Total a ser Dividido (V)",
        width=350,
        keyboard_type=KeyboardType.NUMBER,
        color=obter_cor_do_tema_ativo("texto_padrao"),
        border_color=obter_cor_do_tema_ativo("textfield_border_color")
    )

    grandezas_column_inv = Column(spacing=10, scroll=ScrollMode.AUTO, height=200)
    resultados_column_inv = Column(spacing=5, scroll=ScrollMode.AUTO, height=150)
    feedback_text_divisao_inv = Text("", color=obter_cor_do_tema_ativo("texto_padrao"), size=16)

    def adicionar_campo_grandeza_inv(e=None):
        if len(grandezas_column_inv.controls) >= 10: # Limite de 10 grandezas
            feedback_text_divisao_inv.value = "Limite de 10 grandezas atingido."
            feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            page.update()
            return

        novo_nome_field = TextField(
            label=f"Nome da Parte {len(grandezas_column_inv.controls) + 1}",
            width=160,
            color=obter_cor_do_tema_ativo("texto_padrao"),
            border_color=obter_cor_do_tema_ativo("textfield_border_color")
        )
        nova_grandeza_field = TextField(
            label=f"Valor da Grandeza {len(grandezas_column_inv.controls) + 1} (≠0)",
            width=160,
            keyboard_type=KeyboardType.NUMBER,
            color=obter_cor_do_tema_ativo("texto_padrao"),
            border_color=obter_cor_do_tema_ativo("textfield_border_color")
        )
        grandezas_column_inv.controls.append(
            Row([novo_nome_field, nova_grandeza_field], spacing=10, alignment=MainAxisAlignment.CENTER)
        )
        feedback_text_divisao_inv.value = ""
        page.update()

    def calcular_divisao_handler_inv(e):
        resultados_column_inv.controls.clear()
        try:
            valor_total_str = valor_total_field_inv.value
            if not valor_total_str:
                feedback_text_divisao_inv.value = "Por favor, insira o Valor Total."
                feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                page.update()
                return

            valor_total = float(valor_total_str)
            if valor_total <= 0:
                feedback_text_divisao_inv.value = "O Valor Total deve ser positivo."
                feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                page.update()
                return

            grandezas_input = []
            for i, row_control in enumerate(grandezas_column_inv.controls):
                if isinstance(row_control, Row) and len(row_control.controls) == 2:
                    nome_field = row_control.controls[0]
                    grandeza_val_field = row_control.controls[1]

                    nome = nome_field.value.strip()
                    grandeza_str = grandeza_val_field.value

                    if not nome:
                        feedback_text_divisao_inv.value = f"Por favor, insira o Nome da Parte {i+1}."
                        feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                        page.update()
                        return
                    if not grandeza_str:
                        feedback_text_divisao_inv.value = f"Por favor, insira o Valor da Grandeza {i+1}."
                        feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                        page.update()
                        return

                    grandeza_valor = float(grandeza_str)
                    if grandeza_valor == 0: # Para divisão inversa, grandeza não pode ser zero
                        feedback_text_divisao_inv.value = f"O Valor da Grandeza {i+1} ('{nome}') não pode ser zero."
                        feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                        page.update()
                        return
                    if grandeza_valor < 0: # Geralmente se usa grandezas positivas
                         feedback_text_divisao_inv.value = f"O Valor da Grandeza {i+1} ('{nome}') deve ser positivo."
                         feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                         page.update()
                         return
                    grandezas_input.append((nome, grandeza_valor))

            if not grandezas_input:
                feedback_text_divisao_inv.value = "Adicione pelo menos uma grandeza."
                feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
                page.update()
                return

            resultado_calculo = calc_divisao_inversamente_proporcional(valor_total, grandezas_input)

            if not resultado_calculo or any(val is None for val in resultado_calculo.values()):
                 feedback_text_divisao_inv.value = "Erro no cálculo. Verifique se todas as grandezas são diferentes de zero."
                 feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
            else:
                resultados_column_inv.controls.append(
                    Text("Resultados da Divisão Inversa:", weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos"))
                )
                soma_partes = 0
                for nome, parte in resultado_calculo.items():
                    resultados_column_inv.controls.append(
                        Text(f"{nome}: {parte:.2f}", color=obter_cor_do_tema_ativo("texto_padrao"))
                    )
                    soma_partes += parte
                resultados_column_inv.controls.append(
                    Text(f"Soma das Partes: {soma_partes:.2f} (Original: {valor_total:.2f})", weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_padrao"))
                )
                feedback_text_divisao_inv.value = "Cálculo realizado com sucesso!"
                feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_acerto_texto")

        except ValueError:
            feedback_text_divisao_inv.value = "Erro: Verifique se todos os valores numéricos são válidos e grandezas ≠ 0."
            feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
        except Exception as ex:
            feedback_text_divisao_inv.value = f"Erro inesperado: {str(ex)}"
            feedback_text_divisao_inv.color = obter_cor_do_tema_ativo("feedback_erro_texto")
        page.update()

    adicionar_campo_grandeza_inv()
    adicionar_campo_grandeza_inv()

    add_grandeza_button_inv = ElevatedButton(
        "Adicionar Grandeza", icon=Icons.ADD_CIRCLE_OUTLINE, on_click=adicionar_campo_grandeza_inv,
        width=BOTAO_LARGURA_PRINCIPAL - 80, height=BOTAO_ALTURA_PRINCIPAL -10,
        bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"), color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto")
    )
    remove_grandeza_button_inv = ElevatedButton(
        "Remover Última", icon=Icons.REMOVE_CIRCLE_OUTLINE,
        on_click=lambda _: (grandezas_column_inv.controls.pop() if len(grandezas_column_inv.controls) > 1 else None, page.update()),
        width=BOTAO_LARGURA_PRINCIPAL - 80, height=BOTAO_ALTURA_PRINCIPAL -10,
        bgcolor=obter_cor_do_tema_ativo("botao_opcao_quiz_bg"), color=obter_cor_do_tema_ativo("botao_opcao_quiz_texto"),
        disabled=len(grandezas_column_inv.controls) <= 1
    )

    calcular_button_inv = ElevatedButton(
        "Calcular Divisão Inversa", on_click=calcular_divisao_handler_inv,
        width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL,
        bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto")
    )
    back_button_inv = ElevatedButton(
        "Voltar ao Menu", on_click=lambda _: page.go("/"),
        width=BOTAO_LARGURA_PRINCIPAL, height=BOTAO_ALTURA_PRINCIPAL,
        bgcolor=obter_cor_do_tema_ativo("botao_principal_bg"), color=obter_cor_do_tema_ativo("botao_principal_texto")
    )

    content_inv = Column(
        controls=[
            Text("Divisão Inversamente Proporcional", size=28, weight=FontWeight.BOLD, color=obter_cor_do_tema_ativo("texto_titulos")),
            Container(height=10),
            valor_total_field_inv,
            Container(height=10),
            Text("Insira as Partes e suas Grandezas (valores ≠ 0):", size=18, color=obter_cor_do_tema_ativo("texto_padrao")),
            Container(
                content=grandezas_column_inv,
                border=border.all(1, obter_cor_do_tema_ativo("textfield_border_color")),
                border_radius=5, padding=10, margin=ft.margin.symmetric(vertical=5)
            ),
            Row([add_grandeza_button_inv, remove_grandeza_button_inv], alignment=MainAxisAlignment.CENTER, spacing=10),
            Container(height=15),
            calcular_button_inv,
            Container(height=10),
            feedback_text_divisao_inv,
            Container(height=10),
            Container(
                content=resultados_column_inv,
                border=border.all(1, obter_cor_do_tema_ativo("textfield_border_color")),
                border_radius=5, padding=10, margin=margin.symmetric(vertical=5)
            ),
            Container(height=15),
            back_button_inv,
        ],
        scroll=ScrollMode.AUTO, alignment=MainAxisAlignment.START,
        horizontal_alignment=CrossAxisAlignment.CENTER, spacing=ESPACAMENTO_COLUNA_GERAL
    )

    def update_remove_button_state_inv():
        remove_grandeza_button_inv.disabled = len(grandezas_column_inv.controls) <= 1
        page.update()
    grandezas_column_inv.on_change = lambda _: update_remove_button_state_inv()
    update_remove_button_state_inv()

    view_container = Container(content=content_inv, alignment=alignment.center, expand=True, padding=PADDING_VIEW)
    if tema_ativo_nome == "escuro_moderno":
        view_container.gradient = obter_cor_do_tema_ativo("gradient_page_bg")
        view_container.bgcolor = None
    else:
        view_container.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        view_container.gradient = None
    return view_container

# --- Configuração Principal da Página e Rotas ---
def main(page: Page):
    global tema_ativo_nome, multiplicacoes_data, custom_formulas_data

    # Carrega a configuração. Se não existir, o config.py cria um arquivo padrão.
    tema_salvo, multiplicacoes_salvas, formulas_salvas = carregar_configuracao()

    # Define o tema. Usa o tema salvo ou o padrão "colorido".
    if tema_salvo and tema_salvo in TEMAS:
        tema_ativo_nome = tema_salvo
    else:
        tema_ativo_nome = "colorido" # Garante um fallback se o tema salvo for inválido

    # Carrega as fórmulas personalizadas. Começa com uma lista vazia se não houver dados.
    if formulas_salvas is not None:
        custom_formulas_data = formulas_salvas
    else:
        custom_formulas_data = []

    # Carrega os dados de multiplicação. Se não houver, inicializa-os.
    if multiplicacoes_salvas is not None:
        multiplicacoes_data = multiplicacoes_salvas
    else:
        inicializar_multiplicacoes() # Cria os dados de tabuada pela primeira vez
        # Salva a configuração inicial para que os dados da tabuada persistam
        salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data)

    page.title = "Quiz Mestre da Tabuada"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
    page.window_width = 480
    page.window_height = 800
    page.fonts = {"RobotoSlab": "https://github.com/google/fonts/raw/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf"}

    # Inicializar o global update_dialog que foi definido como None anteriormente
    global update_dialog
    update_dialog = ft.AlertDialog(
        modal=True,
        title=Text("Confirmar Atualização"), # Título padrão
        content=update_dialog_content_text, # Conteúdo global
        # As ações são (re)definidas em show_update_dialog
    )

    def update_ui_elements_for_update_status():
        """Atualiza os elementos da UI com base no status da verificação de atualização."""
        global update_available, latest_version_tag, update_check_status_message, APP_CURRENT_VERSION, local_git_commit
        global update_status_icon, update_status_text, update_action_button # Certificar que estamos usando os globais

        # Atualiza cores baseadas no tema ATIVO
        update_status_icon.tooltip = update_check_status_message # Tooltip primeiro
        update_status_text.color = obter_cor_do_tema_ativo("texto_padrao")
        update_action_button.bgcolor = obter_cor_do_tema_ativo("botao_destaque_bg")
        update_action_button.color = obter_cor_do_tema_ativo("botao_destaque_texto")

        current_commit_hash = local_git_commit.splitlines()[0] if local_git_commit else 'N/A'
        base_text = f"v{APP_CURRENT_VERSION} ({current_commit_hash})"

        if "Erro" in update_check_status_message or "Não foi possível conectar" in update_check_status_message:
            update_status_icon.name = ft.Icons.ERROR_OUTLINE
            update_status_icon.color = obter_cor_do_tema_ativo("update_icon_color_error")
            update_status_text.value = f"{base_text} - {update_check_status_message}"
            update_action_button.visible = False
        elif update_available:
            update_status_icon.name = ft.Icons.NEW_RELEASES
            update_status_icon.color = obter_cor_do_tema_ativo("update_icon_color_available")
            update_status_icon.tooltip = f"Nova versão {latest_version_tag} disponível!"
            update_status_text.value = f"Atualização: v{APP_CURRENT_VERSION} -> {latest_version_tag}"
            update_action_button.visible = True
        else: # Nenhuma atualização ou já atualizado
            update_status_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            update_status_icon.color = obter_cor_do_tema_ativo("update_icon_color_uptodate")
            update_status_icon.tooltip = "Você está na versão mais recente."
            update_status_text.value = f"{base_text} - {update_check_status_message}"
            update_action_button.visible = False

        if page.appbar and hasattr(page.appbar, 'actions'):
            pass

        page.update()

    def run_update_check_and_ui_refresh(page_ref: Page):
        """Executa a verificação de atualização e atualiza a UI."""
        check_for_updates()
        update_ui_elements_for_update_status()

    # Atribuir o on_click para update_action_button aqui, onde 'page' é definido.
    update_action_button.on_click = lambda _: show_update_dialog(page)

    def route_change(route_obj):
        page.bgcolor = obter_cor_do_tema_ativo("fundo_pagina")
        page.views.clear()

        # AppBar unificada para todas as telas
        app_bar = ft.AppBar(
            title=Text("Quiz Mestre da Tabuada", color=obter_cor_do_tema_ativo("texto_titulos")),
            center_title=True,
            bgcolor=obter_cor_do_tema_ativo("fundo_pagina"),
            actions=[
                Row([
                    update_status_icon,
                    Container(width=5),
                    update_status_text,
                    Container(width=10)
                ], alignment=MainAxisAlignment.CENTER, vertical_alignment=CrossAxisAlignment.CENTER),
            ]
        )

        page.views.append(
            View(
                route="/",
                controls=[build_tela_apresentacao(page)],
                vertical_alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                appbar=app_bar
            )
        )
        if page.route == "/quiz":
            page.views.append(View("/quiz", [build_tela_quiz(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/quiz_invertido":
            page.views.append(View("/quiz_invertido", [build_tela_quiz_invertido(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/treino":
            page.views.append(View("/treino", [build_tela_treino(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/estatisticas":
            page.views.append(View("/estatisticas", [build_tela_estatisticas(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/formula_quiz_setup":
            page.views.append(View("/formula_quiz_setup", [build_tela_formula_quiz_setup(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/custom_quiz":
            page.views.append(View("/custom_quiz", [build_tela_custom_quiz(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/divisao_direta":
            page.views.append(View("/divisao_direta", [build_tela_divisao_diretamente_proporcional(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))
        elif page.route == "/divisao_inversa":
            page.views.append(View("/divisao_inversa", [build_tela_divisao_inversamente_proporcional(page)], vertical_alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER, appbar=app_bar))

        update_ui_elements_for_update_status() # Esta função já chama page.update()

    def view_pop(view_instance):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    def window_event_handler(e):
        if e.data == "close":
            # Garante que o estado mais recente seja salvo ao fechar
            salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data)
            page.window_destroy()

    page.on_window_event = window_event_handler
    page.window_prevent_close = True


    update_thread = threading.Thread(target=run_update_check_and_ui_refresh, args=(page,), daemon=True)
    update_thread.start()

    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
