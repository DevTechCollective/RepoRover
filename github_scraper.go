package main

import (
    "fmt"
    "io"
    "net/http"
)

type GitHubScraper struct {
    Owner  string
    Repo   string
    Branch string
}



func (scraper *GitHubScraper) getFileRaw(filePath string) (string, error) {
    url := fmt.Sprintf("https://api.github.com/repos/%s/%s/contents/%s?ref=%s", scraper.Owner, scraper.Repo, filePath, scraper.Branch)
    headers := map[string]string{
        "Accept": "application/vnd.github.v3.raw",
    }

    // Create a new HTTP request
    req, err := http.NewRequest("GET", url, nil)
    if err != nil {
        return "", fmt.Errorf("failed to create request: %v", err)
    }

    // Add headers to the request
    for key, value := range headers {
        req.Header.Add(key, value)
    }

    // Make the HTTP request
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return "", fmt.Errorf("failed to make request: %v", err)
    }
    defer resp.Body.Close()

    // Check the response status code
    if resp.StatusCode != http.StatusOK {
        return "", fmt.Errorf("failed to retrieve file: %d", resp.StatusCode)
    }

    // Read the response body
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", fmt.Errorf("failed to read response body: %v", err)
    }

    return string(body), nil
}

