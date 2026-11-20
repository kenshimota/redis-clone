import asyncio

async def handle_client(reader, writer) -> None:
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            writer.write(b"+PONG\r\n")
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

