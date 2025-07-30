# REQUIRES ~/.ssh/config entry like:
# Host *.ssh.wpengine.net
#     IdentityFile ~/.ssh/wpengine_ed25519
#     IdentitiesOnly yes

import os
import subprocess
import sys
import time

from wp_manage.site_response import check_site_response

ALL_ENV_NAMES = [
    'actravelalert',
    'aikeahawaii',
    'detroitcc',
    'dwfoodalert',
    'eatfairdc',
    'fairfr',
    'fenwayworkers',
    'fertittamoney',
    'greenhotels',
    'handoffpanton',
    'hiltonanch',
    'hgtskeptic',
    'itsourcoast',
    'local261',
    'local26',
    'local47',
    'marriotttimesh',
    'metooterranea',
    'neighborhoods1',
    'nejb',
    'nomissionbay',
    'resortfeerpr',
    'psdirtysecret',
    'rrripodissect',
    'savearapahoepr',
    'stcunion',
    'uhtestsite2024',
    'unionbusting',
    'unioneats',
    'unitehere100',
    'devl11site',
    'local11dev',
    'unitehere19',
    'unitehere1',
    'unitehere23',
    'uh24dev',
    'local24',
    'unitehere2',
    'unitehere355',
    'unitehere49',
    'unitehere57',
    'unitehere5',
    'unitehere610',
    'unitehere878',
    'unitehere8',
    'unitehere17',
    'unitehere362',
    'unitehere40',
    'unitehere54',
    'unitehere737',
    'uhlocal74',
    'unitehere75',
    'unitehere7',
    'uniteherewpdev',
    'uniteherewp',
    'uniteherewpstg',
    'uhphilly',
    'uniteheretest',
    'uphoenixexpose',
    'voteno',
    'wehorising',
    'workfamsunited',
]

DELAY = 60
MAX_RETRIES = 5


def run_ssh_cmd(env_name, cmd, verbose=False):
    retries = 0

    while retries < MAX_RETRIES:
        full_cmd = cmd.copy()
        if verbose:
            full_cmd = ["set", "-x", "&&"] + full_cmd

        ssh_command = ["ssh", f"{env_name}@{env_name}.ssh.wpengine.net"] + full_cmd

        if verbose:
            print(ssh_command, file=sys.stderr)

        result = subprocess.run(ssh_command,
                                stderr=subprocess.PIPE,
                                text=True)

        if "Failed to create shell" in result.stderr:
            retries += 1
            print(f"Retry {retries}/{MAX_RETRIES}: Failed to create shell. Retrying in {DELAY} seconds...",
                  file=sys.stderr)
            time.sleep(DELAY)
        else:
            return result

    raise RuntimeError("Failed to create WP Engine shell after multiple tries.")


def scp_theme_zipfile(env_name, path_to_zipfile, verbose=False):
    zip_basename = os.path.basename(path_to_zipfile)
    cmd = ["mkdir", "-p", f"/home/wpe-user/sites/{env_name}/xfer"]

    if verbose:
        cmd.extend(["&&", "ls", "-l", f"/home/wpe-user/sites/{env_name}/xfer"])

    # makes xfer directory
    run_ssh_cmd(env_name, cmd)

    cmd = ["scp", "-O", path_to_zipfile,
           f"{env_name}@{env_name}.ssh.wpengine.net:/home/wpe-user/sites/{env_name}/xfer/{zip_basename}"]

    if verbose:
        print(cmd, file=sys.stderr)

    subprocess.run(cmd)

    if verbose:
        ls_command = ["ls", "-l", f"/home/wpe-user/sites/{env_name}/xfer"]
        run_ssh_cmd(env_name, ls_command, verbose)

    scp_zip_path = f"/home/wpe-user/sites/{env_name}/xfer/{zip_basename}"
    return scp_zip_path


def delegate_cmd(args):
    envs = []
    cmd = None
    cmd_args = []

    if args.env:
        envs.append(args.env)
    elif args.all_envs:
        envs = ALL_ENV_NAMES
    elif args.print_envs:
        print_all_envs()
        return

    if args.subcommand == 'plugin':
        if args.list:
            cmd = list_active_plugins
        elif args.update_check:
            cmd = list_available_plugin_updates
        elif args.update:
            cmd = update_plugin
            cmd_args.append(args.update)
        elif args.update_all:
            cmd = update_all_plugins

    elif args.subcommand == 'theme':
        if args.list:
            cmd = list_themes
        elif args.status:
            cmd = theme_status
            # args.status refers to name of theme
            cmd_args.append(args.status)
        elif args.install:
            cmd = install_theme
            # args.install refers to the name of the theme
            cmd_args.append(args.install)
            cmd_args.append(args.zip_file_path)

    elif args.subcommand == 'core':
        if args.update_check:
            cmd = check_for_wp_update
        elif args.update:
            cmd = run_wp_update

    elif args.subcommand == 'test-response':
        cmd = check_site_response

    for env in envs:
        env_args = [env] + cmd_args + [args.verbose]
        cmd(*env_args)


def print_all_envs():  # pragma: no cover
    print("\n".join(sorted(ALL_ENV_NAMES)))


def activate_theme(env_name, theme_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "theme", "activate", theme_name])
    run_ssh_cmd(env_name, cmd, verbose)


def list_themes(env_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "theme", "status"])
    run_ssh_cmd(env_name, cmd, verbose)


def theme_status(env_name, theme_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(['wp', 'theme', 'status', theme_name])
    run_ssh_cmd(env_name, cmd, verbose)


def install_theme(env_name, theme_name, path_to_zipfile, verbose=False):
    # scp locally stored zip file to site
    scp_zip_path = scp_theme_zipfile(env_name, path_to_zipfile, verbose)
    # remove old theme back up and rename current theme to 'old theme name'
    rename_old_theme(env_name, theme_name, verbose)

    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])
    # cd to themes directory and unzip ~/xfer/theme.zip to ~/themes/theme_name
    cmd.extend(["cd", f"sites/{env_name}/wp-content/themes", "&&",
                "unzip", "-o", scp_zip_path, "-x", "\'__MACOSX/*\'"])

    if verbose:
        cmd.extend(["&&", "ls"])

    run_ssh_cmd(env_name, cmd, verbose)

    cmd = []
    # cd to themes directory
    cmd.extend(["cd", f"/home/wpe-user/sites/{env_name}/wp-content/themes", "&&"])
    # store DIRNAME
    cmd.extend(["DIRNAME=$(", "unzip", "-l", scp_zip_path, "|",
                "grep", "-v", "__MACOSX", "|",
                "head", "-n4", "|",
                "tail", "-n1", "|",
                "awk", "\\'{print substr($0, index($0, $4))}\\'", "|",
                "tr", "-d", "\\'/\\'", ")", "&&"])

    if verbose:
        cmd.extend(["echo", "$DIRNAME", "&&"])
    # rename DIRNAME TO theme_name
    cmd.extend(["mv", '\\"$DIRNAME\\"', theme_name])

    run_ssh_cmd(env_name, cmd, verbose)

    # activate new theme
    # activate_theme(env_name, theme_name, verbose)

    # remove zip file from tmp directory
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])
    # Clean up xfer directory
    cmd.extend(["rm", "-r", scp_zip_path])
    run_ssh_cmd(env_name, cmd, verbose)


def rename_old_theme(env_name, theme_name, verbose=False):  # pragma: no cover
    # remove old theme back up and rename current theme
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["cd", f"sites/{env_name}/wp-content/themes", "&&"])

    if verbose:
        cmd.extend(["ls", "&&"])

    cmd.extend(["rm", "-r", f"\\'{theme_name} old\\'", "||", "echo", f"No such directory {theme_name}", "&&"])

    if verbose:
        cmd.extend(["ls", "&&"])

    cmd.extend(["mv", f"\\'{theme_name}\\'", f"\\'{theme_name} old\\'"])

    if verbose:
        cmd.extend(["&&", "ls"])

    run_ssh_cmd(env_name, cmd, verbose)


def list_active_plugins(env_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "plugin", "list", "--status=active"])
    run_ssh_cmd(env_name, cmd, verbose)


def list_available_plugin_updates(env_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "plugin", "update", "--all", "--dry-run"])
    run_ssh_cmd(env_name, cmd, verbose)


def update_all_plugins(env_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "plugin", "update", "--all"])
    run_ssh_cmd(env_name, cmd, verbose)


def update_plugin(env_name, plugin, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "plugin", "update", f"{plugin}"])
    run_ssh_cmd(env_name, cmd, verbose)


def check_for_wp_update(env_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "core", "check-update"])
    run_ssh_cmd(env_name, cmd, verbose)


def run_wp_update(env_name, verbose=False):  # pragma: no cover
    cmd = []
    if verbose:
        cmd.extend(["set", "-x", "&&"])

    cmd.extend(["wp", "core", "update"])
    run_ssh_cmd(env_name, cmd, verbose)
