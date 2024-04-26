import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from utils import *

bot = createBot()
dp = Dispatcher(storage=MemoryStorage())

async def checkingLoop(bot : Bot, delay = 30):
    while True:
        logging.info("Check server status")
        serverStats = await checkServer()
        if (serverStats.serverOnline == True):
            logging.info(f"Server is UP at {datetime.now()}")
        else:
            logging.warning(f"!!!Server is DOWN at {datetime.now()}")
            await send_message(bot, environ["CHAT_ID"], f"Сервер лежит на данный момент. время: {datetime.now()}")

        if (serverStats.cpuOK == True):
            logging.info(f"Server cpu load is {serverStats.cpuLoad} at {datetime.now()}")
        else:
            logging.warning(f"!!!Server's cpu is {serverStats.cpuLoad} at {datetime.now()}")
            await send_message(bot, environ["CHAT_ID"], f"Сервер перегружен по цп ({serverStats.cpuLoad}). время: {datetime.now()}")

        if (serverStats.ramOK == True):
            logging.info(f"Server ram used is {serverStats.ramUsed} at {datetime.now()}")
        else:
            logging.warning(f"!!!Server's ram used is {serverStats.ramUsed} at {datetime.now()}")
            await send_message(bot, environ["CHAT_ID"], f"Сервер перегружен по ram ({serverStats.ramUsed}). время: {datetime.now()}")

        await asyncio.sleep(delay)

async def main():
    logging.info(f"--- Start session at {datetime.now()} ---")
    await bot.delete_webhook(drop_pending_updates=True)
    loop = asyncio.create_task(checkingLoop(bot, 60))   # раз в минуту проверяет состояние
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    file = open("log.txt", 'a')
    logging.basicConfig(level=logging.INFO, stream=file)
    asyncio.run(main())