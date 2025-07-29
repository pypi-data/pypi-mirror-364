package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/cloudwatchlogs"
	"github.com/aws/aws-sdk-go-v2/service/cloudwatchlogs/types"
)

// Global variables
var (
	cloudwatch      *cloudwatchlogs.Client
	SLACK_WEBHOOK_URL = os.Getenv("SLACK_WEBHOOK_URL")
	LOG_GROUP_NAME    = os.Getenv("LOG_GROUP_NAME")
	ENVIRONMENT      = os.Getenv("ENVIRONMENT")
)

// Initialize AWS CloudWatch Logs client
func init() {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatalf("Failed to load AWS config: %v", err)
	}
	cloudwatch = cloudwatchlogs.NewFromConfig(cfg)
}

// Format a long message to maintain word boundaries
func formatLongMessage(message string, maxLength int) string {
	words := strings.Fields(message)
	var lines []string
	var currentLine []string

	for _, word := range words {
		if len(strings.Join(currentLine, " "))+len(word)+1 <= maxLength {
			currentLine = append(currentLine, word)
		} else {
			lines = append(lines, strings.Join(currentLine, " "))
			currentLine = []string{word}
		}
	}
	if len(currentLine) > 0 {
		lines = append(lines, strings.Join(currentLine, " "))
	}
	return strings.Join(lines, "\n")
}

// Send messages to Slack
func sendToSlack(messages []map[string]string) {
	headerText := fmt.Sprintf("*:warning: CloudWatch Logs Insights ENV: %s: Top 10 Warnings :warning:*", ENVIRONMENT)
	payload := map[string]interface{}{
		"blocks": []map[string]interface{}{
			{
				"type": "section",
				"text": map[string]string{"type": "mrkdwn", "text": headerText},
			},
			{
				"type": "section",
				"text": map[string]string{"type": "mrkdwn", "text": "```Index   Count     Container                 Message\n--------------------------------------------------------```"},
			},
		},
	}

	// Add messages
	for i, warning := range messages {
		count := warning["cnt"]
		container := warning["kubernetes.container_name"]
		message := formatLongMessage(warning["msg"], 50)

		row := fmt.Sprintf("%-6d%-10s%-25s%s", i+1, count, container, message)
		payload["blocks"] = append(payload["blocks"].([]map[string]interface{}), map[string]interface{}{
			"type": "section",
			"text": map[string]string{"type": "mrkdwn", "text": fmt.Sprintf("```%s```", row)},
		})
	}

	// Convert payload to JSON
	payloadBytes, _ := json.Marshal(payload)
	req, err := http.NewRequest("POST", SLACK_WEBHOOK_URL, bytes.NewBuffer(payloadBytes))
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error sending message to Slack: %v", err)
		return
	}
	defer resp.Body.Close()
	log.Println("Message successfully sent to Slack.")
}

// AWS Lambda function handler
func lambdaHandler(ctx context.Context, event map[string]interface{}) {
	log.Println("Starting lambdaHandler...")

	// Define CloudWatch Logs Insights query
	query := `
		fields namespace_name, kubernetes.container_name
		| parse @message '"level":"*"' as level
		| parse @message '"error":"*"' as error
		| parse @message '"msg":"*"' as msg
		| filter level ~= /(?i)(WARN|ERROR)/
		| stats count(*) as cnt by msg, error, kubernetes.container_name
		| sort cnt desc
		| limit 10
	`

	// Define time range (last 7 days)
	endTime := time.Now().UnixMilli()
	startTime := time.Now().AddDate(0, 0, -7).UnixMilli()
	log.Printf("Time range for query: %d to %d\n", startTime, endTime)

	// Start CloudWatch query
	resp, err := cloudwatch.StartQuery(ctx, &cloudwatchlogs.StartQueryInput{
		LogGroupName: &LOG_GROUP_NAME,
		StartTime:    &startTime,
		EndTime:      &endTime,
		QueryString:  &query,
	})
	if err != nil {
		log.Fatalf("Failed to start query: %v", err)
	}
	queryID := *resp.QueryId
	log.Printf("Started query with ID: %s\n", queryID)

	// Wait for query results
	var queryResults *cloudwatchlogs.GetQueryResultsOutput
	for {
		time.Sleep(2 * time.Second)
		queryResults, err = cloudwatch.GetQueryResults(ctx, &cloudwatchlogs.GetQueryResultsInput{
			QueryId: &queryID,
		})
		if err != nil {
			log.Fatalf("Failed to get query results: %v", err)
		}
		log.Printf("Query status: %s\n", queryResults.Status)
		if queryResults.Status != types.QueryStatusScheduled && queryResults.Status != types.QueryStatusRunning {
			break
		}
	}

	// Process query results
	var messages []map[string]string
	if queryResults != nil && len(queryResults.Results) > 0 {
		for _, result := range queryResults.Results {
			formattedResult := make(map[string]string)
			for _, field := range result {
				formattedResult[*field.Field] = *field.Value
			}
			messages = append(messages, formattedResult)
		}
		log.Printf("messages found: %d\n", len(messages))
	}

	// Send results to Slack
	if len(messages) > 0 {
		sendToSlack(messages)
	} else {
		sendToSlack([]map[string]string{{"msg": "No warnings found in CloudWatch logs.", "cnt": "0"}})
	}
}

// Main function to start AWS Lambda
func main() {
	lambda.Start(lambdaHandler)
}
