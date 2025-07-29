import argparse

from . import config
from . import core

parser = argparse.ArgumentParser(description='EEBackup - A simple backup tool')
parser.add_argument('-c', '--config', type=str, nargs='?', const="eebackup.json", help='Path to config file')
parser.add_argument('-m', '--make', nargs='?', const="eebackup.json", help='Create a new config file')
parser.add_argument('-b', '--backup', help='Perform a backup operation')
parser.add_argument('-s', '--source', type=str, help='Source directory or URL')
parser.add_argument('-t', '--target', type=str, help='Target directory or URL')
parser.add_argument('-d', '--delete', type=str, help='Delete a specific backup file')
parser.add_argument('-a', '--all', action='store_true', help='Perform a full (not incremental) backup')
parser.add_argument("-n", "--name", type=str, help="Backup name")
parser.add_argument('-l', '--list', type=str, nargs='?', const=True, help='List contents of a specific backup file')
parser.add_argument('--max', type=int, metavar='N',
                    help='Maximum number of backups to keep (default: 10, max: 50)')
parser.add_argument('-f', '--format', type=str, help='Backup format, e.g. "%%Y%%m%%d-%%H_%%M_%%S.zip"')
parser.add_argument('-e', '--exclude', type=str, action='append', help='Exclude file(s), using wildcard, repeatable')
parser.add_argument('-r', '--restore', type=str, help='Restore a specific backup file')
args = parser.parse_args()


def main():
    if not args.config:
        if not args.source and not args.target:
            print('Please specify source and target directories or URLs')
            exit(1)
    # 获取配置
    try:
        cfg = config.read_args(args)
    except Exception as e:
        print(e)
        exit(1)

    # 创建配置
    if args.make:
        config.write_config(args.make, cfg)
        print('Created config file:', args.make)

    try:
        # 查看文件
        if file := args.list:
            if file is True:
                core.list_file(cfg)
            else:
                core.show_file(file, cfg)

        # 删除文件
        if file := args.delete:
            core.delete_file(file, cfg)

        # 恢复文件
        if file := args.restore:
            core.restore_file(file, cfg)

        # 执行备份
        if args.backup:
            core.backup_file(cfg, args.name)
    except core.ArgException as e:
        print(e)


if __name__ == '__main__':
    main()
