using Amazon.S3;

namespace App
{
    class App
    {
        public async static Task Main()
        {
            /* Fill in your data */
            string tebiAccessKey = "<PUT_YOUR_ACCESS_KEY>";
            string tebiSecretKey = "<PUT_YOUR_SECRET_KEY>";
            string tebiServiceURL = "https://s3.tebi.io";
            string tebiBucketName = "<PUT_YOUR_BUCKET_NAME>";

            /* S3 Config Service URL */
            Amazon.S3.AmazonS3Config cfg = new AmazonS3Config { ServiceURL = tebiServiceURL };

            // This is a workaround for self signed SSL certificates!
            // cfg.HttpClientFactory = new S3SelfSignedFactory.SSLFactory();

            /* S3 Client Configuration (Key, Secret) */
            Amazon.S3.AmazonS3Client clnt = new AmazonS3Client(awsAccessKeyId: tebiAccessKey, awsSecretAccessKey: tebiSecretKey, clientConfig: cfg);

            /* List Buckets */
            Amazon.S3.Model.ListBucketsResponse lbr = await clnt.ListBucketsAsync();
            foreach (Amazon.S3.Model.S3Bucket b in lbr.Buckets)
            {
                Console.WriteLine("Bucket: {0}", (b.BucketName));
            }

            /* List Objects */
            Console.WriteLine("Getting objects... ");
            Amazon.S3.Model.ListObjectsResponse r = await clnt.ListObjectsAsync(tebiBucketName);
            foreach (Amazon.S3.Model.S3Object s in r.S3Objects)
            {
                Console.WriteLine("Bucket {0} -> File: {1}",s.BucketName,s.Key);
            }
        }
    }
}