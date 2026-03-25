# role-ssh-keys

Ansible role for comprehensive SSH key management, including host keys, user keys, authorized keys,
and known hosts.

## Description

This role provides a robust framework for managing all aspects of SSH key configuration across your
infrastructure. It handles the generation, installation, and management of SSH keys for both servers
and users, enabling secure and consistent SSH authentication throughout your environment.

Key capabilities include:

- Server host key management (creating, installing, and retrieving)
- User SSH key pair management
- Authorized keys configuration (controlling which users can access which servers)
- Known hosts management (controlling which servers are trusted by which users)
- Support for multiple key types (RSA, DSA, ECDSA, Ed25519)
- Flexible key sourcing (from files or variable content)

The role can automatically generate missing keys, install existing keys, and ensure proper
permissions and ownership for all SSH key files.

## Requirements

- **Supported distributions**:
  - CentOS/RedHat 6.0+
  - Debian 7.0+
  - Ubuntu 14.0+
- **SSH** server and client packages must be installed
- **Python** with proper support for the SSH key types you intend to use

## Role Variables

### Path Configuration

| Variable               | Default                           | Description                                      |
|------------------------|-----------------------------------|--------------------------------------------------|
| `ssh_config_path`      | `/etc/ssh`                        | Path to SSH server configuration                 |
| `ssh_keys_base`        | `../storage/ssh_keys`             | Base path for key storage in Ansible repository  |
| `ssh_external_keys_base` | `{{ ssh_keys_base }}/externals` | Path for external keys                           |
| `ssh_host_keys_base`   | `{{ ssh_keys_base }}/servers`     | Path for server host keys                        |
| `ssh_user_keys_base`   | `{{ ssh_keys_base }}/users`       | Path for user keys                               |

### File Paths

| Variable               | Default                      | Description                   |
|------------------------|------------------------------|-------------------------------|
| `ssh_authkeys_files`   | `['~/.ssh/authorized_keys']` | Path to authorized keys files |
| `ssh_identity_files`   | `['~/.ssh/id_rsa']`          | Path to user identity files   |
| `ssh_knownhosts_files` | `['~/.ssh/known_hosts']`     | Path to known hosts files     |

### Key Management

| Variable               | Default | Description                                      |
|------------------------|---------|--------------------------------------------------|
| `ssh_host_keys`        | `[]`    | List of SSH server keys to manage                |
| `ssh_user_keys`        | `[]`    | List of SSH user keys to manage                  |
| `ssh_authorized_keys`  | `[]`    | List of SSH keys to authorize for users          |
| `ssh_known_hosts`      | `[]`    | List of SSH server keys to trust                 |

## Host Keys Management

The `ssh_host_keys` variable defines the SSH server keys to be managed. These are the keys that
identify your SSH servers to clients.

Example:

```yaml
ssh_host_keys:
  # Generate or install an Ed25519 key
  - name: ssh_host_ed25519_key
    key_file: "{{ ssh_host_keys_base }}/ssh_host_ed25519_key"
    type: ed25519
    bits: 256

  # Install keys from variable content (useful with Ansible Vault)
  - name: ssh_host_rsa_key
    key_content:
      private: "{{ vault_ssh_host_rsa_private_key }}"
      public: "ssh-rsa AAAAB3NzaC1yc2EAAA..."
```

Options for host keys:

- `name`: Name of the key (typically matches the basename of the key file)
- `state`: 'present' (default) or 'absent'
- `key_file`: Path to the key file in the Ansible repository
- `key_content`: Dictionary containing 'private' and 'public' key content
- `type`: Key type (rsa, dsa, ecdsa, ed25519)
- `bits`: Key size in bits
- `passphrase`: Optional passphrase for the key
- `ignore_present`: Whether to overwrite existing keys

## User Keys Management

The `ssh_user_keys` variable defines SSH keys for users (clients). These are the keys that users use
to authenticate to SSH servers.

Example:

```yaml
ssh_user_keys:
  # Create or install a key pair for user1
  - username: user1
    state: present
    key_file: "{{ ssh_user_keys_base }}/user1_key"
    target_file: "{{ ssh_identity_files | first }}"
    type: rsa
    bits: 4096

  # Force creation of a new key, overwriting any existing key
  - username: user2
    state: present
    key_file: "{{ ssh_user_keys_base }}/user2_key"
    target_file: "{{ ssh_identity_files | first }}"
    ignore_present: yes

  # Install keys from variable content (useful with Ansible Vault)
  - username: user3
    state: present
    key_content:
      private: "{{ vault_user3_private_key }}"
      public: "ssh-ed25519 AAAAC3NzaC1lZ..."
```

Options for user keys:

- `username`: User that owns the key
- `state`: 'present' (default) or 'absent'
- `key_file`: Path to the key file in the Ansible repository
- `key_content`: Dictionary containing 'private' and 'public' key content
- `target_file`: Where to install the key on the target system
- `type`: Key type (rsa, dsa, ecdsa, ed25519)
- `bits`: Key size in bits
- `passphrase`: Optional passphrase for the key
- `ignore_present`: Whether to overwrite existing keys

## Authorized Keys Management

The `ssh_authorized_keys` variable defines which user keys are authorized to access SSH servers.

Example:

```yaml
ssh_authorized_keys:
  # Allow user1's key on the server
  - username: user1
    state: present
    key_file: "{{ ssh_user_keys_base }}/user1.pub"

  # Allow user2's key with specific options
  - username: user2
    key_options: "no-port-forwarding,no-X11-forwarding"
    key_file: "{{ ssh_user_keys_base }}/user2.pub"
    authkeys_file: "/etc/ssh/authorized_keys/global_keys"

  # Authorize a key specified as content
  - username: user3
    state: present
    key_content: "ssh-rsa AAAAB3NzaC1yc2EAAA..."
```

Options for authorized keys:

- `username`: User to authorize the key for
- `state`: 'present' (default) or 'absent'
- `key_file`: Path to the public key file in the Ansible repository
- `key_content`: Public key content as a string
- `key_options`: SSH options for the authorized key
- `authkeys_file`: Custom path to the authorized_keys file

## Known Hosts Management

The `ssh_known_hosts` variable defines which server keys are trusted by users.

Example:

```yaml
ssh_known_hosts:
  # Configure known hosts for user1
  - username: user1
    target_file: "{{ ssh_knownhosts_files | first }}"
    hosts:
      # Trust server1 using a key from the repository
      - name: server1.example.com
        state: present
        key_file: "{{ ssh_host_keys_base }}/server1.pub"

      # Trust server2 using key content
      - name: server2.example.com
        state: present
        key_content: "ssh-ed25519 AAAAC3NzaC1lZ..."
```

Options for known hosts:

- `username`: User to configure known hosts for
- `target_file`: Path to the known_hosts file
- `hosts`: List of host entries to manage, each containing:
  - `name`: Hostname or IP address
  - `state`: 'present' (default) or 'absent'
  - `key_file`: Path to the public key file in the Ansible repository
  - `key_content`: Public key content as a string

## Example Playbook

Here is a comprehensive example showing the role's capabilities:

```yaml
- hosts: servers
  roles:
    - role: ssh-keys
      ssh_host_keys:
        - name: ssh_host_ed25519_key
          key_file: "{{ ssh_host_keys_base }}/{{ inventory_hostname }}_ed25519_key"
          type: ed25519
        - name: ssh_host_rsa_key
          key_file: "{{ ssh_host_keys_base }}/{{ inventory_hostname }}_rsa_key"
          type: rsa
          bits: 4096

      ssh_user_keys:
        - username: admin
          key_file: "{{ ssh_user_keys_base }}/admin_ed25519"
          type: ed25519
        - username: devops
          key_file: "{{ ssh_user_keys_base }}/devops_rsa"
          type: rsa
          bits: 4096

      ssh_authorized_keys:
        - username: admin
          key_file: "{{ ssh_user_keys_base }}/admin_ed25519.pub"
        - username: devops
          key_file: "{{ ssh_user_keys_base }}/devops_rsa.pub"
        - username: ci
          key_content: "{{ lookup('file', 'ci_deploy_key.pub') }}"
          key_options: "command=\"/usr/bin/deploy-only\",no-port-forwarding"

      ssh_known_hosts:
        - username: admin
          hosts:
            - name: "*.{{ domain_name }}"
              key_file: "{{ ssh_host_keys_base }}/wildcard_{{ domain_name }}.pub"
```

## Advanced Usage

### Using Ansible Vault for Key Protection

For enhanced security, you can store private keys in Ansible Vault:

```yaml
# In a vault-encrypted file:
vault_ssh_host_rsa_private_key: |
  -----BEGIN RSA PRIVATE KEY-----
  MIIEogIBAAKCAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzI
  ...
  -----END RSA PRIVATE KEY-----

# In your playbook:
ssh_host_keys:
  - name: ssh_host_rsa_key
    key_content:
      private: "{{ vault_ssh_host_rsa_private_key }}"
      public: "ssh-rsa AAAAB3NzaC1yc2EAAA..."
```

### Generating Keys With Passphrase Protection

You can generate keys with passphrase protection:

```yaml
ssh_user_keys:
  - username: secure_user
    key_file: "{{ ssh_user_keys_base }}/secure_user_key"
    type: rsa
    bits: 4096
    passphrase: "{{ vault_secure_user_passphrase }}"
```

### Custom SSH Key Options

For more controlled SSH access, you can use custom options in authorized keys:

```yaml
ssh_authorized_keys:
  - username: restricted_user
    key_file: "{{ ssh_user_keys_base }}/restricted_user.pub"
    key_options: "from=\"10.0.0.0/8\",no-agent-forwarding,no-X11-forwarding"
```

## Security Considerations

- **Private Key Protection**: Always encrypt private keys stored in repositories using Ansible Vault
- **Key Rotation**: Establish policies for regular key rotation
- **Passphrase Use**: Consider using passphrases for critical user keys
- **Key Size**: Use appropriate key sizes (RSA: 4096+ bits, Ed25519 recommended when supported)
- **Least Privilege**: Apply restrictive SSH options when necessary
- **Audit Trail**: Keep records of key creation, distribution, and access

## Troubleshooting

Common issues and solutions:

1. **Keys Not Being Generated**:
   - Check file permissions in the target directories
   - Ensure the SSH key type is supported by the version of OpenSSH on the target system
   - Verify that required Python modules are installed

2. **Permission Issues**:
   - Ensure the role has sufficient privileges to write to SSH configuration directories
   - Check SELinux contexts if running on a system with SELinux enabled

3. **Key Not Working for Authentication**:
   - Verify key permissions (private keys should be 600, public keys 644)
   - Check that the key is properly added to the authorized_keys file
   - Ensure the proper key type is being used (some older systems don't support newer key types)

4. **Known Hosts Issues**:
   - If a host's IP changes, the key may need to be updated in known_hosts
   - Format issues in known_hosts can cause authentication failures

## License

MIT

## Author Information

Fabrizio Colonna (@ColOfAbRiX)

## Contributors

Issues, feature requests, ideas, suggestions, etc. are appreciated and can be posted in the Issues
section.

Pull requests are also very welcome. Please create a topic branch for your proposed changes. If you
don't, this will create conflicts in your fork after the merge.
