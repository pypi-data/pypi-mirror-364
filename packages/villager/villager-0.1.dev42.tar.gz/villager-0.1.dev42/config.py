from scheduler.agentManager import AgentModel

Master = {
    "openai_api_key": "sk-3eadaad0b22447db981dcfa3dbd33c23",
    "openai_api_endpoint": "https://api.deepseek.com",
    "default_model": "deepseek-chat",
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
