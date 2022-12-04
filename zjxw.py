"""
License: MIT
Date: 2022/11/23 15:45
"""
import json
from os import path
from argparse import ArgumentParser
from loneanswer import LoneAnswer



def loadConfig():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            temp = json.load(f)
        # test config file is complete or not.
        # if complete, return config dict.
        # if not complete, print "invalid config file, please check it." and exit.
        assert temp.keys() >= {"accounts", "systemPid", "enableDingbot", "dingbotWebhook", "dingbotSecret"}, "invalid config file, please check it."
        assert all(temp.values()), "invalid config file, please check it."
        return temp
    except FileNotFoundError:
        # print en i81n tips.
        print("Not found config file, please run -init to init program and fill config file.")
        exit(0)


def saveConfig(config: dict) -> bool:
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=True, indent=4)
    return True


def generateConfig():
    # generate config file.
    # config file is a json file, it's content is like this:
    # {
    #     "accounts": {
    #             "accountId": "",
    #             "nick_name": "",
    #             "headerImg": "",
    #             "deviceId": "",
    #             "cookie": ""
    #     }
    #     "systemPid": "the activity pid",
    #     "enableDingbot": False,
    #     "dingbotWebhook": "",
    #     "dingbotSecret": ""
    # }
    config = {
        "accounts": {
            "accountId": "",
            "nick_name": "",
            "headerImg": "",
            "deviceId": "",
            "cookie": ""
        },
        "systemPid": "",
        "enableDingbot": False,
        "dingbotWebhook": "",
        "dingbotSecret": ""
    }
    assert saveConfig(config) is True, "Save config file failed."
    print(f"the config file path: {path.join(path.dirname(__file__), 'config.json')}")



if __name__ == '__main__':
    parser = ArgumentParser()
    
    # init program, call generateConfig function.
    parser.add_argument("-init", action="store_true", help="init program")
    # single task, call LoneAnswer class.
    parser.add_argument("-art", action="store_true", help="article task")
    parser.add_argument("-ans", action="store_true", help="answer task")

    args = parser.parse_args()

    if args.init:
        generateConfig()
        exit(0)

    # load config file, call loadConfig function.
    config = loadConfig()
    
    # init LoneAnswer class.
    la = LoneAnswer(account=config["accounts"], rawPid=config["systemPid"])
    if config["enableDingbot"]:
        la.enable_dingbot(config["dingbotWebhook"], config["dingbotSecret"])
    # run program.
    if (args.art and args.ans) or (not args.art and not args.ans):
        la.run()
    elif args.art:
        # todo: article task need cookie (strict).
        # la.article_task()
        print('Not implemented yet.')
    elif args.ans:
        la.answer_task()
    else:
        parser.print_help()
