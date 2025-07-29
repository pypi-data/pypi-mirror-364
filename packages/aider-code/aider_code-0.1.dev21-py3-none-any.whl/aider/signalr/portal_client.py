from signalrcore.hub_connection_builder import HubConnectionBuilder

SERVER_NAME = "devflux-project-portal-server"
HUB_NAME = "aider"


class PortalClient:
    def __init__(self, coder, server_name=SERVER_NAME, hub_name=HUB_NAME):
        """
        SignalR 채팅 클라이언트 초기화

        Args:
            url (str): SignalR 허브 URL
            hub_name (str): 허브 이름 (signalrcore에서는 URL에 포함)
        """
        self.coder = coder
        self.io = coder.io
        self.server_name = server_name
        self.hub_name = hub_name
        self.connection = None
        self.is_connected = False
        self.command_handlers = {}

    def connect(self):
        """SignalR 서버에 연결"""
        try:
            self.connection = (
                HubConnectionBuilder()
                .with_url(
                    f"http://localhost:9988/{self.server_name}/hub/{self.hub_name}"
                )
                .with_automatic_reconnect(
                    {
                        "type": "raw",
                        "keep_alive_interval": 10,
                        "reconnect_interval": 5,
                        "max_attempts": 5,
                    }
                )
                .build()
            )

            # 기본 메시지 핸들러 등록
            self.connection.on("receiveCommand", self._on_receive_command)

            self.connection.start()
            self.is_connected = True
            self.io.tool_output("Portal(@Canopus) 연결 완료")

        except Exception as e:
            self.is_connected = False

    def disconnect(self):
        """SignalR 서버 연결 해제"""
        if self.connection:
            self.connection.stop()
            self.is_connected = False
            self.io.tool_output("Portal(@Canopus) 연결 해제")

    def send_message(self, message):
        """메시지 전송"""
        if not self.is_connected:
            raise Exception("Portal(@Canopus) 서버에 연결되지 않았습니다.")

        try:
            self.connection.send("send", message)
        except Exception as e:
            self.io.tool_error(f"Portal(@Canopus) 메시지 전송 오류: {e}")
            raise

    def _on_receive_command(self, data):
        """기본 메시지 수신 핸들러"""
        # 등록된 커스텀 핸들러들 실행
        for handler in self.command_handlers.values():
            try:
                handler(self.coder, data)
            except Exception as e:
                self.io.tool_error(f"Portal(@Canopus) 메시지 핸들러 실행 중 오류: {e}")

    def add_command_handler(self, name, handler):
        """커스텀 메시지 핸들러 추가"""
        self.command_handlers[name] = handler

    def remove_command_handler(self, name):
        """메시지 핸들러 제거"""
        if name in self.command_handlers:
            del self.command_handlers[name]

    def add_event_handler(self, event_name, handler):
        """다른 SignalR 이벤트 핸들러 추가"""
        if not self.connection:
            raise Exception("연결이 초기화되지 않았습니다.")

        self.connection.on(event_name, handler)

    def invoke_server_method(self, method_name, *args):
        """서버 메서드 호출"""
        if not self.is_connected:
            raise Exception("서버에 연결되지 않았습니다.")

        try:
            return self.connection.send(method_name, *args)
        except Exception as e:
            self.io.tool_error(f"Portal(@Canopus) 서버 메서드 실행 오류: {e}")
            raise

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.disconnect()
