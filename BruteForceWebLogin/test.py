from webLogin import startLogin
import asyncio

async def main():
    await startLogin()  # Usa await se startLogin è una coroutine

# Esegui la coroutine main
asyncio.run(main())
