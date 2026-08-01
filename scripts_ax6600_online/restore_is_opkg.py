import paramiko
import time

host = "192.168.10.1"
port = 22
username = "root"
password = "HZ1314526.com"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=username, password=password, timeout=10)

print("=== 1. Ensuring /usr/libexec/taskd has no 'script' dependency ===")
taskd_content = """#!/bin/sh
TASK_ID="$1"
TASK_CMD="$2"

exec </dev/null >>"/var/log/tasks/$TASK_ID.log" 2>&1

export HOME=/root
export TERM=xterm-256color

onexit() {
    exit_code=$?
    /etc/init.d/tasks _task_onstop "$TASK_ID" "$exit_code"
}
trap 'onexit' EXIT

sh -c "$TASK_CMD"
"""

client.exec_command(f"cat << 'EOF' > /usr/libexec/taskd\n{taskd_content}\nEOF\nchmod 755 /usr/libexec/taskd /etc/init.d/tasks")

print("=== 2. Testing Task Execution for iStore DDNSTO Installation ===")
# 模拟 iStore 网页点击按钮触发命令
test_cmd = "/etc/init.d/tasks task_add 'test_ddnsto' 'is-opkg install app-meta-ddnsto' 300"
stdin, stdout, stderr = client.exec_command(test_cmd)
print("task_add result:", stdout.read().decode('utf-8'), stderr.read().decode('utf-8'))

time.sleep(3)

# 查看生成的任务日志
stdin, stdout, stderr = client.exec_command("cat /var/log/tasks/test_ddnsto.log 2>/dev/null; /etc/init.d/tasks status")
print("\n=== Task Log Output ===")
print(stdout.read().decode('utf-8'))

client.close()
