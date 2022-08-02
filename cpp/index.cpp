
#include <aws/core/Aws.h>
#include <aws/core/auth/AWSCredentialsProviderChain.h>
#include <aws/s3/S3Client.h>

using namespace Aws;
using namespace Aws::Auth;
using namespace Aws::Http;
using namespace Aws::Client;
using namespace Aws::S3;
using namespace Aws::S3::Model;
using namespace Aws::Utils;

const char *secret_id = "YOUR_ACCESS_KEY";
const char *secret_key = "YOUR_ACCESS_SECRET";
const char *custom_endpoint = "s3.tebi.io";
const Aws::Http::Scheme custom_endpoint_scheme = Scheme::HTTPS;

int main() {

  // initialize API
  Aws::SDKOptions options;
  Aws::InitAPI(options);
  {

    // create credential object
    Aws::Auth::AWSCredentials creds(secret_id, secret_key);

    // create config object
    ClientConfiguration config;
    config.scheme = custom_endpoint_scheme;
    config.endpointOverride = custom_endpoint;

    // create s3 client object
    Aws::S3::S3Client s3_client(creds, config);

    // ~~~ functions  ~~~
    Aws::S3::Model::ListBucketsOutcome outcome = s3_client.ListBuckets();
    if (outcome.IsSuccess()) {

      Aws::Vector<Aws::S3::Model::Bucket> bucket_list =
          outcome.GetResult().GetBuckets();

      for (Aws::S3::Model::Bucket const &bucket : bucket_list) {

        std::cout << "Found the bucket: " << bucket.GetName() << std::endl;
      }

    } else {
      std::cout << "ListBuckets error: " << outcome.GetError().GetMessage()
                << std::endl;
    }

    // for more examples see:
    // - https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/cpp
  }

  // clean-up API
  Aws::ShutdownAPI(options);

  return 0;
}