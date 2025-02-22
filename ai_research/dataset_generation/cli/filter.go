package cli

import (
	"bufio"
	"context"
	"fmt"
	"github.com/kdunee/intentguard/dataset-generation/infrastructure"
	"github.com/spf13/cobra"
	"log"
	"os"
	"regexp"
)

var filterInputPath string
var filterOutputPath string

var filterCmd = &cobra.Command{
	Use:   "filter",
	Short: "Filter dataset examples",
	Long:  "Filter dataset examples using LLM-based quality assessment.",
	Run: func(cmd *cobra.Command, args []string) {
		cfg := infrastructure.Config{
			Provider:    provider,
			Model:       model,
			MaxTokens:   maxTokens,
			Temperature: temperature,
			APIKey:      apiKey,
		}

		llm, err := infrastructure.NewLLMProvider(cfg)
		if err != nil {
			log.Fatalf("Failed to create LLM provider: %v", err)
		}

		filterPrompt, err := infrastructure.GetFilteringPrompt()
		if err != nil {
			log.Fatalf("Failed to get filtering prompt: %v", err)
		}

		inFile, err := os.Open(filterInputPath)
		if err != nil {
			log.Fatalf("Failed to open input file: %v", err)
		}
		defer inFile.Close()

		outFile, err := os.Create(filterOutputPath)
		if err != nil {
			log.Fatalf("Failed to create output file: %v", err)
		}
		defer outFile.Close()

		scanner := bufio.NewScanner(inFile)
		ctx := context.Background()

		var verdictAcceptPattern = regexp.MustCompile(`(?i)verdict.*accept`)

		for scanner.Scan() {
			line := scanner.Text()
			response, err := llm.Infer(ctx, string(filterPrompt), map[string]interface{}{
				"Row": line,
			})
			if err != nil {
				log.Printf("Failed to get LLM response: %v", err)
				continue
			}

			if verdictAcceptPattern.MatchString(response) {
				_, err = fmt.Fprintln(outFile, line)
				if err != nil {
					log.Printf("Failed to write to output file: %v", err)
				}
			}
		}

		if err := scanner.Err(); err != nil {
			log.Fatalf("Error reading input file: %v", err)
		}
	},
}

func init() {
	filterCmd.Flags().StringVarP(&filterInputPath, "input", "i", "train.jsonl", "Input file path")
	filterCmd.Flags().StringVarP(&filterOutputPath, "output", "o", "filtered.jsonl", "Output file path")

	// Reuse LLM flags from generate command
	filterCmd.Flags().StringVar(&provider, "provider", "groq", "LLM provider to use (openai, anthropic, groq)")
	filterCmd.Flags().StringVar(&model, "model", "llama-3.3-70b-versatile", "LLM model to use")
	filterCmd.Flags().IntVar(&maxTokens, "max-tokens", 32768, "Maximum number of tokens to generate")
	filterCmd.Flags().Float64Var(&temperature, "temperature", 1.0, "Temperature for LLM inference")
	filterCmd.Flags().StringVar(&apiKey, "api-key", "", "API key for the LLM provider")

	err := filterCmd.MarkFlagRequired("api-key")
	if err != nil {
		log.Fatalf("Failed to mark flag as required: %v", err)
	}

	rootCmd.AddCommand(filterCmd)
}
