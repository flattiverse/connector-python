#!/usr/bin/env python3
#
# Python Connector to Flattiverse Game Server (www.flattiverse.com)
# Harald Melcher (flattiverse@haraldmelcher.com)
# 2019-10-14
#

from flattiverse.connector.difficulty import Difficulty
from flattiverse.connector.privileges import Privileges
from flattiverse.connector.universe_mode import UniverseMode
from flattiverse.connector.universe_status import UniverseStatus
from flattiverse.connector.universe_system import UniverseSystem
from flattiverse.connector.util.binary_memory_reader import BinaryMemoryReader


class Universe:

    def __init__(self, server, packet):
        self.id = packet.base_address
        self.server = server

        self.teams = []
        self.team_map = {}

        self.galaxies = []
        self.galaxy_map = {}

        self.systems = []

        self.name = ""
        self.description = ""
        self.difficulty = Difficulty.Easy
        self.mode = UniverseMode.Mission
        self.owner_id = 0
        self.max_players = 0
        self.max_players_per_team = 0
        self.max_ships_per_player = 0
        self.max_ships_per_team = 0
        self.status = UniverseStatus.Online
        self.default_privileges = Privileges.Nothing

        self.update_from_packet(packet)

    def update_from_packet(self, packet):
        reader: BinaryMemoryReader = packet.reader

        self.name = reader.read_string_non_null()
        self.description = reader.read_string_non_null()

        self.difficulty = Difficulty(reader.read_byte())
        self.mode = UniverseMode(reader.read_byte())

        self.owner_id = reader.read_uint32()

        self.max_players = reader.read_uint16()
        self.max_players_per_team = reader.read_uint16()
        self.max_ships_per_player = reader.read_byte()
        self.max_ships_per_team = reader.read_uint16()

        self.status = UniverseStatus(reader.read_byte())
        self.default_privileges = reader.read_byte()

    def update_systems(self, packet):
        reader: BinaryMemoryReader = packet.reader
        systems = []
        while reader.size > 0:
            system = UniverseSystem(reader)
            if system.in_use:
                systems.append(system)
        self.systems = systems
