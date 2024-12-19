package cli

import (
	"encoding/json"
	"github.com/kdunee/intentguard/dataset-generation/infrastructure"
	"github.com/spf13/cobra"
	"log"
	"os"
)

var transformInputPath string
var transformOutputPath string

var transformCmd = &cobra.Command{
	Use:   "transform",
	Short: "Transform the dataset to the final format",
	Long:  "Transform the dataset to the final format.",
	Run: func(cmd *cobra.Command, args []string) {
		f, err := os.Open(transformInputPath)
		if err != nil {
			log.Fatalf("Failed to open input file: %v", err)
		}
		defer f.Close()

		of, err := os.OpenFile(transformOutputPath, os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatalf("Failed to open output file: %v", err)
		}
		defer of.Close()

		decoder := json.NewDecoder(f)
		for {
			var line infrastructure.OutputLine
			err := decoder.Decode(&line)
			if err != nil {
				break
			}
			for _, example := range line.Examples {
				exampleJsonBytes, err := json.Marshal(example)
				if err != nil {
					log.Fatalf("Failed to marshal example: %v", err)
				}

				_, err = of.WriteString(string(exampleJsonBytes) + "\n")
				if err != nil {
					log.Fatalf("Failed to write to output file: %v", err)
				}
			}
		}
	},
}

func init() {
	transformCmd.Flags().StringVarP(&transformInputPath, "input", "i", "output.jsonl", "Input file path")
	transformCmd.Flags().StringVarP(&transformOutputPath, "output", "o", "train.jsonl", "Output file path")
	rootCmd.AddCommand(transformCmd)
}
