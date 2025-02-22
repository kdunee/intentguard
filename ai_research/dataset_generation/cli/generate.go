package cli

import (
	"context"
	"github.com/kdunee/intentguard/dataset-generation/domain"
	"github.com/kdunee/intentguard/dataset-generation/infrastructure"
	"github.com/spf13/cobra"
	"log"
)

var provider string
var model string
var maxTokens int
var temperature float64
var apiKey string

var generateCmd = &cobra.Command{
	Use:   "generate",
	Short: "Generate examples",
	Long:  "Generate examples for the dataset.",
	Run: func(cmd *cobra.Command, args []string) {
		cfg := infrastructure.Config{
			Provider:    provider,
			Model:       model,
			MaxTokens:   maxTokens,
			Temperature: temperature,
			APIKey:      apiKey,
		}

		provider, err := infrastructure.NewLLMProvider(cfg)
		if err != nil {
			log.Fatalf("Failed to create LLM provider: %v", err)
		}

		ctx := context.Background()

		template, err := infrastructure.GetGenerationPrompt()
		if err != nil {
			log.Fatalf("Failed to get prompt: %v", err)
		}

		for {
			category := domain.GetRandomCategory()
			response, err := provider.Infer(ctx, template, map[string]interface{}{"Category": category})
			if err != nil {
				log.Fatalf("Failed to get response: %v", err)
			}

			examples := domain.ParseExamples(response)

			infrastructure.WriteExamplesToOutput(category, examples)
		}
	},
}

func init() {
	generateCmd.Flags().StringVar(&provider, "provider", "groq", "LLM provider to use (openai, anthropic, groq)")
	generateCmd.Flags().StringVar(&model, "model", "llama-3.3-70b-versatile", "LLM model to use")
	generateCmd.Flags().IntVar(&maxTokens, "max-tokens", 32768, "Maximum number of tokens to generate")
	generateCmd.Flags().Float64Var(&temperature, "temperature", 1.0, "Temperature for LLM inference")
	generateCmd.Flags().StringVar(&apiKey, "api-key", "", "API key for the LLM provider")
	err := generateCmd.MarkFlagRequired("api-key")
	if err != nil {
		log.Fatalf("Failed to mark flag as required: %v", err)
	}

	rootCmd.AddCommand(generateCmd)
}
