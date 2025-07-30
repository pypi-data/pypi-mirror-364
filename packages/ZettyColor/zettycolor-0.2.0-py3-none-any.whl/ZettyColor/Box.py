import unicodedata
from typing import Optional, List, Dict

class ConsoleBox:
    """Classe para criar caixas de texto estilizadas no console."""

    BORDER_STYLES = {
        'single': {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'h': '─', 'v': '│'},
        'double': {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 'h': '═', 'v': '║'},
        'round': {'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'h': '─', 'v': '│'},
        'bold': {'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛', 'h': '━', 'v': '┃'}
    }

    BOX_TYPES = {
        'text': {'color': 'blue', 'icon': 'ℹ'},
        'info': {'color': 'blue', 'icon': 'ℹ'},
        'alert': {'color': 'yellow', 'icon': '⚠'},
        'warning': {'color': 'yellow', 'icon': '⚠'},
        'error': {'color': 'red', 'icon': '✖'},
        'success': {'color': 'green', 'icon': '✔'},
        'question': {'color': 'cyan', 'icon': '?'}
    }

    COLORS = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }

    @staticmethod
    def _get_char_width(char: str) -> int:
        """Retorna a largura do caractere (1 para maioria, 2 para emojis/CJK)."""
        return 2 if unicodedata.east_asian_width(char) in ('W', 'F') else 1

    @staticmethod
    def _get_text_width(text: str) -> int:
        """Calcula a largura real do texto considerando caracteres largos."""
        return sum(ConsoleBox._get_char_width(c) for c in text)

    @staticmethod
    def _pad_text(text: str, width: int, align: str = 'left') -> str:
        """Ajusta o texto para ocupar exatamente a largura especificada."""
        text_width = ConsoleBox._get_text_width(text)
        
        if text_width >= width:
            return text
        
        space = width - text_width
        
        if align == 'right':
            return ' ' * space + text
        elif align == 'center':
            left = space // 2
            right = space - left
            return ' ' * left + text + ' ' * right
        else:
            return text + ' ' * space

    @classmethod
    def create_box(
        cls,
        content: Optional[str] = None,
        title: Optional[str] = None,
        box_type: str = 'text',
        width: Optional[int] = None,
        min_width: int = 20,
        max_width: Optional[int] = None,
        border_style: str = 'single',
        text_align: str = 'left',
        padding: int = 1,
        color: Optional[str] = None,
        margin_top: int = 0,
        margin_bottom: int = 0,
        wrap_words: bool = True
    ) -> str:
        """
        Cria uma caixa de texto estilizada para o console.
        
        Args:
            content: Texto principal da caixa (pode conter múltiplas linhas)
            title: Título exibido na borda superior
            box_type: Tipo de caixa ('text', 'info', 'alert', 'error', 'success', etc.)
            width: Largura fixa da caixa (None para automático)
            min_width: Largura mínima quando calculada automaticamente
            max_width: Largura máxima quando calculada automaticamente
            border_style: Estilo da borda ('single', 'double', 'round', 'bold')
            text_align: Alinhamento do texto ('left', 'center', 'right')
            padding: Espaçamento interno entre texto e bordas
            color: Cor personalizada (sobrescreve a cor do box_type)
            margin_top: Linhas em branco acima da caixa
            margin_bottom: Linhas em branco abaixo da caixa
            wrap_words: Se True, quebra palavras longas para caber na largura
            
        Returns:
            String formatada com a caixa de texto
        """

        if border_style not in cls.BORDER_STYLES:
            border_style = 'single'
            
        if box_type not in cls.BOX_TYPES:
            box_type = 'text'
            
        if text_align not in ('left', 'center', 'right'):
            text_align = 'left'
            
        padding = max(0, padding)
        margin_top = max(0, margin_top)
        margin_bottom = max(0, margin_bottom)

        box_config = cls.BOX_TYPES[box_type]
        icon = box_config['icon']
        color = color or box_config['color']
        color_code = cls.COLORS.get(color, cls.COLORS['blue'])
        reset_color = cls.COLORS['reset']
        style = cls.BORDER_STYLES[border_style]

        lines = []
        if content:
            for line in content.split('\n'):
                lines.append(line)

        if width is None:
            content_width = max(cls._get_text_width(line) for line in lines) if lines else 0
            content_width += padding * 2

            title_width = 0
            if title:
                title_text = f" {icon} {title} "
                title_width = cls._get_text_width(title_text)

            width = max(content_width, title_width + 2, min_width)
            
            if max_width is not None:
                width = min(width, max_width)

        if title:
            title_text = f" {icon} {title} "
            title_line = cls._pad_text(title_text, width - 2, 'center')
            top_border = f"{color_code}{style['tl']}{title_line}{style['tr']}{reset_color}"
        else:
            top_border = f"{color_code}{style['tl']}{style['h'] * (width - 2)}{style['tr']}{reset_color}"

        content_lines = []
        for line in lines:
            padded_line = ' ' * padding + line + ' ' * padding

            if wrap_words and cls._get_text_width(padded_line) > width - 2:
                words = line.split(' ')
                current_line = []
                current_length = padding
                
                for word in words:
                    word_width = cls._get_text_width(word)
                    
                    if current_length + word_width + 1 > width - 2 - padding:
                        content_lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = padding + word_width
                    else:
                        current_line.append(word)
                        current_length += word_width + 1

                if current_line:
                    content_lines.append(' '.join(current_line))
            else:
                content_lines.append(line)

        formatted_lines = []
        for line in content_lines:
            padded_line = ' ' * padding + line + ' ' * padding
            aligned_line = cls._pad_text(padded_line, width - 2, text_align)
            formatted_lines.append(
                f"{color_code}{style['v']}{reset_color}"
                f"{aligned_line}"
                f"{color_code}{style['v']}{reset_color}"
            )

        bottom_border = f"{color_code}{style['bl']}{style['h'] * (width - 2)}{style['br']}{reset_color}"
        
        box_lines = [top_border]
        
        if formatted_lines:
            box_lines.extend(formatted_lines)
        else:
            empty_line = (
                f"{color_code}{style['v']}{reset_color}"
                f"{' ' * (width - 2)}"
                f"{color_code}{style['v']}{reset_color}"
            )
            box_lines.append(empty_line)
        
        box_lines.append(bottom_border)

        full_box = '\n'.join([''] * margin_top + box_lines + [''] * margin_bottom)
        
        return full_box

    @classmethod
    def print_box(
        cls,
        content: Optional[str] = None,
        title: Optional[str] = None,
        box_type: str = 'text',
        width: Optional[int] = None,
        min_width: int = 20,
        max_width: Optional[int] = None,
        border_style: str = 'single',
        text_align: str = 'left',
        padding: int = 1,
        color: Optional[str] = None,
        margin_top: int = 0,
        margin_bottom: int = 0,
        wrap_words: bool = True
    ) -> None:
        """Versão que imprime diretamente no console."""
        box = cls.create_box(
            content=content,
            title=title,
            box_type=box_type,
            width=width,
            min_width=min_width,
            max_width=max_width,
            border_style=border_style,
            text_align=text_align,
            padding=padding,
            color=color,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            wrap_words=wrap_words
        )
        print(box)
        
if __name__ == '__main__':

    ConsoleBox.print_box("Mensagem do caralho", title="Texto", box_type="text")
    ConsoleBox.print_box("Mensagem do caralho", title="Info", box_type="info")
    ConsoleBox.print_box("Mensagem do caralho", title="Alerta", box_type="alert")
    ConsoleBox.print_box("Mensagem do caralho", title="Cuidado", box_type="warning")
    ConsoleBox.print_box("Mensagem do caralho", title="Erro", box_type="error")
    ConsoleBox.print_box("Mensagem do caralho", title="Sucesso", box_type="success")
    ConsoleBox.print_box("Mensagem do caralho", title="Pergunta", box_type="question")   

    box = ConsoleBox.create_box(
        content="Esse é conteudo de um teste de uma box muito foda pra caralho",
        title="Titulo muito foda",
        box_type="error",
        border_style="bold",
        text_align="center",
        padding=0,
        color="magenta",
        margin_top=2,
        margin_bottom=2,
        wrap_words=True
    )
    print(box)