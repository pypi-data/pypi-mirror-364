"""
Table
=====

Tabela estilizada para terminal, com:
- Alinhamento configurável por coluna
- Bordas estéticas (Unicode)
- Cores opcionais via ANSI
"""

from typing import List, Any, Optional


class Align:
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class Table:
    def __init__(
        self,
        headers: List[str],
        align: Optional[List[str]] = None,
        header_color: str = Color.BOLD + Color.GREEN,
        border_color: str = Color.GRAY,
        content_color: str = Color.WHITE,
        separator_style: str = "─"  # Estilo padrão da linha separadora
    ):
        self.headers = headers
        self.align = align or [Align.LEFT] * len(headers)
        self.header_color = header_color
        self.border_color = border_color
        self.content_color = content_color
        self.separator_style = separator_style
        self.rows = []
        self.separators = set()  # Armazena índices onde há separadores

    def add_row(self, row: List[Any]):
        """Adiciona uma linha à tabela."""
        if len(row) != len(self.headers):
            raise ValueError("Número de colunas não corresponde ao cabeçalho.")
        self.rows.append([str(cell) for cell in row])

    def add_separator(self):
        """Marca que a próxima linha terá um separador acima dela."""
        self.separators.add(len(self.rows))  # Adiciona antes da próxima linha

    def _column_widths(self) -> List[int]:
        """Calcula a largura de cada coluna."""
        columns = zip(*([self.headers] + self.rows))
        return [max(len(str(cell)) for cell in col) for col in columns]

    def _align_text(self, text: str, width: int, mode: str) -> str:
        """Alinha texto conforme especificado."""
        if mode == Align.RIGHT:
            return text.rjust(width)
        elif mode == Align.CENTER:
            return text.center(width)
        return text.ljust(width)

    def _draw_border(self, left: str, mid: str, right: str, sep: str, widths: List[int]) -> str:
        return self.border_color + left + sep.join(mid * (w + 2) for w in widths) + right + Color.RESET

    def _draw_separator(self, widths: List[int]) -> str:
        """Desenha uma linha separadora."""
        return self._draw_border("├", self.separator_style, "┤", "┼", widths)

    def _draw_row(self, cells: List[str], widths: List[int], color: str) -> str:
        aligned_cells = []
        for i in range(len(cells)):
            aligned = self._align_text(cells[i], widths[i], self.align[i])
            aligned_cells.append(aligned)
        
        content = self.border_color + "│ " + Color.RESET
        content += color + (" " + self.border_color + "│ " + Color.RESET + color).join(aligned_cells)
        content += " " + self.border_color + "│" + Color.RESET
        
        return content

    def __str__(self) -> str:
        widths = self._column_widths()

        top = self._draw_border("╭", "─", "╮", "┬", widths)
        mid = self._draw_border("├", "─", "┤", "┼", widths)
        bottom = self._draw_border("╰", "─", "╯", "┴", widths)

        result = [top]
        result.append(self._draw_row(self.headers, widths, self.header_color))
        result.append(mid)
        
        for i, row in enumerate(self.rows):
            if i in self.separators:
                result.append(self._draw_separator(widths))
            result.append(self._draw_row(row, widths, self.content_color))
        
        result.append(bottom)

        return "\n".join(result)