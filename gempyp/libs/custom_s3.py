import boto3
import os


def download(bucket=None, file_name=None, folder=None):
    try:
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(bucket)
        for object_summary in my_bucket.objects.filter(Prefix="/".join(folder)):
            body = object_summary.get()['Body'].read()

        fileContent = body.decode().split("\\n")
        path = os.path.join(file_name)
        with open(path, "w+") as fp:
            fp.seek(0)
            fp.write('\n'.join(fileContent))
            fp.truncate()

        return path
    except Exception as e:
        print(str(e))
        return f"error occurred- {str(e)}"