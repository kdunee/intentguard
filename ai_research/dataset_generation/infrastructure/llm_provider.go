package infrastructure

import (
	"context"
	"fmt"
	"time"

	"github.com/teilomillet/gollm"
)

// LLMProvider defines the interface for LLM operations
type LLMProvider interface {
	Infer(ctx context.Context, template string, data map[string]interface{}) (string, error)
}

// Config holds the configuration for the LLM provider
type Config struct {
	Provider    string
	Model       string
	MaxTokens   int
	Temperature float64
	APIKey      string
}

// gollmLLMProvider implements LLMProvider interface
type gollmLLMProvider struct {
	llm gollm.LLM
}

// NewLLMProvider creates a new LLM gollmLLMProvider with the given configuration
func NewLLMProvider(cfg Config) (LLMProvider, error) {
	if cfg.APIKey == "" {
		return nil, fmt.Errorf("API key is required")
	}

	llm, err := gollm.NewLLM(
		gollm.SetProvider(cfg.Provider),
		gollm.SetModel(cfg.Model),
		gollm.SetAPIKey(cfg.APIKey),
		gollm.SetMaxTokens(cfg.MaxTokens),
		gollm.SetTemperature(cfg.Temperature),
		gollm.SetMaxRetries(360),
		gollm.SetRetryDelay(time.Second*10),
		gollm.SetLogLevel(gollm.LogLevelInfo),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create LLM: %w", err)
	}

	return &gollmLLMProvider{
		llm: llm,
	}, nil
}

// Infer performs inference using the configured LLM
func (p *gollmLLMProvider) Infer(ctx context.Context, template string, data map[string]interface{}) (string, error) {
	promptTemplate := gollm.NewPromptTemplate("", "", template)
	prompt, err := promptTemplate.Execute(data)
	if err != nil {
		return "", fmt.Errorf("failed to execute template: %v", err)
	}

	response, err := p.llm.Generate(ctx, prompt)
	if err != nil {
		return "", fmt.Errorf("failed to generate response: %w", err)
	}

	return response, nil
}
