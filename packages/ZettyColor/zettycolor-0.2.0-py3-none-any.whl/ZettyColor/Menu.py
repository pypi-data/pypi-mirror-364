import threading
import keyboard
import time
from os import system, name
from ZtColors import Text, Style, Bg


class Menu:
    """
    Menu interativo no terminal com suporte a layouts horizontal ou em grade (grid), com espaçamentos personalizados.
    """

    def __init__(self, itens, modo='horizontal', cor_normal=Text.BLACK, cor_selecionado=Text.CYAN + Style.BOLD, ao_selecionar=None,
                 espaco_horizontal=1, espaco_vertical=0):
        self.itens = itens
        self.modo = modo
        self.cor_normal = cor_normal
        self.cor_selecionado = cor_selecionado
        self.ao_selecionar = ao_selecionar
        self.espaco_horizontal = espaco_horizontal
        self.espaco_vertical = espaco_vertical

        self.pressed_key = None
        self.executando = True
        self._saida = None

        if self.modo == 'grid':
            self.linha = 0
            self.coluna = 0
        else:
            self.index = 0

    def limpar_tela(self):
        system('cls' if name == 'nt' else 'clear')

    def desenhar(self):
        self.limpar_tela()
        hspace = ' ' * self.espaco_horizontal
        vspace = '\n' * self.espaco_vertical

        if self.modo == 'horizontal':
            texto = ""
            for i, item in enumerate(self.itens):
                if i == self.index:
                    texto += f"{self.cor_selecionado}{item}{Style.RESET_ALL}"
                else:
                    texto += f"{self.cor_normal}{item}{Style.RESET_ALL}"

                if i < len(self.itens) - 1:
                    texto += hspace
            print(texto.strip())

        elif self.modo == 'grid':
            linhas = []
            for i, linha in enumerate(self.itens):
                linha_str = ""
                for j, item in enumerate(linha):
                    if i == self.linha and j == self.coluna:
                        linha_str += f"{self.cor_selecionado}{item}{Style.RESET_ALL}"
                    else:
                        linha_str += f"{self.cor_normal}{item}{Style.RESET_ALL}"

                    if j < len(linha) - 1:
                        linha_str += hspace
                linhas.append(linha_str.strip())
            print(vspace.join(linhas))

    def _escutar_teclas(self):
        while self.executando:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                self.pressed_key = event.name

    def executar(self):
        thread = threading.Thread(target=self._escutar_teclas, daemon=True)
        thread.start()

        self.desenhar()

        while self.executando:
            if self.pressed_key:
                tecla = self.pressed_key
                self.pressed_key = None

                if self.modo == 'horizontal':
                    if tecla == 'left':
                        self.index = (self.index - 1) % len(self.itens)
                    elif tecla == 'right':
                        self.index = (self.index + 1) % len(self.itens)
                    elif tecla == 'enter':
                        self._saida = self.itens[self.index]
                        if self.ao_selecionar:
                            self.ao_selecionar(self.index, self._saida)
                        self.executando = False
                    elif tecla == 'esc':
                        self._saida = None
                        self.executando = False

                elif self.modo == 'grid':
                    linhas = len(self.itens)
                    colunas = len(self.itens[0])
                    if tecla == 'up':
                        self.linha = (self.linha - 1) % linhas
                    elif tecla == 'down':
                        self.linha = (self.linha + 1) % linhas
                    elif tecla == 'left':
                        self.coluna = (self.coluna - 1) % colunas
                    elif tecla == 'right':
                        self.coluna = (self.coluna + 1) % colunas
                    elif tecla == 'enter':
                        self._saida = self.itens[self.linha][self.coluna]
                        if self.ao_selecionar:
                            index_linear = self.linha * colunas + self.coluna
                            self.ao_selecionar(index_linear, self._saida)
                        self.executando = False
                    elif tecla == 'esc':
                        self._saida = None
                        self.executando = False

                self.desenhar()

            time.sleep(0.1)

    def saida(self):
        return self._saida


if __name__ == '__main__':
    itens = [
        ["[1] - Teste 1", "[2] - Teste 2", "[3] - Teste 3"],
        ["[4] - Teste 4", "[5] - Teste 5", "[6] - Teste 6"],
        ["[7] - Teste 7", "[8] - Teste 8", "[9] - Teste 9"]
    ]

    menu = Menu(
        itens=itens,
        modo="grid",
        cor_normal=Text.WHITE,
        espaco_horizontal=7,
        espaco_vertical=3
    )

    menu.executar()
    print(f"\nValor retornado: {menu.saida()}")
