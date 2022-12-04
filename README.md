# ZJXW_ZLCY

🐛第N个脚本，完成浙里潮音。

## Usage

```zsh
git clone https://github.com/Mas0nShi/ZJXW_ZLCY
pip3 install r requirements.txt
python3 zjxw.py -h
```

首次启动请先生成配置文件

```shell
python3 zjxw.py -init
```

配置项说明：



```json
{
        // 以下配置项须自行抓包 
        "accounts": {
            "accountId": "", // 用户ID
            "nick_name": "", // 用户名称
            "headerImg": "", // 用户头像
            "deviceId": "",  // 设备标识
            "cookie": ""     // 用户Cookie
        },
        "systemPid": "",
        
        // 以下配置项为钉钉机器人
        "enableDingbot": False, // 开启机器人
        "dingbotWebhook": "",   // webhook (https://oapi.dingtalk.com/robot/send?access_token=*)
        "dingbotSecret": ""     // SEC*
    }
```

## Feature

- 点赞任务
