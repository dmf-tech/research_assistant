document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const resultsContainer = document.getElementById('results');
    const exportButton = document.getElementById('exportButton');
    let searchResults = [];

    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const query = document.getElementById('searchQuery').value;
        
        // Show loading state
        resultsContainer.innerHTML = '<p class="loading">Searching...</p>';
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `query=${encodeURIComponent(query)}`
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Search failed');
            }
            
            if (data.error) {
                throw new Error(data.error);
            }

            searchResults = data.results || [];
            displayResults(searchResults);
            exportButton.disabled = !searchResults.length;
            
        } catch (error) {
            resultsContainer.innerHTML = `
                <div class="error-message">
                    <p>${error.message || 'Error performing search. Please try again.'}</p>
                    <button onclick="retrySearch()">Retry Search</button>
                </div>`;
            console.error('Search error:', error);
        }
    });

    window.retrySearch = function() {
        searchForm.dispatchEvent(new Event('submit'));
    };

    function displayResults(results) {
        if (!results.length) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }

        const resultsHTML = results.map((result, index) => `
            <div class="result-item">
                <h3>
                    <a href="${result.link}" target="_blank">${result.title}</a>
                </h3>
                <p>${result.snippet}</p>
                <button onclick="analyzeContent('${result.link}', ${index})">
                    Analyze
                </button>
            </div>
        `).join('');

        resultsContainer.innerHTML = resultsHTML;
    }

    window.analyzeContent = async function(url, index) {
        const resultItem = document.querySelectorAll('.result-item')[index];
        resultItem.innerHTML += '<p>Analyzing...</p>';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}`
            });

            const data = await response.json();
            displayAnalysis(data, index);
        } catch (error) {
            resultItem.innerHTML += '<p>Error analyzing content.</p>';
            console.error('Analysis error:', error);
        }
    };

    function displayAnalysis(analysis, index) {
        const resultItem = document.querySelectorAll('.result-item')[index];
        const analysisHTML = `
            <div class="analysis-results">
                <h4>Analysis Results</h4>
                <p>Title: ${analysis.article.title}</p>
                <p>Authors: ${analysis.article.authors.join(', ') || 'Not available'}</p>
                <p>Published: ${analysis.article.publish_date || 'Not available'}</p>
                <p>Domain Info: ${JSON.stringify(analysis.domain_info, null, 2)}</p>
            </div>
        `;
        resultItem.innerHTML += analysisHTML;
    }

    exportButton.addEventListener('click', async function() {
        const format = document.getElementById('exportFormat').value;
        
        try {
            const response = await fetch('/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    format: format,
                    sections: searchResults.map(result => ({
                        title: result.title,
                        content: result.snippet
                    }))
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `research_report.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            alert('Error exporting results. Please try again.');
            console.error('Export error:', error);
        }
    });
}); 