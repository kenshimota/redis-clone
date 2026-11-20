import asyncio
from app.connection import handle_client


async def main():
    print("Logs from your program will appear here!")
    server = await asyncio.start_server(handle_client, "0.0.0.0", 6379)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
