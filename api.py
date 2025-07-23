import random
import time
from config import salvar_configuracao, carregar_configuracao

# --- Data storage ---
multiplicacoes_data = []
custom_formulas_data = []
pontuacao_maxima_cronometrado = 0
tema_ativo_nome = "colorido"

# --- Flet-independent logic from main.py ---

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
        p for p in multiplicacoes_data if (agora_ts - p['ultima_vez_apresentada_ts']) > 30
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

    salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data, pontuacao_maxima_cronometrado)

def gerar_opcoes(fator1: int, fator2: int):
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
            if multiplicacoes_data:
                pergunta_aleatoria = random.choice(multiplicacoes_data)
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

def gerar_opcoes_quiz_invertido(multiplicacao_base_ref):
    resposta_correta_valor = multiplicacao_base_ref['fator1'] * multiplicacao_base_ref['fator2']
    opcao_correta_obj = {'texto': f"{multiplicacao_base_ref['fator1']} x {multiplicacao_base_ref['fator2']}", 'original_ref': multiplicacao_base_ref, 'is_correct': True}
    opcoes_geradas = [opcao_correta_obj]
    candidatos_embaralhados = random.sample(multiplicacoes_data, len(multiplicacoes_data))
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

def get_formula_definitions():
    return FORMULAS_NOTAVEIS

def get_saved_quiz_configs():
    return custom_formulas_data

def save_quiz_config(config):
    global custom_formulas_data
    custom_formulas_data.append(config)
    salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data, pontuacao_maxima_cronometrado)

def set_current_custom_formula_for_quiz(config_name):
    global current_custom_formula_for_quiz
    current_custom_formula_for_quiz = next((cfg for cfg in custom_formulas_data if cfg['name'] == config_name), None)

def save_timed_mode_score(score):
    global pontuacao_maxima_cronometrado
    if score > pontuacao_maxima_cronometrado:
        pontuacao_maxima_cronometrado = score
        salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data, pontuacao_maxima_cronometrado)

def load_initial_data():
    global tema_ativo_nome, multiplicacoes_data, custom_formulas_data, pontuacao_maxima_cronometrado
    config = carregar_configuracao()
    tema_ativo_nome = config.get("tema_ativo", "colorido")
    multiplicacoes_data = config.get("multiplicacoes_data")
    custom_formulas_data = config.get("custom_formulas_data", [])
    pontuacao_maxima_cronometrado = config.get("pontuacao_maxima_cronometrado", 0)

    if not multiplicacoes_data:
        inicializar_multiplicacoes()
        salvar_configuracao(tema_ativo_nome, multiplicacoes_data, custom_formulas_data, pontuacao_maxima_cronometrado)

load_initial_data()

FORMULAS_NOTAVEIS = [
    {
        'id': "quadrado_soma",
        'display_name': "Quadrado da Soma: (a+b)^2",
        'variables': ['a', 'b'],
        'calculation_function': lambda a, b: (a + b) ** 2,
        'question_template': "Se a={a} e b={b}, qual o valor de (a+b)^2?",
        'reminder_template': "(x+y)^2 = x^2 + 2xy + y^2",
        'range_constraints': {},
        'variable_labels': {'a': "Valor de 'a'", 'b': "Valor de 'b'"}
    },
    {
        'id': "quadrado_diferenca",
        'display_name': "Quadrado da Diferença: (a-b)^2",
        'variables': ['a', 'b'],
        'calculation_function': lambda a, b: (a - b) ** 2,
        'question_template': "Se a={a} e b={b}, qual o valor de (a-b)^2?",
        'reminder_template': "(x-y)^2 = x^2 - 2xy + y^2",
        'range_constraints': {},
        'variable_labels': {'a': "Valor de 'a'", 'b': "Valor de 'b'"}
    },
    {
        'id': "produto_soma_diferenca",
        'display_name': "Produto da Soma pela Diferença: (a+b)(a-b)",
        'variables': ['a', 'b'],
        'calculation_function': lambda a, b: a**2 - b**2,
        'question_template': "Se a={a} e b={b}, qual o valor de (a+b)(a-b)?",
        'reminder_template': "(x+y)(x-y) = x^2 - y^2",
        'range_constraints': {'b': {'less_than_equal_a': True}},
        'variable_labels': {'a': "Valor de 'a'", 'b': "Valor de 'b' (b <= a)"}
    },
]
