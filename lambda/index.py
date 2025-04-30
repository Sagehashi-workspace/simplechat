import json
import os
import urllib.request
import urllib.error
import re

# エンドポイントのベースURL（環境変数から取得、末尾のスラッシュは除外）
API_BASE_URL = os.environ.get("FASTAPI_ENDPOINT", "https://your-ngrok-url.ngrok-free.app").rstrip('/')

def extract_region_from_arn(arn):
    match = re.search(r'arn:aws:lambda:([^:]+):', arn)
    if match:
        return match.group(1)
    return "us-east-1"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        
        # FastAPI に送るペイロード
        payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
        
        data = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        
        # POST リクエストを送信
        url = f"{API_BASE_URL}/generate"
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            response_body = response.read()
            response_json = json.loads(response_body)
        
        print("API response:", response_json)

        assistant_response = response_json.get("generated_text", "")

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
                "response": assistant_response
            })
        }

    except urllib.error.HTTPError as e:
        error_message = f"HTTPError: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        error_message = f"URLError: {e.reason}"
    except Exception as e:
        error_message = f"Exception: {str(e)}"

    print("Error:", error_message)

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
            "error": error_message
        })
    }
