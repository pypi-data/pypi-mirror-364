# EEBackup - File Backup Tool
### [中文](README_CN.md)

EEBackup is a lightweight file backup tool that does not rely on any third-party libraries. It supports multiple backup methods and flexible configuration options.

## Core Features

- **Incremental Backup**: Only backs up changed files, saving storage space
- **Command Line Control**: Provides rich command line parameters for precise control
- **Cross-Platform Compatibility**: Based on Python standard library, supports Windows, Linux, and Mac systems

## Quick Start
install
```bash
pip install eebackup
```

```bash
# Perform a simple backup
eebackup -s ./data -t ./backup -b

# Create a configuration file
eebackup -s ./data -t ./backup -m

# Use the configuration file for backup
eebackup -c -b

# View complete help information
eebackup -h
```

## Usage

### Basic Command
```
eebackup [OPTIONS]
```

### Parameter Description
- `-c, --config [FILE]` Specify the configuration file (default: eebackup.json)
- `-m, --make [FILE]` Create a configuration file (default: eebackup.json)
- `-b, --backup [NAME]` Perform a backup operation
- `-s, --source PATH` Specify source directory or URL
- `-t, --target PATH` Specify backup target directory or URL
- `-d, --delete FILE` Delete specified backup file
- `-a, --all` Perform a full backup
- `-l, --list [FILE]` List current backup file information
- `--max N` Set maximum number of backups (default: 10)
- `-n, --name NAME` Name for this backup
- `-f, --format FORMAT` Backup format (e.g., "%Y%m%d-%H_%M_%S.zip")
- `-e, --exclude PATTERN` Exclude file pattern (can be used repeatedly)
- `-r, --restore FILE` Restore specified backup file

## Configuration File

The configuration file is in JSON format and includes:
- `source` Source directory or URL
- `target` Target directory or URL
- `full_backup` Whether to perform a full backup
- `format` Backup format
- `max_backups` Maximum number of backups
- `exclude` List of files to exclude

## Examples

```bash
# Create a configuration file
eebackup -m

# Perform a simple backup
eebackup -s ./data -t ./backup -b

# Use the configuration file for backup
eebackup -c eebackup.json -b
eebackup -c -b  # use ./eebackup.json

# Restore a backup
eebackup -r "2023-10-01:12_00_00" -c eebackup.json
```