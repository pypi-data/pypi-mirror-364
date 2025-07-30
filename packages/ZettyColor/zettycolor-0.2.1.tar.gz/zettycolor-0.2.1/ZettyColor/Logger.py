"""
Logger
======

Classe responsável por registrar erros e exceções em um arquivo de log,
voltado para uso em bibliotecas, scripts e APIs por programadores Python.

Exemplo de uso:
---------------
Logger.log_error("Erro genérico")
try:
    1 / 0
except Exception as e:
    Logger.log_exception(e)
"""

import os
import traceback
from datetime import datetime


class Logger:
    """
    Classe utilitária para registro de logs de erro e exceção.
    """
    LOG_FILE = "system/log.log"

    @staticmethod
    def log_error(message: str, source: str = None) -> None:
        """
        Registra uma mensagem de erro genérica no log.

        Parameters:
        -----------
        message : str
            Mensagem descritiva do erro.
        source : str, optional
            Origem do erro (nome do módulo, classe, etc).
        """
        Logger._write_log("ERROR", message, source)

    @staticmethod
    def log_exception(exc: BaseException, source: str = None) -> None:
        """
        Registra uma exceção no log, com stack trace completo.

        Parameters:
        -----------
        exc : BaseException
            Exceção capturada (Exception, RuntimeError, etc).
        source : str, optional
            Origem do erro.
        """
        tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        Logger._write_log("EXCEPTION", tb, source)

    @staticmethod
    def _write_log(level: str, message: str, source: str = None) -> None:
        """
        Escreve uma entrada no arquivo de log.

        Parameters:
        -----------
        level : str
            Tipo da mensagem (ex: "ERROR", "EXCEPTION").
        message : str
            Conteúdo da mensagem.
        source : str, optional
            Informação adicional sobre a origem.
        """
        directory = os.path.dirname(Logger.LOG_FILE)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        origem = f"[{source}]" if source else ""
        separador = "=" * 100
        entry = f"[{now}] [{level}] {origem}\n{message.strip()}\n{separador}\n\n"

        # Escreve no arquivo com lock
        with open(Logger.LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(entry)
