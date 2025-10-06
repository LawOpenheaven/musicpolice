// Bias Analysis Visualization Functions
function displayBiasAnalysis(analysisId) {
    fetch(`/api/analyses/${analysisId}/bias-details`)
        .then(response => response.json())
        .then(data => {
            if (data.bias_analysis) {
                showBiasAnalysisModal(data);
            } else {
                showNotification('No bias analysis available for this song', 'warning');
            }
        })
        .catch(error => {
            console.error('Error fetching bias analysis:', error);
            showNotification('Error loading bias analysis', 'error');
        });
}

function showBiasAnalysisModal(data) {
    const modal = document.getElementById('bias-analysis-modal') || createBiasAnalysisModal();
    const content = modal.querySelector('#bias-analysis-content');
    
    content.innerHTML = generateBiasAnalysisHTML(data);
    modal.style.display = 'flex';
}

function createBiasAnalysisModal() {
    const modal = document.createElement('div');
    modal.id = 'bias-analysis-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Bias Analysis</h3>
                <span class="close" onclick="closeBiasAnalysisModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="bias-analysis-content"></div>
            </div>
            <div class="modal-footer">
                <button class="btn-primary" onclick="closeBiasAnalysisModal()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function generateBiasAnalysisHTML(data) {
    const analysis = data.bias_analysis;
    const categories = analysis.overall_analysis;
    
    let html = `
        <div class="bias-analysis-container">
            <h4>Bias Category Analysis</h4>
            <div class="bias-category-grid">
    `;
    
    // Generate category cards
    const categoryMap = {
        'hate_speech': { name: 'Hate Speech', key: 'hate_speech' },
        'offensive_language': { name: 'Offensive Language', key: 'offensive_language' },
        'racial_bias': { name: 'Racial Bias', key: 'racial_bias' },
        'gender_bias': { name: 'Gender Bias', key: 'gender_bias' }
    };
    
    Object.entries(categoryMap).forEach(([key, info]) => {
        const score = categories[info.key] || 0;
        const severity = score > 0.7 ? 'high' : score > 0.3 ? 'medium' : 'low';
        const percentage = Math.round(score * 100);
        
        html += `
            <div class="bias-category-card ${key}">
                <div class="bias-category-header">
                    <span class="bias-category-name">${info.name}</span>
                    <span class="bias-category-score ${severity}">${percentage}%</span>
                </div>
                <div class="bias-progress-bar">
                    <div class="bias-progress-fill ${key}" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            
            <h4>Lyrics Analysis</h4>
            <div class="lyrics-container">
    `;
    
    // Generate lyrics with highlighting
    if (analysis.line_analysis && analysis.line_analysis.length > 0) {
        analysis.line_analysis.forEach(line => {
            html += `
                <div class="lyrics-line problematic">
                    <span class="lyrics-line-number">${line.line_number}</span>
                    <span class="lyrics-text">${highlightProblematicWords(line.text, line.problematic_words)}</span>
                </div>
            `;
        });
    } else {
        html += '<p style="color: #44aa44; text-align: center; padding: 2rem;">No problematic content detected in lyrics</p>';
    }
    
    html += `
            </div>
            
            <div style="margin-top: 1rem; padding: 1rem; background: #1a1d29; border-radius: 8px;">
                <h5>Summary</h5>
                <p>Total lines analyzed: ${analysis.total_lines}</p>
                <p>Problematic lines: ${analysis.problematic_lines}</p>
                <p>Overall bias score: ${Math.round((categories.bias_score || 0) * 100)}%</p>
            </div>
        </div>
    `;
    
    return html;
}

function highlightProblematicWords(text, problematicWords) {
    if (!problematicWords || problematicWords.length === 0) {
        return text;
    }
    
    let highlightedText = text;
    problematicWords.forEach(wordInfo => {
        const word = wordInfo.word;
        const category = wordInfo.category;
        const tooltip = `${category.replace('_', ' ').toUpperCase()}`;
        
        const highlightedWord = `<span class="problematic-word ${category}" title="${tooltip}">${word}</span>`;
        highlightedText = highlightedText.replace(new RegExp(word, 'gi'), highlightedWord);
    });
    
    return highlightedText;
}

function closeBiasAnalysisModal() {
    const modal = document.getElementById('bias-analysis-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Similarity Analysis Visualization Functions
function displaySimilarityAnalysis(analysisId) {
    fetch(`/api/analyses/${analysisId}/similarity-details`)
        .then(response => response.json())
        .then(data => {
            if (data.similar_songs && data.similar_songs.length > 0) {
                showSimilarityAnalysisModal(data);
            } else {
                showNotification('No similar songs found', 'info');
            }
        })
        .catch(error => {
            console.error('Error fetching similarity analysis:', error);
            showNotification('Error loading similarity analysis', 'error');
        });
}

function showSimilarityAnalysisModal(data) {
    const modal = document.getElementById('similarity-analysis-modal') || createSimilarityAnalysisModal();
    const content = modal.querySelector('#similarity-analysis-content');
    
    content.innerHTML = generateSimilarityAnalysisHTML(data);
    modal.style.display = 'flex';
}

function createSimilarityAnalysisModal() {
    const modal = document.createElement('div');
    modal.id = 'similarity-analysis-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Similarity Analysis</h3>
                <span class="close" onclick="closeSimilarityAnalysisModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="similarity-analysis-content"></div>
            </div>
            <div class="modal-footer">
                <button class="btn-primary" onclick="closeSimilarityAnalysisModal()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function generateSimilarityAnalysisHTML(data) {
    const summary = data.similarity_summary;
    const similarSongs = data.similar_songs;
    
    let html = `
        <div class="similarity-analysis-container">
            <h4>Similarity Summary</h4>
            <div class="similarity-summary">
                <div class="similarity-metric">
                    <div class="similarity-metric-value">${summary.total_similar_songs}</div>
                    <div class="similarity-metric-label">Similar Songs</div>
                </div>
                <div class="similarity-metric">
                    <div class="similarity-metric-value">${Math.round(summary.highest_similarity * 100)}%</div>
                    <div class="similarity-metric-label">Highest Similarity</div>
                </div>
                <div class="similarity-metric">
                    <div class="similarity-metric-value">${Math.round(summary.average_similarity * 100)}%</div>
                    <div class="similarity-metric-label">Average Similarity</div>
                </div>
                <div class="similarity-metric">
                    <div class="similarity-metric-value">${Math.round(summary.similarity_threshold * 100)}%</div>
                    <div class="similarity-metric-label">Threshold</div>
                </div>
            </div>
            
            <h4>Similar Songs</h4>
            <div class="similar-songs-list">
    `;
    
    similarSongs.forEach(song => {
        const breakdown = song.similarity_breakdown;
        const score = Math.round(song.similarity_score * 100);
        
        html += `
            <div class="similar-song-card">
                <div class="similar-song-header">
                    <div class="similar-song-info">
                        <h4>${song.original_filename}</h4>
                        <p>Uploaded: ${new Date(song.original_created_at).toLocaleDateString()}</p>
                    </div>
                    <div class="similarity-score-badge ${breakdown.level}">
                        ${score}%
                    </div>
                </div>
                
                <div class="similar-song-details">
                    <div class="similar-song-detail">
                        <div class="similar-song-detail-label">Similarity</div>
                        <div class="similar-song-detail-value">${breakdown.description}</div>
                    </div>
                    <div class="similar-song-detail">
                        <div class="similar-song-detail-label">Compliance</div>
                        <div class="similar-song-detail-value">${Math.round(song.original_compliance_score * 100)}%</div>
                    </div>
                    <div class="similar-song-detail">
                        <div class="similar-song-detail-label">Plagiarism</div>
                        <div class="similar-song-detail-value">${Math.round(song.audio_features.plagiarism_score * 100)}%</div>
                    </div>
                    <div class="similar-song-detail">
                        <div class="similar-song-detail-label">Bias</div>
                        <div class="similar-song-detail-value">${Math.round(song.audio_features.bias_score * 100)}%</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

function closeSimilarityAnalysisModal() {
    const modal = document.getElementById('similarity-analysis-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Enhanced Analysis Details Modal
function showEnhancedAnalysisDetails(analysisId) {
    fetch(`/api/analyses/${analysisId}`)
        .then(response => response.json())
        .then(data => {
            showAnalysisModal(data);
        })
        .catch(error => {
            console.error('Error fetching analysis details:', error);
            showNotification('Error loading analysis details', 'error');
        });
}

function showAnalysisModal(data) {
    const modal = document.getElementById('analysis-modal');
    const content = document.getElementById('analysis-content');
    
    let html = `
        <div class="analysis-details">
            <div class="analysis-header">
                <h3>${data.filename}</h3>
                <div class="analysis-score">
                    <span class="score-label">Compliance Score:</span>
                    <span class="score-value">${Math.round(data.compliance_score * 100)}%</span>
                </div>
            </div>
            
            <div class="analysis-sections">
    `;
    
    // Issues section
    if (data.issues && data.issues.length > 0) {
        html += `
            <div class="analysis-section">
                <h4>Issues Detected</h4>
                <div class="issues-list">
        `;
        data.issues.forEach(issue => {
            const severityClass = issue.severity === 'high' ? 'high' : issue.severity === 'medium' ? 'medium' : 'low';
            html += `
                <div class="issue-item ${severityClass}">
                    <div class="issue-header">
                        <span class="issue-type">${issue.type.toUpperCase()}</span>
                        <span class="issue-severity">${issue.severity.toUpperCase()}</span>
                    </div>
                    <div class="issue-detail">${issue.detail}</div>
                    <div class="issue-confidence">Confidence: ${Math.round(issue.confidence * 100)}%</div>
                </div>
            `;
        });
        html += `</div></div>`;
    }
    
    // Similar songs section
    if (data.similar_songs && data.similar_songs.length > 0) {
        html += `
            <div class="analysis-section">
                <h4>Similar Songs Found</h4>
                <div class="similar-songs-preview">
        `;
        data.similar_songs.slice(0, 3).forEach(song => {
            html += `
                <div class="similar-song-preview">
                    <span class="song-name">${song.filename}</span>
                    <span class="similarity-score">${Math.round(song.similarity_score * 100)}%</span>
                </div>
            `;
        });
        if (data.similar_songs.length > 3) {
            html += `<p>... and ${data.similar_songs.length - 3} more</p>`;
        }
        html += `</div></div>`;
    }
    
    // Action buttons
    html += `
                <div class="analysis-actions" style="display: flex; gap: 1rem; margin-top: 2rem; justify-content: center;">
                    <button class="btn-secondary" onclick="displayBiasAnalysis(${data.id})" style="background: #232740; border: 1px solid #3a3f5c; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; transition: all 0.3s ease;">
                        <i class="fas fa-exclamation-triangle"></i>
                        View Bias Analysis
                    </button>
                    <button class="btn-secondary" onclick="displaySimilarityAnalysis(${data.id})" style="background: #232740; border: 1px solid #3a3f5c; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; transition: all 0.3s ease;">
                        <i class="fas fa-search"></i>
                        View Similarity Details
                    </button>
                    <button class="btn-secondary" onclick="showLyrics(${data.id})" style="background: #232740; border: 1px solid #3a3f5c; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; transition: all 0.3s ease;">
                        <i class="fas fa-music"></i>
                        View Lyrics
                    </button>
                </div>
            </div>
        </div>
    `;
    
    content.innerHTML = html;
    modal.style.display = 'flex';
}

// Update existing functions to use enhanced analysis
function showAnalysisDetails(analysisId) {
    showEnhancedAnalysisDetails(analysisId);
}
