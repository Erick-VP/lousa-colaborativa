import asyncio
import websockets
import json
import os

connected = set()
drawing_history = []

async def server(websocket):
    """Gerencia conexões de clientes WebSocket"""
    
    connected.add(websocket)
    print(f"✅ Cliente conectado: {websocket.remote_address}")
    print(f"📊 Total de clientes: {len(connected)}")

    
    if drawing_history:
        await websocket.send(json.dumps({
            "type": "history", 
            "data": drawing_history
        }))

    try:
        async for message in websocket:
            data = json.loads(message)

            drawing_history.append(data)

            websockets_to_remove = set()
            for conn in connected:
                if conn != websocket:
                    try:
                        await conn.send(message)
                    except Exception as e:
                        print(f"❌ Erro ao enviar: {e}")
                        websockets_to_remove.add(conn)
            
            connected.difference_update(websockets_to_remove)

    except websockets.exceptions.ConnectionClosedOK:
        print(f"👋 Cliente desconectado: {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"⚠️ Conexão perdida: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if websocket in connected:
            connected.remove(websocket)
        print(f"📊 Clientes restantes: {len(connected)}")

async def main():
    """Função principal para iniciar o servidor"""

    port = int(os.environ.get("PORT", 8765))
    print(f"🚀 Iniciando servidor WebSocket em 0.0.0.0:{port}...")
    # print(f"✅ Servidor rodando em ws://localhost:{port}")
    print("⏳ Aguardando conexões... (Ctrl+C para parar)\n")

    async with websockets.serve(server, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:

        print("\n🛑 Servidor encerrado")
