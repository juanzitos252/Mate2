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
        self.pesos_tabuadas = {str(i): 1.0 for i in range(1, 11)}
        self.tema_ativo = "colorido"
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

    def registrar_resposta(self, pergunta_selecionada, acertou: bool, tempo_resposta: float = None, modo_jogo: str = 'quiz'):
        """Registra a resposta do usuário, atualiza os dados e salva a configuração."""
        if not pergunta_selecionada:
            return

        pergunta_ref = next((p for p in self.multiplicacoes_data
                             if p['fator1'] == pergunta_selecionada['fator1'] and
                                p['fator2'] == pergunta_selecionada['fator2']), None)

        if pergunta_ref:
            self._atualizar_dados_resposta(pergunta_ref, acertou, tempo_resposta, modo_jogo)
            self._atualizar_pesos_tabuadas(pergunta_ref['fator1'], pergunta_ref['fator2'], acertou)
            self.salvar_dados()

    def _atualizar_dados_resposta(self, pergunta, acertou, tempo_resposta, modo_jogo):
        """Atualiza os dados de uma pergunta com base na resposta."""
        pergunta['vezes_apresentada'] = pergunta.get('vezes_apresentada', 0) + 1
        pergunta['ultima_vez_apresentada_ts'] = time.time()

        historico = pergunta.get('historico_erros', [])
        historico.append(acertou)
        pergunta['historico_erros'] = historico[-5:]

        if acertou:
            pergunta['vezes_correta'] = pergunta.get('vezes_correta', 0) + 1
            fator_reducao = 0.7 if modo_jogo == 'quiz' else 0.4 # Recompensa maior na memorização
            if tempo_resposta is not None and modo_jogo == 'quiz':
                if tempo_resposta < 2:
                    fator_reducao = 0.5
                elif tempo_resposta < 5:
                    fator_reducao = 0.7
                else:
                    fator_reducao = 0.9
            pergunta['peso'] = max(1.0, pergunta.get('peso', 10.0) * fator_reducao)
            pergunta['erros_consecutivos'] = 0
        else:
            fator_aumento = 1.6 if modo_jogo == 'quiz' else 1.8 # Penalidade maior na memorização
            pergunta['peso'] = min(100.0, pergunta.get('peso', 10.0) * fator_aumento)
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

    def sugerir_tabuada_para_memorizacao(self):
        """Sugere uma tabuada para o modo de memorização com base nos pesos."""
        if not self.multiplicacoes_data:
            return random.randint(1, 10)

        media_pesos = self._calcular_media_pesos_tabuadas()
        if not any(v > 0 for v in media_pesos.values()):
            return random.randint(1, 10)

        # Adiciona um pouco de aleatoriedade para não ficar sempre na mesma tabuada
        tabuadas_ordenadas = sorted(media_pesos.items(), key=lambda item: item[1], reverse=True)

        # Pega as 3 com maior peso
        top_3_tabuadas = [tab for tab, peso in tabuadas_ordenadas[:3]]

        return random.choice(top_3_tabuadas)

    def _calcular_media_pesos_tabuadas(self):
        """Calcula a média de pesos para cada tabuada."""
        pesos_por_tabuada = {i: [] for i in range(1, 11)}
        # Usar um conjunto para rastrear as multiplicações já consideradas para uma tabuada
        # para evitar a contagem dupla (ex: 3x5 e 5x3).
        # A chave será uma tupla ordenada dos fatores.
        multiplicacoes_contabilizadas = {i: set() for i in range(1, 11)}

        for item in self.multiplicacoes_data:
            f1, f2, peso = item['fator1'], item['fator2'], item.get('peso', 10.0)

            fatores_ordenados = tuple(sorted((f1, f2)))

            if fatores_ordenados not in multiplicacoes_contabilizadas[f1]:
                pesos_por_tabuada[f1].append(peso)
                multiplicacoes_contabilizadas[f1].add(fatores_ordenados)

            if f1 != f2 and fatores_ordenados not in multiplicacoes_contabilizadas[f2]:
                pesos_por_tabuada[f2].append(peso)
                multiplicacoes_contabilizadas[f2].add(fatores_ordenados)


        return {
            tab: sum(pesos) / len(pesos) if pesos else 0
            for tab, pesos in pesos_por_tabuada.items()
        }

    def get_estatisticas_gerais(self):
        """Retorna um resumo das estatísticas gerais."""
        if not self.multiplicacoes_data or all(p.get('vezes_apresentada', 0) == 0 for p in self.multiplicacoes_data):
            return {
                'total_respondidas': 0, 'percentual_acertos_geral': 0,
                'tempo_medio_resposta_geral': 0, 'progresso_geral': 0
            }

        total_respondidas = sum(p.get('vezes_apresentada', 0) for p in self.multiplicacoes_data)
        total_acertos = sum(p.get('vezes_correta', 0) for p in self.multiplicacoes_data)
        percentual_acertos = (total_acertos / total_respondidas * 100) if total_respondidas > 0 else 0

        tempos_respostas = [t for p in self.multiplicacoes_data for t in p.get('tempos_resposta', [])]
        tempo_medio_geral = sum(tempos_respostas) / len(tempos_respostas) if tempos_respostas else 0

        # O progresso geral pode ser a média da proficiência em todas as tabuadas
        proficiencia_por_tabuada = self.get_proficiencia_por_tabuada()
        progresso_geral = sum(proficiencia_por_tabuada.values()) / len(proficiencia_por_tabuada) if proficiencia_por_tabuada else 0

        return {
            'total_respondidas': total_respondidas,
            'percentual_acertos_geral': round(percentual_acertos, 1),
            'tempo_medio_resposta_geral': round(tempo_medio_geral, 2),
            'progresso_geral': round(progresso_geral, 1)
        }

    def get_estatisticas_detalhadas(self):
        """Retorna estatísticas mais detalhadas para a página de estatísticas."""
        if not self.multiplicacoes_data:
            return self._estatisticas_detalhadas_padrao()

        top_3_dificeis = self._get_top_questoes('peso', reverse=True, count=3)
        top_3_faceis = self._get_top_questoes('peso', reverse=False, count=3)
        top_3_lentas = self._get_top_questoes_por_tempo_medio(count=3)
        top_3_rapidas = self._get_top_questoes_por_tempo_medio(count=3, reverse=False)

        return {
            'top_3_dificeis': top_3_dificeis,
            'top_3_faceis': top_3_faceis,
            'top_3_lentas': top_3_lentas,
            'top_3_rapidas': top_3_rapidas,
        }

    def _estatisticas_detalhadas_padrao(self):
        return {
            'top_3_dificeis': [], 'top_3_faceis': [],
            'top_3_lentas': [], 'top_3_rapidas': []
        }

    def _get_top_questoes(self, sort_key, reverse, count):
        """Helper para buscar questões com base em uma chave de ordenação."""
        questoes_apresentadas = [p for p in self.multiplicacoes_data if p.get('vezes_apresentada', 0) > 0]
        questoes_apresentadas.sort(key=lambda x: x.get(sort_key, 0), reverse=reverse)
        return [f"{item['fator1']} x {item['fator2']}" for item in questoes_apresentadas[:count]]

    def _get_top_questoes_por_tempo_medio(self, count, reverse=True):
        """Retorna as questões mais lentas ou rápidas com base no tempo médio de resposta."""
        questoes_com_tempo = [
            {
                'texto': f"{p['fator1']} x {p['fator2']}",
                'tempo_medio': sum(p['tempos_resposta']) / len(p['tempos_resposta'])
            }
            for p in self.multiplicacoes_data if p.get('tempos_resposta')
        ]
        if not questoes_com_tempo:
            return []

        questoes_com_tempo.sort(key=lambda x: x['tempo_medio'], reverse=reverse)
        return [f"{q['texto']} ({q['tempo_medio']:.2f}s)" for q in questoes_com_tempo[:count]]

    def get_proficiencia_por_tabuada(self):
        """Calcula a proficiência do usuário para cada tabuada."""
        proficiencia = {i: 0.0 for i in range(1, 11)}
        media_pesos = self._calcular_media_pesos_tabuadas()

        for tab, media in media_pesos.items():
            if media > 0:
                proficiencia_percentual = max(0, 100 - (media - 1) * (100 / 99))
                proficiencia[tab] = round(proficiencia_percentual, 1)
        return proficiencia

    def get_estatisticas_por_tabuada(self):
        """Calcula e retorna estatísticas detalhadas para cada tabuada."""
        stats_por_tabuada = {i: self._inicializar_stats_tabuada() for i in range(1, 11)}

        for item in self.multiplicacoes_data:
            f1, f2 = item['fator1'], item['fator2']
            self._acumular_stats_para_tabuada(stats_por_tabuada[f1], item)
            if f1 != f2:
                self._acumular_stats_para_tabuada(stats_por_tabuada[f2], item)

        # Calcular médias e percentuais
        for i in range(1, 11):
            stats = stats_por_tabuada[i]
            if stats['total_respostas'] > 0:
                stats['percentual_acertos'] = round((stats['total_acertos'] / stats['total_respostas']) * 100, 1)
            if stats['tempos']:
                stats['tempo_medio'] = round(sum(stats['tempos']) / len(stats['tempos']), 2)
            del stats['tempos'] # Remover a lista de tempos antes de retornar

        return stats_por_tabuada

    def _inicializar_stats_tabuada(self):
        return {'total_respostas': 0, 'total_acertos': 0, 'tempo_medio': 0, 'tempos': []}

    def _acumular_stats_para_tabuada(self, stats_tabuada, item):
        stats_tabuada['total_respostas'] += item.get('vezes_apresentada', 0)
        stats_tabuada['total_acertos'] += item.get('vezes_correta', 0)
        if item.get('tempos_resposta'):
            stats_tabuada['tempos'].extend(item['tempos_resposta'])

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
        self.pesos_tabuadas = user_data.get("table_weights", {str(i): 1.0 for i in range(1, 11)})

        if not self.multiplicacoes_data:
            self.inicializar_multiplicacoes()
            self.salvar_dados()

    def salvar_dados(self):
        """Salva todos os dados atuais na configuração."""
        user_data = {
            "multiplications_data": self.multiplicacoes_data,
            "table_weights": self.pesos_tabuadas,
        }
        self.config_manager.save_user_data(user_data)
