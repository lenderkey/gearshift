#
#   commands/checksync.py
#   
#   David Janes
#   Gearshift
#   2023-03-24
#

from Context import Context

import click
import yaml
import sys

L = "dst-sync"

@cli.command("dst-sync", help="See if records have been synced") # type: ignore
@click.option("--dry-run/--no-dry-run", is_flag=True)
@click.option("--input",
              help="file to read from (YAML))", 
              default="-")
@click.option("--output",
                help="file to write to (YAML)", 
                default="-")
def dst_sync(dry_run:bool, input:str, output:str):
    context = Context.instance

    if input == "-":
        data = yaml.safe_load(sys.stdin)
    else:
        with open(input) as fp:
            data = yaml.safe_load(fp)

    nrecords = []
    for record in data.get("records", []):
        data_hash = record.get("data_hash")
        dst_name = record.get("filename")
        if not data_hash or not dst_name:
            continue

        if record.get("is_deleted"):
            pass
        else:
            if context.ingest_link(data_hash, dst_name):
                ## already downloaded and now linked
                continue

            nrecords.append(record)

    data["records"] = nrecords

    if output == "-":
        print(yaml.dump(data))
    else:
        with open(output, "w") as fp:
            yaml.dump(data, fp)
