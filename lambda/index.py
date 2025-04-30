import json
import os
import urllib.request
import urllib.error
import re

FASTAPI_URL = "https://e883-104-196-235-104.ngrok-free.app"

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
            "stopSequences": [],
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
        
        data = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        
        # POST リクエストを送信
        url = f"{FASTAPI_URL}/generate"
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            response_body = response.read()
            response_json = json.loads(response_body)
        
        print("API response:", response_json)

        assistant_response = response_json.get("generated_text", "")
        response_time = response_json.get("response_time", 0)

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
                "responseTime": response_time
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
