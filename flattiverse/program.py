#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-13
#
import asyncio
import colorama
from flattiverse.connector.server import Server


async def main():
    print("Starting...")
    server = Server()
    login_status = await server.login("Player2", "Password")

    if login_status != 0:
        print("Login status", login_status)
    else:
        colorama.init()
        for universe in server.universes:
            print("{:<15.15} | {:<30.30} | {:<10.10} | {:<10.10}"
                  .format(universe.name, universe.description, universe.difficulty.name, universe.mode.name))

            for team in universe.teams:
                print("*  [\x1b[3"+str(team.console_color())+"m████\x1b[0m]", team.name)

        colorama.deinit()
    print("... Ready")

asyncio.run(main())
