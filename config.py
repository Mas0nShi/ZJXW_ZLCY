# -*- coding:utf-8 -*-
"""
@Author: Mas0n
@File: config.py
@Time: 2022/11/23 10:21
@Desc: It's all about getting better.
"""
USER_AGENT = "Mozilla/5.0 (Linux; Android 12; RMX3350 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36; ; zjxw; 9.1.3; 00000000-67f6-d122-ffff-ffffe7284c73; RMX3350 20,9; Android; 12; zh; oppo Edg/107.0.0.0"
ENTRY_URL = "https://api-new.8531.cn/api/article/discovery_list"
API_LOGIN = "https://passport.8531.cn/web/oauth/credential_auth"


class API1:
    _API_CPLOGIN = "https://ser-html5.8531.cn/app/?m=api&subm=user&action=cplogin&pid={systemPid}"
    _API_START_ANSWER = "https://ser-html5.8531.cn/app/?m=api&action=startanswer&truesubm=answer&subm=loneanswer&pid={systemPid}"
    _API_SUBMIT_ANSWER = "https://ser-html5.8531.cn/app/?m=api&subm=loneanswer&truesubm=answer&action=submitallanswer&pid={systemPid}"

    def __init__(self, systemPid: str):
        self._API_START_ANSWER = self._API_START_ANSWER.format(systemPid=systemPid)
        self._API_SUBMIT_ANSWER = self._API_SUBMIT_ANSWER.format(systemPid=systemPid)
        self._API_CPLOGIN = self._API_CPLOGIN.format(systemPid=systemPid)

    @property
    def API_START_ANSWER(self): return self._API_START_ANSWER
    @property
    def API_SUBMIT_ANSWER(self): return self._API_SUBMIT_ANSWER
    @property
    def API_CPLOGIN(self): return self._API_CPLOGIN

class API2:
    _API2_CPLOGIN = "https://ser-html5.8531.cn/app/?m=api&subm=user&action=cplogin&pid={rawPid}"
    _API2_INIT = "https://ser-html5.8531.cn/app/?m=api&subm=zjqnxj&pid={rawPid}&action=init"
    _API2_LOTTERY = "https://ser-html5.8531.cn/app/?m=api&subm=zjqnxj&action=dolottery&truesubm=lottery&pid={rawPid}"
    _API2_ARTICLE_ACTION_SIGN = "https://ser-html5.8531.cn/app/?m=api&subm=zjqnxj&pid={rawPid}&action=articleactionsign"
    _API2_ARTICLE = "https://ser-html5.8531.cn/app/?m=api&subm=zjqnxj&pid={rawPid}&action=article"
    _API2_GET_ARTICLE_LIST = "https://ser-html5.8531.cn/app/?m=api&subm=zjqnxj&pid={rawPid}&action=getarticlelist"

    def __init__(self, rawPid: str):
        self._API2_CPLOGIN = self._API2_CPLOGIN.format(rawPid=rawPid)
        self._API2_INIT = self._API2_INIT.format(rawPid=rawPid)
        self._API2_LOTTERY = self._API2_LOTTERY.format(rawPid=rawPid)
        self._API2_ARTICLE_ACTION_SIGN = self._API2_ARTICLE_ACTION_SIGN.format(rawPid=rawPid)
        self._API2_ARTICLE = self._API2_ARTICLE.format(rawPid=rawPid)
        self._API2_GET_ARTICLE_LIST = self._API2_GET_ARTICLE_LIST.format(rawPid=rawPid)

    @property
    def API2_CPLOGIN(self): return self._API2_CPLOGIN
    @property
    def API2_INIT(self): return self._API2_INIT
    @property
    def API2_LOTTERY(self): return self._API2_LOTTERY
    @property
    def API2_ARTICLE_ACTION_SIGN(self): return self._API2_ARTICLE_ACTION_SIGN
    @property
    def API2_ARTICLE(self): return self._API2_ARTICLE
    @property
    def API2_GET_ARTICLE_LIST(self): return self._API2_GET_ARTICLE_LIST