from .main import main
import asyncio


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

