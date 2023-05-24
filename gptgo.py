from json import loads
from textwrap import dedent

from httpx import Client
from rich.console import Console
from rich.markdown import Markdown


class Colors:
    GREEN = '\033[38;5;121m'
    END = '\033[0m'


class GptGo:
    OPTIONS = """
        GPTGo - A command-line tool for interacting with GPTGo chatbot. (https://gptgo.ai)
            DOUBLE "enter" to send a message.
            - Type "!exit" to exit the program.
            - Type "!clear" to clear the console.
    """

    def __init__(self):
        self.base_url = 'https://gptgo.ai'
        self.console = Console()
        self.client = Client(timeout=180)
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
        })

    def __del__(self):
        self.client.close()

    def get_query(
        self, prompt: str
        ):

        print(prompt, end='')
        return '\n'.join(iter(input, ''))

    def get_token(
        self, query: str
        ):

        response = self.client.get(
            f'{self.base_url}/action_get_token.php',
            params={'q': query, 'hlgpt': 'default'}
        )
        content = response.json()
        token = content.get('token')
        if not token:
            raise ValueError("Can't get a token!")
        return token

    def process_data(
        self, response: bytes
        ):

        full_response = [
            loads(line[6:])['choices'][0]['delta'].get('content', '')
            for line in response.decode('utf-8').splitlines()
            if line.startswith('data: ') and line[6:] != '[DONE]'
        ]
        full_response = ''.join(full_response)
        return (
            full_response[:-6]
            if full_response.endswith('[DONE]')
            else 'An error occurred while processing the response!'
        )

    def run(self):
        self.console.clear()
        print(dedent(self.OPTIONS))
        while True:
            query = self.get_query(f'{Colors.GREEN}You{Colors.END} : ').lower()
            if query == '!exit':
                break
            elif query == '!clear':
                self.console.clear()
                print(dedent(self.OPTIONS))
            else:
                token = self.get_token(query)
                response = self.client.get(
                    f'{self.base_url}/action_ai_gpt.php',
                    params={'token': str(token)}
                )
                result = self.process_data(response.content)
                self.console.print(Markdown(result, code_theme='fruity'))
                print()


if __name__ =='__main__':
    GptGo().run()
