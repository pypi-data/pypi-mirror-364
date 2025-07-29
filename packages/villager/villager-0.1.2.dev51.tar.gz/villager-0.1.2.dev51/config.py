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
        "base_url": "http://10.10.3.119:25989",
        "mcp_url": "http://10.10.3.119:1611/mcp",
    },
    "server":{
        "kali_driver": "http://10.10.3.119:1611/mcp",
        "browser_use": "http://10.10.3.208:8080/mcp",
    }
}
