// Global variables
let currentBook = null;
let currentChapter = null;
let ttsEnabled = true;
let ttsSpeed = 1.0;
let currentSpeech = null;

// DOM loaded event
document.addEventListener('DOMContentLoaded', function() {
    loadBooks();
    loadAlphabet();
    initializeTTS();
    
    // Modal functionality
    const modal = document.getElementById('letter-modal');
    const closeBtn = document.getElementsByClassName('close')[0];
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
        stopTTS(); // Stop any playing TTS when modal closes
    }
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            stopTTS();
        }
    }
    
    // Enter key for search
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchVerses();
        }
    });
    
    // Enter key for converter
    document.getElementById('hebrew-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            convertText();
        }
    });
    
    // TTS speed control
    document.getElementById('tts-speed').addEventListener('change', function(e) {
        ttsSpeed = parseFloat(e.target.value);
        stopTTS(); // Stop current speech when speed changes
    });
});

// Navigation functions
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Reset views for books section
    if (sectionName === 'books') {
        showBooks();
    }
}

// Books section functions
async function loadBooks() {
    try {
        const response = await fetch('/api/books');
        const books = await response.json();
        
        const booksContainer = document.getElementById('books-list');
        booksContainer.innerHTML = books.map(book => `
            <div class="book-card" onclick="showBookChapters(${book.id})">
                <div class="book-name">${book.name}</div>
                <div class="book-hebrew">${book.hebrew_name}</div>
                <div class="book-paleo">${book.paleo_name}</div>
                <div class="chapter-count">${book.chapter_count} chapters</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading books:', error);
        document.getElementById('books-list').innerHTML = '<p>Error loading books. Please try again.</p>';
    }
}

async function showBookChapters(bookId) {
    try {
        const response = await fetch(`/api/books/${bookId}`);
        const book = await response.json();
        currentBook = book;
        
        document.getElementById('books-list').classList.add('hidden');
        document.getElementById('current-book-title').textContent = `${book.name} (${book.hebrew_name})`;
        
        // Generate chapter buttons
        const chaptersContainer = document.getElementById('chapters-list');
        const chapters = Array.from({length: book.chapter_count}, (_, i) => i + 1);
        
        chaptersContainer.innerHTML = chapters.map(chapterNum => `
            <div class="chapter-card" onclick="showChapterVerses(${bookId}, ${chapterNum})">
                ${chapterNum}
            </div>
        `).join('');
        
        document.getElementById('chapter-view').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading book chapters:', error);
    }
}

async function showChapterVerses(bookId, chapterNumber) {
    try {
        const response = await fetch(`/api/books/${bookId}/chapters/${chapterNumber}`);
        const chapter = await response.json();
        currentChapter = chapter;
        
        document.getElementById('chapter-view').classList.add('hidden');
        document.getElementById('current-chapter-title').textContent = 
            `${chapter.book.name} Chapter ${chapter.chapter_number}`;
        
        const versesContainer = document.getElementById('verses-list');
        versesContainer.innerHTML = chapter.verses.map(verse => `
            <div class="verse-card">
                <div class="verse-header">
                    <div class="verse-number">Verse ${verse.verse_number}</div>
                    <button class="tts-btn" onclick="speakVerseEnhanced(${verse.id}, ${JSON.stringify(verse).replace(/"/g, '&quot;')})">
                        <i class="fas fa-play"></i>
                    </button>
                </div>
                <div class="verse-paleo">${verse.paleo_text}</div>
                <div class="verse-paleo-transliteration"><strong>Paleo:</strong> ${verse.paleo_transliteration || verse.modern_transliteration}</div>
                <div class="verse-hebrew">${verse.hebrew_text}</div>
                <div class="verse-modern-transliteration"><strong>Modern:</strong> ${verse.modern_transliteration}</div>
                <div class="verse-english">${verse.english_translation || ''}</div>
                ${verse.literal_translation ? `<div class="verse-literal"><strong>Literal:</strong> ${verse.literal_translation}</div>` : ''}
            </div>
        `).join('');
        
        document.getElementById('verse-view').classList.remove('hidden');
    } catch (error) {
        console.error('Error loading chapter verses:', error);
    }
}

function showBooks() {
    document.getElementById('books-list').classList.remove('hidden');
    document.getElementById('chapter-view').classList.add('hidden');
    document.getElementById('verse-view').classList.add('hidden');
}

function showChapters() {
    document.getElementById('chapter-view').classList.remove('hidden');
    document.getElementById('verse-view').classList.add('hidden');
}

// Alphabet section functions
async function loadAlphabet() {
    try {
        const response = await fetch('/api/alphabet');
        const letters = await response.json();
        
        const alphabetContainer = document.getElementById('alphabet-grid');
        alphabetContainer.innerHTML = letters.map(letter => `
            <div class="letter-card" onclick="showLetterDetails('${letter.letter}')">
                <div class="letter-symbols">
                    <div class="hebrew-letter">${letter.letter}</div>
                    <div class="paleo-symbol">${letter.paleo_symbol}</div>
                </div>
                <div class="letter-name">${letter.name}</div>
                <div class="letter-meaning">${letter.meaning.split(',')[0]}</div>
                <button class="tts-btn letter-tts" onclick="event.stopPropagation(); speakLetter('${letter.letter}', '${letter.paleo_symbol}', '${letter.name}')">
                    <i class="fas fa-play"></i>
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading alphabet:', error);
        document.getElementById('alphabet-grid').innerHTML = '<p>Error loading alphabet. Please try again.</p>';
    }
}

async function showLetterDetails(letter) {
    try {
        const response = await fetch(`/api/alphabet/${letter}`);
        const letterData = await response.json();
        
        // Populate modal with letter data
        document.getElementById('modal-letter-name').textContent = letterData.name;
        document.getElementById('modal-hebrew-letter').textContent = letterData.letter;
        document.getElementById('modal-paleo-symbol').textContent = letterData.paleo_symbol;
        document.getElementById('modal-letter-meaning').textContent = letterData.meaning;
        document.getElementById('modal-pictograph').textContent = letterData.pictograph_description;
        document.getElementById('modal-sound').textContent = letterData.sound;
        document.getElementById('modal-numerical').textContent = letterData.numerical_value;
        
        // Show modal
        document.getElementById('letter-modal').style.display = 'block';
    } catch (error) {
        console.error('Error loading letter details:', error);
    }
}

// Search functions
async function searchVerses() {
    const query = document.getElementById('search-input').value.trim();
    const searchType = document.getElementById('search-type').value;
    
    if (!query) {
        alert('Please enter a search term');
        return;
    }
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&type=${searchType}`);
        const results = await response.json();
        
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching verses:', error);
        document.getElementById('search-results').innerHTML = '<p>Error performing search. Please try again.</p>';
    }
}

function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    
    if (results.count === 0) {
        container.innerHTML = `
            <div class="search-result">
                <p>No results found for "${results.query}"</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <h3>Found ${results.count} result(s) for "${results.query}"</h3>
        ${results.results.map(verse => `
            <div class="search-result">
                <div class="result-header">
                    <div class="result-reference">
                        ${verse.book.name} ${verse.chapter.chapter_number}:${verse.verse_number}
                    </div>
                    <button class="tts-btn" onclick="speakVerse('${verse.id}', '${verse.hebrew_text.replace(/'/g, "\\'")}', '${verse.paleo_text.replace(/'/g, "\\'")}')">
                        <i class="fas fa-play"></i>
                    </button>
                </div>
                <div class="verse-paleo">${verse.paleo_text}</div>
                <div class="verse-hebrew">${verse.hebrew_text}</div>
                <div class="verse-transliteration">${verse.transliteration}</div>
                ${verse.english_translation ? `<div class="verse-english">${verse.english_translation}</div>` : ''}
            </div>
        `).join('')}
    `;
}

// Converter functions
async function convertText() {
    const hebrewText = document.getElementById('hebrew-input').value.trim();
    
    if (!hebrewText) {
        alert('Please enter Hebrew text to convert');
        return;
    }
    
    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: hebrewText })
        });
        
        const result = await response.json();
        
        // Display conversion result
        document.getElementById('original-hebrew').textContent = result.hebrew;
        document.getElementById('paleo-result').textContent = result.paleo;
        document.getElementById('pronunciation-result').textContent = result.pronunciation;
        
        document.getElementById('conversion-result').classList.remove('hidden');
    } catch (error) {
        console.error('Error converting text:', error);
        alert('Error converting text. Please try again.');
    }
}

// Utility functions
function highlightSearchTerm(text, term) {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Could show a toast notification here
        console.log('Text copied to clipboard');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+K to focus search
    if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        document.getElementById('search-input').focus();
    }
    
    // Escape to close modal or stop TTS
    if (e.key === 'Escape') {
        document.getElementById('letter-modal').style.display = 'none';
        stopTTS();
    }
    
    // Spacebar to stop TTS
    if (e.key === ' ' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        stopTTS();
    }
});

// ==================== TTS FUNCTIONALITY ====================

function initializeTTS() {
    // Check if browser supports Speech Synthesis
    if (!('speechSynthesis' in window)) {
        console.warn('Speech Synthesis not supported in this browser');
        document.getElementById('global-tts-toggle').style.display = 'none';
        return;
    }
    
    // Initialize TTS status
    updateTTSStatus();
    
    console.log('TTS initialized successfully');
}

function toggleGlobalTTS() {
    ttsEnabled = !ttsEnabled;
    updateTTSStatus();
    
    if (!ttsEnabled) {
        stopTTS();
    }
}

function updateTTSStatus() {
    const statusElement = document.getElementById('tts-status');
    const iconElement = document.querySelector('#global-tts-toggle i');
    
    if (ttsEnabled) {
        statusElement.textContent = 'TTS On';
        iconElement.className = 'fas fa-volume-up';
        document.getElementById('global-tts-toggle').classList.remove('tts-disabled');
    } else {
        statusElement.textContent = 'TTS Off';
        iconElement.className = 'fas fa-volume-mute';
        document.getElementById('global-tts-toggle').classList.add('tts-disabled');
    }
}

function stopTTS() {
    if (currentSpeech) {
        speechSynthesis.cancel();
        currentSpeech = null;
    }
    
    // Remove playing states from all TTS buttons
    document.querySelectorAll('.tts-btn').forEach(btn => {
        btn.classList.remove('playing');
        const icon = btn.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-play';
        }
    });
}

async function speakVerse(verseId, hebrewText, paleoText) {
    // Legacy function for backward compatibility
    return speakVerseEnhanced(verseId, {
        id: verseId,
        hebrew_text: hebrewText,
        paleo_text: paleoText,
        paleo_transliteration: '',
        modern_transliteration: ''
    });
}

async function speakVerseEnhanced(verseId, verseData) {
    if (!ttsEnabled || !('speechSynthesis' in window)) {
        return;
    }
    
    try {
        // Stop any currently playing speech
        stopTTS();
        
        // Get TTS pronunciation from API with all verse data
        const response = await fetch('/api/tts/verse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                verse_id: verseId,
                hebrew: verseData.hebrew_text || '',
                paleo: verseData.paleo_text || '',
                paleo_transliteration: verseData.paleo_transliteration || ''
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error('TTS API error:', data.error);
            return;
        }
        
        console.log('TTS using:', data.pronunciation_source, 'Text:', data.tts_text);
        
        // Create speech synthesis utterance
        const utterance = new SpeechSynthesisUtterance(data.tts_text);
        utterance.rate = ttsSpeed * 0.9; // Slightly slower for better pronunciation
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Try to use a voice that might pronounce Hebrew-like sounds better
        const voices = speechSynthesis.getVoices();
        const preferredVoices = voices.filter(voice => 
            voice.lang.includes('he') || // Hebrew
            voice.lang.includes('ar') || // Arabic (similar sounds)
            voice.lang.includes('en')    // English as fallback
        );
        
        if (preferredVoices.length > 0) {
            utterance.voice = preferredVoices[0];
        }
        
        // Set up event listeners
        const ttsButton = document.querySelector(`[onclick*="speakVerseEnhanced(${verseId}"]`);
        
        utterance.onstart = function() {
            currentSpeech = utterance;
            if (ttsButton) {
                ttsButton.classList.add('playing');
                const icon = ttsButton.querySelector('i');
                if (icon) icon.className = 'fas fa-stop';
            }
            // Highlight the verse being spoken
            const verseCard = ttsButton?.closest('.verse-card');
            if (verseCard) verseCard.classList.add('tts-playing');
        };
        
        utterance.onend = function() {
            currentSpeech = null;
            if (ttsButton) {
                ttsButton.classList.remove('playing');
                const icon = ttsButton.querySelector('i');
                if (icon) icon.className = 'fas fa-play';
            }
            // Remove highlight
            const verseCard = ttsButton?.closest('.verse-card');
            if (verseCard) verseCard.classList.remove('tts-playing');
        };
        
        utterance.onerror = function(event) {
            console.error('TTS Error:', event.error);
            currentSpeech = null;
            if (ttsButton) {
                ttsButton.classList.remove('playing');
                const icon = ttsButton.querySelector('i');
                if (icon) icon.className = 'fas fa-play';
            }
            // Remove highlight
            const verseCard = ttsButton?.closest('.verse-card');
            if (verseCard) verseCard.classList.remove('tts-playing');
        };
        
        // Speak the text
        speechSynthesis.speak(utterance);
        
    } catch (error) {
        console.error('Error in enhanced TTS:', error);
    }
}

async function speakLetter(letter, paleoSymbol, letterName) {
    if (!ttsEnabled || !('speechSynthesis' in window)) {
        return;
    }
    
    try {
        stopTTS();
        
        const response = await fetch('/api/tts/letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                letter: letter,
                paleo_symbol: paleoSymbol,
                name: letterName
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error('TTS API error:', data.error);
            return;
        }
        
        // Speak the letter name followed by its sound
        const text = `${data.name_pronunciation}. Sound: ${data.sound_pronunciation}`;
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = ttsSpeed * 0.8; // Slightly slower for letters
        utterance.pitch = 1.1;
        utterance.volume = 1.0;
        
        const ttsButton = document.querySelector(`[onclick="speakLetter('${letter}', '${paleoSymbol}', '${letterName}')"]`);
        
        utterance.onstart = function() {
            currentSpeech = utterance;
            if (ttsButton) {
                ttsButton.classList.add('playing');
                const icon = ttsButton.querySelector('i');
                if (icon) icon.className = 'fas fa-stop';
            }
        };
        
        utterance.onend = function() {
            currentSpeech = null;
            if (ttsButton) {
                ttsButton.classList.remove('playing');
                const icon = ttsButton.querySelector('i');
                if (icon) icon.className = 'fas fa-play';
            }
        };
        
        speechSynthesis.speak(utterance);
        
    } catch (error) {
        console.error('Error in letter TTS:', error);
    }
}

async function speakWord(word) {
    if (!ttsEnabled || !('speechSynthesis' in window)) {
        return;
    }
    
    try {
        stopTTS();
        
        const response = await fetch('/api/tts/word', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ word: word })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error('TTS API error:', data.error);
            return;
        }
        
        const utterance = new SpeechSynthesisUtterance(data.tts_text);
        utterance.rate = ttsSpeed;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        speechSynthesis.speak(utterance);
        
    } catch (error) {
        console.error('Error in word TTS:', error);
    }
}