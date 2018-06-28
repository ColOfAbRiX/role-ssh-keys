# role-ssh-keys

Ansible role to install and configure Sudo and Sudo-LDAP.

The role is fully generic and supports all the Sudo settings plus some more behaviours. It also supports the configuration of SUDO-LDAP, to integrate SUDO with any LDAP system and store the configuration in one central place.

The role is configured to create the default OS configuration.

## Requirements

The role requires RHEL/CentOS 7 to work.

## Role Variables

The variables are fully documented in the [default configuration](defaults/main.yml) file, including their default values and some examples. This file contains all the settings that can be configured.

Please refer to the default configuration file for the full list and use Linux man pages if you need more information on Sudo.

| Variable               | Default                 | Description                                  |
| :---                   | :---                    | :---                                         |
| `sudo_safety_state`    | `present`               | If 'present' it will create a safety system that replaces wrong sudo files. |
| `sudo_safe_file`       | `/etc/sudo-safe.tar.gz` | Name of the backup file.                     |
| `sudoers_host_aliases` | `[]`                    | Host aliases to add into /etc/sudoers.       |
| `sudoers_user_aliases` | `[]`                    | User aliases to add into /etc/sudoers.       |
| `sudoers_cmnd_aliases` | `...`                   | Command aliases to add into /etc/sudoers.    |
| `sudoers_defaults`     | `...`                   | Defaults to add into /etc/sudoers.           |
| `sudoers_entries`      | `...`                   | The custom entries to put into /etc/sudoers. |
| `sudoers_sudoers_d`    | `[]`                    | Custom files into /etc/sudoers.d.            |

## Example Playbook

Using the role without any specific configuration is very simple:

```Yaml
- hosts: servers
  roles:
   - role: sudo
```

## License

MIT

## Author Information

[Fabrizio Colonna](colofabrix@tin.it)

## Contributors

Pull requests are also very welcome. Please create a topic branch for your proposed changes. If you don't, this will create conflicts in your fork after the merge.
