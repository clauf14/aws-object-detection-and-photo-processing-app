import json
import boto3
import base64
import logging
import io
from PIL import Image, ImageDraw, ImageFont
from decimal import Decimal
import time
import botocore

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = "ImageMetadata"
BUCKET_NAME = "ai-image-processing-tests"
TOPIC_ARN = "arn:aws:sns:us-east-1:088178734864:ImageProcessingTopic"
FONT_KEY = "fonts/Roboto_Condensed-Black.ttf"

def download_font():
    font_path = "/tmp/custom_font.ttf"
    
    # Download the font from S3 and save it to /tmp
    s3.download_file(BUCKET_NAME, FONT_KEY, font_path)
    
    return font_path


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_float(value) for key, value in obj.items()}
    return obj


def draw_bounding_boxes(image, labels):
    draw = ImageDraw.Draw(image)
    font_path = download_font()
    
    try:
        font = ImageFont.truetype(font_path, 35)
    except IOError:
        font = ImageFont.load_default()
    
    for label in labels:
        bbox = label.get('BoundingBox')
        if not bbox:
            continue
        
        left = bbox['Left'] * image.width
        top = bbox['Top'] * image.height
        right = (bbox['Left'] + bbox['Width']) * image.width
        bottom = (bbox['Top'] + bbox['Height']) * image.height
        
        text = f"{label['Name']} ({label['Confidence']:.2f}%)"
        draw.rectangle([left, top, right, bottom], outline="red", width=5)
        draw.text((left, top - 45), text, fill="red", font=font)
    
    return image


def detect_labels_with_retry(bucket_name, image_key, retries=5, delay=1):
    for attempt in range(retries):
        try:
            return rekognition.detect_labels(
                Image={'S3Object': {'Bucket': bucket_name, 'Name': image_key}},
                MaxLabels=10
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ProvisionedThroughputExceededException' and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )


def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    logger.info(f"file: {event['file']}")
    try:
        #body = json.loads(event['body'])
        #print(body)
        filename = event['filename']
        image_data = base64.b64decode(event['file'], validate=True)
        #filename = body.get('filename', f"upload_{int(time.time())}.jpg")
        
        # Upload original file to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=image_data,
            ContentType='image/jpeg'
        )
        
        # Run Rekognition
        response = detect_labels_with_retry(BUCKET_NAME, filename)
        labels = [
            {
                'Name': label['Name'],
                'Confidence': Decimal(str(label['Confidence'])),
                'BoundingBox': {k: Decimal(str(v)) for k, v in label['Instances'][0]['BoundingBox'].items()} if label['Instances'] else {}
            }
            for label in response['Labels']
        ]
        
        # Open image and draw bounding boxes
        image = Image.open(io.BytesIO(image_data))
        image_with_boxes = draw_bounding_boxes(image, labels)
        
        # Save processed image
        output_image_key = f"processed/{filename}"
        output_buffer = io.BytesIO()
        image_with_boxes.save(output_buffer, format="JPEG")
        output_buffer.seek(0)
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=output_image_key,
            Body=output_buffer,
            ContentType='image/jpeg'
        )
        
        # Store metadata in DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={'image_key': filename, 'labels': labels})

        presigned_url = generate_presigned_url(BUCKET_NAME, output_image_key)
        
        # Prepare response payload
        response_payload = {
            'statusCode': 200,
            'processed_image_url': presigned_url,
            'labels': decimal_to_float(labels)
        }

        pretty_message = json.dumps(response_payload, indent=4)

        # Publish the SNS message with a prettier body and filename in the subject
        sns_response = sns.publish(
            TopicArn=TOPIC_ARN,
            Message="Response body:\n" + pretty_message,  # Send the prettified JSON message body
            Subject=f"Image Processing Completed for {filename}"  # Include the filename in the subject
        )

        logger.info(f"SNS publish response: {sns_response}")

        return response_payload
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e)
        }
