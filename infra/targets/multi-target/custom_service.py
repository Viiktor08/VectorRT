"""Servicio TCP mínimo en el puerto 9000 para dar variedad al escaneo de puertos."""
import socketserver


class BannerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.sendall(b"VectorRT-lab-custom-service/1.0\r\n")


if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", 9000), BannerHandler) as server:
        server.serve_forever()
