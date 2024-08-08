package main

import (
	"fmt"
	"sync"
    "context"

	"github.com/pkoukk/tiktoken-go"
	"github.com/sashabaranov/go-openai"
)

func Trim(encoder *tiktoken.Tiktoken, text string, tokenLimit int) string {
	tokens := encoder.Encode(text, nil,nil)
	if len(tokens) > tokenLimit {
		tokens = tokens[:tokenLimit]
	}
	return encoder.Decode(tokens)
}

func codeSummary(client *openai.Client, encoder *tiktoken.Tiktoken, filePath string, query string, wg *sync.WaitGroup, ch chan<- string) {
	defer wg.Done()

	code, err := scraper.getFileRaw(filePath)
	fmt.Printf("Code: %s\n", code)

	customPrompt := fmt.Sprintf(`
    Provide a clear and concise summary on the code that you will be given as it relates to a user query. 
    You should reference specific parts of the code. 
    Be technical. Your summary will be used by another LLM to explain specific parts of the code. 
    Focus on those parts that are most relevant to the user query, the user may ask for specific code snippets which you will provide.
    Do not speak to or address the user. 
    Limit your response to 200 words.
    Code: %s
    User Query: %s`, code, query)

	resp, err := client.CreateChatCompletion(
        context.Background(),
		openai.ChatCompletionRequest{
			Model: openai.GPT3Dot5Turbo,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: customPrompt,
				},
			},
	    },
	)
	fmt.Printf("Completion response: %v\n", resp)

	if err != nil {
		fmt.Printf("Completion error: %v\n", err)
		return 
	}

	ch <- Trim(encoder, resp.Choices[0].Message.Content, 200)
}

// Function to process all file paths concurrently
func processFilePaths(client *openai.Client, filePaths []Documents, query string) []string {
	var wg sync.WaitGroup
	ch := make(chan string, len(filePaths))
	summaries := make([]string, len(filePaths))

    encoder, err := tiktoken.EncodingForModel("gpt-3.5-turbo")

    if err != nil {
        fmt.Printf("Error creating encoder: %v\n", err)
        return summaries
    }

	for _, doc := range filePaths {
		wg.Add(1)
		go codeSummary(client, encoder, doc.page_content, query, &wg, ch)
	}

	wg.Wait()
	close(ch)

	i := 0
	for summary := range ch {
		summaries[i] = summary
		i++
	}

	return summaries
}

// func processReadme(client *openai.Client, readmePath string, query string) string {

// }
