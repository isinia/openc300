#!/usr/bin/env python3
from argparse import ArgumentParser
from loguru import logger
import socket
import re

OWN_BUFFER_SIZE = 1028

# this list was extracted from the MyHOME Suite binary
# the only values really being used by the C300 are 7 and 8,
# but i decided to keep them all for reference
OWN_WHO_VALUES = {
    0: 'SCENARIOS',
    1: 'LIGHTING',
    2: 'AUTOMATION_SYSTEMS',
    3: 'APPLIANCES',
    4: 'HEATING_ADJUSTMENT',
    5: 'ALARMS',
    6: 'VIDEO_DOOR_ENTRY_SYSTEM',
    7: 'MULTIMEDIA',
    8: 'VIDEO_DOOR_ENTRY_SYSTEM_OVER_IP',
    9: 'AUXILIARIES',
    10: 'NAVIGATION',
    11: 'ENERGY_DISTRIBUTION',
    13: 'EXTERNAL_INTERFACE_DEVICES',
    14: 'SPECIAL_COMMANDS',
    15: 'HOME_AUTOMATION_MAIN_UNIT_COMMAND',
    16: 'SOUND_SYSTEM',
    17: 'HOME_AUTOMATION_MAIN_UNIT_MANAGEMENT',
    99: 'SERVICE_IDENTIFICATION',
    1001: 'DIAGNOSTIC_OF_LIGHTING_SYSTEM',
    1004: 'DIAGNOSTIC_OF_HEATING_SYSTEM',
    1013: 'DIAGNOSTIC_OF_DEVICE_SYSTEM',
}

OWN_ACK = '*#*1##'
OWN_NACK = '*#*0##'

# based on the BTicino specification
# https://developer.legrand.com/uploads/2019/12/OWN_Intro_ENG.pdf
OWN_CMD_REGEXES = {
    'NORMAL': r'\*([0-9][0-9]?[0-9]?[0-9]?)\*([0-9#]*)\*([0-9#]*)##',
    'STATUS_REQUEST': r'\*#([0-9][0-9]?[0-9]?[0-9]?)\*([0-9#]*)##',
    'DIMENSION_REQUEST': r'\*#([0-9][0-9]?[0-9]?[0-9]?)\*([0-9#]*)\*([0-9#]*)##',
    'DIMENSION_WRITING': r'\*#([0-9][0-9]?[0-9]?[0-9]?)\*([0-9#]*)\*([0-9#\*]*)##',
}

OWN_COMMANDS = {
    'monitor_mode_session': '*99*1##',
    'command_mode_session': '*99*0##',
}


class OpenWebNetNACKException(Exception):
    pass


class OpenWebNetCommand:
    def __init__(self, raw):
        self.raw = raw

    def _parse_command_syntax(self):
        if self.raw == OWN_ACK:
            return ('ACK', ())
        if self.raw == OWN_NACK:
            return ('NACK', ())

        for _type in OWN_CMD_REGEXES:
            match = re.fullmatch(OWN_CMD_REGEXES[_type], self.raw)
            if match:
                return (_type, match.groups())

        logger.error(f'failed to parse OpenWebNet command: {self.raw}')
        return ('UNDEFINED', ())

    def _parse_command_who(self, groups):
        who = int(groups[0])
        return OWN_WHO_VALUES[who] if who in OWN_WHO_VALUES else who

    def parse(self):
        parsed = {}
        _type, groups = self._parse_command_syntax()
        parsed['type'] = _type

        if _type not in ('ACK', 'NACK', 'UNDEFINED'):
            parsed['who'] = self._parse_command_who(groups)

        return parsed


class Connection:
    def __init__(self, host, port):
        self.socket_host = host
        self.socket_port = port

    def _init_socket(self):
        self.sock = socket.socket()

    def _is_nack(self, res):
        return res == OWN_NACK

    def _recv_raw_cmd(self):
        res = self.sock.recv(OWN_BUFFER_SIZE).decode()
        if len(res):
            logger.debug(f'received OpenWebNet command: {res}')

        if self._is_nack(res):
            raise OpenWebNetNACKException(f'received {OWN_NACK} response')

        return self.sock.recv(1024).decode()

    def _send_raw_cmd(self, cmd):
        logger.debug(f'sending OpenWebNet command: {cmd}')
        self.sock.send(cmd.encode())

    def connect(self):
        self._init_socket()
        self.sock.connect((self.socket_host, self.socket_port))

    def disconnect(self):
        self.sock.close()


def start_monitor_mode(conn):
    logger.info('monitor mode on, listening to intercom\'s commands')
    conn._send_raw_cmd(OWN_COMMANDS['monitor_mode_session'])

    while True:
        try:
            conn._recv_raw_cmd()
        except KeyboardInterrupt:
            logger.debug('received keyboard interrupt')
            break
        except Exception as e:
            print(e)


def start_command_mode(conn):
    logger.info('command mode on, waiting for commands')
    conn._send_raw_cmd(OWN_COMMANDS['command_mode_session'])
    conn._recv_raw_cmd()

    while True:
        try:
            queue = []
            while True:
                cmd = input('> ')
                if len(cmd):
                    queue.append(cmd)
                else:
                    break
            for i in queue:
                conn._send_raw_cmd(i)
            conn._recv_raw_cmd()
        except KeyboardInterrupt:
            logger.debug('received keyboard interrupt')
            break
        except Exception as e:
            print(e)


if __name__ == '__main__':
    arg_parser = ArgumentParser(prog='oc300')
    arg_parser.add_argument(
        '-H',
        '--host',
        help='hostname or IP of your intercom',
        default='192.168.129.1',
    )
    arg_parser.add_argument(
        '-p',
        '--port',
        help='port of your intercom\'s Open Web Net interface',
        default=20000,
        type=int,
    )
    arg_group = arg_parser.add_mutually_exclusive_group()
    arg_group.add_argument(
        '-m',
        '--monitor-mode',
        help='monitor intercom\'s communication',
        action='store_true',
    )
    arg_group.add_argument(
        '-c',
        '--command-mode',
        help='send commands to your intercom',
        action='store_true',
    )
    args = arg_parser.parse_args()

    conn = Connection(args.host, args.port)
    conn.connect()
    logger.info(f'connected to {args.host}:{args.port}')

    if args.monitor_mode:
        start_monitor_mode(conn)
    elif args.command_mode:
        start_command_mode(conn)

    conn.disconnect()
    logger.info('closed socket connection')
