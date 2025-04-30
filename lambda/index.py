# lambda/index.py
import json
import os
import boto3
import re  # 正規表現モジュールをインポート
from botocore.exceptions import ClientError


# Lambda コンテキストからリージョンを抽出する関数
def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
    match = re.search('arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"  # デフォルト値


def lambda_handler(event, context):
    try:
        # Lambda コンテキストの情報をログ出力（認証済みユーザー情報の取得など）
        print("Received event:", json.dumps(event))

        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        
        print("Processing message:", message)
        
        FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://example.com/numbertheory")
        print("Calling FastAPI at:", FASTAPI_URL)
        
        # 受け取った message をそのまま prompt として利用
        request_payload = {
            "prompt": message
        }
        # JSONエンコードしてbytesに変換
        data = json.dumps(request_payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        
        req = urllib.request.Request(url=FASTAPI_URL, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            # APIからのレスポンスをデコードし、JSONとしてパース
            response_body = json.loads(response.read().decode('utf-8'))
        
        print("FastAPI response:", json.dumps(response_body, ensure_ascii=False))
        
        assistant_response = response_body.get("result")
        if not assistant_response:
            raise Exception("No result returned from FastAPI")
        
        # 必要に応じて、会話履歴の保持処理
        conversation_history = body.get('conversationHistory', [])
        conversation_history.append({
            "role": "user",
            "content": message
        })
        conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # 成功レスポンスを返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
