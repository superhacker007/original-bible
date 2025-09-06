// Global variables
let currentBook = null;
let currentChapter = null;
let ttsEnabled = true;
let ttsSpeed = 1.0;
let currentSpeech = null;
let isAuthenticated = false;

// DOM loaded event
document.addEventListener('DOMContentLoaded', function() {
    loadBooks();
    loadAlphabet();
    initializeTTS();
    checkAuthStatus();
    
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
    
    // Load facts when DOM is ready
    loadGodFacts();
    
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
    
    // Load Strong's data when section is shown
    if (sectionName === 'strongs' && !strongsData) {
        loadStrongs();
    }
    
    // Load Dictionary data when section is shown
    if (sectionName === 'dictionary' && !dictionaryData) {
        loadDictionary();
    }
    
    // Load Admin data when section is shown
    if (sectionName === 'admin') {
        if (isAuthenticated) {
            loadAdminStats();
            loadAdminFactsList();
        } else {
            showLoginPrompt();
        }
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
                <div class="verse-paleo">${makePaleoWordsInteractive(verse.paleo_text, verse.hebrew_text, verse)}</div>
                <div class="verse-paleo-transliteration"><strong>Paleo:</strong> ${verse.paleo_transliteration || verse.modern_transliteration}</div>
                <div class="verse-hebrew">${verse.hebrew_text}</div>
                <div class="verse-modern-transliteration"><strong>Modern:</strong> ${verse.modern_transliteration}</div>
                <div class="verse-english">${verse.english_translation || ''}</div>
                ${verse.literal_translation ? `<div class="verse-literal"><strong>Literal:</strong> ${verse.literal_translation}</div>` : ''}
            </div>
        `).join('');
        
        document.getElementById('verse-view').classList.remove('hidden');
        
        // Update navigation buttons
        updateChapterNavigation();
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

// Chapter Navigation Functions
async function updateChapterNavigation() {
    if (!currentChapter) return;
    
    const prevBtn = document.getElementById('prev-chapter-btn');
    const nextBtn = document.getElementById('next-chapter-btn');
    
    try {
        // Get navigation info from API
        const response = await fetch(`/api/books/${currentChapter.book.id}/chapters/${currentChapter.chapter_number}/navigation`);
        const navInfo = await response.json();
        
        // Update previous button
        if (navInfo.previous) {
            prevBtn.disabled = false;
            prevBtn.innerHTML = `<i class="fas fa-chevron-left"></i> ${navInfo.previous.book_name} ${navInfo.previous.chapter_number}`;
            prevBtn.setAttribute('data-book-id', navInfo.previous.book_id);
            prevBtn.setAttribute('data-chapter', navInfo.previous.chapter_number);
        } else {
            prevBtn.disabled = true;
            prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i> Previous Chapter';
        }
        
        // Update next button
        if (navInfo.next) {
            nextBtn.disabled = false;
            nextBtn.innerHTML = `${navInfo.next.book_name} ${navInfo.next.chapter_number} <i class="fas fa-chevron-right"></i>`;
            nextBtn.setAttribute('data-book-id', navInfo.next.book_id);
            nextBtn.setAttribute('data-chapter', navInfo.next.chapter_number);
        } else {
            nextBtn.disabled = true;
            nextBtn.innerHTML = 'Next Chapter <i class="fas fa-chevron-right"></i>';
        }
        
    } catch (error) {
        console.error('Error updating chapter navigation:', error);
        // Fallback to basic navigation within current book
        updateBasicNavigation();
    }
}

async function updateBasicNavigation() {
    if (!currentChapter) return;
    
    const prevBtn = document.getElementById('prev-chapter-btn');
    const nextBtn = document.getElementById('next-chapter-btn');
    
    // Simple navigation within current book
    const currentChapterNum = currentChapter.chapter_number;
    const totalChapters = currentChapter.book.chapter_count || 50; // fallback
    
    // Previous chapter
    if (currentChapterNum > 1) {
        prevBtn.disabled = false;
        prevBtn.innerHTML = `<i class="fas fa-chevron-left"></i> Chapter ${currentChapterNum - 1}`;
        prevBtn.setAttribute('data-book-id', currentChapter.book.id);
        prevBtn.setAttribute('data-chapter', currentChapterNum - 1);
    } else {
        prevBtn.disabled = true;
    }
    
    // Next chapter
    if (currentChapterNum < totalChapters) {
        nextBtn.disabled = false;
        nextBtn.innerHTML = `Chapter ${currentChapterNum + 1} <i class="fas fa-chevron-right"></i>`;
        nextBtn.setAttribute('data-book-id', currentChapter.book.id);
        nextBtn.setAttribute('data-chapter', currentChapterNum + 1);
    } else {
        nextBtn.disabled = true;
    }
}

async function navigateToPrevChapter() {
    const prevBtn = document.getElementById('prev-chapter-btn');
    if (prevBtn.disabled) return;
    
    const bookId = prevBtn.getAttribute('data-book-id');
    const chapterNum = parseInt(prevBtn.getAttribute('data-chapter'));
    
    if (bookId && chapterNum) {
        await showChapterVerses(bookId, chapterNum);
        // Scroll to top of chapter
        document.getElementById('verse-view').scrollIntoView({ behavior: 'smooth' });
    }
}

async function navigateToNextChapter() {
    const nextBtn = document.getElementById('next-chapter-btn');
    if (nextBtn.disabled) return;
    
    const bookId = nextBtn.getAttribute('data-book-id');
    const chapterNum = parseInt(nextBtn.getAttribute('data-chapter'));
    
    if (bookId && chapterNum) {
        await showChapterVerses(bookId, chapterNum);
        // Scroll to top of chapter
        document.getElementById('verse-view').scrollIntoView({ behavior: 'smooth' });
    }
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
                <button class="tts-btn letter-tts" onclick="event.stopPropagation(); speakLetter('${letter.letter.replace(/'/g, "\\'")}', '${letter.paleo_symbol.replace(/'/g, "\\'")}', '${letter.name.replace(/'/g, "\\'")}')">
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
                <div class="verse-paleo">${makePaleoWordsInteractive(verse.paleo_text, verse.hebrew_text, verse)}</div>
                <div class="verse-hebrew">${verse.hebrew_text}</div>
                <div class="verse-transliteration">${verse.transliteration}</div>
                ${verse.english_translation ? `<div class="verse-english">${verse.english_translation}</div>` : ''}
            </div>
        `).join('')}
    `;
}

// God Facts functions
let currentFacts = [];
let currentFilter = 'all';
let factsOffset = 0;
const factsLimit = 12;

async function loadGodFacts(reset = true) {
    try {
        if (reset) {
            factsOffset = 0;
            currentFacts = [];
        }
        
        const response = await fetch(`/api/god-facts?category=${currentFilter}&offset=${factsOffset}&limit=${factsLimit}`);
        const data = await response.json();
        
        if (reset) {
            currentFacts = data.facts;
        } else {
            currentFacts.push(...data.facts);
        }
        
        displayGodFacts();
        
        // Update load more button
        const loadMoreBtn = document.getElementById('load-more-facts');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = data.has_more ? 'block' : 'none';
        }
        
        factsOffset += factsLimit;
        
    } catch (error) {
        console.error('Error loading God facts:', error);
        const factsGrid = document.getElementById('facts-grid');
        if (factsGrid) {
            factsGrid.innerHTML = '<p class="error-message">Error loading God facts. Please try again.</p>';
        }
    }
}

function displayGodFacts() {
    const factsGrid = document.getElementById('facts-grid');
    if (!factsGrid) return;
    
    if (currentFacts.length === 0) {
        factsGrid.innerHTML = `
            <div class="no-facts-message">
                <i class="fas fa-lightbulb"></i>
                <h3>No facts found</h3>
                <p>No amazing God facts available in this category yet.</p>
            </div>
        `;
        return;
    }
    
    factsGrid.innerHTML = currentFacts.map(fact => `
        <div class="fact-card" data-category="${fact.category}">
            <div class="fact-header">
                <span class="fact-category ${fact.category}">${fact.category}</span>
                <span class="fact-views"><i class="fas fa-eye"></i> ${fact.views}</span>
            </div>
            
            ${fact.image_url ? `<div class="fact-image">
                <img src="${fact.image_url}" alt="${fact.title}" loading="lazy">
            </div>` : ''}
            
            <div class="fact-content">
                <h3 class="fact-title">${fact.title}</h3>
                <p class="fact-excerpt">${fact.content.substring(0, 150)}${fact.content.length > 150 ? '...' : ''}</p>
                
                ${fact.source ? `<div class="fact-source">
                    <i class="fas fa-link"></i> ${fact.source}
                </div>` : ''}
                
                <div class="fact-footer">
                    <span class="fact-date">${new Date(fact.created_at).toLocaleDateString()}</span>
                    <button class="read-more-btn" onclick="showFactDetails(${fact.id})">
                        <i class="fas fa-book-open"></i> Read More
                    </button>
                </div>
            </div>
            
            ${fact.video_url ? `<div class="fact-video-indicator">
                <i class="fas fa-play-circle"></i> Has Video
            </div>` : ''}
        </div>
    `).join('');
}

function filterFacts(category) {
    currentFilter = category;
    
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Load facts with new filter
    loadGodFacts(true);
}

function loadMoreFacts() {
    loadGodFacts(false);
}

async function showFactDetails(factId) {
    try {
        const response = await fetch(`/api/god-facts/${factId}`);
        const fact = await response.json();
        
        // Create modal or detailed view
        showFactModal(fact);
        
    } catch (error) {
        console.error('Error loading fact details:', error);
        alert('Error loading fact details. Please try again.');
    }
}

function showFactModal(fact) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'fact-modal-overlay';
    modal.innerHTML = `
        <div class="fact-modal">
            <div class="fact-modal-header">
                <h2>${fact.title}</h2>
                <button class="fact-modal-close" onclick="closeFactModal()">&times;</button>
            </div>
            
            <div class="fact-modal-content">
                <div class="fact-modal-meta">
                    <span class="fact-category ${fact.category}">${fact.category}</span>
                    <span class="fact-date">${new Date(fact.created_at).toLocaleDateString()}</span>
                    <span class="fact-views"><i class="fas fa-eye"></i> ${fact.views}</span>
                </div>
                
                ${fact.image_url ? `<div class="fact-modal-image">
                    <img src="${fact.image_url}" alt="${fact.title}">
                </div>` : ''}
                
                <div class="fact-modal-text">
                    ${fact.content.split('\\n').map(p => `<p>${p}</p>`).join('')}
                </div>
                
                ${fact.video_url ? `<div class="fact-modal-video">
                    <video controls>
                        <source src="${fact.video_url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>` : ''}
                
                ${fact.source ? `<div class="fact-modal-source">
                    <strong>Source:</strong> ${fact.source}
                </div>` : ''}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

function closeFactModal() {
    const modal = document.querySelector('.fact-modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Admin Dashboard Functions
async function loadAdminStats() {
    try {
        const response = await fetch('/api/admin/facts-stats');
        if (response.status === 401) {
            isAuthenticated = false;
            showLoginPrompt();
            return;
        }
        const stats = await response.json();
        
        document.getElementById('total-facts').textContent = stats.total;
        document.getElementById('published-facts').textContent = stats.published;
        document.getElementById('draft-facts').textContent = stats.drafts;
        
    } catch (error) {
        console.error('Error loading admin stats:', error);
    }
}

function showAddFactForm() {
    const form = document.getElementById('add-fact-form');
    if (form) {
        form.classList.remove('hidden');
        document.getElementById('fact-title').focus();
    }
}

function hideAddFactForm() {
    const form = document.getElementById('add-fact-form');
    if (form) {
        form.classList.add('hidden');
        form.querySelector('#fact-form').reset();
        // Clear file previews
        document.getElementById('image-preview').innerHTML = '';
        document.getElementById('video-preview').innerHTML = '';
    }
}

function refreshFactsList() {
    loadAdminFactsList();
    loadAdminStats();
}

async function loadAdminFactsList() {
    try {
        const response = await fetch('/api/god-facts?status=all&limit=100');
        const data = await response.json();
        
        displayAdminFactsTable(data.facts);
        
    } catch (error) {
        console.error('Error loading admin facts list:', error);
    }
}

function displayAdminFactsTable(facts) {
    const tableContainer = document.getElementById('admin-facts-table');
    if (!tableContainer) return;
    
    if (facts.length === 0) {
        tableContainer.innerHTML = '<p>No facts created yet. Add your first amazing God fact!</p>';
        return;
    }
    
    tableContainer.innerHTML = `
        <table class="admin-facts-table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Views</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${facts.map(fact => `
                    <tr>
                        <td class="fact-title-cell">
                            ${fact.title}
                            ${fact.image_filename ? '<i class="fas fa-image" title="Has image"></i>' : ''}
                            ${fact.video_filename ? '<i class="fas fa-video" title="Has video"></i>' : ''}
                        </td>
                        <td><span class="category-badge ${fact.category}">${fact.category}</span></td>
                        <td><span class="status-badge ${fact.status}">${fact.status}</span></td>
                        <td>${fact.views}</td>
                        <td>${new Date(fact.created_at).toLocaleDateString()}</td>
                        <td class="actions-cell">
                            <button class="action-btn edit-btn" onclick="editFact(${fact.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn delete-btn" onclick="deleteFact(${fact.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            ${fact.status === 'draft' ? 
                                `<button class="action-btn publish-btn" onclick="publishFact(${fact.id})" title="Publish">
                                    <i class="fas fa-eye"></i>
                                </button>` : ''}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    const factForm = document.getElementById('fact-form');
    if (factForm) {
        factForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitFactForm();
        });
    }
    
    // File preview handlers
    const imageInput = document.getElementById('fact-image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            previewFile(e.target, 'image-preview', 'image');
        });
    }
    
    const videoInput = document.getElementById('fact-video');
    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            previewFile(e.target, 'video-preview', 'video');
        });
    }
});

function previewFile(input, previewId, type) {
    const preview = document.getElementById(previewId);
    const file = input.files[0];
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (type === 'image') {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px;">`;
            } else if (type === 'video') {
                preview.innerHTML = `<video src="${e.target.result}" controls style="max-width: 200px; max-height: 200px;"></video>`;
            }
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
    }
}

async function submitFactForm() {
    const form = document.getElementById('fact-form');
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/god-facts', {
            method: 'POST',
            body: formData
        });
        
        if (response.status === 401) {
            isAuthenticated = false;
            showLoginPrompt();
            alert('Your session has expired. Please log in again.');
            return;
        }
        
        const result = await response.json();
        
        if (response.ok) {
            alert('God fact created successfully!');
            hideAddFactForm();
            refreshFactsList();
        } else {
            alert('Error: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error submitting fact:', error);
        alert('Error creating fact. Please try again.');
    }
}

async function deleteFact(factId) {
    if (!confirm('Are you sure you want to delete this fact? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/god-facts/${factId}`, {
            method: 'DELETE'
        });
        
        if (response.status === 401) {
            isAuthenticated = false;
            showLoginPrompt();
            alert('Your session has expired. Please log in again.');
            return;
        }
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Fact deleted successfully');
            refreshFactsList();
        } else {
            alert('Error: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error deleting fact:', error);
        alert('Error deleting fact. Please try again.');
    }
}

async function publishFact(factId) {
    try {
        const formData = new FormData();
        formData.append('status', 'published');
        
        const response = await fetch(`/api/god-facts/${factId}`, {
            method: 'PUT',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Fact published successfully');
            refreshFactsList();
        } else {
            alert('Error: ' + result.error);
        }
        
    } catch (error) {
        console.error('Error publishing fact:', error);
        alert('Error publishing fact. Please try again.');
    }
}

function editFact(factId) {
    // For now, just show an alert. Could implement inline editing later
    alert(`Edit functionality for fact ${factId} would be implemented here`);
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
        
        const ttsButton = document.querySelector(`[onclick="speakLetter('${letter.replace(/'/g, "\\'")}', '${paleoSymbol.replace(/'/g, "\\'")}', '${letterName.replace(/'/g, "\\'")}')"]`);
        
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

// Strong's Concordance Functions
let strongsData = null;
let currentStrongsTab = 'hebrew';

// Dictionary Functions
let dictionaryData = null;

// Hebrew to Paleo Hebrew conversion mapping
const HEBREW_TO_PALEO = {
    'א': '𐤀', 'ב': '𐤁', 'ג': '𐤂', 'ד': '𐤃', 'ה': '𐤄', 'ו': '𐤅', 'ז': '𐤆', 'ח': '𐤇',
    'ט': '𐤈', 'י': '𐤉', 'כ': '𐤊', 'ך': '𐤊', 'ל': '𐤋', 'מ': '𐤌', 'ם': '𐤌', 'נ': '𐤍',
    'ן': '𐤍', 'ס': '𐤎', 'ע': '𐤏', 'פ': '𐤐', 'ף': '𐤐', 'צ': '𐤑', 'ץ': '𐤑', 'ק': '𐤒',
    'ר': '𐤓', 'ש': '𐤔', 'ת': '𐤕', ' ': ' ', '.': '.', ',': ',', ':': ':', ';': ';'
};

function hebrewToPaleo(hebrewText) {
    if (!hebrewText) return '';
    
    // Remove nikud (vowel points) first
    let cleanText = removeNikud(hebrewText);
    
    // Convert each character
    let paleoText = '';
    for (let char of cleanText) {
        paleoText += HEBREW_TO_PALEO[char] || char;
    }
    
    return paleoText;
}

function removeNikud(hebrewText) {
    // Remove Hebrew nikud/vowel points (Unicode ranges)
    return hebrewText.replace(/[\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7]/g, '');
}

async function loadStrongs() {
    try {
        const response = await fetch('/api/strongs');
        strongsData = await response.json();
        displayStrongsData(strongsData);
    } catch (error) {
        console.error('Error loading Strong\'s concordance:', error);
        const resultsDiv = document.getElementById('strongs-results');
        resultsDiv.innerHTML = '<div class="error-message">Error loading Strong\'s concordance data</div>';
    }
}

function displayStrongsData(data) {
    const resultsDiv = document.getElementById('strongs-results');
    const currentData = data[currentStrongsTab] || {};
    
    if (Object.keys(currentData).length === 0) {
        resultsDiv.innerHTML = '<div class="no-results">No results found</div>';
        return;
    }
    
    let html = '<div class="strongs-entries">';
    
    Object.entries(currentData).forEach(([strongNumber, entry]) => {
        // Convert Hebrew to Paleo Hebrew
        const paleoText = currentStrongsTab === 'hebrew' ? hebrewToPaleo(entry.word) : '';
        
        html += `
            <div class="strongs-entry">
                <div class="strongs-header">
                    <span class="strong-number">${strongNumber}</span>
                    <div class="word-display">
                        <div class="hebrew-word">${entry.word}</div>
                        ${paleoText ? `<span class="separator">→</span><div class="paleo-word">${paleoText}</div>` : ''}
                        <span class="separator">→</span>
                        <div class="transliteration">${entry.transliteration}</div>
                    </div>
                </div>
                <div class="strongs-content">
                    <div class="meaning">${entry.meaning}</div>
                    <div class="definition">${entry.definition}</div>
                    ${entry.root_meaning ? `
                        <div class="root-meaning-section">
                            <div class="root-meaning-label">Root Meaning:</div>
                            <div class="root-meaning-content">
                                <div class="pictographic-analysis">${entry.root_meaning.pictographic_analysis}</div>
                                <div class="formation-explanation">${entry.root_meaning.formation_explanation}</div>
                                <div class="original-concept">${entry.root_meaning.original_concept}</div>
                            </div>
                        </div>
                    ` : ''}
                    <div class="usage-count">Used ${entry.usage_count} times</div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}

function showStrongsTab(tab) {
    currentStrongsTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.strongs-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Display data for selected tab
    if (strongsData) {
        displayStrongsData(strongsData);
    }
}

async function searchStrongs() {
    const searchTerm = document.getElementById('strongs-search').value.trim();
    
    if (searchTerm === '') {
        loadStrongs();
        return;
    }
    
    try {
        const response = await fetch(`/api/strongs?search=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();
        displayStrongsData(data);
    } catch (error) {
        console.error('Error searching Strong\'s concordance:', error);
        const resultsDiv = document.getElementById('strongs-results');
        resultsDiv.innerHTML = '<div class="error-message">Error searching Strong\'s concordance</div>';
    }
}


// Add enter key support for Strong's search
document.addEventListener('DOMContentLoaded', function() {
    const strongsSearch = document.getElementById('strongs-search');
    if (strongsSearch) {
        strongsSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchStrongs();
            }
        });
    }
    
    // Dictionary search event listener
    const dictionarySearchInput = document.getElementById('dictionary-search');
    if (dictionarySearchInput) {
        dictionarySearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchDictionary();
            }
        });
    }
    
    // Word analyzer event listener
    const analyzerInput = document.getElementById('analyzer-input');
    if (analyzerInput) {
        analyzerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeWord();
            }
        });
    }
});

// Dictionary Functions
function loadDictionary() {
    const resultsContainer = document.getElementById('dictionary-results');
    resultsContainer.innerHTML = '<div class="loading-message">Loading Paleo Dictionary...</div>';
    
    console.log('Loading dictionary...');
    
    fetch('/api/paleo-dictionary')
        .then(response => {
            console.log('Dictionary API response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Dictionary API data:', data);
            if (data.entries && data.entries.length > 0) {
                console.log('Found', data.entries.length, 'entries');
                dictionaryData = data; // Store the data
                displayDictionaryEntries(data.entries);
            } else {
                console.log('No entries found or invalid data structure');
                resultsContainer.innerHTML = '<div class="no-results">No dictionary entries found.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading dictionary:', error);
            resultsContainer.innerHTML = '<div class="error-message">Error loading dictionary. Please try again.</div>';
        });
}

function searchDictionary() {
    const searchTerm = document.getElementById('dictionary-search').value.trim();
    const resultsContainer = document.getElementById('dictionary-results');
    
    if (!searchTerm) {
        loadDictionary();
        return;
    }
    
    resultsContainer.innerHTML = '<div class="loading-message">Searching...</div>';
    
    fetch(`/api/paleo-dictionary?search=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.entries && data.entries.length > 0) {
                displayDictionaryEntries(data.entries);
            } else {
                resultsContainer.innerHTML = '<div class="no-results">No matching entries found.</div>';
            }
        })
        .catch(error => {
            console.error('Error searching dictionary:', error);
            resultsContainer.innerHTML = '<div class="error-message">Error searching. Please try again.</div>';
        });
}

function analyzeWord() {
    const hebrewWord = document.getElementById('analyzer-input').value.trim();
    const resultContainer = document.getElementById('word-analysis-result');
    
    if (!hebrewWord) {
        resultContainer.classList.add('hidden');
        return;
    }
    
    resultContainer.innerHTML = '<div class="loading-message">Analyzing word...</div>';
    resultContainer.classList.remove('hidden');
    
    fetch(`/api/paleo-dictionary/analyze/${encodeURIComponent(hebrewWord)}`)
        .then(response => response.json())
        .then(data => {
            if (data.hebrew_word || data.error === undefined) {
                displayWordAnalysis(data);
            } else {
                resultContainer.innerHTML = '<div class="no-results">Word not found in dictionary.</div>';
            }
        })
        .catch(error => {
            console.error('Error analyzing word:', error);
            resultContainer.innerHTML = '<div class="error-message">Error analyzing word. Please try again.</div>';
        });
}

function displayDictionaryEntries(entries) {
    const resultsContainer = document.getElementById('dictionary-results');
    let html = '<div class="dictionary-entries">';
    
    entries.forEach(entry => {
        const paleContent = hebrewToPaleo(entry.hebrew_word);
        
        html += `
            <div class="dictionary-entry" onclick="showFullEntry('${entry.id}')">
                <div class="entry-header">
                    <div class="word-display">
                        <span class="hebrew-word">${entry.hebrew_word}</span>
                        <span class="arrow">→</span>
                        <span class="paleo-word">${paleContent}</span>
                        <span class="arrow">→</span>
                        <span class="transliteration">${entry.transliteration}</span>
                    </div>
                    <div class="english-meaning">${entry.english_meaning}</div>
                </div>
                <div class="pictographic-preview">
                    ${entry.pictographic_analysis}
                </div>
                ${entry.strong_number ? `<div class="strong-ref">Strong's: ${entry.strong_number}</div>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayWordAnalysis(entry) {
    const resultContainer = document.getElementById('word-analysis-result');
    const paleContent = convertHebrewToPaleo(entry.hebrew_word);
    
    let html = `
        <div class="word-analysis">
            <div class="analysis-header">
                <div class="word-display">
                    <span class="hebrew-word">${entry.hebrew_word}</span>
                    <span class="arrow">→</span>
                    <span class="paleo-word">${paleContent}</span>
                    <span class="arrow">→</span>
                    <span class="transliteration">${entry.transliteration}</span>
                </div>
                <div class="english-meaning">${entry.english_meaning}</div>
            </div>
            
            <div class="root-analysis">
                <h4>Root Letter Analysis:</h4>
                <div class="letter-breakdown">
    `;
    
    if (entry.letter_meanings && entry.letter_meanings.length > 0) {
        entry.letter_meanings.forEach(letterInfo => {
            const paleoLetter = hebrewToPaleo(letterInfo.letter);
            html += `
                <div class="letter-item">
                    <span class="letter-paleo-primary">${paleoLetter}</span>
                    <span class="letter-meaning">${letterInfo.meaning}</span>
                </div>
            `;
        });
    }
    
    html += `
                </div>
            </div>
            
            <div class="pictographic-section">
                <h4>Pictographic Analysis:</h4>
                <p>${entry.pictographic_analysis}</p>
            </div>
            
            <div class="original-concept">
                <h4>Original Concept:</h4>
                <p>${entry.original_concept}</p>
            </div>
            
            <div class="formation-explanation">
                <h4>Word Formation:</h4>
                <p>${entry.formation_explanation}</p>
            </div>
    `;
    
    if (entry.usage_examples && entry.usage_examples.length > 0) {
        html += `
            <div class="usage-examples">
                <h4>Biblical Usage:</h4>
        `;
        entry.usage_examples.forEach(example => {
            html += `
                <div class="example-item">
                    <strong>${example.reference}:</strong> "${example.text}"
                </div>
            `;
        });
        html += '</div>';
    }
    
    if (entry.first_occurrence) {
        html += `<div class="first-occurrence"><strong>First Occurrence:</strong> ${entry.first_occurrence}</div>`;
    }
    
    if (entry.frequency_count) {
        html += `<div class="frequency"><strong>Frequency in Scripture:</strong> ${entry.frequency_count} times</div>`;
    }
    
    html += '</div>';
    resultContainer.innerHTML = html;
}

function showFullEntry(entryId) {
    // Implement modal or expanded view for full dictionary entry
    console.log('Show full entry for ID:', entryId);
}

// Interactive Hebrew Words Functions
// Store current verse data for word lookups
let currentVerseData = {};

function makePaleoWordsInteractive(paleoText, hebrewText, verseData = null) {
    if (!paleoText || !hebrewText) return paleoText || '';
    
    // Store verse data for word lookups
    if (verseData) {
        currentVerseData[verseData.id] = verseData;
    }
    
    // First, preserve existing HTML tags by temporarily replacing them
    const htmlTagRegex = /<[^>]*>/g;
    const htmlTags = [];
    let tempPaleoText = paleoText;
    let match;
    let placeholderIndex = 0;
    
    // Extract HTML tags and replace with placeholders
    while ((match = htmlTagRegex.exec(paleoText)) !== null) {
        const placeholder = `__HTML_TAG_${placeholderIndex}__`;
        htmlTags.push({ placeholder, tag: match[0] });
        tempPaleoText = tempPaleoText.replace(match[0], placeholder);
        placeholderIndex++;
    }
    
    // Clean Hebrew text of HTML tags for word matching
    const cleanHebrewText = hebrewText.replace(/<[^>]*>/g, ' ');
    
    // Split both texts into words for matching
    const paleoWords = tempPaleoText.split(/(\s+)/);
    const hebrewWords = cleanHebrewText.split(/(\s+)/);
    
    let result = paleoWords.map((part, index) => {
        // Check if this part contains only Paleo Hebrew characters (no punctuation or HTML)
        const trimmedPart = part.trim();
        
        // Check if all characters are Paleo Hebrew (U+10900-U+1091F)
        let isPaleoWord = false;
        if (trimmedPart && trimmedPart.length > 0) {
            isPaleoWord = true;
            for (let char of trimmedPart) {
                const codePoint = char.codePointAt(0);
                if (codePoint < 0x10900 || codePoint > 0x1091F) {
                    isPaleoWord = false;
                    break;
                }
            }
        }
        
        if (isPaleoWord) {
            // This is a Paleo Hebrew word - get corresponding Hebrew word
            const correspondingHebrew = hebrewWords[index] ? hebrewWords[index].trim() : part.trim();
            const cleanHebrew = correspondingHebrew.replace(/[^\u0590-\u05FF]/g, '');
            
            // Calculate word position for literal translation lookup
            const wordPosition = Math.floor(index / 2); // Account for spaces
            const verseId = verseData ? verseData.id : 'unknown';
            
            return `<span class="paleo-word-interactive" onclick="showWordOverlay('${cleanHebrew.replace(/'/g, "\\'")}', ${wordPosition}, '${verseId}')" title="Click for root analysis">${part}</span>`;
        } else {
            // This is whitespace, punctuation, or HTML tags
            return part;
        }
    }).join('');
    
    // Restore HTML tags
    htmlTags.forEach(({ placeholder, tag }) => {
        result = result.replace(placeholder, tag);
    });
    
    return result;
}

async function showWordOverlay(hebrewWord, wordPosition = -1, verseId = 'unknown') {
    const overlay = document.getElementById('word-overlay');
    const loadingMessage = 'Loading word analysis...';
    
    try {
        // Show overlay with loading state
        document.getElementById('overlay-hebrew-word').textContent = hebrewWord;
        document.getElementById('overlay-paleo-word').textContent = hebrewToPaleo(hebrewWord);
        document.getElementById('overlay-transliteration').textContent = generatePaleoTransliteration(hebrewWord);
        document.getElementById('overlay-english-word').textContent = 'loading...';
        document.getElementById('overlay-pictographic-breakdown').textContent = loadingMessage;
        document.getElementById('overlay-formation-explanation').textContent = '';
        document.getElementById('overlay-formation-summary').textContent = '';
        document.getElementById('overlay-usage-count').textContent = 'Loading usage data...';
        
        overlay.classList.remove('hidden');
        
        // Direct paleo script analysis - no concordance lookup needed
        let wordData = null;
        
        // Clean the Hebrew word by removing vowel points and punctuation
        const cleanHebrewWord = hebrewWord.replace(/[^\u05D0-\u05EA]/g, '');
        const paleoScript = hebrewToPaleo(cleanHebrewWord);
        console.log('Analyzing directly:', hebrewWord, '→', cleanHebrewWord, '→', paleoScript);
        
        // Generate direct analysis from paleo letters
        wordData = generateDirectPaleoAnalysis(cleanHebrewWord, paleoScript);
        console.log('Generated direct analysis:', wordData);
        
        
        if (wordData) {
            populateWordOverlay(wordData);
        } else {
            showWordNotFound(hebrewWord);
        }
        
    } catch (error) {
        console.error('Error fetching word analysis:', error);
        showWordError(hebrewWord);
    }
}

function populateWordOverlay(wordData) {
    // Display Hebrew → Paleo → Transliteration → English sequence
    document.getElementById('overlay-hebrew-word').textContent = wordData.hebrew_word || wordData.clean_hebrew;
    document.getElementById('overlay-paleo-word').textContent = wordData.paleo_word || hebrewToPaleo(wordData.hebrew_word || wordData.clean_hebrew);
    document.getElementById('overlay-transliteration').textContent = wordData.transliteration || generatePaleoTransliteration(wordData.hebrew_word || wordData.clean_hebrew);
    
    // Get English word from COMPLETE Paleo mapping
    const hebrewWord = wordData.hebrew_word || wordData.clean_hebrew;
    const paleoWord = wordData.paleo_word || hebrewToPaleo(hebrewWord);
    let englishWord = 'word'; // default fallback
    
    // Direct lookup from complete mapping (43,000+ words)
    if (window.COMPLETE_PALEO_ENGLISH && window.COMPLETE_PALEO_ENGLISH[paleoWord]) {
        englishWord = window.COMPLETE_PALEO_ENGLISH[paleoWord];
    }
    
    console.log('Complete Paleo lookup:', paleoWord, '->', englishWord);
    document.getElementById('overlay-english-word').textContent = englishWord;
    
    // Display pictographic breakdown (purple text)
    if (wordData.pictographic_analysis) {
        document.getElementById('overlay-pictographic-breakdown').textContent = wordData.pictographic_analysis;
    } else {
        document.getElementById('overlay-pictographic-breakdown').textContent = 'Pictographic analysis not available';
    }
    
    // Display formation explanation (green text)  
    if (wordData.formation_explanation) {
        document.getElementById('overlay-formation-explanation').textContent = wordData.formation_explanation;
    } else {
        document.getElementById('overlay-formation-explanation').textContent = 'Formation explanation not available';
    }
    
    // Display concept summary in orange box
    if (wordData.original_concept) {
        document.getElementById('overlay-formation-summary').textContent = wordData.original_concept;
    } else {
        document.getElementById('overlay-formation-summary').textContent = 'Concept explanation not available';
    }
    
    // Display usage count
    const usageCount = wordData.frequency_count || wordData.usage_count || 0;
    document.getElementById('overlay-usage-count').textContent = `Used ${usageCount} times`;
}

function generateDirectPaleoAnalysis(hebrewWord, paleoScript) {
    // Paleo Hebrew letter meanings for direct analysis
    const letterMeanings = {
        '𐤀': { name: 'Aleph', meaning: 'ox head, strong leader', concept: 'strength, power, leadership' },
        '𐤁': { name: 'Bet', meaning: 'tent floor plan, house', concept: 'dwelling, family, containment' },
        '𐤂': { name: 'Gimel', meaning: 'camel, foot of man', concept: 'movement, gathering, pride' },
        '𐤃': { name: 'Dalet', meaning: 'tent door hanging', concept: 'entrance, pathway, movement' },
        '𐤄': { name: 'Hey', meaning: 'man with arms raised, window', concept: 'revelation, breath, spirit' },
        '𐤅': { name: 'Vav', meaning: 'tent peg, nail', concept: 'connection, security, adding' },
        '𐤆': { name: 'Zayin', meaning: 'mattock, cutting tool', concept: 'cutting, dividing, weapon' },
        '𐤇': { name: 'Chet', meaning: 'tent wall, fence', concept: 'separation, protection, boundary' },
        '𐤈': { name: 'Tet', meaning: 'coiled serpent, basket', concept: 'surrounding, containing, good' },
        '𐤉': { name: 'Yod', meaning: 'closed hand, arm', concept: 'work, deed, worship' },
        '𐤊': { name: 'Kaf', meaning: 'open palm', concept: 'opening, allowing, bending' },
        '𐤋': { name: 'Lamed', meaning: 'shepherd staff, cattle prod', concept: 'authority, teaching, leading' },
        '𐤌': { name: 'Mem', meaning: 'waves of water', concept: 'chaos, mighty, mass' },
        '𐤍': { name: 'Nun', meaning: 'swimming fish', concept: 'life, activity, movement' },
        '𐤎': { name: 'Samech', meaning: 'thorn, prop', concept: 'support, protection, grabbing' },
        '𐤏': { name: 'Ayin', meaning: 'eye', concept: 'seeing, knowing, understanding' },
        '𐤐': { name: 'Pe', meaning: 'mouth', concept: 'speaking, communication, blowing' },
        '𐤑': { name: 'Tsade', meaning: 'fish hook, man on side', concept: 'hunting, desire, righteousness' },
        '𐤒': { name: 'Qof', meaning: 'back of head, horizon', concept: 'time, behind, gathering' },
        '𐤓': { name: 'Resh', meaning: 'head of man', concept: 'head, chief, beginning' },
        '𐤔': { name: 'Shin', meaning: 'two front teeth', concept: 'sharpness, eating, destroying' },
        '𐤕': { name: 'Tav', meaning: 'crossed sticks, mark', concept: 'sign, covenant, mark' }
    };
    
    if (!paleoScript || paleoScript.length === 0) {
        return null;
    }
    
    // Analyze each paleo letter
    const letters = Array.from(paleoScript);
    const letterAnalysis = [];
    const concepts = [];
    const pictographs = [];
    
    for (const paleoLetter of letters) {
        if (letterMeanings[paleoLetter]) {
            const letterInfo = letterMeanings[paleoLetter];
            letterAnalysis.push({
                paleo_symbol: paleoLetter,
                name: letterInfo.name,
                meaning: letterInfo.meaning,
                concept: letterInfo.concept
            });
            concepts.push(letterInfo.concept);
            pictographs.push(`${paleoLetter} (${letterInfo.meaning})`);
        }
    }
    
    if (letterAnalysis.length === 0) {
        return null;
    }
    
    // Generate pictographic breakdown
    const pictographicBreakdown = pictographs.join(' + ');
    
    // Generate formation explanation based on concepts
    let formationExplanation = '';
    if (concepts.length === 1) {
        formationExplanation = `Word relates to ${concepts[0]}`;
    } else if (concepts.length === 2) {
        formationExplanation = `${concepts[0]} connected to ${concepts[1]}`;
    } else if (concepts.length >= 3) {
        formationExplanation = `${concepts[0]} that ${concepts[1]} through ${concepts[2]}`;
        if (concepts.length > 3) {
            formationExplanation += ` and involves ${concepts.slice(3).join(', ')}`;
        }
    }
    
    // Generate concept summary
    const conceptSummary = `The ${concepts[0] || 'concept'} with ${concepts[1] || 'meaning'} that brings ${concepts[2] || 'purpose'}`;
    
    // Get English meaning from our complete mapping
    let englishMeaning = 'Ancient Word Analysis';
    if (window.COMPLETE_PALEO_ENGLISH && window.COMPLETE_PALEO_ENGLISH[paleoScript]) {
        englishMeaning = window.COMPLETE_PALEO_ENGLISH[paleoScript];
    }
    
    return {
        hebrew_word: hebrewWord,
        paleo_word: paleoScript,
        transliteration: generatePaleoTransliteration(hebrewWord),
        english_meaning: englishMeaning,
        pictographic_analysis: pictographicBreakdown,
        formation_explanation: formationExplanation,
        original_concept: conceptSummary,
        letter_analysis: letterAnalysis,
        usage_count: 0
    };
}

function generatePaleoTransliteration(hebrewWord) {
    // Paleo Hebrew transliteration mapping
    const transliterationMap = {
        'א': 'a', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h', 'ו': 'w', 'ז': 'z', 'ח': 'ch',
        'ט': 't', 'י': 'y', 'כ': 'k', 'ך': 'k', 'ל': 'l', 'מ': 'm', 'ם': 'm', 'נ': 'n', 
        'ן': 'n', 'ס': 's', 'ע': 'aa', 'פ': 'p', 'ף': 'p', 'צ': 'ts', 'ץ': 'ts', 'ק': 'q', 
        'ר': 'r', 'ש': 'sh', 'ת': 't'
    };
    
    // Common Hebrew word patterns with proper vowelization
    const commonWords = {
        // From your example format
        'ונחש': 'wahenachesh',
        'היה': 'hayeh', 
        'ערום': 'aarawem',
        'מכל': 'makel',
        'חית': 'chayet',
        'השדה': 'hashadeh',
        'אשר': 'sher',
        'עשה': 'aasheh',
        'יהוה': 'yahaweh',
        'אלהים': 'eh-lo-heem',
        'ויאמר': 'wa-yo-mer',
        'אל': 'l',
        'האשה': 'hasheh',
        'אף': 'p',
        'כי': 'kee',
        'אמר': 'mer',
        'לא': 'la',
        'תאכלו': 'takelew',
        'עץ': 'aats',
        'הגן': 'hagan',
        
        // Common roots and patterns
        'ברא': 'bara',
        'אלה': 'eleh', 
        'השמים': 'hashamayem',
        'הארץ': 'haarets',
        'על': 'aal',
        'פני': 'peney',
        'המים': 'hamayem',
        'ויהי': 'wayehey',
        'אור': 'awr',
        'טוב': 'tawb',
        'ויבדל': 'wayabdel',
        'בין': 'beyn',
        'חשך': 'choshek',
        'יום': 'yawm',
        'לילה': 'laylah'
    };
    
    // Remove Hebrew vowel points and punctuation, keep only Hebrew consonants
    const cleanHebrew = hebrewWord.replace(/[^\u05D0-\u05EA]/g, '');
    
    // Check if we have a direct match in common words
    if (commonWords[cleanHebrew]) {
        return commonWords[cleanHebrew];
    }
    
    // Generate syllable-based transliteration
    let transliteration = '';
    const letters = cleanHebrew.split('');
    
    for (let i = 0; i < letters.length; i++) {
        const letter = letters[i];
        const nextLetter = letters[i + 1];
        const consonant = transliterationMap[letter] || letter;
        
        if (i === 0) {
            // First letter - add vowel after consonant
            transliteration += consonant === 'a' ? 'a' : consonant + 'a';
        } else if (i === letters.length - 1) {
            // Last letter - usually no vowel
            transliteration += consonant;
        } else {
            // Middle letters - add vowel between consonants
            transliteration += consonant + 'e';
        }
    }
    
    // Clean up and apply paleo pronunciation rules
    transliteration = transliteration
        .replace(/aa+/g, 'aa')  // Keep double-a for ayin
        .replace(/ee+/g, 'e')   // Single e
        .replace(/([bcdfghjklmnpqrstvwxz])a([bcdfghjklmnpqrstvwxz])/g, '$1a$2') // Better vowel placement
        .toLowerCase();
    
    return transliteration;
}

function showWordNotFound(hebrewWord) {
    document.getElementById('overlay-hebrew-word').textContent = hebrewWord;
    document.getElementById('overlay-paleo-word').textContent = hebrewToPaleo(hebrewWord);
    document.getElementById('overlay-transliteration').textContent = generatePaleoTransliteration(hebrewWord);
    document.getElementById('overlay-english-word').textContent = 'unknown';
    document.getElementById('overlay-pictographic-breakdown').textContent = `No analysis available for "${hebrewWord}". This word may be a variant or not in our dictionary.`;
    document.getElementById('overlay-formation-explanation').textContent = 'Try searching in the Dictionary tab for similar words.';
    document.getElementById('overlay-formation-summary').textContent = 'Analysis unavailable for this word';
    document.getElementById('overlay-usage-count').textContent = 'Usage data not available';
}

function showWordError(hebrewWord) {
    document.getElementById('overlay-hebrew-word').textContent = hebrewWord;
    document.getElementById('overlay-paleo-word').textContent = hebrewToPaleo(hebrewWord);
    document.getElementById('overlay-transliteration').textContent = generatePaleoTransliteration(hebrewWord);
    document.getElementById('overlay-english-word').textContent = 'error';
    document.getElementById('overlay-pictographic-breakdown').textContent = 'There was an error retrieving the word analysis. Please try again.';
    document.getElementById('overlay-formation-explanation').textContent = 'Network or server error occurred';
    document.getElementById('overlay-formation-summary').textContent = 'Please try again later';
    document.getElementById('overlay-usage-count').textContent = 'Usage data unavailable';
}

function hideWordOverlay() {
    const overlay = document.getElementById('word-overlay');
    overlay.classList.add('hidden');
}

// Close overlay when clicking outside
document.addEventListener('click', function(event) {
    const overlay = document.getElementById('word-overlay');
    if (event.target === overlay) {
        hideWordOverlay();
    }
});

// Close overlay with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        hideWordOverlay();
    }
});

// Authentication Functions
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/admin/facts-stats');
        if (response.ok) {
            isAuthenticated = true;
            updateAuthUI();
        } else if (response.status === 401) {
            isAuthenticated = false;
            updateAuthUI();
        }
    } catch (error) {
        console.log('Authentication check failed:', error);
        isAuthenticated = false;
        updateAuthUI();
    }
}

function updateAuthUI() {
    const adminSection = document.getElementById('admin');
    if (!adminSection) return;
    
    if (isAuthenticated) {
        // User is authenticated, show normal admin interface
        adminSection.innerHTML = `
            <h2>🔧 Admin Dashboard</h2>
            <div class="auth-controls">
                <button onclick="logout()" class="logout-btn">🚪 Logout</button>
            </div>
            <div class="admin-stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-facts">0</div>
                    <div class="stat-label">Total Facts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="published-facts">0</div>
                    <div class="stat-label">Published</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="draft-facts">0</div>
                    <div class="stat-label">Drafts</div>
                </div>
            </div>
            
            <div class="admin-actions">
                <button class="admin-btn add-fact-btn" onclick="showAddFactForm()">
                    <i class="fas fa-plus"></i> Add New Fact
                </button>
            </div>
            
            <div id="add-fact-form" class="add-fact-form hidden">
                <h3>Add New God Fact</h3>
                <form id="fact-form" onsubmit="event.preventDefault(); submitFactForm();">
                    <div class="form-group">
                        <label for="fact-title">Title *</label>
                        <input type="text" id="fact-title" name="title" required maxlength="200">
                    </div>
                    
                    <div class="form-group">
                        <label for="fact-content">Content *</label>
                        <textarea id="fact-content" name="content" required rows="8" 
                                placeholder="Write an amazing fact that proves God is real..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="fact-category">Category *</label>
                        <select id="fact-category" name="category" required>
                            <option value="">Select category...</option>
                            <option value="science">Science</option>
                            <option value="history">History</option>
                            <option value="prophecy">Prophecy</option>
                            <option value="miracles">Miracles</option>
                            <option value="creation">Creation</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="fact-source">Source</label>
                        <input type="text" id="fact-source" name="source" 
                               placeholder="Citation or reference (optional)">
                    </div>
                    
                    <div class="form-group">
                        <label for="fact-status">Status</label>
                        <select id="fact-status" name="status">
                            <option value="draft">Draft</option>
                            <option value="published">Published</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="fact-image">Image (optional)</label>
                        <input type="file" id="fact-image" name="image" accept="image/*" 
                               onchange="previewFile(this, 'image-preview')">
                        <div id="image-preview" class="file-preview"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="fact-video">Video (optional)</label>
                        <input type="file" id="fact-video" name="video" accept="video/*" 
                               onchange="previewFile(this, 'video-preview')">
                        <div id="video-preview" class="file-preview"></div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="submit-btn">Create Fact</button>
                        <button type="button" class="cancel-btn" onclick="hideAddFactForm()">Cancel</button>
                    </div>
                </form>
            </div>
            
            <div class="admin-facts-list">
                <h3>Manage Facts</h3>
                <div id="admin-facts-table"></div>
            </div>
        `;
    } else {
        // User is not authenticated, show login prompt
        showLoginPrompt();
    }
}

function showLoginPrompt() {
    const adminSection = document.getElementById('admin');
    if (!adminSection) return;
    
    adminSection.innerHTML = `
        <h2>🔒 Admin Access Required</h2>
        <div class="login-prompt">
            <p>You need to be logged in as an administrator to access this section.</p>
            <button onclick="window.location.href='/login'" class="login-btn">
                🔑 Admin Login
            </button>
        </div>
    `;
}

async function logout() {
    try {
        const response = await fetch('/logout');
        if (response.ok) {
            isAuthenticated = false;
            updateAuthUI();
            alert('Logged out successfully');
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}