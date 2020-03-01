#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-14
#


import asyncio
from enum import Enum
from flattiverse.connector.connection import Connection
from flattiverse.connector.galaxy import Galaxy
from flattiverse.connector.player import Player
from flattiverse.connector.team import Team
from flattiverse.connector.universe import Universe
from flattiverse.connector.util import event


class Server:
    class ServerCommand(Enum):
        player_created = 0x0b
        login_completed = 0x0f
        universe_meta_info_updated = 0x10
        universe_team_meta_info_updated = 0x11
        universe_galaxy_meta_info_updated = 0x12
        universe_systems_meta_info_updated = 0x13

    def __init__(self):
        self.login_completed_event = asyncio.Event()

        self._players_map = {}
        self.players = []

        self._universe_map = {}
        self.universes = []

        self.login_completed_status = 0

        self.scan_event = event.Event("Scan event")

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
                self.ServerCommand.player_created.value: self.player_created,
                self.ServerCommand.login_completed.value: self.login_completed,
                self.ServerCommand.universe_meta_info_updated.value: self.universe_meta_info_updated,
                self.ServerCommand.universe_team_meta_info_updated.value: self.universe_team_meta_info_updated,
                self.ServerCommand.universe_galaxy_meta_info_updated.value: self.universe_galaxy_meta_info_updated,
                self.ServerCommand.universe_systems_meta_info_updated.value: self.universe_systems_meta_info_updated
            }.get(packet.command, self.unknown_command)(packet)

    def player_created(self, packet):
        self._players_map[packet.base_address] = Player(packet)
        self.players = self._players_map.values()

    def login_completed(self, packet):
        self.login_completed_status = packet.helper
        self.login_completed_event.set()

    def universe_meta_info_updated(self, packet):
        universe_id = packet.base_address

        if packet.reader.size == 0:
            del self._universe_map[universe_id]
        elif universe_id not in self._universe_map.keys():
            self._universe_map[universe_id] = Universe(self, packet)
        else:
            self._universe_map[universe_id].update_from_packet(packet)
        self.universes = self._universe_map.values()

    def universe_team_meta_info_updated(self, packet):
        universe_id = packet.base_address
        team_id = packet.sub_address

        if universe_id not in self._universe_map.keys():
            return

        universe = self._universe_map[universe_id]

        if packet.reader.size == 0:
            del universe.team_map[team_id]
        elif team_id not in universe.team_map.keys():
            universe.team_map[team_id] = Team(universe, packet)
        else:
            universe.team_map[team_id].update_from_packet(packet)

        universe.teams = universe.team_map.values()

    def universe_galaxy_meta_info_updated(self, packet):
        universe_id = packet.base_address
        galaxy_id = packet.sub_address

        if universe_id not in self._universe_map.keys():
            return

        universe = self._universe_map[universe_id]

        if packet.reader.size == 0:
            del universe.galaxy_map[galaxy_id]
        elif galaxy_id not in universe.galaxy_map.keys():
            universe.galaxy_map[galaxy_id] = Galaxy(universe, packet)
        else:
            universe.galaxy_map[galaxy_id].update_from_packet(packet)

        universe.galaxies = universe.galaxy_map.values()

    def universe_systems_meta_info_updated(self, packet):
        universe_id = packet.base_address
        if universe_id not in self._universe_map.keys():
            return
        self._universe_map[universe_id].update_systems(packet)
        self.universes = self._universe_map.values()

    def unknown_command(self, packet):
        print("Unknown command: 0x{:02x}".format(packet.command))
        pass
