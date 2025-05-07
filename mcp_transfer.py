from mcp.server.fastmcp import FastMCP
import paramiko
from typing import Optional, Dict
import yaml
import os

def ensure_remote_dir(sftp, remote_dir: str):
    """Ensure that remote_dir exists on the server; create it if needed (recursive)."""
    dirs = []
    while remote_dir not in ('', '/', '.'):
        dirs.insert(0, remote_dir)
        remote_dir = os.path.dirname(remote_dir)

    for dir_path in dirs:
        try:
            sftp.stat(dir_path)
        except IOError:
            sftp.mkdir(dir_path)


mcp = FastMCP("transfer")
@mcp.tool()
def sftp_upload(file_name:str, code: str) -> Dict[str, str]:
    """Upload a Python code string to a remote server via SFTP.

    Args:
        file_name: Name of the target file to create on the remote server.
        code: Python source code as a string. The content will be directly written
              to the specified file on the remote server.

    Returns:
        A dictionary containing the upload status and a descriptive message.
    """
    ssh = None

    # === 读取配置文件并提取第一个主机配置 ===
    try:
        with open("sftp_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if not config or not isinstance(config, dict):
            return {"status": "error", "message": "Invalid config structure."}
        alias, cfg = next(iter(config.items()))  # 使用第一个配置
    except Exception as e:
        return {"status": "error", "message": f"Failed to read config file: {e}"}

    # === 提取参数 ===
    host = cfg["host"]
    port = cfg["port"]
    username = cfg["username"]
    remote_path = cfg["remote_path"]
    password = cfg.get("password")
    key_file_path = cfg.get("key_file_path")

    # === 建立 SSH 连接并写入远程文件 ===
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if key_file_path:
            key = paramiko.RSAKey.from_private_key_file(key_file_path)
            ssh.connect(hostname=host, port=port, username=username, pkey=key)
            login_type = "key-based"
        elif password:
            ssh.connect(hostname=host, port=port, username=username, password=password)
            login_type = "password"
        else:
            return {"status": "error", "message": "No login method provided in config."}

        with ssh.open_sftp() as sftp:
            ensure_remote_dir(sftp, remote_path)
            with sftp.open(f"{remote_path}/{file_name}", 'w') as remote_file:
                remote_file.write(code)

        message = f"[SFTP-{login_type}] Code written to {alias}: {remote_path}/{file_name}"
        print(message)
        return {"status": "success", "message": message}

    except paramiko.AuthenticationException:
        message = "[Error] Authentication failed. Check your credentials."
    except paramiko.SSHException as e:
        message = f"[Error] SSH error: {e}"
    except Exception as e:
        message = f"[Error] Unexpected error: {e}"
    finally:
        if ssh:
            try:
                ssh.close()
            except:
                pass

    print(message)
    return {"status": "error", "message": message}





if __name__ == "__main__":
    # Initialize and run the server
    # print("Starting mcp-transfer server...")
    # msg = sftp_upload(file_name="test.py", code="print('Hello, World!')")
    # print(msg)
    mcp.run(transport='stdio')

