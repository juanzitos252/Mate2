import unittest
from unittest.mock import patch, MagicMock
from api import Api

class TestApi(unittest.TestCase):

    @patch('api.carregar_configuracao')
    def setUp(self, mock_carregar_configuracao):
        # Mock para evitar a leitura/escrita de arquivos de configuração durante os testes
        mock_carregar_configuracao.return_value = {
            "tema_ativo": "colorido",
            "multiplicacoes_data": None,
            "custom_formulas_data": [],
            "pesos_tabuadas": {str(i): 1.0 for i in range(1, 11)},
            "pontuacao_maxima_cronometrado": 0
        }
        with patch('api.salvar_configuracao'):
            self.api = Api()

    def test_inicializacao_api(self):
        self.assertIsNotNone(self.api.multiplicacoes_data)
        self.assertEqual(len(self.api.multiplicacoes_data), 100)
        self.assertEqual(self.api.multiplicacoes_data[0]['fator1'], 1)
        self.assertEqual(self.api.multiplicacoes_data[0]['fator2'], 1)

    def test_selecionar_proxima_pergunta_retorna_pergunta(self):
        question = self.api.selecionar_proxima_pergunta()
        self.assertIn('fator1', question)
        self.assertIn('fator2', question)
        self.assertIn('peso', question)

    def test_registrar_resposta_correta_diminui_peso(self):
        question = self.api.multiplicacoes_data[0] # 1x1
        initial_weight = question['peso']
        with patch('api.salvar_configuracao'):
            self.api.registrar_resposta(question, True, 1.0)
        self.assertLess(self.api.multiplicacoes_data[0]['peso'], initial_weight)

    def test_registrar_resposta_incorreta_aumenta_peso(self):
        question = self.api.multiplicacoes_data[0] # 1x1
        initial_weight = question['peso']
        with patch('api.salvar_configuracao'):
            self.api.registrar_resposta(question, False, 5.0)
        self.assertGreater(self.api.multiplicacoes_data[0]['peso'], initial_weight)

    def test_registrar_resposta_atualiza_pesos_tabuada_corretamente(self):
        question = self.api.multiplicacoes_data[0] # 1x1
        fator1_str = str(question['fator1'])
        initial_weight_fator1 = self.api.pesos_tabuadas[fator1_str]

        with patch('api.salvar_configuracao'):
            self.api.registrar_resposta(question, True, 1.0)

        self.assertLess(self.api.pesos_tabuadas[fator1_str], initial_weight_fator1)

    def test_gerar_opcoes_contem_resposta_correta(self):
        options = self.api.gerar_opcoes(2, 3)
        self.assertEqual(len(options), 4)
        self.assertIn(6, options)
        self.assertTrue(all(isinstance(opt, int) for opt in options))

    def test_gerar_opcoes_sem_duplicatas(self):
        options = self.api.gerar_opcoes(5, 5)
        self.assertEqual(len(set(options)), 4)

    def test_sugerir_tabuada_para_treino_retorna_int_valido(self):
        table = self.api.sugerir_tabuada_para_treino()
        self.assertIsInstance(table, int)
        self.assertGreaterEqual(table, 1)
        self.assertLessEqual(table, 10)

    def test_calcular_estatisticas_gerais_com_dados(self):
        with patch('api.salvar_configuracao'):
            self.api.registrar_resposta(self.api.multiplicacoes_data[0], True, 2.0)
            self.api.registrar_resposta(self.api.multiplicacoes_data[1], False, 3.0)

        stats = self.api.calcular_estatisticas_gerais()
        self.assertEqual(stats['total_respondidas'], 2)
        self.assertEqual(stats['percentual_acertos_geral'], 50.0)
        self.assertIsNotNone(stats['top_3_dificeis'])

    def test_calcular_estatisticas_sem_dados(self):
        self.api.multiplicacoes_data = []
        stats = self.api.calcular_estatisticas_gerais()
        self.assertEqual(stats['total_respondidas'], 0)
        self.assertEqual(stats['percentual_acertos_geral'], 0)
        self.assertEqual(stats['top_3_dificeis'], [])

    def test_calcular_proficiencia_tabuadas(self):
        proficiency = self.api.calcular_proficiencia_tabuadas()
        self.assertEqual(len(proficiency), 10)
        self.assertTrue(all(isinstance(p, float) for p in proficiency.values()))

    def test_gerar_dados_heatmap(self):
        heatmap, min_peso, max_peso = self.api.gerar_dados_heatmap()
        self.assertEqual(len(heatmap), 10)
        self.assertEqual(len(heatmap[0]), 10)
        self.assertIsInstance(min_peso, float)
        self.assertIsInstance(max_peso, float)

    def test_save_quiz_config(self):
        config = {'name': 'Test Config', 'formula_id': 'quadrado_soma', 'ranges': {'a': '1-5', 'b': '1-5'}}
        with patch('api.salvar_configuracao') as mock_salvar:
            self.api.save_quiz_config(config)
            self.assertIn(config, self.api.custom_formulas_data)
            mock_salvar.assert_called_once()

            # Testa a atualização de uma config existente
            config_updated = {'name': 'Test Config', 'formula_id': 'quadrado_diferenca', 'ranges': {'a': '1-5', 'b': '1-5'}}
            self.api.save_quiz_config(config_updated)
            self.assertNotIn(config, self.api.custom_formulas_data)
            self.assertIn(config_updated, self.api.custom_formulas_data)


    def test_save_timed_mode_score(self):
        self.api.pontuacao_maxima_cronometrado = 10
        with patch('api.salvar_configuracao') as mock_salvar:
            # Pontuação menor não deve salvar
            self.api.save_timed_mode_score(5)
            mock_salvar.assert_not_called()

            # Pontuação maior deve salvar
            self.api.save_timed_mode_score(15)
            self.assertEqual(self.api.pontuacao_maxima_cronometrado, 15)
            mock_salvar.assert_called_once()

if __name__ == '__main__':
    unittest.main()
