from walker.commands.cp import ClipboardCopy
from walker.commands.bash import Bash
from walker.commands.cd import Cd
from walker.commands.check import Check
from walker.commands.command import Command
from walker.commands.cqlsh import Cqlsh
from walker.commands.exit import Exit
from walker.commands.param_get import GetParam
from walker.commands.help import Help
from walker.commands.issues import Issues
from walker.commands.ls import Ls
from walker.commands.nodetool import NodeTool
from walker.commands.processes import Processes
from walker.commands.reaper import Reaper
from walker.commands.report import Report
from walker.commands.restart import Restart
from walker.commands.rolling_restart import RollingRestart
from walker.commands.param_set import SetParam
from walker.commands.show import Show
from walker.commands.status import Status
from walker.commands.storage import Storage
from walker.commands.watch import Watch
from walker.commands.repair import Repair

def repl_cmd_list() -> list[Command]:
    return [Bash(), Cd(), Check(), ClipboardCopy(), Cqlsh(), GetParam(), Help(), Issues(), Ls(), NodeTool(),
            Processes()] + Reaper.cmd_list() + Repair.cmd_list() + [
            Report(), Restart(), RollingRestart(), SetParam()] + Show.cmd_list() + [
            Status(), Storage(), Watch(), Exit()]