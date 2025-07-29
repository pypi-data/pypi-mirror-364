from aider.io import InputOutput
from aider.coders import Coder
from .command_handler import command_handler
from .portal_client import PortalClient


class ClientManager:
    def __init__(self, coder: Coder, config_connect=None):
        """
        SignalR 채팅 클라이언트 초기화

        Args:
            coder (Coder): coder
        """
        self.coder = coder
        self.io = coder.io
        self.is_connected = False
        self.portalClient = None
        self.config_connect = config_connect

        # connect가 사전이고 portal 키가 있는지 확인
        if self.config_connect:
            self.portalClient = PortalClient(coder)

    def connect(self):
        """SignalR 서버에 연결"""
        try:
            if self.config_connect:
                self.portalClient.connect()
                self.portalClient.add_command_handler("portal", command_handler)
                self.is_connected = True

        except Exception as e:
            self.is_connected = False
            raise

    def disconnect(self):
        """SignalR 서버 연결 해제"""
        self.portalClient.disconnect()
        self.is_connected = False

    def send_message(self, client, message):
        """메시지 전송"""
        if not self.is_connected:
            self.io.tool_error("Server is not connected.")
            return

        if client == "portal":
            self.portalClient.send_message(message)

    def invoke_server_method(self, client, method_name, *args):
        """서버 메서드 실행"""
        if not self.is_connected:
            self.io.tool_error("Server is not connected.")
            return None

        if client == "portal":
            return self.portalClient.invoke_server_method(method_name, *args)
        return None

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.disconnect()
