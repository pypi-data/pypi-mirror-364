"""
Gerenciamento de conexão com aplicações.

Fornece funcionalidades robustas para conectar e gerenciar aplicações,
com tratamento de erros e recuperação automática.
"""

import logging
import time
from typing import Optional, Union
import psutil

from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class RMApplication:
    """
    Gerenciador de conexão com a aplicação RM.
    
    Encapsula a lógica de conexão, reconexão e gerenciamento do ciclo de vida
    da aplicação RM, fornecendo uma interface robusta e confiável.
    """
    
    def __init__(self):
        self.config = get_ui_config()
        self._app: Optional[Application] = None
        self._process_id: Optional[int] = None
        self._is_connected: bool = False
    
    @property
    def app(self) -> Application:
        """
        Retorna a instância da aplicação, conectando se necessário.
        
        Returns:
            Application: Instância da aplicação conectada.
            
        Raises:
            UIConnectionError: Se não for possível conectar à aplicação.
        """
        if not self._is_connected or not self._app:
            self.connect()
        return self._app
    
    def connect(
        self, 
        process_id: Optional[int] = None,
        window_title: Optional[str] = None
    ) -> Application:
        """
        Conecta-se à aplicação RM.
        
        Args:
            process_id: ID específico do processo. Se None, tenta encontrar automaticamente.
            window_title: Título específico da janela. Se None, usa o padrão da configuração.
            
        Returns:
            Application: Instância da aplicação conectada.
            
        Raises:
            UIConnectionError: Se não for possível conectar após todas as tentativas.
        """
        window_title = window_title or self.config.window_title
        
        for attempt in range(1, self.config.max_connection_attempts + 1):
            try:
                logger.info(f"Tentativa {attempt}/{self.config.max_connection_attempts} de conexão")
                
                if process_id:
                    self._app = self._connect_by_process_id(process_id)
                elif self._process_id:
                    self._app = self._connect_by_process_id(self._process_id)
                else:
                    self._app = self._connect_by_title_or_process()
                
                self._is_connected = True
                logger.info("Conexão estabelecida com sucesso")
                return self._app
                
            except Exception as e:
                logger.warning(f"Tentativa {attempt} falhou: {e}")
                if attempt == self.config.max_connection_attempts:
                    error_msg = f"Falha ao conectar após {self.config.max_connection_attempts} tentativas"
                    capture_screenshot_on_error("connection_failed")
                    raise UIConnectionError(error_msg, str(e))
                
                time.sleep(self.config.wait_between_retries)
    
    def _connect_by_process_id(self, process_id: int) -> Application:
        """Conecta pela ID do processo."""
        logger.debug(f"Conectando pelo PID: {process_id}")
        app = Application(backend=self.config.backend).connect(process=process_id)
        self._process_id = process_id
        return app
    
    def _connect_by_title_or_process(self) -> Application:
        """Conecta pelo título da janela ou nome do processo."""
        try:
            # Primeira tentativa: por título da janela
            logger.debug(f"Conectando pelo título: {self.config.window_title}")
            app = Application(backend=self.config.backend).connect(title=self.config.window_title)
            return app
        except ElementNotFoundError:
            # Segunda tentativa: por nome do processo
            logger.debug(f"Conectando pelo processo: {self.config.process_name}")
            return self._connect_by_process_name()
    
    def _connect_by_process_name(self) -> Application:
        """Conecta pelo nome do processo."""
        rm_processes = [p for p in psutil.process_iter(['pid', 'name']) 
                       if p.info['name'].lower() == self.config.process_name.lower()]
        
        if not rm_processes:
            raise UIConnectionError(f"Processo {self.config.process_name} não encontrado")
        
        # Usa o primeiro processo encontrado
        process_id = rm_processes[0].info['pid']
        logger.debug(f"Processo RM encontrado com PID: {process_id}")
        return self._connect_by_process_id(process_id)
    
    def disconnect(self) -> None:
        """Desconecta da aplicação."""
        if self._app:
            logger.info("Desconectando da aplicação")
            self._app = None
            self._is_connected = False
            self._process_id = None
    
    def is_connected(self) -> bool:
        """
        Verifica se a conexão está ativa.
        
        Returns:
            bool: True se conectado, False caso contrário.
        """
        if not self._is_connected or not self._app:
            return False
        
        try:
            # Tenta uma operação simples para verificar se a conexão ainda é válida
            _ = self._app.windows()
            return True
        except Exception:
            logger.warning("Conexão perdida, marcando como desconectado")
            self._is_connected = False
            return False
    
    def reconnect(self) -> Application:
        """
        Força uma reconexão com a aplicação.
        
        Returns:
            Application: Nova instância da aplicação conectada.
        """
        logger.info("Forçando reconexão")
        self.disconnect()
        return self.connect()
    
    def get_main_window(self):
        """
        Retorna a janela principal da aplicação.
        
        Returns:
            HwndWrapper: Janela principal da aplicação.
        """
        return self.app.window(title=self.config.window_title)