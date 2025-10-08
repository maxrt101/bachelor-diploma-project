#!/usr/bin/env python3
import json
import sys
import os

config = json.loads(open('rpi.json', 'r').read())


def log(*args):
    if not ('quiet' in config and config['quiet']):
        print('[rpi]', *args)


def usage():
    print(
        'Usage: ./rpi.py COMMAND [ARGS...]\n'
        'Commands:\n'
        '    u|upload|copy [LOCAL_FILE REMOTE_FILE] - Copies config.project.files by default\n'
        '    d|download|rcopy REMOTE_FILE           - File will be saved locally in CWD\n'
        '    r|run [FILE]                           - By default config.project.main will run\n'
        '    s|ssh|c|connect                        - Opens ssh session\n'
        '    sh|shell [COMMAND]                     - Runs shell command on RPI\n'
        '    o|off|shutdown                         - Shuts down RPI\n'
        '    reboot|restart                         - Restart RPI\n'
    )


def argv_get(n: int, die=True) -> list | None:
    if len(sys.argv) < n:
        if die:
            print('Error: Invalid arguments')
            usage()
            exit(1)
        else:
            return None
    return sys.argv[2:2+n]


def expand_path(path: str, remote=True) -> str:
    if remote:
        return path.replace('%', config['project']['work_dir']) if path[0] == '%' else path
    else:
        return path.replace('%', '')


class remote:
    use_sshpass = True
    print_exec = False
    print_copy = False
    rm_on_upload = False

    @classmethod
    def __exec(cls, cmd: str):
        os.system('{} {}'.format(
            f'sshpass -p {config["password"]}' if remote.use_sshpass else '',
            cmd
        ))

    @classmethod
    def connect(cls):
        log(f'Starting ssh session on {config["ip"]}')
        cls.__exec('ssh {}@{}'.format(config['user'], config['ip']))

    @classmethod
    def exec(cls, cmd: str):
        if cls.print_exec:
            log(f'Run "{cmd}" on {config["ip"]}')
        cls.__exec('ssh {}@{} "{}"'.format(
            config['user'],
            config['ip'],
            cmd
        ))

    @classmethod
    def upload(cls, local: str, remote: str):
        log(f'Upload {local} to remote {config["ip"]}')
        if cls.print_copy:
            log(f'       {local} -> {remote}')
        if cls.rm_on_upload:
            cls.exec('rm -rf {}'.format(expand_path(remote)))
        cls.__exec('scp -r "{}" "{}@{}:{}"'.format(
            local,
            config['user'],
            config['ip'],
            expand_path(remote)
        ))

    @classmethod
    def download(cls, remote: str, local: str):
        log(f'Download {remote} from {config["ip"]}')
        if cls.print_copy:
            log(f'          {remote} -> {local}')
        cls.__exec('scp -r "{}@{}:{}" "{}"'.format(
            config['user'],
            config['ip'],
            expand_path(remote),
            local
        ))

    @classmethod
    def py_exec(cls, file):
        log(f'Run {file} on {config["ip"]}')
        cls.exec('cd {} && source {}/bin/activate && python3 {}'.format(
            config['project']['work_dir'],
            expand_path(config['project']['venv']),
            file
        ))


def main():
    if len(sys.argv) < 2:
        usage()
        exit(1)

    cmd = sys.argv[1]

    if cmd in ['u', 'upload', 'copy']:
        args = argv_get(2, die=False)
        if args:
            remote.upload(args[0], expand_path(args[1]))
        else:
            for file in config['project']['files']:
                remote.upload(file, expand_path('%'))

    elif cmd in ['d', 'download', 'rcopy']:
        args = argv_get(1)
        remote.download(expand_path(args[0]), expand_path(args[0].split('/')[-1], remote=False))

    elif cmd in ['r', 'run']:
        args = argv_get(1, die=False)
        if args:
            remote.py_exec(args[0])
        else:
            remote.py_exec(config['project']['main'])

    elif cmd in ['sh', 'shell']:
        args = argv_get(1)
        log(f'Execute "{args[0]}" on {config["ip"]}')
        remote.exec(args[0])

    elif cmd in ['s', 'ssh', 'c', 'connect']:
        remote.connect()

    elif cmd in ['o', 'off', 'shutdown']:
        log(f'Send shutdown to {config["ip"]}')
        remote.exec('sudo shutdown now')

    elif cmd in ['reboot', 'restart']:
        log(f'Send reboot to {config["ip"]}')
        remote.exec('sudo reboot')

    else:
        print('Error: Unrecognized command')
        usage()
        exit(1)


if __name__ == '__main__':
    main()
