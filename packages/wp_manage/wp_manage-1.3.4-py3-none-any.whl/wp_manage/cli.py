import argparse

WP_MANAGE_DESC = """
    Process for updating WP Engine sites

    For all commands either specify a single environment with --env or include
    --all-envs argument (use --print-envs to see list of envs --all-envs will update)

    If installing/upgrading a theme, please ensure you have the latest theme
    stored locally on your machine and the file path readily available.
"""
WP_MANAGE_EPILOG = """
    For help with subcommands, do `wp-manage {subcommand} --help`
"""

class WPManageArgParser(argparse.ArgumentParser):

    def parse_args(self, args=None, namespace=None):
        args = super().parse_args(args=args, namespace=namespace)
        if args.subcommand == 'theme' and args.install and not args.zip_file_path:
            raise ValueError('theme --install requires a --zip-file-path argument')

        if not args.subcommand and (args.env is not None or args.all_envs):
            raise ValueError('Please provide a subcommand and action. Use --help to see options.')

        if args.print_envs and args.subcommand is not None:
            raise ValueError('--print-envs does not accept a subcommand. Did you mean --env or --env-name?')

        return args


wp_manage_argparser = WPManageArgParser(description=WP_MANAGE_DESC,
                                        epilog=WP_MANAGE_EPILOG,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
wp_manage_argparser.add_argument('--verbose', action='store_true', help='create debug log for dev team')
env_group = wp_manage_argparser.add_mutually_exclusive_group(required=True)
env_group.add_argument('--env', help='WP environment to work on (ex uhtestsite2024)')
env_group.add_argument('--all-envs', action='store_true', help='run command on all environments')
env_group.add_argument('--print-envs', action='store_true', help='print list of known envs')
subparsers = wp_manage_argparser.add_subparsers(dest='subcommand', help='subcommands')

# THEME
theme_subparser = subparsers.add_parser('theme', help='run themes-related command')
theme_action_group = theme_subparser.add_mutually_exclusive_group(required=True)
theme_action_group.add_argument('--list', action='store_true', help='list themes installed in env')
theme_action_group.add_argument('--status', help='lists status and version details for a specified theme')
theme_action_group.add_argument('--install', type=str, help='name of theme to be installed or updated')
theme_subparser.add_argument('--zip-file-path', type=str, help='path to zip file to be installed or updated')

# PLUGINS
plugin_subparser = subparsers.add_parser('plugin', help='run plugins-related command')
plugin_action_group = plugin_subparser.add_mutually_exclusive_group(required=True)
plugin_action_group.add_argument('--list', action='store_true', help='list plugins installed in env')
plugin_action_group.add_argument('--update', help='name of plugin to update in env(s)')
plugin_action_group.add_argument('--update-check', action='store_true', help='list plugins with available updates in env')
plugin_action_group.add_argument('--update-all', action='store_true', help='update all plugins in env(s)')

# WORDPRESS
core_subparser = subparsers.add_parser('core', help='run system-related command')
core_action_group = core_subparser.add_mutually_exclusive_group(required=True)
core_action_group.add_argument('--update-check', action='store_true', help='check for wordpress updates')
core_action_group.add_argument('--update', action='store_true', help='update wordpress')

# CHECK SITE RESPONSE
test_response_subparser = subparsers.add_parser('test-response', help='send a http request to the site')