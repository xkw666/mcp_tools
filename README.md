# MCP Tools

## MCP Transfer - Upload Code via SFTP
mcp_transfer.py 是一个基于 Python 的轻量级工具，通过 `sftp` 将代码上传到远程服务器上的指定位置。支持密钥登录或密码登录，支持自动创建远程目录。

### Prerequisites
- uv (Python package manager)

### QuickStart

#### Step1
Clone this repository
```
git clone https://github.com/xkw666/mcp_tools.git
```
#### Step2
set sftp config in `sftp_config.yaml`
```
your_server:
  host: xxxx
  port: xxxx
  username: xxx
  
  ## 两种连接方式 
  # password: xxxx
  key_file_path: C:/Users/usr/.ssh/id_rsa

  remote_path: /home/xxx/mcp
```

#### Step3
Usage with Claude Desktop (or others)
Add this to your `claude_desktop_config.json` (Example in windows):
```
{
  "mcpServers": {
      "transfer": {
        "command": "uv",
        "args": [
            "--directory",
            "C:\\Users\\user\\Desktop\\mcp_tools",
            "run",
            "mcp_transfer.py"
        ]
    }
  }
}
```