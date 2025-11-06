import asyncio
import websockets
import json
import os

connected = set()
drawing_history = []

async def server(websocket):
    
    
    connected.add(websocket)
    print(f" Cliente conectado: {websocket.remote_address}")
    print(f" Total de clientes: {len(connected)}")

    
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
                        print(f" Erro ao enviar: {e}")
                        websockets_to_remove.add(conn)
            
            connected.difference_update(websockets_to_remove)

    except websockets.exceptions.ConnectionClosedOK:
        print(f" Cliente desconectado: {websocket.remote_address}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f" Conexão perdida: {e}")
    except Exception as e:
        print(f" ERROR: {e}")
    finally:
        if websocket in connected:
            connected.remove(websocket)

async def main():
    port = int(os.environ.get("PORT", 8765))  
    host = "0.0.0.0"  
    
    async with websockets.serve(server, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Servidor encerrado")