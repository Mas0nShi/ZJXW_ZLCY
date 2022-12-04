# -*- coding:utf-8 -*-
"""
@Author: Mas0n
@File: loneanswer.py
@Time: 2022/11/23 11:06
@Desc: It's all about getting better.
"""
import json
import re
import time
from uuid import uuid4
from loguru import logger
from urllib3 import encode_multipart_formdata
from urllib.parse import urlencode
from random import sample as rand_sample, randint, randbytes
from string import ascii_letters, digits
from Crypto.Hash import SHA256
from requests import session, Session, sessions, get as requests_get
from config import USER_AGENT, API1, API2, ENTRY_URL
from dingtalkchatbot import chatbot

RAND_LETTER = ascii_letters + digits
del ascii_letters, digits


class LoneAnswer:
    account: dict
    http: Session
    log: logger
    bot: chatbot.DingtalkChatbot | None
    api: API1
    iApi: API2
    study_season_id: int
    is_answer: bool
    

    def __init__(self, account: dict, rawPid: str):
        assert account.keys() >= {'accountId', 'headerImg', 'nick_name', 'deviceId', 'cookie'}, 'Your Info is not complete'
        # value cannot be empty.
        assert all(account.values()), 'Your Info is not complete'
        self.account = account
        self.http = session()
        # self.http.verify = False
        self.http.headers = {"User-Agent": USER_AGENT}
        self.http.cookies = sessions.cookiejar_from_dict({"PHPSESSID": self.account['cookie']})
        self.log = logger
        self.log.add("loneanswer.log", rotation="100 MB", encoding="utf-8")

        self.iApi = API2(rawPid=rawPid)
        status, message = self.get_system_pid(rawPid=rawPid)
        if not status: raise Exception(message)
        self.log.debug(message)
        
        self.is_answer = True if message['is_answer'] == 1 else False
        self.study_season_id = message['study_season_id']
        self.api = API1(systemPid=message['systemPid'])

    @logger.catch
    def _refresh_web_login(self) -> bool:
        # generate timestamp.
        timestamp = int(time.time() * 1000)
        uniqueId = randbytes(12).hex()  # length: 24
        accountId = self.account['accountId']
        headerImg = self.account['headerImg']
        nickName = self.account['nick_name']
        deviceId = self.account['deviceId']
        signature = SHA256.new(f"{deviceId}&&{timestamp}&&MJ<?TH4&9w^".encode()).hexdigest()

        body = urlencode({
            "uniqueId": uniqueId,
            "accountId": accountId,
            "headerImg": headerImg,
            "nickName": nickName,
            "deviceId": deviceId,
            "signature": signature,
            "timestamp": timestamp,
        })
        # need to select pid when refresh cookie.
        url = self.iApi.API2_CPLOGIN if not getattr(self, "api", False) else self.api.API_CPLOGIN
        req = self.http.post(url=url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
        params = req.json()
        self.log.debug(params)
        if params['code'] != 3001:
            self.try_send_message(f"刷新登录状态出错了，请自行检查错误")
            return False
        return True

    @logger.catch
    def enable_dingbot(self, webhook: str, secret: str):
        self.bot = chatbot.DingtalkChatbot(webhook, secret)
        return 1

    @logger.catch
    def try_send_message(self, msg: str):
        if getattr(self, "bot", False):
            self.bot.send_text(msg=msg)
        return 1

    def get_system_pid(self, rawPid: str, recurse=0) -> (bool, dict):
        if recurse > 3:
            self.try_send_message('GG了，自行检查')
            self.log.error('Max recursion reached, plz check your code.')
            return 0, {}
        req = self.http.get(url=self.iApi.API2_INIT.format(rawPid=rawPid))
        if req.headers['Content-Type'] == 'text/html; charset=utf-8':
            # self.try_send_message('cookie失效了，尝试刷新')
            self.log.error('cookie expired, try to refresh.')

            if self._refresh_web_login():
                self.log.success('cookie refreshed.')
                # self.try_send_message('cookie刷新成功')
                return self.get_system_pid(rawPid, recurse=recurse+1)
            return 0, req.text

        params = req.json()
        self.log.debug(params)
        if params['code'] != 3001:
            self.log.error('Fail to get systemPid.')
            self.try_send_message(f"获取任务Pid失败，请自行检查错误")
            return 0, params['msg']
        return 1, {
            'systemPid': re.match(r".*?pid=(.*)", params['data']['answer']['jump_url']).group(1),
            'study_season_id': params['data']['answer']['study_season_id'],
            'is_answer': params['data']['answer']['is_answer'],
        }

    @logger.catch
    def start_answer(self, recurse: int = 0) -> (bool, dict):

        if recurse > 3:
            self.try_send_message('GG了，自行检查')
            self.log.error('Max recursion reached, plz check your code.')
            return 0, {}
        req = self.http.get(url=self.api.API_START_ANSWER)
        if req.headers['Content-Type'] == 'text/html; charset=utf-8':
            # self.try_send_message('cookie失效了，尝试刷新')
            self.log.error('cookie expired, try to refresh.')

            if self._refresh_web_login():
                self.log.success('cookie refreshed.')
                # self.try_send_message('cookie刷新成功')
                return self.start_answer(recurse=recurse+1)
            return 0, req.text

        params = req.json()
        self.log.debug(params)
        if params['msg'] != 'ok':
            self.try_send_message(f"出错了: {params['msg']}")
            self.log.error('Fail to start answer: %s' % params['msg'])
            return 0, params['msg']
        # TODO: optional.
        self.try_send_message(self._visual_answer(params))
        # self.log.info(self._visual_answer(params))
        return 1, params

    @logger.catch
    def _visual_answer(self, message: dict) -> str:
        visual_obj = {}
        # serialize.
        for answer in message['data']['chooseAnswerList']:
            title = answer['title'].replace("&nbsp;", "")
            visual_obj[title] = []
            # multiple choice.
            optionId = answer['optionId'] if not answer['optionId'].split(",") else [option.strip(' ') for option in answer['optionId'].split(",")]
            for option in answer['option']:
                if option['optionId'] in optionId:
                    visual_obj[title].append(f"{option['letter']}. {option['option_title']}")
        self.log.info(visual_obj)
        # to be visual.
        output = "###每日答题###\n"
        for title in visual_obj:
            options = '\n'.join(visual_obj[title])
            output += f"{title}\n\n✅答案：{options}\n"
        return output

    @logger.catch
    def submit_answer(self, message: dict) -> (bool, dict):
        # Generate answer.
        paperId = message['data']['paperId']

        answerData = {}
        totalTime = 0
        for answer in message['data']['chooseAnswerList']:
            # random times.
            useTime = randint(30, 200)
            # multiple choice.
            if answer['optionId'].split(","):
                answer['optionId'] = [option.strip(' ') for option in answer['optionId'].split(",")]

            answerData[answer['answer_id']] = {"value": answer['optionId'], "useTime": useTime}
            totalTime += useTime

        boundary = f"----WebKitFormBoundary{''.join(rand_sample(RAND_LETTER, 16))}"
        body = encode_multipart_formdata({
            'answerData': json.dumps(answerData, separators=(',', ':')),
            'useTime': totalTime,
            'paperId': paperId
        }, boundary=boundary)[0].decode()

        req = self.http.post(url=self.api.API_SUBMIT_ANSWER, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        params = req.json()
        self.log.debug(params)
        if params['msg'] != '答题成功':
            self.try_send_message(f"答题出错了: {params['msg']}")
            return 0, params['msg']

        self.try_send_message(f"{params['msg']}\n正确{params['data']['paperData']['right_num']}题，得分{params['data']['paperData']['score']}分")

        return 1, params
    
    @logger.catch
    def lottery(self, message: dict):
        if message['data']['successInfo']['isSuccess'] == 0:
            self.try_send_message('没有抽奖资格，跳过')
            return 0, 'not success'
        assert message['data']['successInfo']['isSuccess'] == 1, '抽奖资格异常'

        req = self.http.post(url=self.iApi.API2_LOTTERY)

        params = req.json()
        self.log.debug(params)
        if params['msg'] != '抽奖成功':
            self.try_send_message(f"抽奖出错了: {params['msg']}")
            return 0, params['msg']

        prize_name = params['data']['prize']['prize_name']
        self.try_send_message(f"抽奖结果：{params['msg']}\n{'没抽到' if prize_name == '' else prize_name}")
        return 1, params


    @logger.catch
    def answer_task(self):
        # start answer.
        status, message = self.start_answer()
        if not status:
            return

        # submit answer.
        status, message = self.submit_answer(message)
        if not status:
            return

        # lottery.
        self.lottery(message)

    # TODO: need cookie strictly.
    @logger.catch
    def article_task(self):
        taskEndCount = 2
        page = 1
        while True:
            status, articleInfo = self.get_article_list(page, 10)
            if not status:
                break
            if not articleInfo:
                break
            for article in articleInfo:
                article_id = article['article_id']
                status, isLiked = self.get_article_liked(article_id)
                if not status:
                    continue
                if isLiked:
                    self.log.debug(f"skip article {article_id}.")
                    continue
                
                self.articleActionSign(article_id, 'read')
                self.articleActionSign(article_id, 'zan')
                self.try_send_message(f"文章点赞成功：{article['article_title']}")
                taskEndCount -= 1
                if taskEndCount == 0:
                    self.log.debug('article task end.')
                    return
            page += 1
            


    @logger.catch
    def get_article_list(self, page:int = 0, pageCount: int = 10) -> dict:
        req = self.http.get(url=self.iApi.API2_GET_ARTICLE_LIST, params={
            'page': page,
            'pageCount': pageCount,
            'study_season_id': self.study_season_id,
            'articleclassify_id': -1
        })
        params = req.json()
        self.log.debug(params)
        if params['code'] != 3001:
            self.try_send_message(f"获取文章列表出错了: {params['msg']}")
            return 0, params['msg']
        return 1, params['data']
        
    @logger.catch
    def get_article_liked(self, articleId: str) -> (bool, bool):
        req = self.http.get(url=self.iApi.API2_ARTICLE, params={"articleId": articleId, "studyseasonid": self.study_season_id},
            headers={
                'Referer': 'https://ser-html5.8531.cn'
            })
        params = req.json()
        self.log.debug(params)
        if params['code'] != 3001:
            self.try_send_message(f"获取文章信息出错: {params['msg']}")
            return 0, params['msg']

        return 1, params['data']['article']['liked']

    @logger.catch
    def articleActionSign(self, articleId: int, readaction: str):
        boundary = f"----WebKitFormBoundary{''.join(rand_sample(RAND_LETTER, 16))}"
        params = {
            'articleId': articleId,
            'studyseasonid': self.study_season_id,
            'readaction': readaction
        }
        body = encode_multipart_formdata(params, boundary=boundary)[0].decode()

        req = self.http.post(url=self.iApi._API2_ARTICLE_ACTION_SIGN, params=params, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        params = req.json()
        self.log.debug(params)
        if params['code'] != 3001:
            return 0, params['msg']
        return 1, params


    def run(self):
        if self.is_answer:
            self.log.info('has been answered.')
            self.try_send_message('今天已经答过题了')
            return
        # answer task.
        self.answer_task()
        # todo: article task.
        # self.article_task()


# todo: Experimental feature.
def getSystemPid(account: dict):
    cilent_version = '9.1.5'
    phone_model = 'Pixel 2'.replace(' ', '+')
    screen_ratio = '16,9'
    system = 'Android'
    lauguage = 'en'
    system_version = '11'
    channel = 'googleplay'
    deviceId = account['deviceId']

    sessionId = randbytes(12).hex()  # length: 24
    requestId = str(uuid4())
    timestamp = int(time.time() * 1000)
    signature = SHA256.new(f"/api/article/discovery_list&&{sessionId}&&{requestId}&&{timestamp}&&XG?4VZ&4>9w".encode()).hexdigest()
    req = requests_get(ENTRY_URL, headers={
        "User-Agent": f"zjxw; {cilent_version}; {deviceId}; {phone_model} {screen_ratio}; {system}; {system_version}; {lauguage}; {channel}",
        "X-SESSION-ID": sessionId,
        "X-REQUEST-ID": requestId,
        "X-TIMESTAMP": str(timestamp),
        "X-SIGNATURE": signature,
        "Referer": "https://api-new.8531.cn/api/article/discovery_list"
    }, verify=False)

    return re.match(r".*?systemPid=(.*)&", req.text).group(1)


if __name__ == '__main__':
    # print(getSystemPid(account_info))
    pass
