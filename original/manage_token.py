import json
import websockets
import asyncio
import os

# Configuration
ADMINTOKEN = "<YOUR ADMIN TOKEN HERE>" #used to rotate API keys
HAHOST = "ws://<YOUR LOCAL HA ADDRESS>:8123/api/websocket"
TOKENNAME = "jukeboxtoken"
TOKENPATH = "/config/www/jukeboxtoken.key"

def create_token():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(generate_token())
    finally:
        loop.close()

def delete_token():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(remove_token())
    finally:
        loop.close()

async def generate_token():
    try:
        async with websockets.connect(HAHOST) as websocket:
            # Receive auth required message
            authrequired = await websocket.recv()
            print(f"Initial message: {authrequired}")

            # Send authentication
            auth = {
                "type": "auth",
                "access_token": ADMINTOKEN
            }
            await websocket.send(json.dumps(auth))
            authresponse = await websocket.recv()
            print(f"Auth response: {authresponse}")

            # Request long-lived token
            tokenrequest = {
                "id": 1,
                "type": "auth/long_lived_access_token",
                "client_name": TOKENNAME,
                "lifespan": 1
            }
            await websocket.send(json.dumps(tokenrequest))
            tokenresponse = await websocket.recv()
            
            result = json.loads(tokenresponse)
            if result.get("success"):
                with open(TOKENPATH, "w") as f:
                    f.write(result["result"])
                print(f"Token saved to {TOKENPATH}")
            else:
                print("Failed to generate token")

    except Exception as e:
        print(f"Error: {str(e)}")

async def remove_token():
    try:
        async with websockets.connect(HAHOST) as websocket:
            # Auth process
            await websocket.recv()
            auth = {
                "type": "auth",
                "access_token": ADMINTOKEN
            }
            await websocket.send(json.dumps(auth))
            authresponse = await websocket.recv()
            
            if json.loads(authresponse)["type"] == "auth_ok":
                # List tokens
                listcmd = {
                    "id": 1,
                    "type": "auth/refresh_tokens"
                }
                await websocket.send(json.dumps(listcmd))
                response = await websocket.recv()
                
                tokens = json.loads(response)["result"]
                tokenid = None
                
                for token in tokens:
                    if token["client_name"] == TOKENNAME:
                        tokenid = token["id"]
                        break
                
                if tokenid:
                    deletecmd = {
                        "id": 2,
                        "type": "auth/delete_refresh_token",
                        "refresh_token_id": tokenid
                    }
                    await websocket.send(json.dumps(deletecmd))
                    deleteresponse = await websocket.recv()
                    
                    if json.loads(deleteresponse)["success"]:
                        print("Token deleted successfully")
                        if os.path.exists(TOKENPATH):
                            os.remove(TOKENPATH)
                    else:
                        print("Failed to delete token")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        delete_token()
    else:
        create_token()
