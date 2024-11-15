# Website FAQ Generator

Automatically generate comprehensive FAQs for any website using AI. This tool scrapes website content and uses OpenAI's GPT to create relevant, accurate FAQs.

## Features

- 🌐 Website Content Scraping
- 🤖 AI-Powered FAQ Generation
- 📸 Website Screenshots
- ⚡ Fast Processing
- 🎨 Clean, Modern UI

## Tech Stack

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- AI: OpenAI GPT-3.5
- Web Scraping: Playwright
- Deployment: Railway.app

## Quick Start

1. Clone the repository:
```bash
git clone <your-repo-url>
cd website-faq-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. Run the application:
```bash
python app.py
```

## Usage

1. Enter any website URL
2. Click "Generate FAQ"
3. Get AI-generated FAQs and website screenshots

## Deployment

This application is configured for easy deployment on Railway.app. See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed deployment instructions.

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_ENV`: Development/Production
- `SECRET_KEY`: Flask secret key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - feel free to use this project for any purpose.

## Support

For support, open an issue in the GitHub repository.
