import json
import tempfile
import time
from datetime import timedelta
from typing import Annotated

import typer
from rich import box
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, TimeElapsedColumn
from rich.table import Table

from .helper.conversion import b2gb
from .helper.migration import check_vm_migrate, migrate_vms
from .helper.ui import spinner_col, text_col, usage_bar
from .proxmox import Proxmox
from .util.exceptions import PVECLIError, PVECLIMigrationCheckError

cluster_cli = typer.Typer()
vm_mapping_cli = typer.Typer()
cluster_cli.add_typer(vm_mapping_cli, name='vm-mapping')


@cluster_cli.callback()
def cluster_cli_callback(
    ctx: typer.Context,
    parallel: Annotated[
        int, typer.Option('--parallel', '-p', show_default=True, help='Sets how many migrations should be run in parallel')
    ] = 4,
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    ctx.obj['nodes'] = proxmox_api.node.list_()
    ctx.obj['cluster'] = proxmox_api.cluster.info()
    ctx.obj['parallel_migrations'] = parallel


@cluster_cli.command()
def reboot(
    ctx: typer.Context,
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    nodes = ctx.obj['nodes']
    parallel_migrations = ctx.obj['parallel_migrations']
    vms_all = proxmox_api.vm.list_()
    vms_to_migrate = [vm for vm in vms_all if vm['status'] == 'running' and 'do-not-migrate' not in vm.get('tags', [])]

    node_migration_map = {nodes[i]['node']: nodes[i - 1]['node'] for i in range(len(nodes))}
    migration_blockers = []
    with_local_disks = False
    for vm in vms_to_migrate:
        try:
            migration_check_result = check_vm_migrate(proxmox_api=proxmox_api, vm=vm, dest_node=node_migration_map[vm['node']])
            if migration_check_result['local_disks']:
                with_local_disks = True
        except PVECLIMigrationCheckError as err:
            migration_blockers.append(err)

    if migration_blockers:
        raise PVECLIError(
            'Can not automatically reboot cluster because running VM(s) are not online-migration ready:\n'
            + '\n'.join([blocker.message for blocker in migration_blockers])
        )

    for node_data in nodes:
        node = node_data['node']
        tmp_node = node_migration_map[node]
        node_running_vms = [vm['vmid'] for vm in vms_to_migrate if vm['node'] == node]

        migration_failed = migrate_vms(
            api=proxmox_api,
            dest_node=tmp_node,
            vmid_list=node_running_vms,
            parallel_migrations=parallel_migrations,
            with_local_disks=with_local_disks,
        )
        if migration_failed:
            with tempfile.NamedTemporaryFile(mode='wt', delete=False, prefix='pve-cli') as tmpfile:
                json.dump(vms_all, tmpfile, indent=2)
                raise PVECLIError(
                    f'Migration failed. Aborting cluster reboot. Initial VM-Mapping has been saved to {tmpfile.name}'
                )

        with Progress(spinner_col, TimeElapsedColumn(), text_col) as progress:
            task_id = progress.add_task(description=f'[white]Rebooting {node}...', total=1)
            proxmox_api.node.reboot(node)
            # wait for node to go offline
            while proxmox_api.node.get(node)['status'] == 'online':
                time.sleep(10)  # it is not necessary to check this to often, check node status every 10 seconds should be fine
            # wait for node to come online
            while proxmox_api.node.get(node)['status'] != 'online':
                time.sleep(10)  # it is not necessary to check this to often, check node status every 10 seconds should be fine
            progress.update(task_id, completed=1, refresh=True, description=f'[green]Done: Rebooted {node}')

        migration_failed = migrate_vms(
            api=proxmox_api,
            dest_node=node,
            vmid_list=node_running_vms,
            parallel_migrations=parallel_migrations,
            with_local_disks=with_local_disks,
        )
        if migration_failed:
            with tempfile.NamedTemporaryFile(mode='wt', delete=False, prefix='pve-cli') as tmpfile:
                json.dump(vms_all, tmpfile, indent=2)
                raise PVECLIError(
                    f'Migration failed. Aborting cluster reboot. Initial VM-Mapping has been saved to {tmpfile.name}'
                )


@cluster_cli.command('list')
def list_(ctx: typer.Context) -> None:
    cluster = ctx.obj['cluster']
    nodes = ctx.obj['nodes']

    table = Table(title=f'Nodes in cluster {cluster["name"]}', box=box.ROUNDED)
    table.add_column('Node')
    table.add_column('Status', justify='center')
    table.add_column('Cores', justify='right')
    table.add_column('CPU Usage')
    table.add_column('RAM')
    table.add_column('RAM Usage')
    table.add_column('Disk Usage')
    table.add_column('Uptime')

    for node in nodes:
        status = '🚀 online' if node['status'] == 'online' else f'💀 {node["status"]}'
        ram = int(b2gb(node['maxmem']))
        cpu_bar = usage_bar(node['cpu'])
        ram_bar = usage_bar(node['mem'] / node['maxmem'])
        disk_bar = usage_bar(node['disk'] / node['maxdisk'])

        table.add_row(
            node['node'],
            status,
            str(node['maxcpu']),
            cpu_bar,
            f'{ram} GiB',
            ram_bar,
            disk_bar,
            str(timedelta(seconds=node['uptime'])),
        )

    console = Console()
    console.print(table)


@vm_mapping_cli.command('dump')
def mapping_dump(
    ctx: typer.Context,
    outfile: Annotated[typer.FileTextWrite, typer.Argument(help='JSON output filepath')],
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vms = proxmox_api.vm.list_()

    result = {vm['vmid']: vm['node'] for vm in vms}
    json.dump(result, outfile, indent=2)


@vm_mapping_cli.command('restore')
def mapping_restore(
    ctx: typer.Context,
    infile: Annotated[typer.FileText, typer.Argument(help='JSON input file (created with dump-vms')],
    verbose: Annotated[bool, typer.Option('--verbose', '-v', help='Verbose output')] = False,
    force: Annotated[bool, typer.Option('--force', '-f', help='Force VM migration')] = False,
) -> None:
    proxmox_api: Proxmox = ctx.obj['proxmox_api']
    vms = proxmox_api.vm.list_()
    nodes = ctx.obj['nodes']
    parallel_migrations = ctx.obj['parallel_migrations']

    mapping = json.load(infile)

    migration_vms: dict[str, list[dict]] = {node['node']: [] for node in nodes}
    for vm in vms:
        try:
            wanted_node = mapping[str(vm['vmid'])]
        except KeyError:
            continue

        if wanted_node == vm['node']:
            if verbose:
                rprint(spinner_col.finished_text, f'[green]✅ VM {vm["name"]} ({vm["vmid"]}) is on node {wanted_node}')
        else:
            migration_vms[wanted_node].append(vm)

    for dest_node, vms_to_migrate in migration_vms.items():
        if vms_to_migrate:
            with_local_disks = False
            for vm in vms_to_migrate:
                if 'do-not-migrate' in vm.get('tags', []) and not force:
                    rprint(
                        spinner_col.finished_text,
                        f'[red]❌ VM {vm["name"]} ({vm["vmid"]}) was not migrated because of "do-not-migrate" tag. '
                        f'Use --force to migrate anyways.',
                    )
                    vms_to_migrate.remove(vm)
                    continue

                migration_check_result = check_vm_migrate(proxmox_api=proxmox_api, dest_node=dest_node, vm=vm)
                if migration_check_result['local_disks']:
                    with_local_disks = True

            migrate_vms(
                api=proxmox_api,
                dest_node=dest_node,
                vmid_list=[vm['vmid'] for vm in vms_to_migrate],
                parallel_migrations=parallel_migrations,
                with_local_disks=with_local_disks,
            )
