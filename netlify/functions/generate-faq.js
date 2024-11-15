const chromium = require('@sparticuz/chromium')
const playwright = require('playwright-core')
const { Configuration, OpenAIApi } = require('openai')

// Configure OpenAI
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
})
const openai = new OpenAIApi(configuration)

// Configure Playwright
const getChromium = async () => {
  const executablePath = await chromium.executablePath
  const browser = await playwright.chromium.launch({
    args: chromium.args,
    executablePath: executablePath,
    headless: true,
  })
  return browser
}

// Helper function to extract text content
const extractContent = async (page) => {
  const content = await page.evaluate(() => {
    const getVisibleText = (element) => {
      if (!element) return ''
      const style = window.getComputedStyle(element)
      if (style.display === 'none' || style.visibility === 'hidden') return ''
      
      let text = ''
      for (let child of element.childNodes) {
        if (child.nodeType === 3) text += child.textContent.trim() + ' '
        else if (child.nodeType === 1) text += getVisibleText(child) + ' '
      }
      return text.trim()
    }
    return getVisibleText(document.body)
  })
  return content
}

// Main handler
exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' }
  }

  try {
    const { url } = JSON.parse(event.body)
    if (!url) {
      return { 
        statusCode: 400, 
        body: JSON.stringify({ error: 'URL is required' })
      }
    }

    // Initialize browser
    const browser = await getChromium()
    const context = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    // Navigate and extract content
    const page = await context.newPage()
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    const content = await extractContent(page)
    
    // Take screenshot
    const screenshot = await page.screenshot({ 
      type: 'jpeg',
      quality: 80,
      fullPage: true
    })
    
    await browser.close()

    // Generate FAQ using OpenAI
    const completion = await openai.createChatCompletion({
      model: "gpt-3.5-turbo",
      messages: [{
        role: "system",
        content: "You are a helpful assistant that generates comprehensive FAQs based on website content. Create clear, concise questions and answers that would be most useful for users of this website."
      }, {
        role: "user",
        content: `Generate a list of 5-10 frequently asked questions and answers based on this website content: ${content.substring(0, 4000)}`
      }],
      temperature: 0.7,
      max_tokens: 1000
    })

    // Process the response
    const faq = completion.data.choices[0].message.content

    return {
      statusCode: 200,
      body: JSON.stringify({
        faq,
        screenshot: screenshot.toString('base64')
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    }

  } catch (error) {
    console.error('Error:', error)
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        error: 'Failed to generate FAQ',
        details: error.message 
      })
    }
  }
}
