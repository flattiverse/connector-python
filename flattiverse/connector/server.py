#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-14
#


import asyncio
from enum import Enum
from flattiverse.connector.connection import Connection
from flattiverse.connector.team import Team
from flattiverse.connector.universe import Universe


class Server:
    class ServerCommand(Enum):
        login_completed = 0x0f
        universe_meta_info_updated = 0x10
        universe_team_meta_info_updated = 0x11

    def __init__(self):
        self.login_completed_event = asyncio.Event()
        self._universe_array = {}
        self.universes = []
        self.login_completed_status = 0

    async def login(self, username, password):
        if username == "":
            raise ValueError("username required")
        if password == "":
            raise ValueError("password required")

        connection = Connection()
        connection.packets_received = self.received
        connection.connect(username, password)

        await self.login_completed_event.wait()
        return self.login_completed_status

    def received(self, packets):
        for packet in packets:
            {
                self.ServerCommand.login_completed.value: self.login_completed,
                self.ServerCommand.universe_meta_info_updated.value: self.universe_meta_info_updated,
                self.ServerCommand.universe_team_meta_info_updated.value: self.universe_team_meta_info_updated
            }.get(packet.command, self.unknown_command)(packet)

    def login_completed(self, packet):
        self.login_completed_status = packet.helper
        self.login_completed_event.set()

    def universe_meta_info_updated(self, packet):
        universe_id = packet.base_address

        if packet.reader.size == 0:
            del self._universe_array[universe_id]
        elif universe_id not in self._universe_array.keys():
            self._universe_array[universe_id] = Universe(packet)
        else:
            self._universe_array[universe_id].update_from_packet(packet)
        self.universes = self._universe_array.values()

    def universe_team_meta_info_updated(self, packet):
        universe_id = packet.base_address
        team_id = packet.sub_address

        if universe_id not in self._universe_array.keys():
            return

        universe = self._universe_array[universe_id]

        if packet.reader.size == 0:
            del universe.team_array[team_id]
        elif team_id not in universe.team_array.keys():
            universe.team_array[team_id] = Team(self._universe_array[universe_id], packet)
        else:
            universe.team_array[team_id].update_from_packet(packet)

        universe.teams = universe.team_array.values()

    def unknown_command(self, packet):
        print("Unknown command: 0x{:02x}".format(packet.command))
        pass
