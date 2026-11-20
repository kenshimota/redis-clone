import asyncio

from app.inputs.read_input_redis import read_input_redis


async def main():
    print("Logs from your program will appear here!")
    server = await asyncio.start_server(read_input_redis, "0.0.0.0", 6379)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
