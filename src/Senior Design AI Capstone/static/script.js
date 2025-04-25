async function getRecommendations() {
    const query = document.getElementById('query').value.trim();
    if (!query) {
        alert("Please enter a topic before searching.");
        return;
    }
// Getting recommended articles
    try {
        const response = await fetch(`http://ec2-18-209-55-158.compute-1.amazonaws.com:5000/recommend?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        const recommendationsDiv = document.getElementById('recommendations');
        recommendationsDiv.innerHTML = ""; // Clear previous results
// Determing if any articles are found
        if (data.gpt_keywords && data.gpt_keywords.length > 0) {
            recommendationsDiv.innerHTML += `
                <h2>AI-Generated Keywords for "${query}"</h2>
                <ul>
                    ${data.gpt_keywords.map(keyword => `<li>${keyword}</li>`).join('')}
                </ul>
            `;
        } else {
            recommendationsDiv.innerHTML += "<p><strong>No AI insights found.</strong></p>";
        }

        // Display arXiv Article Recommendations
        if (data.arxiv_papers && Array.isArray(data.arxiv_papers) && data.arxiv_papers.length > 0) {
            let arxivContent = "<h2>Related arXiv Articles:</h2><ul>";
            data.arxiv_papers.forEach(article => {
                arxivContent += `<li><a href="${article.url}" target="_blank">${article.title}</a></li>`;
            });
            arxivContent += "</ul>";
            recommendationsDiv.innerHTML += arxivContent;
        } else {
            recommendationsDiv.innerHTML += "<p><strong>No related arXiv articles found.</strong></p>";
        }
// Error Message
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        document.getElementById('recommendations').innerHTML = `
            <p style="color: red;">There was an error retrieving the recommendations. Please try again later.</p>
        `;
    }
}
