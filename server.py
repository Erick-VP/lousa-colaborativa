import asyncio
import websockets
import json
import os
import logging

# Configura o log para ser mais claro
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Variáveis Globais ---
connected_clients = set()
drawing_history = []

# --- Funções Principais ---

async def handle_connection(websocket):
    """
    Lida com um cliente que se conectou com sucesso.
    """
    # Adiciona o cliente à lista de conectados
    connected_clients.add(websocket)
    logging.info(f"✅ Cliente conectado. Total de usuários: {len(connected_clients)}")

    try:
        # Envia o histórico de desenhos para o novo cliente
        if drawing_history:
            await websocket.send(json.dumps({"type": "history", "data": drawing_history}))

        # Fica escutando por novas mensagens (desenhos) do cliente
        async for message in websocket:
            data = json.loads(message)
            
            # Adiciona o novo desenho ao histórico
            drawing_history.append(data)
            
            # Envia o desenho para todos os outros clientes conectados
            other_clients = connected_clients - {websocket}
            if other_clients:
                websockets.broadcast(other_clients, message)

    except websockets.exceptions.ConnectionClosedError:
        logging.info("🔌 Conexão perdida de forma inesperada.")
    except websockets.exceptions.ConnectionClosedOK:
        logging.info("👋 Cliente desconectou normalmente.")
    finally:
        # Remove o cliente da lista ao desconectar
        connected_clients.remove(websocket)
        logging.info(f"📉 Cliente removido. Usuários restantes: {len(connected_clients)}")

async def main():
    """
    Função principal que inicia o servidor e lida com as conexões.
    """
    # ESTA É A PARTE IMPORTANTE:
    # O 'handler' principal que decide o que fazer com cada nova conexão.
    async def health_check_handler(websocket, path):
        try:
            # Se a conexão for um WebSocket válido, passa para a nossa lógica principal
            await handle_connection(websocket)
        except websockets.exceptions.InvalidMessage:
            # Se for uma requisição HTTP inválida (como a do Render),
            # ele captura o erro e simplesmente IGNORA, mantendo o servidor VIVO.
            logging.warning("⚠️ Requisição HTTP inválida foi ignorada. Servidor continua de pé.")
            return  # Encerra o handler para esta conexão específica, sem travar.

    port = int(os.environ.get("PORT", 8765))
    host = "0.0.0.0"
    
    logging.info(f"🚀 Servidor WebSocket iniciando em {host}:{port}")
    
    # Inicia o servidor usando nosso handler "à prova de balas"
    async with websockets.serve(health_check_handler, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Servidor encerrado manualmente.")











# import asyncio
# import websockets
# import json
# import os

# connected = set()
# drawing_history = []

# async def server(websocket):
#     """Gerencia conexões de clientes WebSocket"""
    
#     connected.add(websocket)
#     print(f"✅ Cliente conectado: {websocket.remote_address}")
#     print(f"📊 Total de clientes: {len(connected)}")

    
#     if drawing_history:
#         await websocket.send(json.dumps({
#             "type": "history", 
#             "data": drawing_history
#         }))

#     try:
#         async for message in websocket:
#             data = json.loads(message)

#             drawing_history.append(data)

#             websockets_to_remove = set()
#             for conn in connected:
#                 if conn != websocket:
#                     try:
#                         await conn.send(message)
#                     except Exception as e:
#                         print(f"❌ Erro ao enviar: {e}")
#                         websockets_to_remove.add(conn)
            
#             connected.difference_update(websockets_to_remove)

#     except websockets.exceptions.ConnectionClosedOK:
#         print(f"👋 Cliente desconectado: {websocket.remote_address}")
#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"⚠️ Conexão perdida: {e}")
#     except Exception as e:
#         print(f"❌ Erro: {e}")
#     finally:
#         if websocket in connected:
#             connected.remove(websocket)
#         print(f"📊 Clientes restantes: {len(connected)}")

# async def main():
#     """Função principal para iniciar o servidor"""
    
#     # ⚠️ MUDANÇAS AQUI ⚠️
#     port = int(os.environ.get("PORT", 8765))  # Usa porta do ambiente ou 8765
#     host = "0.0.0.0"  # ⚠️ IMPORTANTE: Mudar de "localhost" para "0.0.0.0"
    
#     print("🚀 Iniciando servidor WebSocket...")
#     print(f"✅ Servidor rodando em ws://{host}:{port}")
#     print("⏳ Aguardando conexões... (Ctrl+C para parar)\n")
    
#     # ⚠️ MUDANÇA AQUI TAMBÉM ⚠️
#     async with websockets.serve(server, host, port):
#         await asyncio.Future()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\n🛑 Servidor encerrado")