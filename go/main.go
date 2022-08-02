package main

import (
	"context"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func main() {
	customResolver := aws.EndpointResolverWithOptionsFunc(func(service, region string, options ...interface{}) (aws.Endpoint, error) {
		return aws.Endpoint{
			PartitionID:   "aws",
			URL:           "https://s3.tebi.io",
			SigningRegion: "de",
		}, nil
	})

	customConfig := config.LoadOptionsFunc(func(configOptions *config.LoadOptions) error {
		configOptions.Credentials = credentials.StaticCredentialsProvider{Value: aws.Credentials{AccessKeyID: "YOUR_ACCESS_KEY", SecretAccessKey: "YOUR_SECRET_KEY"}}
		return nil
	})

	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithEndpointResolverWithOptions(customResolver), customConfig)
	if err != nil {
		log.Fatalf("unable to load SDK config, %v", err)
	}

	svc := s3.NewFromConfig(cfg)

	resp, err := svc.ListBuckets(context.TODO(), &s3.ListBucketsInput{})
	if err != nil {
		log.Fatalf("unable to fetch buckets --> %v", err)
	}

	fmt.Println("Buckets: ")
	for _, bucketEntry := range resp.Buckets {
		fmt.Printf("resp.Buckets entry -> %+v", bucketEntry)
		fmt.Printf(" - real name: %v\n", aws.ToString(bucketEntry.Name))
	}

}
