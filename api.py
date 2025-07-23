import random
import time
from config import ConfigManager

class Api:
    """
    API principal para o Quiz Mestre da Tabuada.
    Gerencia a lógica do quiz, dados do usuário e estatísticas.
    """
    def __init__(self):
        """Inicializa a API, carregando os dados ou criando novos."""
        self.config_manager = ConfigManager()
        self.multiplicacoes_data = []
        self.custom_formulas_data = []
        self.pesos_tabuadas = {str(i): 1.0 for i in range(1, 11)}
        self.pontuacao_maxima_cronometrado = 0
        self.tema_ativo = "colorido"
        self.current_custom_formula_for_quiz = None
        self.load_initial_data()

    def inicializar_multiplicacoes(self):
        """Cria o conjunto de dados inicial de multiplicações."""
        self.multiplicacoes_data = [
            {
                'fator1': i,
                'fator2': j,
                'peso': 10.0,
                'historico_erros': [],
                'vezes_apresentada': 0,
                'vezes_correta': 0,
                'ultima_vez_apresentada_ts': 0.0,
                'tempos_resposta': [],
                'erros_consecutivos': 0
            }
            for i in range(1, 11) for j in range(1, 11)
        ]

    def _calcular_prioridade_pergunta(self, pergunta, agora_ts):
        """Calcula a prioridade de uma única pergunta."""
        fator_peso = pergunta.get('peso', 10.0)

        erros = pergunta.get('historico_erros', [])
        fator_erro_recente = 1.0
        if erros:
            erros_recentes = sum(1 for erro in erros if not erro)
            fator_erro_recente = 1 + (erros_recentes / len(erros))

        fator_novidade = 1 / (1 + pergunta.get('vezes_apresentada', 0) * 0.05)

        prioridade_base = fator_peso * fator_erro_recente * fator_novidade

        fator1 = str(pergunta['fator1'])
        fator2 = str(pergunta['fator2'])
        fator_ajuste_tabuada = (self.pesos_tabuadas.get(fator1, 1.0) + self.pesos_tabuadas.get(fator2, 1.0)) / 2

        return prioridade_base * fator_ajuste_tabuada

    def selecionar_proxima_pergunta(self):
        """Seleciona a próxima pergunta a ser feita com base em um algoritmo de prioridade."""
        agora_ts = time.time()
        perguntas_potenciais = [p for p in self.multiplicacoes_data if (agora_ts - p.get('ultima_vez_apresentada_ts', 0.0)) > 30]
        if not perguntas_potenciais:
            perguntas_potenciais = self.multiplicacoes_data

        if not perguntas_potenciais:
            return None

        prioridades = [self._calcular_prioridade_pergunta(p, agora_ts) for p in perguntas_potenciais]

        if not prioridades:
            return random.choice(self.multiplicacoes_data) if self.multiplicacoes_data else None

        return random.choices(perguntas_potenciais, weights=prioridades, k=1)[0]

    def _atualizar_dados_resposta(self, pergunta, acertou, tempo_resposta):
        """Atualiza os dados de uma pergunta com base na resposta."""
        pergunta['vezes_apresentada'] = pergunta.get('vezes_apresentada', 0) + 1
        pergunta['ultima_vez_apresentada_ts'] = time.time()

        historico = pergunta.get('historico_erros', [])
        historico.append(acertou)
        pergunta['historico_erros'] = historico[-5:]

        if acertou:
            pergunta['vezes_correta'] = pergunta.get('vezes_correta', 0) + 1
            fator_reducao = 0.7
            if tempo_resposta is not None:
                if tempo_resposta < 2:
                    fator_reducao = 0.5
                elif tempo_resposta < 5:
                    fator_reducao = 0.7
                else:
                    fator_reducao = 0.9
            pergunta['peso'] = max(1.0, pergunta.get('peso', 10.0) * fator_reducao)
            pergunta['erros_consecutivos'] = 0
        else:
            pergunta['peso'] = min(100.0, pergunta.get('peso', 10.0) * 1.6)
            pergunta['erros_consecutivos'] = pergunta.get('erros_consecutivos', 0) + 1

        if tempo_resposta is not None:
            tempos = pergunta.get('tempos_resposta', [])
            tempos.append(tempo_resposta)
            pergunta['tempos_resposta'] = tempos[-10:]

    def _atualizar_pesos_tabuadas(self, fator1, fator2, acertou):
        """Atualiza os pesos das tabuadas com base na resposta."""
        f1_str = str(fator1)
        f2_str = str(fator2)
        if acertou:
            self.pesos_tabuadas[f1_str] = max(0.1, self.pesos_tabuadas.get(f1_str, 1.0) * 0.95)
            self.pesos_tabuadas[f2_str] = max(0.1, self.pesos_tabuadas.get(f2_str, 1.0) * 0.95)
        else:
            self.pesos_tabuadas[f1_str] = min(100.0, self.pesos_tabuadas.get(f1_str, 1.0) * 1.1)
            self.pesos_tabuadas[f2_str] = min(100.0, self.pesos_tabuadas.get(f2_str, 1.0) * 1.1)

    def registrar_resposta(self, pergunta_selecionada, acertou: bool, tempo_resposta: float = None):
        """Registra a resposta do usuário, atualiza os dados e salva a configuração."""
        if not pergunta_selecionada:
            return

        # Encontra a referência da pergunta nos dados da API para garantir a modificação
        pergunta_ref = next((p for p in self.multiplicacoes_data
                             if p['fator1'] == pergunta_selecionada['fator1'] and
                                p['fator2'] == pergunta_selecionada['fator2']), None)

        if pergunta_ref:
            self._atualizar_dados_resposta(pergunta_ref, acertou, tempo_resposta)
            self._atualizar_pesos_tabuadas(pergunta_ref['fator1'], pergunta_ref['fator2'], acertou)
            self.salvar_dados()

    def gerar_opcoes(self, fator1: int, fator2: int):
        """Gera 4 opções de resposta para uma pergunta, incluindo a correta."""
        resposta_correta = fator1 * fator2
        opcoes = {resposta_correta}

        # Tenta adicionar opções com base em variações
        self._adicionar_opcoes_variadas(opcoes, fator1, fator2, resposta_correta)

        # Preenche com opções aleatórias se necessário
        self._preencher_opcoes_restantes(opcoes, resposta_correta)

        lista_opcoes = list(opcoes)
        random.shuffle(lista_opcoes)
        return lista_opcoes

    def _adicionar_opcoes_variadas(self, opcoes, fator1, fator2, resposta_correta):
        """Adiciona opções de resposta variadas (adjacentes, próximas, etc.)."""
        tentativas = 0
        while len(opcoes) < 4 and tentativas < 30:
            tipo_variacao = random.choice(['fator_adjacente', 'resultado_proximo', 'aleatorio_da_lista'])
            nova_opcao = -1
            if tipo_variacao == 'fator_adjacente':
                if random.choice([True, False]):
                    f1_mod = max(1, fator1 + random.choice([-2, -1, 1, 2]))
                    nova_opcao = f1_mod * fator2
                else:
                    f2_mod = max(1, fator2 + random.choice([-2, -1, 1, 2]))
                    nova_opcao = fator1 * f2_mod
            elif tipo_variacao == 'resultado_proximo':
                offset = random.choice([-3, -2, -1, 1, 2, 3])
                nova_opcao = resposta_correta + offset
            elif tipo_variacao == 'aleatorio_da_lista' and self.multiplicacoes_data:
                pergunta_aleatoria = random.choice(self.multiplicacoes_data)
                nova_opcao = pergunta_aleatoria['fator1'] * pergunta_aleatoria['fator2']

            if nova_opcao > 0 and nova_opcao != resposta_correta:
                opcoes.add(nova_opcao)
            tentativas += 1

    def _preencher_opcoes_restantes(self, opcoes, resposta_correta):
        """Preenche as opções de resposta restantes para garantir que haja 4."""
        idx = 1
        while len(opcoes) < 4:
            if resposta_correta + idx not in opcoes:
                opcoes.add(resposta_correta + idx)
            if len(opcoes) < 4 and resposta_correta - idx > 0 and resposta_correta - idx not in opcoes:
                opcoes.add(resposta_correta - idx)
            idx += 1
            if idx > 50:  # Evita loop infinito
                break

        # Fallback final para garantir 4 opções
        while len(opcoes) < 4:
            rand_num = random.randint(1, max(100, resposta_correta + 20))
            if rand_num > 0 and rand_num not in opcoes:
                opcoes.add(rand_num)

    def gerar_opcoes_quiz_invertido(self, multiplicacao_base):
        """Gera opções para o modo de quiz invertido."""
        resposta_correta_valor = multiplicacao_base['fator1'] * multiplicacao_base['fator2']
        opcao_correta = {'texto': f"{multiplicacao_base['fator1']} x {multiplicacao_base['fator2']}", 'is_correct': True}

        opcoes = [opcao_correta]
        candidatos = [item for item in self.multiplicacoes_data
                      if item['fator1'] * item['fator2'] != resposta_correta_valor and
                         (item['fator1'] != multiplicacao_base['fator1'] or item['fator2'] != multiplicacao_base['fator2'])]

        random.shuffle(candidatos)

        for candidato in candidatos:
            if len(opcoes) >= 4:
                break
            opcoes.append({'texto': f"{candidato['fator1']} x {candidato['fator2']}", 'is_correct': False})

        # Fallback se não houver candidatos suficientes
        tentativas_fallback = 0
        while len(opcoes) < 4 and tentativas_fallback < 50:
            f1, f2 = random.randint(1, 10), random.randint(1, 10)
            if f1 * f2 != resposta_correta_valor and not any(op['texto'] == f"{f1} x {f2}" for op in opcoes):
                opcoes.append({'texto': f"{f1} x {f2}", 'is_correct': False})
            tentativas_fallback += 1

        random.shuffle(opcoes)
        return opcoes[:4]

    def sugerir_tabuada_para_treino(self):
        """Sugere uma tabuada para o modo de treino com base nos pesos."""
        if not self.multiplicacoes_data:
            return random.randint(1, 10)

        media_pesos = self._calcular_media_pesos_tabuadas()
        if not any(v > 0 for v in media_pesos.values()):
            return random.randint(1, 10)

        peso_maximo = max(media_pesos.values())
        tabuadas_sugeridas = [tab for tab, peso in media_pesos.items() if peso == peso_maximo]

        return random.choice(tabuadas_sugeridas)

    def _calcular_media_pesos_tabuadas(self):
        """Calcula a média de pesos para cada tabuada."""
        pesos_por_tabuada = {i: [] for i in range(1, 11)}
        for item in self.multiplicacoes_data:
            f1, f2, peso = item['fator1'], item['fator2'], item.get('peso', 10.0)
            pesos_por_tabuada[f1].append(peso)
            if f1 != f2:
                pesos_por_tabuada[f2].append(peso)

        return {
            tab: sum(pesos) / len(pesos) if pesos else 0
            for tab, pesos in pesos_por_tabuada.items()
        }

    def sugerir_tabuada_para_memorizacao(self):
        """Sugere uma tabuada para o modo de memorização."""
        # A lógica pode ser a mesma do treino ou diferente no futuro.
        return self.sugerir_tabuada_para_treino()

    def calcular_estatisticas_gerais(self):
        """Calcula e retorna as estatísticas gerais de desempenho."""
        if not self.multiplicacoes_data or all(p.get('vezes_apresentada', 0) == 0 for p in self.multiplicacoes_data):
            return self._estatisticas_padrao()

        total_respondidas = sum(item.get('vezes_apresentada', 0) for item in self.multiplicacoes_data)
        total_acertos = sum(item.get('vezes_correta', 0) for item in self.multiplicacoes_data)
        percentual_acertos = (total_acertos / total_respondidas * 100) if total_respondidas > 0 else 0

        top_3_dificeis = self._get_top_3_dificeis()
        tempo_medio_geral, questao_mais_lenta = self._get_metricas_tempo()
        questao_mais_errada = self._get_questao_mais_errada()

        return {
            'total_respondidas': total_respondidas,
            'percentual_acertos_geral': round(percentual_acertos, 1),
            'top_3_dificeis': top_3_dificeis,
            'tempo_medio_resposta_geral': round(tempo_medio_geral, 2),
            'questao_mais_lenta': questao_mais_lenta,
            'questao_mais_errada_consecutivamente': questao_mais_errada
        }

    def _estatisticas_padrao(self):
        """Retorna um dicionário de estatísticas padrão."""
        return {
            'total_respondidas': 0, 'percentual_acertos_geral': 0, 'top_3_dificeis': [],
            'tempo_medio_resposta_geral': 0, 'questao_mais_lenta': 'N/A',
            'questao_mais_errada_consecutivamente': 'N/A'
        }

    def _get_top_3_dificeis(self):
        """Retorna as 3 questões mais difíceis."""
        questoes_apresentadas = [p for p in self.multiplicacoes_data if p.get('vezes_apresentada', 0) > 0]
        questoes_apresentadas.sort(key=lambda x: x.get('peso', 10.0), reverse=True)
        return [f"{item['fator1']} x {item['fator2']}" for item in questoes_apresentadas[:3]]

    def _get_metricas_tempo(self):
        """Calcula o tempo médio de resposta e a questão mais lenta."""
        tempos_respostas = [t for item in self.multiplicacoes_data for t in item.get('tempos_resposta', [])]
        if not tempos_respostas:
            return 0, "N/A"

        tempo_medio_geral = sum(tempos_respostas) / len(tempos_respostas)

        questoes_com_tempo = [
            {'item': item, 'tempo_medio': sum(item['tempos_resposta']) / len(item['tempos_resposta'])}
            for item in self.multiplicacoes_data if item.get('tempos_resposta')
        ]

        if not questoes_com_tempo:
            return tempo_medio_geral, "N/A"

        mais_lenta = max(questoes_com_tempo, key=lambda x: x['tempo_medio'])
        return tempo_medio_geral, f"{mais_lenta['item']['fator1']} x {mais_lenta['item']['fator2']}"

    def _get_questao_mais_errada(self):
        """Retorna a questão com mais erros consecutivos."""
        questoes_com_erros = [p for p in self.multiplicacoes_data if p.get('erros_consecutivos', 0) > 0]
        if not questoes_com_erros:
            return "N/A"

        mais_errada = max(questoes_com_erros, key=lambda x: x['erros_consecutivos'])
        return f"{mais_errada['fator1']} x {mais_errada['fator2']} ({mais_errada['erros_consecutivos']} erros)"

    def calcular_proficiencia_tabuadas(self):
        """Calcula a proficiência do usuário para cada tabuada."""
        proficiencia = {i: 0.0 for i in range(1, 11)}
        if not self.multiplicacoes_data:
            return proficiencia

        media_pesos = self._calcular_media_pesos_tabuadas()

        for tab, media in media_pesos.items():
            if media > 0:
                # Normaliza o peso (que vai de 1 a 100) para uma proficiência de 0 a 100
                proficiencia_percentual = max(0, 100 - (media - 1))
                proficiencia[tab] = round(proficiencia_percentual, 1)

        return proficiencia

    def gerar_dados_heatmap(self):
        """Gera os dados para o heatmap de dificuldade."""
        if not self.multiplicacoes_data:
            return [[0] * 10 for _ in range(10)], 1.0, 10.0

        heatmap_data = [[10.0] * 10 for _ in range(10)]
        pesos = [item.get('peso', 10.0) for item in self.multiplicacoes_data]
        min_peso, max_peso = min(pesos) if pesos else 1.0, max(pesos) if pesos else 10.0

        data_dict = {(item['fator1'], item['fator2']): item.get('peso', 10.0) for item in self.multiplicacoes_data}

        for i in range(1, 11):
            for j in range(1, 11):
                heatmap_data[i-1][j-1] = data_dict.get((i, j), data_dict.get((j, i), 10.0))

        return heatmap_data, min_peso, max_peso

    def get_formula_definitions(self):
        """Retorna as definições das fórmulas notáveis."""
        return FORMULAS_NOTAVEIS

    def get_saved_quiz_configs(self):
        """Retorna as configurações de quiz salvas."""
        return self.custom_formulas_data

    def save_quiz_config(self, config):
        """Salva uma nova configuração de quiz."""
        if any(c['name'] == config['name'] for c in self.custom_formulas_data):
            # Atualiza a configuração existente
            self.custom_formulas_data = [c for c in self.custom_formulas_data if c['name'] != config['name']]
        self.custom_formulas_data.append(config)
        self.salvar_dados()

    def set_current_custom_formula_for_quiz(self, config_name):
        """Define a fórmula customizada para o próximo quiz."""
        self.current_custom_formula_for_quiz = next(
            (cfg for cfg in self.custom_formulas_data if cfg['name'] == config_name), None
        )

    def save_timed_mode_score(self, score):
        """Salva a pontuação do modo cronometrado se for um novo recorde."""
        if score > self.pontuacao_maxima_cronometrado:
            self.pontuacao_maxima_cronometrado = score
            self.salvar_dados()

    def salvar_tema(self, tema):
        """Salva a preferência de tema do usuário."""
        self.tema_ativo = tema
        settings = self.config_manager.load_settings()
        settings["theme"] = tema
        self.config_manager.save_settings(settings)

    def load_initial_data(self):
        """Carrega os dados da configuração ou inicializa se não existirem."""
        settings = self.config_manager.load_settings()
        self.tema_ativo = settings.get("theme", "colorido")

        user_data = self.config_manager.load_user_data()
        self.multiplicacoes_data = user_data.get("multiplications_data", [])
        self.custom_formulas_data = user_data.get("custom_formulas_data", [])
        self.pesos_tabuadas = user_data.get("table_weights", {str(i): 1.0 for i in range(1, 11)})
        self.pontuacao_maxima_cronometrado = user_data.get("timed_mode_highscore", 0)

        if not self.multiplicacoes_data:
            self.inicializar_multiplicacoes()
            self.salvar_dados()

    def salvar_dados(self):
        """Salva todos os dados atuais na configuração."""
        user_data = {
            "multiplications_data": self.multiplicacoes_data,
            "custom_formulas_data": self.custom_formulas_data,
            "table_weights": self.pesos_tabuadas,
            "timed_mode_highscore": self.pontuacao_maxima_cronometrado,
        }
        self.config_manager.save_user_data(user_data)


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
