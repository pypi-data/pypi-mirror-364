import re
import click
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.key_binding import KeyBindings

from walker.cli_group import cli
from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from walker.config import Config
from walker.repl_commands import repl_cmd_list
from walker.repl_session import ReplSession
from walker.repl_state import ReplState
from walker.k8s_utils import init_config, init_params, list_sts_name_and_ns
from walker.utils import deep_merge_dicts, lines_to_tabular, log2
from . import __version__

def enter_repl(state: ReplState):
    cmd_list = repl_cmd_list()
    # head with the Chain of Responsibility pattern
    cmds: Command = Command.chain(cmd_list)
    session = ReplSession().prompt_session

    def prompt_msg():
        msg = ''
        if state.pod:
            # cs-d0767a536f-cs-d0767a536f-default-sts-0
            group = re.match(r".*?-.*?-(.*)", state.pod)
            msg = group[1]
        elif state.sts:
            # cs-d0767a536f-cs-d0767a536f-default-sts
            group = re.match(r".*?-.*?-(.*)", state.sts)
            msg = group[1]

        return f"{msg}$ " if state.bash_session else f"{msg}> "

    log2(f'kaqing {__version__}')
    ss = list_sts_name_and_ns()

    if not ss:
        raise Exception("no Cassandra clusters found")
    elif len(ss) == 1 and Config().get('repl.auto-enter-only-cluster', True):
        cluster = ss[0]
        state.sts = cluster[0]
        state.namespace = cluster[1]
        state.wait_log(f'Moving to the only Cassandra cluster: {state.sts}@{state.namespace}...')

    kb = KeyBindings()

    @kb.add('c-c')
    def _(event):
        event.app.current_buffer.text = ''

    while True:
        try:
            completer = NestedCompleter.from_nested_dict({})
            if not state.bash_session:
                completions = {}
                for cmd in cmd_list:
                    completions = deep_merge_dicts(completions, cmd.completion(state))

                completer = NestedCompleter.from_nested_dict(completions)

            cmd = session.prompt(prompt_msg(), completer=completer, key_bindings=kb)

            if state.bash_session:
                if cmd.strip(' ') == 'exit':
                    state.exit_bash()
                    continue

                cmd = f'bash {cmd}'

            if cmd and cmd.strip(' ') and not cmds.run(cmd, state):
                log2(f'* Invalid command: {cmd}')
                log2()
                lines = [c.help(state) for c in cmd_list if c.help(state)]
                log2(lines_to_tabular(lines, separator=':'))
        except EOFError:  # Handle Ctrl+D (EOF) for graceful exit
            break
        except Exception as e:
            # raise e
            log2(e)
        finally:
            state.clear_wait_log_flag()

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterCommandHelper, help="Enter interactive shell.")
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaqing parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.argument('extra_args', nargs=-1, metavar='[cluster]', type=click.UNPROCESSED)
def repl(kubeconfig: str, config: str, param: list[str], cluster:str, namespace: str, extra_args):
    init_config(kubeconfig)
    if not init_params(config, param):
        return

    state = ReplState(ns_statefulset=cluster, namespace=namespace, in_repl=True)
    state, _ = state.apply_args(extra_args)
    enter_repl(state)