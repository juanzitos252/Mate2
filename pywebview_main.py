import webview
from api import Api

def main():
    api = Api()
    window = webview.create_window('Quiz Mestre da Tabuada', 'index.html', width=480, height=800, js_api=api)
    webview.start()

if __name__ == '__main__':
    main()
