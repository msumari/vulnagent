import json

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event, indent=2)}")
    
    # Extract Inspector finding details
    detail = event.get('detail', {})
    finding_arn = detail.get('findingArn', '')
    severity = detail.get('severity', '')
    title = detail.get('title', '')
    
    print(f"Finding: {title}, Severity: {severity}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Inspector finding processed',
            'findingArn': finding_arn
        })
    }
