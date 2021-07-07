import logging
import json
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    teams_incoming_webhook = os.environ['TEAMS_INCOMING_WEBHOOK']     # 環境変数よりTeams Incoming WebhookのURL取得
    bl_body=json.loads(event['body'])
    #イベントデータなどロギング
    logger.debug("Event Data:" + json.dumps(dict(event)))
    logger.debug("Backlog Body:" + json.dumps(bl_body))

    # Backlogで定義された更新の種別
    bl_issue_type = {1:"課題の追加", 2:"課題の更新", 3:"課題にコメント", 4:"課題の削除",14:"課題をまとめて更新",17:"コメントにお知らせを追加"}
    # Backlogで操作した更新
    bl_type = bl_body['type']

    # Backlog課題に関するイベントのみ許可(キーがなければ例外発生)
    if bl_type in bl_issue_type.keys():
        # Teamsに通知するタイトル
        teams_title = bl_issue_type[bl_type]
    else:
        raise KeyError

    #更新種別を判別して通知メッセージ作成
    if bl_type == 1:      #課題追加
        payload_dic = issue_add(teams_title,bl_body)
    elif bl_type == 2:    #課題更新
        payload_dic = issue_update(teams_title,bl_body)
    elif bl_type == 3:    #課題コメント
        payload_dic = issue_comment(teams_title,bl_body)
    elif bl_type == 4:    #課題削除
        payload_dic = issue_delete(teams_title,bl_body)
    elif bl_type == 14:    #課題複数更新
        payload_dic = issue_multi_update(teams_title,bl_body)
    elif bl_type == 17:    #コメントお知らせ追加
        payload_dic = issue_comment_notice_add(teams_title,bl_body)
    else:
        raise Exception

    response = requests.post(teams_incoming_webhook, data=json.dumps(payload_dic))
    # ステータスコードを判定してロギング
    if response.status_code == requests.codes.ok:
        logger.info("Status Code :" + str(response.status_code) + " Response Header:" + json.dumps(dict(response.headers)))
        return response.status_code
    else:
        logger.info("Status Code :" + str(response.status_code) + " Response Header:" + json.dumps(dict(response.headers)))
        raise Exception

#課題追加時のメッセージ作成
def issue_add(teams_title,bl_body):
    bl_summary = bl_body['content']['summary']
    bl_description = bl_body['content']['description']
    bl_created = bl_body['created']
    teams_text = '件名：{0}<br/>課題の詳細：{1}<br/>日時：{2}'.format(bl_summary,bl_description,bl_created)
    #Teamsへの通知本文作成
    payload_dic = {
        "title": teams_title,
        "text": teams_text,
    }
    return payload_dic

#課題更新時のメッセージ作成
def issue_update(teams_title,bl_body):
    bl_summary = bl_body['content']['summary']
    bl_description = bl_body['content']['description']
    bl_created = bl_body['created']
    teams_text = '件名：{0}<br/>課題の詳細：{1}<br/>日時：{2}'.format(bl_summary,bl_description,bl_created)
    #Teamsへの通知本文
    payload_dic = {
        "title": teams_title,
        "text": teams_text,
    }
    return payload_dic

#課題コメント時のメッセージ作成
def issue_comment(teams_title,bl_body):
    bl_summary = bl_body['content']['summary']
    bl_comment = bl_body['content']['comment']['content']
    bl_created = bl_body['created']
    teams_text = '件名：{0}<br/>コメント：{1}<br/>日時：{2}'.format(bl_summary,bl_comment,bl_created)
    #Teamsへの通知本文
    payload_dic = {
        "title": teams_title,
        "text": teams_text,
    }
    return payload_dic

#課題削除時のメッセージ作成
def issue_delete(teams_title,bl_body):
    bl_created = bl_body['created']
    teams_text = '日時：{0}'.format(bl_created)
    #Teamsへの通知本文
    payload_dic = {
        "title": teams_title,
        "text": teams_text,
    }
    return payload_dic

#課題複数更新時のメッセージ作成
def issue_multi_update(teams_title,bl_body):
    bl_created = bl_body['created']
    #纏めて更新した要素数
    testt = range(len(bl_body['content']['link']))

    teams_text = ""
    for i in testt:
        print(bl_body['content']['link'][i]['title'])
        teams_text += '件名：{0}<br/>'.format(bl_body['content']['link'][i]['title'])
    teams_text += '日時：{0}'.format(bl_created)

    #Teamsへの通知本文
    payload_dic = {
        "title": teams_title,
        "text": teams_text,
    }
    return payload_dic

#コメントお知らせ追加時のメッセージ作成
def issue_comment_notice_add(teams_title,bl_body):
    bl_summary = bl_body['content']['summary']
    bl_comment = bl_body['content']['comment']['content']
    bl_created = bl_body['created']
    teams_text = '件名：{0}<br/>課題の詳細：{1}<br/>日時：{2}'.format(bl_summary,bl_comment,bl_created)
    #Teamsへの通知本文作成
    payload_dic = {
        "title": teams_title,
        "text": teams_text,
    }
    return payload_dic