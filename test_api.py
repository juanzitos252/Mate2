import unittest
from api import Api

class TestApi(unittest.TestCase):

    def setUp(self):
        self.api = Api()

    def test_selecionar_proxima_pergunta(self):
        # Test that a question is returned
        question = self.api.selecionar_proxima_pergunta()
        self.assertIsNotNone(question)
        self.assertIn('fator1', question)
        self.assertIn('fator2', question)

    def test_registrar_resposta(self):
        # Test that the weight of a question is updated correctly
        question = self.api.selecionar_proxima_pergunta()
        initial_weight = question['peso']
        self.api.registrar_resposta(question, True, 1.0)
        self.assertLess(question['peso'], initial_weight)

    def test_registrar_resposta_atualiza_pesos_tabuada(self):
        # Test that the weights of the times tables are updated correctly
        question = self.api.selecionar_proxima_pergunta()
        fator1 = str(question['fator1'])
        fator2 = str(question['fator2'])
        initial_weight_fator1 = self.api.pesos_tabuadas[fator1]
        initial_weight_fator2 = self.api.pesos_tabuadas[fator2]
        self.api.registrar_resposta(question, True, 1.0)
        self.assertLess(self.api.pesos_tabuadas[fator1], initial_weight_fator1)
        self.assertLess(self.api.pesos_tabuadas[fator2], initial_weight_fator2)

    def test_gerar_opcoes(self):
        # Test that 4 options are returned, including the correct answer
        options = self.api.gerar_opcoes(2, 3)
        self.assertEqual(len(options), 4)
        self.assertIn(6, options)

    def test_sugerir_tabuada_para_treino(self):
        # Test that a valid table is suggested
        table = self.api.sugerir_tabuada_para_treino()
        self.assertGreaterEqual(table, 1)
        self.assertLessEqual(table, 10)

    def test_calcular_estatisticas_gerais(self):
        # Test that the statistics are calculated correctly
        stats = self.api.calcular_estatisticas_gerais()
        self.assertIn('total_respondidas', stats)
        self.assertIn('percentual_acertos_geral', stats)
        self.assertIn('top_3_dificeis', stats)

    def test_calcular_proficiencia_tabuadas(self):
        # Test that the proficiency is calculated correctly
        proficiency = self.api.calcular_proficiencia_tabuadas()
        self.assertEqual(len(proficiency), 10)
        for i in range(1, 11):
            self.assertIn(i, proficiency)

    def test_gerar_dados_heatmap(self):
        # Test that the heatmap data is generated correctly
        heatmap, min_peso, max_peso = self.api.gerar_dados_heatmap()
        self.assertEqual(len(heatmap), 10)
        for row in heatmap:
            self.assertEqual(len(row), 10)

if __name__ == '__main__':
    unittest.main()
