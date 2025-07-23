import unittest
from unittest.mock import Mock, patch
import sys

# Mock para pywebview
sys.modules['webview'] = Mock()

from pywebview_main import main

class TestGUI(unittest.TestCase):
    @patch('webview.create_window')
    def test_initial_screen_loads(self, mock_create_window):
        # Mock para a API
        mock_api = Mock()
        mock_create_window.return_value = None

        # Executa a função principal
        main()

        # Verifica se a janela foi criada com o arquivo HTML correto
        mock_create_window.assert_called_with('Quiz Mestre da Tabuada', 'index.html', width=480, height=800, js_api=unittest.mock.ANY)

if __name__ == '__main__':
    unittest.main()
