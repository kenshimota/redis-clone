import asyncio

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """function that handle connection for client
    Args:
        reader(asyncio.StreamReader): allow us to get buffer by stream.
        writer(asyncio.StreamWriter): allow us to send or write a message to client did a request.
    Returns:
        None
    """
    try:
        while True:
            data: bytes = await reader.read(1024)
            if not data:
                break
            writer.write(b"+PONG\r\n")
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

