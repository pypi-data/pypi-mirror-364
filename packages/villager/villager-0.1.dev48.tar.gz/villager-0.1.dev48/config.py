from scheduler.agentManager import AgentModel

Master = {
    "openai_api_key": "sk-RpXOjFy0W4ojjGl51jLOpKJTcdf9EEwLRsfhcgkufioHNNXQ",
    "openai_api_endpoint": "https://api.gptgod.online/v1",
    "default_model": "deepseek-v3-250324",
    "prefix": "",
    "misc": {
        "shell_encode": "gbk"
    }
}

MCP = {
    "client":{
        "base_url": "http://127.0.0.1:25989",
        "mcp_url": "http://127.0.0.1:1611/mcp",
    },
    "server":{
        "kali_driver": "http://127.0.0.1:1611/mcp",
        "browser_use": "http://127.0.0.1:8080/mcp",
    }
}
