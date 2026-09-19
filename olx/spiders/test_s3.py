import boto3
bucket = 'my-bucket'
#Make sure you provide / in the end
prefix = 'prefix-name-with-slash/'  

client = boto3.client('s3')
result = client.list_objects(Bucket=bucket, Prefix=prefix, Delimiter='/')
for o in result.get('CommonPrefixes'):
    print 'sub folder : ', o.get('Prefix')