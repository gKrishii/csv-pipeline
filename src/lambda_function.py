import os
import csv
import boto3
import io

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    """
    Triggered by an S3 event when a .csv file is uploaded to InputBucket.
    """
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    output_bucket = os.environ['OUTPUT_BUCKET']

    try:
        # Grab S3 info from the event
        record = event['Records'][0]
        input_bucket = record['s3']['bucket']['name']
        input_key = record['s3']['object']['key']

        # Download CSV
        response = s3_client.get_object(Bucket=input_bucket, Key=input_key)
        csv_content = response['Body'].read().decode('utf-8')

        # Transform the CSV
        transformed_data = transform_csv(csv_content)

        # Upload to OutputBucket with a new file name
        output_key = f"transformed_{input_key}"
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=transformed_data.encode('utf-8')
        )

        print(f"SUCCESS: Processed {input_key} -> {output_key} in bucket {output_bucket}")

    except Exception as e:
        error_msg = f"ERROR while processing {input_key}: {str(e)}"
        print(error_msg)

        # Send SNS alert
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject="CSV Processing Failure",
            Message=error_msg
        )

        raise e


def transform_csv(csv_content):
    """
    Simple transformation: Add a 'Processed' column with value 'Yes'
    """
    input_stream = io.StringIO(csv_content)
    reader = csv.reader(input_stream)
    output_stream = io.StringIO()
    writer = csv.writer(output_stream)

    # 1) Read headers
    headers = next(reader)
    headers.append("Processed")
    writer.writerow(headers)

    # 2) For each row, add 'Yes'
    for row in reader:
        row.append("Yes")
        writer.writerow(row)

    return output_stream.getvalue()
