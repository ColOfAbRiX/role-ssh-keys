#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Fabrizio Colonna <colofabrix@tin.it>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import tempfile
from ansible.module_utils.basic import *


DOCUMENTATION = '''
---
author:
 - "Fabrizio Colonna (@ColOfAbRiX)"
module: ssh_keygen
short_description: Generate SSH Keys
version_added: "2.3"
description: Generates SSH keys using the system command ssh-keygen.
options:
  bits:
    description: Specifies the number of bits in the key to create.
    default: 1024
  comment:
    description: Provides a new comment.
    default: ""
  force:
    description: If set to C(true) overwrite existing keys.
    default: false
  new_format:
    description:
      Causes ssh-keygen to save SSH protocol 2 private keys using the new
      OpenSSH format rather than the more compatible PEM format.
    default: fase
  options:
    description: A list of option when signing a key.
    default: []
  passphrase:
    description: Provides the passphrase.
    default: ""
  path:
    description:
      Path and name of the keys. The public key will add ".pub" to this name.
    required: yes
  rounds:
    description:
      When saving a new-format private key, this option specifies the number of
      key derivation function rounds used.
  type:
    description:
      Specifies the type of key to create.
    choices: ['rsa1', 'dsa', 'ecdsa', 'ed25519', 'rsa']
    default: rsa
'''


def exit_fail(**kwargs):
    global module, tmp_path
    if tmp_path is not None and os.path.isdir(tmp_path):
        shutil.rmtree(tmp_path)
    module.fail_json(**kwargs)


def exit_success(**kwargs):
    global module, tmp_path
    if tmp_path is not None and os.path.isdir(tmp_path):
        shutil.rmtree(tmp_path)
    module.exit_json(**kwargs)


def main():
    global module, tmp_path

    module = AnsibleModule(
        argument_spec={
            'bits': {'type': 'int', 'default': 1024},
            'comment': {'type': 'str', 'default': ""},
            'force': {'type': 'bool', 'default': False},
            'new_format': {'type': 'bool', 'default': False},
            'options': {'type': 'list', 'default': []},
            'passphrase': {'type': 'str', 'default': ''},
            'path': {'type': 'str', 'required': True},
            'rounds': {'type': 'int'},
            'type': {
                'type': 'str',
                'choices': ['rsa1', 'dsa', 'ecdsa', 'ed25519', 'rsa'],
                'default': 'rsa'
            }
        },
        supports_check_mode=True
    )

    module.run_command_environ_update = {'LANG': 'C'}

    path_key = module.params['path']
    path_key = os.path.expanduser(path_key)
    path_key = os.path.abspath(path_key)

    cmd = [module.get_bin_path('ssh-keygen', True)]

    # Set command options
    if module.params['bits']:
        cmd.extend(['-b', str(module.params['bits'])])
    cmd.extend(['-C', module.params['comment']])
    if module.params['new_format']:
        cmd.append('-o')
    for option in module.params['options']:
        cmd.extend(['-O', option])
    cmd.extend(['-N', module.params['passphrase']])
    if module.params['rounds']:
        cmd.extend(['-a', str(module.params['rounds'])])
    cmd.extend(['-t', module.params['type']])

    # Keys are created in a temporary directory
    tmp_path = tempfile.mkdtemp(prefix='tmp')
    tmp_key = os.path.join(tmp_path, "ssh_key")
    cmd.extend(['-f', tmp_key])

    # Check for existing keys and check mode
    if os.path.isfile(path_key):
        if not module.params['force']:
            exit_success(changed=False)
        if module.check_mode:
            exit_success(changed=True)
    elif module.check_mode:
        exit_success(changed=False)

    # Create keys
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        exit_fail(msg="Failed to generate ssh key.",
                  rc=rc, out=out, err=err, cmd=cmd)

    # Move the keys to the right place
    try:
        module.atomic_move(tmp_key, path_key)
        module.atomic_move(tmp_key + ".pub", path_key + ".pub")
    except:
        e = get_exception()
        exit_fail(msg=e)

    exit_success(changed=True)

if __name__ == '__main__':
    module = None
    tmp_path = None

    main()
