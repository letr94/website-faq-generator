async function generateFAQ() {
    const urlInput = document.getElementById('urlInput');
    const customPrompt = document.getElementById('customPrompt');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const screenshots = document.getElementById('screenshots');
    const progressInfo = loading.querySelector('.progress-info');
    
    if (!urlInput.value) {
        alert('Please enter a URL');
        return;
    }

    loading.classList.remove('hidden');
    result.innerHTML = '';
    screenshots.classList.add('hidden');
    screenshots.querySelector('.screenshots-grid').innerHTML = '';

    // Update loading message periodically
    let loadingStep = 0;
    const loadingMessages = [
        'Connecting to website...',
        'Loading main page content...',
        'Discovering additional pages...',
        'Analyzing website content...',
        'Generating comprehensive FAQs...'
    ];
    
    const loadingInterval = setInterval(() => {
        if (loadingStep < loadingMessages.length) {
            progressInfo.textContent = loadingMessages[loadingStep];
            loadingStep++;
        }
    }, 3000);

    try {
        const response = await fetch('/generate-faq', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url: urlInput.value,
                custom_prompt: customPrompt.value.trim()
            })
        });

        const data = await response.json();
        
        if (data.error) {
            result.innerHTML = `<div class="error">${data.error}</div>`;
        } else {
            // Display screenshots
            const screenshotsGrid = screenshots.querySelector('.screenshots-grid');
            data.screenshots.forEach(screenshot => {
                const screenshotItem = document.createElement('div');
                screenshotItem.className = 'screenshot-item';
                screenshotItem.innerHTML = `
                    <h3>${screenshot.type} Page</h3>
                    <img src="${screenshot.path}" alt="${screenshot.type} page screenshot" loading="lazy">
                    <div class="page-url">${screenshot.url}</div>
                `;
                screenshotsGrid.appendChild(screenshotItem);
            });
            screenshots.classList.remove('hidden');
            
            // Display FAQs
            result.innerHTML = formatFAQs(data.faqs);
        }
    } catch (error) {
        result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    } finally {
        clearInterval(loadingInterval);
        loading.classList.add('hidden');
    }
}

function formatFAQs(faqText) {
    // Split the text into lines and format as HTML
    const lines = faqText.split('\n');
    let html = '';
    let currentQuestion = '';

    for (const line of lines) {
        if (line.trim() === '') continue;
        
        if (line.startsWith('Q:') || line.startsWith('Question:')) {
            if (currentQuestion) {
                html += '</div>';
            }
            currentQuestion = line;
            html += `<div class="faq-item"><h3>${line}</h3>`;
        } else if (line.startsWith('A:') || line.startsWith('Answer:')) {
            html += `<p>${line}</p>`;
        } else {
            html += `<p>${line}</p>`;
        }
    }

    if (currentQuestion) {
        html += '</div>';
    }

    return html;
}
