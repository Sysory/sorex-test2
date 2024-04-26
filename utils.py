import asyncio
import requests
import logging
import subprocess
from datetime import datetime
from os import environ
from aiogram import Bot
from bs4 import BeautifulSoup, Tag, NavigableString

class ServerStatus:
    def __init__(self, status, cpu, ram, ramUsed, cpuLoad):
        self.serverOnline = status
        self.cpuOK = cpu
        self.ramOK = ram
        self.cpuLoad = cpuLoad
        self.ramUsed = ramUsed


async def checkServer() -> ServerStatus | None:
    url = environ["SERVER_URL"]
    login = environ["MONITOR_LOGIN"]
    pswd = environ["MONITOR_PSWD"]
    serverName = environ["SERVER_NAME"]

    page = requests.get(url=url, auth=(login, pswd))
    await asyncio.sleep(0)
    soup = BeautifulSoup(page.text, "html.parser")

    server = soup.find('a', href=serverName)
    isServerMonitored = server is not None
    if (not isServerMonitored):
        logging.warning("Server not monitored with Monitor")
        return None
    serverON = await checkServerStatus(soup, server)
    cpuOK, ramOK, cpuLoad, ramLoad = await checkServerResourses(soup, server)

    return ServerStatus(serverON, cpuOK, ramOK, cpuLoad, ramLoad)

async def checkServerStatus(soup : BeautifulSoup, server : Tag | NavigableString | None) -> bool:
    status = server.parent.parent.select_one(".green-text")
    isOk = status is not None

    return isOk

async def checkServerResourses(soup : BeautifulSoup, server : Tag | NavigableString | None):
    cpuLoadStr : NavigableString = list(server.parent.parent.find_all("td", class_="right column"))[1]
    cpuVals = cpuLoadStr.getText().split(",\xa0")
    for i in range(len(cpuVals)):
        cpuVals[i] = cpuVals[i].split("%")[0]
    cpuLoad = sum(map(float, cpuVals))

    ramUsageStr : NavigableString = list(server.parent.parent.find_all("td", class_="right column"))[2]
    ramLoad = float(ramUsageStr.getText().split("%")[0])
    
    cpuOK = cpuLoad < 95
    ramOK = ramLoad < 95
    
    return cpuOK, ramOK, cpuLoad, ramLoad

# async def checkServerResourses() -> bool:
#     cpuOK = False
#     ramOK = False
#     # disks = True # TODO пока не поддерживается

#     cpu_command = """top -bn1 | awk '/Cpu/ { print $2}'"""
#     ramUsed_command = """free -m | awk '/Mem/{print $3}'"""
#     ramTotal_command = """free -m | awk '/Mem/{print $2}'"""
#     # disks

#     # try:
#     cpuLoad = subprocess.run([cpu_command], stdout=subprocess.PIPE, text=True)
#     logging.info(f"cpuLoad {cpuLoad} at {datetime.now()}")
#     ramUsed = subprocess.run([ramUsed_command], stdout=subprocess.PIPE, text=True)
#     logging.info(f"ramUsed {ramUsed} at {datetime.now()}")
#     ramTotal = subprocess.run([ramTotal_command], stdout=subprocess.PIPE, text=True)
#     logging.info(f"ramTotal {ramTotal} at {datetime.now()}")
#     ramLoad = float(ramUsed) / float(ramTotal) * 100
#     logging.info(f"ramLoad {ramLoad} at {datetime.now()}")

#     cpuOK = float(cpuLoad) < 95
#     ramOK = float(ramLoad) < 95
#     return cpuOK, ramOK, cpuLoad, ramLoad
#     # except:
#         # logging.error("An error with parsing server loads")

#     # print(useless_cat_call.stdout)  # Hello from the other side

def createBot():
    try:
        bot = Bot(token=environ["BOT_TOKEN"])
        return bot
    except:
        logging.error("Bot can't be created, maybe 'BOT_TOKEN' unvalid")
        exit(1)

async def send_message(bot : Bot, channel_id: int, text: str):
    logging.info(f"Sending message... channel_id: {channel_id}, text: {text}")
    await bot.send_message(channel_id, text)
    logging.info(f"Sending message... Done")