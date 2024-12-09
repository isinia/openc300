#!/usr/bin/env python3
from argparse import ArgumentParser
from loguru import logger
import socket

OWN_BUFFER_SIZE = 1028
OWN_COMMANDS = {
    'monitor_mode_session': '*99*1##',
    'command_mode_session': '*99*0##',
}

ACK = '*#*1##'
NACK = '*#*0##'


class OpenWebNetNACKException(Exception):
    pass


class Connection:
    def __init__(self, host, port):
        self.socket_host = host
        self.socket_port = port

    def _init_socket(self):
        self.sock = socket.socket()

    def _is_nack(self, res):
        return res == NACK

    def _recv_raw_cmd(self):
        res = self.sock.recv(OWN_BUFFER_SIZE).decode()
        if len(res):
            logger.debug(f'received OpenWebNet command: {res}')

        if self._is_nack(res):
            raise OpenWebNetNACKException(f'received {NACK} response')

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
