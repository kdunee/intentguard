package cli

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "dataset-generation",
	Short: "Dataset generation toolset for IntentGuard",
	Long:  `dataset-generation is a toolset for generating datasets for IntentGuard.`,
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
