from walker.commands.cp import ClipboardCopy
from walker.commands.bash import Bash
from walker.commands.cd import Cd
from walker.commands.check import Check
from walker.commands.command import Command
from walker.commands.cqlsh import Cqlsh
from walker.commands.device_c import DeviceCass
from walker.commands.device_p import DevicePostgres
from walker.commands.exit import Exit
from walker.commands.param_get import GetParam
# from walker.commands.help import Help
from walker.commands.issues import Issues
from walker.commands.ls import Ls
from walker.commands.nodetool import NodeTool
from walker.commands.postgres import Postgres
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

class ReplCommands:
    def repl_cmd_list() -> list[Command]:
        return [DevicePostgres(), DeviceCass()] + ReplCommands.navigation() + ReplCommands.cassandra_check() + ReplCommands.cassandra_ops() + ReplCommands.tools() + ReplCommands.exit()
        # return [DevicePostgres(), DeviceCass(), Ls(), Cd(), ClipboardCopy(), Bash(), Cqlsh(), Check(), GetParam(), Help(), Issues(), NodeTool(),
        #         Postgres(), Processes()] + Reaper.cmd_list() + Repair.cmd_list() + [
        #         Report(), Restart(), RollingRestart(), SetParam()] + Show.cmd_list() + [
        #         Status(), Storage(), Watch(), Exit()]

    def navigation() -> list[Command]:
        return [Ls(), Cd(), ClipboardCopy(), GetParam(), SetParam()] + Show.cmd_list()

    def cassandra_check() -> list[Command]:
        return [Check(), Issues(), NodeTool(), Processes(), Report(), Status(), Storage()]

    def cassandra_ops() -> list[Command]:
        return [Restart(), RollingRestart(), Watch()] + Reaper.cmd_list() + Repair.cmd_list()

    def tools() -> list[Command]:
        return [Cqlsh(), Postgres(), Bash()]

    def exit() -> list[Command]:
        return [Exit()]
    # def tools() -> list[Command]:
    #     return [Bash(), Cqlsh(), Check(), GetParam(), Help(), Issues(), NodeTool(),
    #             Postgres(), Processes()] + Reaper.cmd_list() + Repair.cmd_list() + [
    #             Report(), Restart(), RollingRestart(), SetParam()] + Show.cmd_list() + [
    #             Status(), Storage(), Watch(), Exit()]