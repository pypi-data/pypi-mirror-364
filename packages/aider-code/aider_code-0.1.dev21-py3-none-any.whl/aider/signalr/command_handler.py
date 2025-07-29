def command_handler(coder, data):
    """기본 메시지 수신 핸들러"""
    print(f"받은 메시지: {data}")
    message = '메시지 받은, "{}"'.format(data)
    coder.run(with_message=message)
    return "처리 완료"
