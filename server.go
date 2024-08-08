package main

import (
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/sashabaranov/go-openai"
)

var scraper *GitHubScraper

type Documents struct {
    page_content string
	metadata []string
}

type SummaryRequest struct {
	ReadmeQuery []Documents `json:"readme_query"`
    FileQuery []Documents `json:"file_query"`
    Query    string `json:"query"`
}

type SummaryResponse struct {
    ReadmeSummary []string `json:"readme_summary"`
    CodeSummary   []string `json:"code_summary"`
}

type URLReq struct {
    owner string `json:"Owner"`
    repo string `json:"Repo"`
    branch string `json:"Branch"`
}


func main() {
    router := gin.Default()
	apiKey := os.Getenv("OPENAI_API_KEY")
    client := openai.NewClient(apiKey)

    router.POST("/info", func(c *gin.Context) {
        var urlreq URLReq
        if err := c.ShouldBindJSON(&urlreq); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        
        scraper = &GitHubScraper{
			Owner:  urlreq.owner,
			Repo:   urlreq.repo,
			Branch: urlreq.branch,
		}

        c.JSON(http.StatusOK, gin.H{"message": "Scraper initialized"})
    },
    )

	//get code summary
    router.POST("/summary", func(c *gin.Context) {
        var req SummaryRequest
        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }

        codeSummary := processFilePaths(client, req.FileQuery, req.Query)
		// readmeSummary := processReadme(client, req.ReadmeQuery, req.Query)

        response := SummaryResponse{
            // ReadmeSummary: readmeSummary,
            CodeSummary:   codeSummary,
        }

        c.JSON(http.StatusOK, response)
    })

    router.Run(":8080")
}