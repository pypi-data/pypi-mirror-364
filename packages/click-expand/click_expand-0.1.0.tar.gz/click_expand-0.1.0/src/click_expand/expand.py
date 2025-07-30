# stdlib imports
from pathlib import Path

def clean_name(name):
  return name.replace('-', '_')

#########################################################################
# Group Template ########################################################
#########################################################################

GROUP_DEF = '''@{parent_group}.group(name="{group}")
def {full_group_name}():
  """{desc}"""
  pass
'''

def print_group_def(desc, parent_group, group, full_group_name):
  if not parent_group:
    parent_group = 'click'

  parent_group = clean_name(parent_group)
  full_group_name = clean_name(full_group_name)

  print(GROUP_DEF.format(desc=desc, parent_group=parent_group, group=group, full_group_name=full_group_name))

#########################################################################
# Command Template ######################################################
#########################################################################

COMMAND = '''@{group}.command(name="{name}")
def {cmdname}():
  """{desc}"""
  raise NotImplementedError()
'''

def print_command(desc, group, cmdname):
  name = cmdname

  cmdname = clean_name(cmdname)

  print(COMMAND.format(desc=desc, group=group, cmdname=cmdname, name=name))

#########################################################################

def process_file(filepath: str):
  path = Path(filepath)

  if not path.exists():
    raise FileNotFoundError(filepath)

  if not path.is_file():
    raise ValueError(f'Not a file: {filepath}')

  seen_groups = set()

  with open(path) as f:
    for line in f:
      # Just passthrough non-click-expand lines
      if not line.startswith('# click-expand:'):
        print(line, end='')
        continue

      # Handle click-expand lines
      _, _, argsline = line.partition(':')
      argsline = argsline.strip()

      # Get the description
      desc = "### TODO: Add a description for this command"
      if argsline.endswith('"'):

        # Trim off the ending quote
        argsline = argsline[:-1]

        argsline, sep, desc = argsline.rpartition('"')
        if not sep:
          # Invalid line, just print the original line
          print(line, end='')
          continue

      # TODO: Get Options and Args

      # Split on whitespace
      args = argsline.split()
      num_args = len(args)

      if num_args == 0:
        # Invalid line, just print the original line
        print(line, end='')
        continue

      groups = args[:-1]
      cmd = args[-1]

      if cmd.startswith('@'):
        # This is a group
        groups.append(cmd[1:])
        cmd = None

      group_tree = []
      for group in groups:
        parent_group = '_'.join(group_tree)

        group_tree.append(group)
        full_group_name = '_'.join(group_tree)

        if full_group_name not in seen_groups:
          seen_groups.add(full_group_name)
          print(f'# From: {line[1:-1].strip()}')
          print_group_def(desc, parent_group, group, full_group_name)

      if cmd:
        parent_group = '_'.join(group_tree)
        print(f'# From: {line[1:-1].strip()}')
        print_command(desc, parent_group, cmd)
