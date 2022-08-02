package main

import (
	"context"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

func main() {
	customResolver := aws.EndpointResolverWithOptionsFunc(func(service, region string, options ...interface{}) (aws.Endpoint, error) {
		return aws.Endpoint{
			PartitionID:   "aws",
			URL:           "http://s3.docker.tebi.io",
			SigningRegion: "de",
		}, nil
	})

	//Credentials: credentials.StaticCredentialsProvider{Value: aws.Credentials{AccessKeyID: "", SecretAccessKey: ""}},
	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithEndpointResolverWithOptions(customResolver), config.LoadOptionsFunc(func() (config.LoadOptions, err) {

	}))
	if err != nil {
		log.Fatalf("unable to load SDK config, %v", err)
	}

	svc := s3.NewFromConfig(cfg)
	resp, err := svc.ListBuckets(context.TODO(), &s3.ListBucketsInput{})
	if err != nil {
		log.Fatalf("unable to fetch buckets --> %v", err)
	}

	fmt.Println("Buckets: ")
	for _, bucketName := range resp.Buckets {
		fmt.Println(bucketName)
	}

	/*
	   // Build the request with its input parameters
	   resp, err := svc.ListTables(context.TODO(), &dynamodb.ListTablesInput{
	       Limit: aws.Int32(5),
	   })
	   if err != nil {
	       log.Fatalf("failed to list tables, %v", err)
	   }

	   fmt.Println("Tables:")
	   for _, tableName := range resp.TableNames {
	       fmt.Println(tableName)
	   }*/
}
