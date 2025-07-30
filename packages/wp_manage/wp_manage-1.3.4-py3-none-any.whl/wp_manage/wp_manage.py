#!/usr/bin/env python3
import sys

from wp_manage.cli import wp_manage_argparser
from wp_manage.commands import delegate_cmd


def main():
    args = wp_manage_argparser.parse_args()
    if args.verbose:
        print(args, file=sys.stderr)
    delegate_cmd(args)
