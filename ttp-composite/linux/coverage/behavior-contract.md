# Shared Linux composite behavior contract

Every language implements the same case IDs and exact target rules in
`manifest.json`. A port may change language/library APIs; it must preserve the
operation, fixture inputs, and independently checked outcome below. A valid
no-alert outcome does not authorize changing the rule or substituting another
behavior to obtain an alert. Additional matches are retained separately.

Every case is a standalone program. Its `--control` mode skips only its tested
behavior. Setup completes before capture, and a fresh isolated container is
used for each execution. The payload is exactly `telemetry-lab-fixture\n`.
All networking stays within that container's network namespace. The helper at
`/opt/coverage/helper` is the same static binary for every configuration and
prints `HELPER_OK\n`. No persistence fixture is activated.

| Case | Operation and fixed inputs | Required outcome |
| --- | --- | --- |
| traversal_read | Read `/tmp/lab/../../etc/shadow`, preserving the traversal path | Exact payload read |
| sensitive_read | Read `/etc/shadow` | Exact payload read |
| log_truncate | Open `/var/log/lab.log` for writing with truncation | Existing file becomes empty |
| sensitive_symlink | Link `/tmp/lab/link` to `/etc/shadow` | Target verified; link removed |
| sensitive_hardlink | Link `/etc/shadow` at `/tmp/lab/hard` | Same inode/device verified; link removed |
| packet_socket | Open AF_PACKET/SOCK_RAW with ETH_P_ALL | Socket opens and closes; no capture |
| reverse_shell | Loopback TCP `127.0.0.1:4444`; `/bin/sh` executes `printf 'SHELL_OK\n'; exit` | `SHELL_OK\n` returned over connection; shell exits successfully |
| ptrace_attach | Attach to and detach from own disposable, live child | Trace stop verified; child terminated by SIGTERM and reaped |
| ptrace_traceme | Child requests PTRACE_TRACEME | Request succeeds; child exits successfully and is reaped |
| exec_shm | Copy fixed helper to `/dev/shm/lab-helper` and execute | Exact helper output; successful child completion |
| drop_execute | Copy fixed helper to `/tmp/lab-helper` and execute | Exact helper output; successful child completion |
| memfd_execute | Copy fixed helper into memfd `lab-helper` and execute it | Exact helper output; successful child completion |
| shell_config_write | Write payload to `/root/.bashrc` | Expected file size |
| cron_write | Write payload to `/etc/cron.d/lab_fixture` | Expected file size |
| ssh_read | Read `/root/.ssh/lab_key` | Exact payload read |
| udp_exchange | Connected UDP send to private peer `198.18.0.1:44445` | Peer receives exact payload |
| dev_file | Write payload to `/dev/lab_fixture` | Expected file size |
| metadata_ec2 | TCP exchange with private emulator `169.254.169.254:80` | Exact payload sent and echoed |
| metadata_cloud | Same private metadata exchange; score its distinct mapped rule | Exact payload sent and echoed |
| history_truncate | Open `/root/.bash_history` for writing with truncation | Existing file becomes empty |
| setid_mode | Write `/tmp/lab/mode`; set permissions to 0600 plus setuid | Setuid bit verified; file never executed |
| proc_environ | Read `/proc/self/environ` | Contains `TELEMETRY_LAB_FIXTURE=1` |
| authorized_keys | Write payload to `/root/.ssh/authorized_keys` | Expected file size |
| repository_write | Write payload to `/etc/apt/sources.list.d/lab.list` | Expected file size; no package update |
| binary_write | Write payload to `/usr/bin/lab_fixture` | Expected file size; file never executed |
| monitored_write | Write payload to `/boot/lab_fixture` | Expected file size |
| etc_write | Write payload to `/etc/lab_fixture` | Expected file size |
| root_write | Write payload to `/root/lab_fixture` | Expected file size |
| binary_rename | Rename `/usr/bin/lab_old` to `/usr/bin/lab_new` | Old name absent; exact payload at new name |
| binary_mkdir | Create `/usr/bin/lab_directory` with mode 0700 | Directory verified and removed |

New regular payload files have mode 0600; executable helper copies have mode
0700. Disposable-container removal cleans up any fixtures not explicitly
removed by a program. Success checks and language runtime startup also emit
telemetry; they are part of the measured implementation.

Equivalent behavior does not require identical syscalls. For example, Go may
relay shell I/O through pipes, copy files via kernel-assisted APIs, execute a
memfd through procfs, or launch a child instead of using a bare fork. These
choices must be documented, held constant between configurations of the same
language, and considered before attributing a difference to runtime alone.

This is the Linux contract. Windows will need explicit platform-equivalent
operations and a separately frozen detector mapping; Linux paths and Falco
rule names must not be presented as Windows coverage.
