# 🕊️ Paleo Hebrew Bible

A comprehensive digital study platform for the complete Bible with ancient Hebrew script, Greek New Testament, and modern study tools.

![Bible Study Platform](https://img.shields.io/badge/Bible-Study%20Platform-blue)
![Hebrew Scripture](https://img.shields.io/badge/Hebrew-Scripture-gold)
![Paleo Hebrew](https://img.shields.io/badge/Paleo-Hebrew-purple)
![Strong's Concordance](https://img.shields.io/badge/Strong's-Concordance-green)

## ✨ Features

### 📖 Complete Biblical Text
- **39 Hebrew Bible Books** (Torah, Nevi'im, Ketuvim)
- **27 New Testament Books** with Greek text and KJV translations
- **24,983 total verses** across all 66 books
- **1,189 chapters** with complete structure

### 🔤 Ancient Scripts & Languages
- **Paleo Hebrew Script** (𐤀-𐤕) for authentic ancient appearance
- **Modern Hebrew** with vowel points (nikud)
- **Greek New Testament** with transliterations
- **Hebrew consonantal text** for linguistic study

### 🔍 Study Tools
- **Strong's Concordance** integration (H/G numbers)
- **Transliterations** for pronunciation guidance
- **Literal translations** alongside standard translations
- **Morphological analysis** fields for advanced study

### 🎵 Text-to-Speech (TTS)
- **Ancient Hebrew pronunciation** based on Pre-Exilic phonology (c. 1000-600 BCE)
- **Paleo transliterations** like "barashyt bara" for Genesis 1:1
- **Web Speech API** integration for modern browsers
- **Authentic biblical pronunciation** following historical linguistics

## What is Paleo Hebrew?

Paleo Hebrew is the original ancient script used to write Hebrew before the adoption of the Aramaic-derived square script (Ashuri) that is used today. Each letter was originally a pictograph representing physical objects and concepts:

- **Aleph (𐤀)** - Bull's head representing strength, leadership
- **Bet (𐤁)** - House/tent representing dwelling, family
- **Gimel (𐤂)** - Camel's foot representing walking, journey
- And 19 more letters, each with deep pictographic meaning...

## Installation and Setup

### Prerequisites

- Python 3.11+
- pip (Python package manager)

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd /path/to/paleo
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv paleo_env
   
   # On macOS/Linux:
   source paleo_env/bin/activate
   
   # On Windows:
   paleo_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python init_data.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser and visit:**
   ```
   http://localhost:5000
   ```

## API Endpoints

The application provides a RESTful API with the following endpoints:

### Books and Verses
- `GET /api/books` - List all biblical books
- `GET /api/books/{book_id}` - Get specific book with chapters
- `GET /api/books/{book_id}/chapters/{chapter_number}` - Get chapter with verses

### Alphabet
- `GET /api/alphabet` - Get complete Paleo Hebrew alphabet
- `GET /api/alphabet/{letter}` - Get detailed info about a specific letter

### Search and Conversion
- `GET /api/search?q={query}&type={search_type}` - Search verses
- `POST /api/convert` - Convert Hebrew text to Paleo Hebrew
- `POST /api/analyze` - Analyze Paleo Hebrew word meanings
- `GET /api/pronunciation/{word}` - Get pronunciation guide

## Deployment

### Heroku Deployment

1. **Install Heroku CLI and login:**
   ```bash
   # Install Heroku CLI (macOS with Homebrew)
   brew tap heroku/brew && brew install heroku
   
   # Login to Heroku
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   heroku create your-paleo-bible-app
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY=your-super-secret-key
   heroku config:set FLASK_ENV=production
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Initialize database:**
   ```bash
   heroku run python init_data.py
   ```

### Railway Deployment

1. **Connect to Railway:**
   - Go to [Railway](https://railway.app)
   - Import your GitHub repository
   - Railway will automatically detect the Python app

2. **Environment Variables:**
   Set these in Railway dashboard:
   - `SECRET_KEY`: Your secret key
   - `FLASK_ENV`: production

3. **Custom Start Command:**
   ```
   python init_data.py && python app.py
   ```

### Other Platforms (Render, DigitalOcean, etc.)

The application is designed to work with any platform that supports Python Flask applications. Key requirements:

- Python 3.11+
- Install dependencies from requirements.txt
- Run database initialization: `python init_data.py`
- Start application: `python app.py`

## Project Structure

```
paleo/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── init_data.py           # Database initialization script
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── runtime.txt           # Python version specification
├── README.md             # This file
├── data/
│   └── paleo_alphabet.py # Paleo Hebrew alphabet data
├── utils/
│   ├── __init__.py
│   └── hebrew_converter.py # Hebrew conversion utilities
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── styles.css    # Application styles
    └── js/
        └── app.js        # Frontend JavaScript
```

## Usage Guide

### Browsing Scripture

1. **Books Tab**: Browse available biblical books
2. **Click a book**: View chapters in that book
3. **Click a chapter**: Read verses in Paleo Hebrew, Hebrew, and transliteration

### Exploring the Alphabet

1. **Alphabet Tab**: View all 22 Paleo Hebrew letters
2. **Click any letter**: See detailed information about its pictographic meaning
3. **Learn the connections**: Understand how each letter's shape relates to its meaning

### Searching

1. **Search Tab**: Enter Hebrew text, English words, or concepts
2. **Choose search type**: Hebrew only, Paleo Hebrew only, English only, or all
3. **View results**: See matching verses with full context

### Converting Text

1. **Converter Tab**: Enter modern Hebrew text
2. **Click Convert**: Get Paleo Hebrew version with pronunciation guide
3. **Learn pronunciation**: Use the transliteration guide

## Understanding Paleo Hebrew Letters

Each letter tells a story:

- **Visual**: What the original pictograph looked like
- **Meaning**: The concept it represented
- **Sound**: How it was pronounced
- **Usage**: How it was used in words to convey meaning

For example, the word "house" (בית):
- ב (Bet) = House pictograph
- י (Yod) = Hand/work pictograph  
- ת (Tav) = Mark/sign pictograph

Together: "House of work/activity with a sign" - a dwelling place where activity happens.

## Contributing

This project aims to make ancient Hebrew script accessible to modern learners. Contributions welcome for:

- Additional biblical text
- Improved pronunciation guides
- Enhanced letter analysis
- UI/UX improvements
- Mobile responsiveness
- Performance optimizations

## Technical Notes

- **Unicode Support**: Uses proper Unicode ranges for Paleo Hebrew (𐤀-𐤕)
- **RTL Text**: Properly handles right-to-left Hebrew text rendering
- **Responsive Design**: Works on desktop and mobile devices
- **API-First**: Clean REST API for integration with other applications
- **Progressive Enhancement**: Works with JavaScript disabled (basic functionality)

## License

This project is open source and available for educational and religious purposes. The Paleo Hebrew alphabet information is based on historical and archaeological research.

## Support

For questions, issues, or suggestions:
- Create an issue on GitHub
- Email: [your-email@example.com]
- Documentation: See API endpoints above

---

*"In the beginning was the Word"* - Now explore it in its original script.