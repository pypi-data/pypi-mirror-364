import json
from dataclasses import dataclass, asdict, field


@dataclass
class Config:
    source: str
    target: str
    full_backup: bool = False
    name: str = "default"
    format: str = '%Y%m%d-%H_%M_%S.zip'
    max_backups: int = 10
    exclude: list[str] = field(default_factory=list)


def read_args(args) -> Config:
    cfg_dict = {}
    if args.source:
        cfg_dict['source'] = args.source
        if not args.name:
            cfg_dict['name'] = args.source.split('/')[-1]
    if args.target:
        cfg_dict['target'] = args.target
    if args.max:
        cfg_dict['max_backups'] = args.max
    if args.name:
        cfg_dict['name'] = args.name
    if args.exclude:
        cfg_dict['exclude'] = args.exclude
    if args.format:
        cfg_dict['format'] = args.format
    cfg_dict["full_backup"] = args.all

    if args.config:
        cfg = json.load(open(args.config))
        cfg.__dict__.update(cfg_dict)
    else:
        cfg = Config(**cfg_dict)
    return cfg


def write_config(file, cfg):
    with open(file, 'w') as f:
        json.dump(asdict(cfg), f, indent=4)

