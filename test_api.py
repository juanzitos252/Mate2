import unittest
import api

class TestApi(unittest.TestCase):

    def test_selecionar_proxima_pergunta(self):
        # Test that a question is returned
        question = api.selecionar_proxima_pergunta()
        self.assertIsNotNone(question)
        self.assertIn('fator1', question)
        self.assertIn('fator2', question)

    def test_registrar_resposta(self):
        # Test that the weight of a question is updated correctly
        question = api.selecionar_proxima_pergunta()
        initial_weight = question['peso']
        api.registrar_resposta(question, True)
        self.assertLess(question['peso'], initial_weight)

    def test_gerar_opcoes(self):
        # Test that 4 options are returned, including the correct answer
        options = api.gerar_opcoes(2, 3)
        self.assertEqual(len(options), 4)
        self.assertIn(6, options)

    def test_sugerir_tabuada_para_treino(self):
        # Test that a valid table is suggested
        table = api.sugerir_tabuada_para_treino()
        self.assertGreaterEqual(table, 1)
        self.assertLessEqual(table, 10)

    def test_calcular_estatisticas_gerais(self):
        # Test that the statistics are calculated correctly
        stats = api.calcular_estatisticas_gerais()
        self.assertIn('total_respondidas', stats)
        self.assertIn('percentual_acertos_geral', stats)
        self.assertIn('top_3_dificeis', stats)

    def test_calcular_proficiencia_tabuadas(self):
        # Test that the proficiency is calculated correctly
        proficiency = api.calcular_proficiencia_tabuadas()
        self.assertEqual(len(proficiency), 10)
        for i in range(1, 11):
            self.assertIn(i, proficiency)

    def test_gerar_dados_heatmap(self):
        # Test that the heatmap data is generated correctly
        heatmap, min_peso, max_peso = api.gerar_dados_heatmap()
        self.assertEqual(len(heatmap), 10)
        for row in heatmap:
            self.assertEqual(len(row), 10)

if __name__ == '__main__':
    unittest.main()
