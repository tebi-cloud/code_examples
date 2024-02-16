<?php
/* for more general info check the following links:
   * https://docs.amazonaws.cn/en_us/sdk-for-php/v3/developer-guide/s3-examples-creating-buckets.html
   * https://docs.aws.amazon.com/aws-sdk-php/v3/api/class-Aws.AwsClient.html 
   * https://docs.aws.amazon.com/aws-sdk-php/v3/api/class-Aws.S3.S3Client.html 
   also, make sure to install the SDK with `composer install` first!
   * https://getcomposer.org/download/
*/

require __DIR__ . '/vendor/autoload.php';
use Aws\S3\S3Client;  
use Aws\Exception\AwsException;


const YOUR_KEY = '<INSERT YOUR KEY HERER>';
const YOUR_SECRET = '<INSERT YOUR SECRET>';
const TEST_BUCKET = '<INSERT YOUR BUCKET NAME HERE>';

/* initialize connection*/
$s3Client = new Aws\S3\S3Client([
    "credentials" => [
        "key" => YOUR_KEY,
        "secret" => YOUR_SECRET
    ],
    "endpoint" => "https://s3.tebi.io",
	"region" => "global"
]);

echo "Listing available buckets: "."\n";
$buckets = $s3Client->listBuckets();
foreach($buckets["Buckets"] as $b) {
    echo $b["Name"] . "\n";
}
echo "---"."\n";

echo "Uploading test file..."."\n";
$result = $s3Client->putObject([
    'Bucket' => TEST_BUCKET,
    'Key' => "composer.json",
    'SourceFile' => "./composer.json",
]);
echo "Upload result: ".$result["@metadata"]["statusCode"]."\n"."---"."\n";


echo "Content of bucket:"."\n"."---"."\n";
$objs = $s3Client->listObjects(['Bucket' => TEST_BUCKET]);
foreach($objs["Contents"] as $o) {
    echo $o["Key"]."\n";
}
