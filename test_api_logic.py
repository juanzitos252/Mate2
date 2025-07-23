import unittest
from api import Api

class TestApiLogic(unittest.TestCase):

    def setUp(self):
        self.api = Api()
        self.api.inicializar_multiplicacoes()

    def test_sugerir_tabuada_para_memorizacao(self):
        # No início, qualquer tabuada pode ser sugerida
        sugerida = self.api.sugerir_tabuada_para_memorizacao()
        self.assertIn(sugerida, range(1, 11))

        # Vamos dificultar a tabuada do 7
        for i in range(1, 11):
            pergunta = {'fator1': 7, 'fator2': i}
            self.api.registrar_resposta(pergunta, False, modo_jogo='quiz')

        # Agora, a tabuada do 7 deve ser uma das mais prováveis
        sugestoes = [self.api.sugerir_tabuada_para_memorizacao() for _ in range(20)]
        self.assertIn(7, sugestoes)

    def test_retroalimentacao_quiz_memorizacao(self):
        # Errar uma questão no quiz deve aumentar o peso
        pergunta = {'fator1': 5, 'fator2': 5}
        peso_antes = self.api.multiplicacoes_data[4 * 10 + 4]['peso']
        self.api.registrar_resposta(pergunta, False, modo_jogo='quiz')
        peso_depois_quiz = self.api.multiplicacoes_data[4 * 10 + 4]['peso']
        self.assertGreater(peso_depois_quiz, peso_antes)

        # Errar a mesma questão na memorização deve aumentar ainda mais o peso
        self.api.registrar_resposta(pergunta, False, modo_jogo='memorizacao')
        peso_depois_memo = self.api.multiplicacoes_data[4 * 10 + 4]['peso']
        self.assertGreater(peso_depois_memo, peso_depois_quiz)

    def test_acerto_total_memorizacao(self):
        # Simula o acerto de todas as questões da tabuada do 3, duas vezes
        for _ in range(2):
            for i in range(1, 11):
                pergunta = {'fator1': 3, 'fator2': i}
                self.api.registrar_resposta(pergunta, True, modo_jogo='memorizacao')

        # O peso da tabuada do 3 deve ser baixo
        media_pesos = self.api._calcular_media_pesos_tabuadas()
        self.assertLess(media_pesos[3], 3.3)

if __name__ == '__main__':
    unittest.main()
