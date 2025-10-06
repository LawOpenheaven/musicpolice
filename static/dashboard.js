// AI Compliance Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeProgressCircles();
    setupNavigation();
    loadDashboardData();
    
    // Setup additional handlers
    setupComplianceHandlers();
    
    // Setup analyze button
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', () => {
            handleNavigation('uploads');
        });
    }
    
    // Setup search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            performSearch(e.target.value);
        });
    }
});

// Initialize Chart.js charts
function initializeCharts() {
    const ctx = document.getElementById('trendsChart');
    if (!ctx) return;

    // Create initial chart with empty data - will be updated with real data
    window.trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Analysis Trends',
                data: [],
                borderColor: '#f5576c',
                backgroundColor: 'rgba(245, 87, 108, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#f5576c',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            return `Analyses: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: false,
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: false,
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                point: {
                    hoverBackgroundColor: '#f5576c'
                }
            }
        }
    });
}

// Initialize progress circles with animation
function initializeProgressCircles() {
    const circles = document.querySelectorAll('.progress-circle');
    
    circles.forEach(circle => {
        const percentage = parseInt(circle.dataset.percentage);
        const degrees = (percentage / 100) * 360;
        
        setTimeout(() => {
            circle.style.background = `conic-gradient(
                from 0deg,
                #f5576c 0deg,
                #f5576c ${degrees}deg,
                #3a3f5c ${degrees}deg,
                #3a3f5c 360deg
            )`;
        }, 500);
    });
}

// Setup navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item a');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // Allow external links to work normally
            if (this.classList.contains('external-link') || this.getAttribute('target') === '_blank') {
                return; // Let the browser handle the link
            }
            
            e.preventDefault();
            
            // Remove active class from all items
            document.querySelectorAll('.nav-item').forEach(nav => {
                nav.classList.remove('active');
            });
            
            // Add active class to clicked item
            this.parentElement.classList.add('active');
            
            // Handle navigation based on href
            const section = this.getAttribute('href').substring(1);
            handleNavigation(section);
        });
    });
}

// Handle navigation between sections
function handleNavigation(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show/hide main dashboard elements based on section
    const statsGrid = document.querySelector('.stats-grid');
    const analysisTable = document.querySelector('.analysis-table');
    
    if (section === 'dashboard') {
        // Show main dashboard elements
        if (statsGrid) statsGrid.style.display = 'grid';
        if (analysisTable) analysisTable.style.display = 'block';
    } else {
        // Hide main dashboard elements on other pages
        if (statsGrid) statsGrid.style.display = 'none';
        if (analysisTable) analysisTable.style.display = 'none';
    }
    
    // Show selected section
    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Update page title and subtitle
    updatePageHeader(section);
    
    switch(section) {
        case 'dashboard':
            showDashboard();
            break;
        case 'compliance':
            showComplianceSection();
            break;
        case 'uploads':
            showUploadSection();
            break;
        case 'reports':
            showReportsSection();
            break;
        case 'settings':
            showSettingsSection();
            break;
        default:
            showDashboard();
    }
}

// Update page header based on current section
function updatePageHeader(section) {
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    
    const headers = {
        dashboard: {
            title: 'Daily Analysis',
            subtitle: '"Only photograph what you love." — Tim Walker'
        },
        compliance: {
            title: 'Compliance Rules',
            subtitle: 'Configure and manage compliance rules for content analysis'
        },
        uploads: {
            title: 'Content Upload',
            subtitle: 'Upload audio files for compliance analysis'
        },
        reports: {
            title: 'Analysis Reports',
            subtitle: 'View and export detailed analysis reports'
        },
        settings: {
            title: 'System Settings',
            subtitle: 'Configure system preferences and notifications'
        }
    };
    
    if (headers[section]) {
        pageTitle.textContent = headers[section].title;
        pageSubtitle.textContent = headers[section].subtitle;
    }
}

// Show dashboard (current view)
function showDashboard() {
    console.log('Dashboard view active');
    // Dashboard is already visible by default
}

// Show compliance section
function showComplianceSection() {
    console.log('Compliance section active');
    loadComplianceRules();
}

// Show upload section
function showUploadSection() {
    console.log('Upload section active');
    setupUploadHandlers();
}

// Show reports section
function showReportsSection() {
    console.log('Reports section active');
    loadReportsData();
}

// Show settings section
function showSettingsSection() {
    console.log('Settings section active');
    loadSettingsData();
}

// Load dashboard data from API
async function loadDashboardData() {
    try {
        // Load dashboard stats
        const statsResponse = await fetch('/api/dashboard-stats');
        const stats = await statsResponse.json();
        
        // Load recent analyses (get more for better search functionality)
        const analysesResponse = await fetch('/api/analyses?limit=100&offset=0');
        let analyses = [];
        
        if (analysesResponse.ok) {
            const analysesData = await analysesResponse.json();
            analyses = analysesData.analyses || [];
        }
        
        // Load compliance rules
        const rulesResponse = await fetch('/api/rules');
        const rules = await rulesResponse.json();
        
        updateDashboardMetrics(stats, analyses, rules);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Use mock data as fallback
        updateDashboardMetrics(getMockStats(), getMockAnalyses(), getMockRules());
    }
}

// Update dashboard metrics
function updateDashboardMetrics(stats, analyses, rules) {
    // Update compliance scores from stats - use actual backend data
    const copyrightScore = Math.round(stats.compliance_scores?.copyright || 0);
    const biasScore = Math.round(stats.compliance_scores?.bias || 0);
    
    // Show empty state if no data
    if (stats.total_analyses === 0) {
        // Update progress circles to show 0
        updateProgressCircle(0, 0);
        updateProgressCircle(1, 0);
        
        // Update big number to show 0
        const bigNumber = document.querySelector('.big-number');
        if (bigNumber) {
            bigNumber.textContent = '0';
        }
        
        // Show empty state message
        const chartContainer = document.querySelector('#trendsChart');
        if (chartContainer) {
            chartContainer.innerHTML = '<p style="text-align: center; color: #888; padding: 2rem;">No analyses yet. Upload your first audio file to see data!</p>';
        }
        
        return; // Skip the rest of the updates
    }
    
    // Update progress circles
    updateProgressCircle(0, copyrightScore);
    updateProgressCircle(1, biasScore);
    
    // Update big number with real data
    const bigNumber = document.querySelector('.big-number');
    if (bigNumber) {
        bigNumber.textContent = stats.total_analyses.toLocaleString();
    }
    
    // Update analysis queue metrics with real data
    updateAnalysisQueue(analyses, stats);
    
    // Update trend chart with real data
    if (stats.trend_data && stats.trend_data.labels && stats.trend_data.labels.length > 0) {
        updateTrendChart(stats.trend_data);
    } else {
        // Show empty chart state if no data
        const chartContainer = document.querySelector('#trendsChart');
        if (chartContainer) {
            chartContainer.innerHTML = '<p style="text-align: center; color: #888; padding: 2rem;">No trend data available</p>';
        }
    }
    
    // Update analysis table with real data
    updateAnalysisTable(analyses);
}

// Calculate compliance score for a specific type
function calculateComplianceScore(analyses, type) {
    if (!analyses || analyses.length === 0) return 0; // No data = 0 score
    
    const typeAnalyses = analyses.filter(a => a.type === type);
    if (typeAnalyses.length === 0) return 0;
    
    const avgScore = typeAnalyses.reduce((sum, a) => sum + a.score, 0) / typeAnalyses.length;
    return Math.round(avgScore);
}

// Update progress circle
function updateProgressCircle(index, percentage) {
    const circles = document.querySelectorAll('.progress-circle');
    if (circles[index]) {
        circles[index].dataset.percentage = percentage;
        const percentageSpan = circles[index].querySelector('.percentage');
        if (percentageSpan) {
            percentageSpan.textContent = `${percentage}%`;
        }
        
        // Animate the circle
        const degrees = (percentage / 100) * 360;
        setTimeout(() => {
            circles[index].style.background = `conic-gradient(
                from 0deg,
                #f5576c 0deg,
                #f5576c ${degrees}deg,
                #3a3f5c ${degrees}deg,
                #3a3f5c 360deg
            )`;
        }, 100);
    }
}

// Update analysis queue metrics
function updateAnalysisQueue(analyses, stats) {
    // Use real data from analyses and stats
    const totalAnalyses = stats.total_analyses || 0;
    const recentAnalyses = stats.recent_analyses || 0;
    const copyrightScore = Math.round(stats.compliance_scores?.copyright || 0);
    const biasScore = Math.round(stats.compliance_scores?.bias || 0);
    
    // Show empty state if no data
    if (totalAnalyses === 0) {
        const metrics = [
            { label: '0', percentage: 0, score: 'Total Analyses' },
            { label: '0', percentage: 0, score: 'Recent Analyses' },
            { label: '0%', percentage: 0, score: 'Avg Compliance' },
            { label: '0', percentage: 0, score: 'Issues Found' }
        ];
        
        const metricItems = document.querySelectorAll('.metric-item');
        metricItems.forEach((item, index) => {
            if (metrics[index]) {
                const barFill = item.querySelector('.bar-fill');
                const labelSpan = item.querySelector('.metric-label');
                const scoreSpan = item.querySelector('.metric-score');
                
                if (barFill) {
                    barFill.style.width = '0%';
                }
                if (labelSpan) {
                    labelSpan.textContent = metrics[index].label;
                }
                if (scoreSpan) {
                    scoreSpan.textContent = metrics[index].score;
                }
            }
        });
        return;
    }
    
    const avgCompliance = Math.round((copyrightScore + biasScore) / 2);
    const issuesFound = stats.issues_found || 0;
    
    const metrics = [
        { label: totalAnalyses.toLocaleString(), percentage: Math.min(copyrightScore, 100), score: 'Total Analyses' },
        { label: recentAnalyses.toLocaleString(), percentage: Math.min(biasScore, 100), score: 'Recent Analyses' },
        { label: `${avgCompliance}%`, percentage: avgCompliance, score: 'Avg Compliance' },
        { label: issuesFound.toLocaleString(), percentage: Math.min(issuesFound * 10, 100), score: 'Issues Found' }
    ];
    
    const metricItems = document.querySelectorAll('.metric-item');
    metricItems.forEach((item, index) => {
        if (metrics[index]) {
            const barFill = item.querySelector('.bar-fill');
            const labelSpan = item.querySelector('.metric-label');
            const scoreSpan = item.querySelector('.metric-score');
            
            if (barFill) {
                setTimeout(() => {
                    barFill.style.width = `${metrics[index].percentage}%`;
                }, index * 200);
            }
            if (labelSpan) {
                labelSpan.textContent = metrics[index].label;
            }
            if (scoreSpan) {
                scoreSpan.textContent = metrics[index].score;
            }
        }
    });
}

// Update trend chart with real data
function updateTrendChart(trendData) {
    if (!window.trendsChart || !trendData) return;
    
    // Format labels for better display
    const formattedLabels = (trendData.labels || []).map(label => {
        const date = new Date(label);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    // Update the existing chart with real data
    window.trendsChart.data.labels = formattedLabels;
    window.trendsChart.data.datasets[0].data = trendData.values || [];
    
    // Update tooltip callbacks to show real data
    window.trendsChart.options.plugins.tooltip = {
        callbacks: {
            title: function(context) {
                const originalLabel = trendData.labels[context[0].dataIndex];
                const date = new Date(originalLabel);
                return date.toLocaleDateString('en-US', { 
                    weekday: 'short', 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                });
            },
            label: function(context) {
                return `Analyses: ${context.parsed.y}`;
            }
        }
    };
    
    // Update the chart
    window.trendsChart.update();
}

// Global variables for analysis table management
let allAnalyses = [];
let filteredAnalyses = [];
let currentPage = 1;
let itemsPerPage = 10;
let isShowingAll = false;

// Update analysis table with real data
function updateAnalysisTable(analyses) {
    allAnalyses = analyses;
    filteredAnalyses = analyses;
    currentPage = 1;
    
    // Update analysis count
    const analysisCount = document.getElementById('analysis-count');
    if (analysisCount) {
        analysisCount.textContent = `${analyses.length} analyses`;
    }
    
    // Show recent analyses (first 5) by default
    if (!isShowingAll) {
        displayAnalyses(analyses.slice(0, 5));
    } else {
        displayAnalysesWithPagination(analyses);
    }
}

// Display analyses in the table
function displayAnalyses(analyses) {
    const tableBody = document.getElementById('analysis-table-body');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Show empty state if no analyses
    if (analyses.length === 0) {
        tableBody.innerHTML = `
            <div class="table-row empty-state">
                <div class="col" style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                    <i class="fas fa-music" style="font-size: 2rem; color: #8892b0; margin-bottom: 1rem;"></i>
                    <p style="color: #8892b0; margin: 0;">No analyses found</p>
                    <p style="color: #667eea; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Upload your first audio file to get started</p>
                </div>
            </div>
        `;
        return;
    }
    
    // Create table rows for each analysis
    analyses.forEach((analysis, index) => {
        const row = createAnalysisRow(analysis);
        tableBody.appendChild(row);
    });
}

// Create a single analysis table row
function createAnalysisRow(analysis) {
    const row = document.createElement('div');
    row.className = 'table-row';
    
    // Calculate compliance score for stars
    const complianceScore = Math.round((analysis.compliance_score || 0.8) * 5);
    const issuesCount = analysis.issues_count || 0;
    
    // Format date
    const analysisDate = new Date(analysis.created_at);
    const formattedDate = analysisDate.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Determine status
    const statusText = issuesCount === 0 ? 'Clear Analysis' : 'Issues Found';
    const statusClass = issuesCount === 0 ? 'status-badge closed' : 'status-badge open';
    
    // Create stars HTML
    const starsHTML = Array.from({length: 5}, (_, i) => 
        `<i class="fas fa-star ${i < complianceScore ? 'active' : ''}"></i>`
    ).join('');
    
    row.innerHTML = `
        <div class="col">
            <button class="play-button" onclick="playAudio(${analysis.id})" title="Play audio">
                <i class="fas fa-play"></i>
            </button>
            <i class="fas fa-music"></i>
            <span>${analysis.filename || 'Unknown File'}</span>
        </div>
        <div class="col">
            <div class="rating">
                ${starsHTML}
            </div>
        </div>
        <div class="col">
            <span class="${statusClass}">${statusText}</span>
        </div>
        <div class="col">
            <span class="details-link" onclick="showAnalysisDetails(${analysis.id})">Details</span>
            <span class="lyrics-link" onclick="showLyrics(${analysis.id})" style="margin-left: 10px; color: #f5576c; cursor: pointer;">View Lyrics</span>
            <span class="bias-link" onclick="displayBiasAnalysis(${analysis.id})" style="margin-left: 10px; color: #f5576c; cursor: pointer; font-weight: 600; font-size: 0.8rem;">Bias</span>
            <span class="similarity-link" onclick="displaySimilarityAnalysis(${analysis.id})" style="margin-left: 10px; color: #667eea; cursor: pointer; font-weight: 600; font-size: 0.8rem;">Similar</span>
        </div>
        <div class="col">
            <span class="date">${formattedDate}</span>
        </div>
    `;
    
    return row;
}

// Display analyses with pagination
function displayAnalysesWithPagination(analyses) {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageAnalyses = analyses.slice(startIndex, endIndex);
    
    displayAnalyses(pageAnalyses);
    updatePagination(analyses.length);
}

// Update pagination controls
function updatePagination(totalItems) {
    const pagination = document.getElementById('table-pagination');
    const pageInfo = document.getElementById('page-info');
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');
    
    if (!pagination || !pageInfo || !prevBtn || !nextBtn) return;
    
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    // Show/hide pagination
    if (totalPages > 1) {
        pagination.style.display = 'flex';
    } else {
        pagination.style.display = 'none';
    }
    
    // Update page info
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    
    // Update button states
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
}

// Search functionality
function performSearch(searchTerm) {
    const searchClearBtn = document.getElementById('search-clear-btn');
    
    // Show/hide clear button
    if (searchClearBtn) {
        searchClearBtn.style.display = searchTerm ? 'block' : 'none';
    }
    
    if (!searchTerm.trim()) {
        // No search term, show all analyses
        filteredAnalyses = allAnalyses;
    } else {
        // Filter analyses by filename (case-insensitive)
        // Also search by analysis ID for more comprehensive search
        filteredAnalyses = allAnalyses.filter(analysis => {
            const filename = analysis.filename ? analysis.filename.toLowerCase() : '';
            const searchLower = searchTerm.toLowerCase();
            
            return filename.includes(searchLower) || 
                   analysis.id.toString().includes(searchLower);
        });
    }
    
    // Reset to first page
    currentPage = 1;
    
    // Update display
    if (isShowingAll) {
        displayAnalysesWithPagination(filteredAnalyses);
    } else {
        displayAnalyses(filteredAnalyses.slice(0, 5));
    }
    
    // Update analysis count
    const analysisCount = document.getElementById('analysis-count');
    if (analysisCount) {
        if (searchTerm.trim()) {
            analysisCount.textContent = `${filteredAnalyses.length} of ${allAnalyses.length} analyses`;
            analysisCount.style.background = 'rgba(245, 87, 108, 0.2)';
            analysisCount.style.color = '#f5576c';
        } else {
            analysisCount.textContent = `${allAnalyses.length} analyses`;
            analysisCount.style.background = 'rgba(102, 126, 234, 0.2)';
            analysisCount.style.color = '#667eea';
        }
    }
    
    // Show search feedback
    if (searchTerm.trim() && filteredAnalyses.length === 0) {
        showNotification(`No analyses found matching "${searchTerm}"`, 'warning', 3000);
    } else if (searchTerm.trim() && filteredAnalyses.length > 0) {
        showNotification(`Found ${filteredAnalyses.length} analyses matching "${searchTerm}"`, 'success', 2000);
    }
}

// Clear search
function clearSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
        performSearch('');
    }
}

// Show all analyses with pagination
function showAllAnalyses() {
    isShowingAll = true;
    currentPage = 1;
    
    // Update button text
    const viewAllBtn = document.getElementById('view-all-btn');
    if (viewAllBtn) {
        viewAllBtn.innerHTML = '<i class="fas fa-compress"></i> Show Recent';
        viewAllBtn.onclick = showRecentAnalyses;
    }
    
    // Display with pagination
    displayAnalysesWithPagination(filteredAnalyses);
    
    showNotification('Showing all analyses with pagination', 'info', 2000);
}

// Show recent analyses only
function showRecentAnalyses() {
    isShowingAll = false;
    currentPage = 1;
    
    // Update button text
    const viewAllBtn = document.getElementById('view-all-btn');
    if (viewAllBtn) {
        viewAllBtn.innerHTML = '<i class="fas fa-list"></i> View All';
        viewAllBtn.onclick = showAllAnalyses;
    }
    
    // Hide pagination
    const pagination = document.getElementById('table-pagination');
    if (pagination) {
        pagination.style.display = 'none';
    }
    
    // Display recent analyses
    displayAnalyses(filteredAnalyses.slice(0, 5));
    
    showNotification('Showing recent analyses only', 'info', 2000);
}

// Change page
function changePage(direction) {
    const totalPages = Math.ceil(filteredAnalyses.length / itemsPerPage);
    const newPage = currentPage + direction;
    
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        displayAnalysesWithPagination(filteredAnalyses);
    }
}

// Refresh analyses
async function refreshAnalyses() {
    showNotification('Refreshing analyses...', 'info', 1000);
    
    try {
        // Reload dashboard data
        await loadDashboardData();
        showNotification('Analyses refreshed successfully!', 'success', 2000);
    } catch (error) {
        console.error('Error refreshing analyses:', error);
        showNotification('Failed to refresh analyses', 'error', 3000);
    }
}

// Mock data functions
function getMockStats() {
    return {
        total_analyses: 0,
        compliance_scores: {
            copyright: 0,
            bias: 0,
            content_filter: 0
        },
        trend_data: {
            labels: ['Jan 01', 'Feb 01', 'Mar 01', 'Apr 01', 'May 01', 'Jun 01', 'Jul 01', 'Aug 01'],
            values: [120, 190, 300, 500, 200, 300, 450, 600]
        },
        recent_analyses: 87
    };
}

function getMockRules() {
    return {
        copyright_rules: {
            similarity_threshold: 0.7,
            enabled: true
        },
        bias_detection: {
            enabled: true,
            categories: ["gender", "race", "age"]
        },
        content_filtering: {
            explicit_content: true,
            hate_speech: true
        }
    };
}

function getMockAnalyses() {
    return [
        {
            id: 1,
            filename: 'sample_song.mp3',
            compliance_score: 0.87,
            issues_count: 0,
            created_at: new Date().toISOString()
        },
        {
            id: 2,
            filename: 'another_track.wav',
            compliance_score: 0.0,
            issues_count: 0,
            created_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
            id: 3,
            filename: 'test_audio.flac',
            compliance_score: 0.83,
            issues_count: 2,
            created_at: new Date(Date.now() - 172800000).toISOString()
        }
    ];
}

function getMockReportsSummary() {
    return {
        total_analyses: 1243,
        average_compliance_score: 94.2,
        issues_found: 87,
        compliance_rate: 93.0
    };
}

function getMockTrendsData() {
    return {
        labels: ['2025-09-29', '2025-09-30', '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04', '2025-10-05'],
        analysis_counts: [0, 0, 0, 0, 0, 0, 0],
        average_scores: [0, 0, 0, 0, 0, 0, 0],
        issue_counts: [0, 0, 0, 0, 0, 0, 0]
    };
}

// Real-time updates (placeholder for WebSocket integration)
function setupRealTimeUpdates() {
    // TODO: Implement WebSocket connection for real-time updates
    setInterval(() => {
        // Simulate real-time data updates
        loadDashboardData();
    }, 30000); // Update every 30 seconds
}

// Initialize real-time updates
setTimeout(setupRealTimeUpdates, 5000);

// ===== COMPLIANCE SECTION FUNCTIONS =====

// Load compliance rules from API
async function loadComplianceRules() {
    try {
        const response = await fetch('/api/rules');
        const rules = await response.json();
        updateComplianceUI(rules);
    } catch (error) {
        console.error('Error loading compliance rules:', error);
        // Use default rules
        updateComplianceUI(getMockRules());
    }
}

// Update compliance UI with rules data
function updateComplianceUI(rules) {
    // Update copyright toggle
    const copyrightToggle = document.getElementById('copyright-toggle');
    if (copyrightToggle) {
        copyrightToggle.checked = rules.copyright_rules?.enabled || false;
    }
    
    // Update similarity threshold
    const similarityThreshold = document.getElementById('similarity-threshold');
    const thresholdValue = document.getElementById('threshold-value');
    if (similarityThreshold && thresholdValue) {
        similarityThreshold.value = rules.copyright_rules?.similarity_threshold || 0.7;
        thresholdValue.textContent = similarityThreshold.value;
    }
    
    // Update bias toggle
    const biasToggle = document.getElementById('bias-toggle');
    if (biasToggle) {
        biasToggle.checked = rules.bias_detection?.enabled || false;
    }
    
    // Update bias threshold if it exists
    const biasThreshold = document.getElementById('bias-threshold');
    const biasThresholdValue = document.getElementById('bias-threshold-value');
    if (biasThreshold && biasThresholdValue) {
        biasThreshold.value = rules.bias_detection?.toxicity_threshold || 0.4;
        biasThresholdValue.textContent = biasThreshold.value;
    }
    
    // Update content toggle
    const contentToggle = document.getElementById('content-toggle');
    if (contentToggle) {
        contentToggle.checked = rules.content_filtering?.explicit_content || false;
    }
}

// Setup compliance section event handlers
function setupComplianceHandlers() {
    // Similarity threshold slider
    const similarityThreshold = document.getElementById('similarity-threshold');
    const thresholdValue = document.getElementById('threshold-value');
    if (similarityThreshold && thresholdValue) {
        similarityThreshold.addEventListener('input', function() {
            thresholdValue.textContent = this.value;
        });
    }
    
    // Bias threshold slider
    const biasThreshold = document.getElementById('bias-threshold');
    const biasThresholdValue = document.getElementById('bias-threshold-value');
    if (biasThreshold && biasThresholdValue) {
        biasThreshold.addEventListener('input', function() {
            biasThresholdValue.textContent = this.value;
        });
    }
    
    // Save rules button
    const saveRulesBtn = document.getElementById('save-rules-btn');
    if (saveRulesBtn) {
        saveRulesBtn.addEventListener('click', saveComplianceRules);
    }
    
    // Reset rules button
    const resetRulesBtn = document.getElementById('reset-rules-btn');
    if (resetRulesBtn) {
        resetRulesBtn.addEventListener('click', resetComplianceRules);
    }
}

// Save compliance rules
async function saveComplianceRules() {
    const rules = {
        copyright_rules: {
            enabled: document.getElementById('copyright-toggle').checked,
            similarity_threshold: parseFloat(document.getElementById('similarity-threshold').value)
        },
        bias_detection: {
            enabled: document.getElementById('bias-toggle').checked,
            toxicity_threshold: parseFloat(document.getElementById('bias-threshold')?.value || 0.4),
            categories: Array.from(document.querySelectorAll('#bias-toggle').closest('.rule-card').querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.nextSibling.textContent.trim())
        },
        content_filtering: {
            explicit_content: document.getElementById('content-toggle').checked,
            hate_speech: true
        }
    };
    
    // Show loading notification
    showNotification('Saving compliance rules...', 'info');
    
    try {
        const response = await fetch('/api/rules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rules)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('✅ Compliance rules saved successfully to database!', 'success');
            
            // Show detailed feedback
            setTimeout(() => {
                showDetailedSaveFeedback(rules);
            }, 1000);
        } else {
            const errorData = await response.json();
            showNotification(`❌ Failed to save rules: ${errorData.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error saving rules:', error);
        showNotification('❌ Network error while saving rules. Please check your connection.', 'error');
    }
}

// Show detailed feedback about what was saved
function showDetailedSaveFeedback(rules) {
    const details = [];
    
    if (rules.copyright_rules.enabled) {
        details.push(`Copyright detection enabled (threshold: ${rules.copyright_rules.similarity_threshold})`);
    } else {
        details.push('Copyright detection disabled');
    }
    
    if (rules.bias_detection.enabled) {
        details.push(`Bias detection enabled (${rules.bias_detection.categories.length} categories)`);
    } else {
        details.push('Bias detection disabled');
    }
    
    if (rules.content_filtering.explicit_content) {
        details.push('Content filtering enabled');
    } else {
        details.push('Content filtering disabled');
    }
    
    const message = `Settings saved:\n• ${details.join('\n• ')}`;
    showNotification(message, 'info', 5000);
}

// Reset compliance rules to default
async function resetComplianceRules() {
    if (confirm('Are you sure you want to reset all rules to default values?')) {
        // Reset UI to default values
        document.getElementById('copyright-toggle').checked = true;
        document.getElementById('similarity-threshold').value = 0.7;
        document.getElementById('threshold-value').textContent = '0.7';
        document.getElementById('bias-toggle').checked = true;
        document.getElementById('bias-threshold').value = 0.4;
        document.getElementById('bias-threshold-value').textContent = '0.4';
        document.getElementById('content-toggle').checked = true;
        
        // Save the reset values
        await saveComplianceRules();
        showNotification('Rules reset to default values and saved', 'success');
    }
}

// ===== UPLOAD SECTION FUNCTIONS =====

// Setup upload handlers
function setupUploadHandlers() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const startAnalysisBtn = document.getElementById('start-analysis-btn');
    
    // Browse button click
    if (browseBtn && fileInput) {
        browseBtn.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent event bubbling to upload area
            fileInput.click();
        });
    }
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelection);
    }
    
    // Drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        uploadArea.addEventListener('click', (event) => {
            // Only open file picker if clicking on the upload area itself, not on buttons
            if (event.target === uploadArea || event.target.classList.contains('upload-content')) {
                fileInput.click();
            }
        });
    }
    
    // Start analysis button
    if (startAnalysisBtn) {
        startAnalysisBtn.addEventListener('click', startAnalysis);
    }
}

// Handle file selection
function handleFileSelection(event) {
    const files = Array.from(event.target.files);
    addFilesToQueue(files);
    
    // Clear the input to allow selecting the same file again if needed
    event.target.value = '';
}

// Handle drag over
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

// Handle drop
function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = Array.from(event.dataTransfer.files);
    addFilesToQueue(files);
}

// Store uploaded files globally
let uploadedFiles = [];

// Clear upload queue
function clearUploadQueue() {
    const queueList = document.getElementById('queue-list');
    const uploadQueue = document.getElementById('upload-queue');
    
    if (queueList) {
        queueList.innerHTML = '';
    }
    
    if (uploadQueue) {
        uploadQueue.style.display = 'none';
    }
    
    uploadedFiles = [];
}

// Add files to upload queue
function addFilesToQueue(files) {
    const queueList = document.getElementById('queue-list');
    const uploadQueue = document.getElementById('upload-queue');
    
    if (!queueList || !uploadQueue) return;
    
    files.forEach(file => {
        if (isValidAudioFile(file)) {
            // Store the file for later use
            uploadedFiles.push(file);
            const queueItem = createQueueItem(file);
            queueList.appendChild(queueItem);
        } else {
            showNotification(`Invalid file type: ${file.name}`, 'error');
        }
    });
    
    if (queueList.children.length > 0) {
        uploadQueue.style.display = 'block';
    }
}

// Check if file is valid audio file
function isValidAudioFile(file) {
    const validTypes = ['.mp3', '.wav', '.flac', '.m4a', '.ogg'];
    return validTypes.some(type => file.name.toLowerCase().endsWith(type));
}

// Create queue item element
function createQueueItem(file) {
    const item = document.createElement('div');
    item.className = 'queue-item';
    item.innerHTML = `
        <div class="file-info">
            <i class="fas fa-music"></i>
            <span>${file.name}</span>
        </div>
        <div class="file-size">${formatFileSize(file.size)}</div>
    `;
    return item;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Start analysis
async function startAnalysis() {
    const queueList = document.getElementById('queue-list');
    
    if (queueList.children.length === 0) {
        showNotification('No files in queue', 'warning');
        return;
    }
    
    if (uploadedFiles.length === 0) {
        showNotification('No files available for analysis', 'warning');
        return;
    }
    
    // Get analysis options
    const options = {
        copyright: document.getElementById('copyright-analysis').checked,
        bias: document.getElementById('bias-analysis').checked,
        content: document.getElementById('content-analysis').checked,
        priority: document.getElementById('priority-select').value
    };
    
    showNotification('Starting analysis...', 'info');
    
    // Process each uploaded file
    const queueItems = Array.from(queueList.children);
    
    for (let i = 0; i < uploadedFiles.length && i < queueItems.length; i++) {
        const file = uploadedFiles[i];
        const item = queueItems[i];
        const fileName = file.name;
        item.style.opacity = '0.5';
        
        try {
            // Use async analysis endpoint
            const formData = new FormData();
            formData.append('file', file);
            formData.append('lyrics', ''); // Optional lyrics
            formData.append('priority', options.priority);
            
            const response = await fetch('/api/analyze/async', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                item.innerHTML = `
                    <div class="file-info">
                        <i class="fas fa-spinner fa-spin" style="color: #2196F3;"></i>
                        <span>${fileName}</span>
                    </div>
                    <div class="file-size">Processing...</div>
                `;
                
                // Poll for task completion
                pollTaskStatus(result.task_id, item, fileName);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed to start');
            }
        } catch (error) {
            console.error('Error analyzing file:', error);
            item.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-exclamation-circle" style="color: #f44336;"></i>
                    <span>${fileName}</span>
                </div>
                <div class="file-size">Failed: ${error.message}</div>
            `;
            showNotification(`Failed to analyze ${fileName}: ${error.message}`, 'error');
        }
    }
    
    showNotification('Analysis started for all files!', 'success');
}

// Poll task status
async function pollTaskStatus(taskId, item, fileName) {
    const maxAttempts = 30; // 30 seconds max
    let attempts = 0;
    
    const poll = async () => {
        try {
            const response = await fetch(`/api/tasks/${taskId}`);
            if (response.ok) {
                const status = await response.json();
                
                if (status.status === 'completed') {
                    item.innerHTML = `
                        <div class="file-info">
                            <i class="fas fa-check-circle" style="color: #4CAF50;"></i>
                            <span>${fileName}</span>
                        </div>
                        <div class="file-size">Completed</div>
                    `;
                    showNotification(`Analysis completed for ${fileName}`, 'success');
                    
                    // Clear the queue after a short delay to show completion
                    setTimeout(() => {
                        clearUploadQueue();
                    }, 2000);
                } else if (status.status === 'failed') {
                    item.innerHTML = `
                        <div class="file-info">
                            <i class="fas fa-exclamation-circle" style="color: #f44336;"></i>
                            <span>${fileName}</span>
                        </div>
                        <div class="file-size">Failed</div>
                    `;
                    showNotification(`Analysis failed for ${fileName}`, 'error');
                } else if (status.status === 'running' && attempts < maxAttempts) {
                    // Still running, poll again in 1 second
                    attempts++;
                    setTimeout(poll, 1000);
                } else {
                    // Timeout
                    item.innerHTML = `
                        <div class="file-info">
                            <i class="fas fa-clock" style="color: #ff9800;"></i>
                            <span>${fileName}</span>
                        </div>
                        <div class="file-size">Timeout</div>
                    `;
                }
            }
        } catch (error) {
            console.error('Error polling task status:', error);
            item.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-exclamation-circle" style="color: #f44336;"></i>
                    <span>${fileName}</span>
                </div>
                <div class="file-size">Error</div>
            `;
        }
    };
    
    poll();
}

// ===== REPORTS SECTION FUNCTIONS =====

// Load reports data
async function loadReportsData() {
    try {
        // Get current filter values
        const startDate = document.getElementById('start-date')?.value || '';
        const endDate = document.getElementById('end-date')?.value || '';
        const reportType = document.getElementById('report-type-filter')?.value || 'all';
        const status = document.getElementById('status-filter')?.value || 'all';
        
        // Build query parameters
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (reportType && reportType !== 'all') params.append('analysis_type', reportType);
        if (status && status !== 'all') params.append('status', status);
        
        // Load reports summary with filters
        const summaryUrl = `/api/reports/summary${params.toString() ? '?' + params.toString() : ''}`;
        const summaryResponse = await fetch(summaryUrl);
        const summary = await summaryResponse.json();
        
        // Load trend data with filters
        const trendsParams = new URLSearchParams();
        trendsParams.append('days', '30');
        if (reportType && reportType !== 'all') trendsParams.append('analysis_type', reportType);
        
        const trendsUrl = `/api/reports/trends?${trendsParams.toString()}`;
        const trendsResponse = await fetch(trendsUrl);
        const trends = await trendsResponse.json();
        
        updateReportsUI(summary, trends);
    } catch (error) {
        console.error('Error loading reports data:', error);
        // Use mock data as fallback
        updateReportsUI(getMockReportsSummary(), getMockTrendsData());
    }
    
    setupReportsHandlers();
}

// Update reports UI
function updateReportsUI(summary, trends) {
    // Update metrics
    const metrics = document.querySelectorAll('.metric-value');
    if (metrics.length >= 3) {
        metrics[0].textContent = (summary.total_analyses || 0).toLocaleString();
        metrics[1].textContent = `${summary.average_compliance_score || 0}%`;
        metrics[2].textContent = (summary.issues_found || 0).toString();
    }
    
    // Initialize trend chart with real data
    if (trends && trends.labels && trends.labels.length > 0) {
        initializeTrendChart(trends);
    } else {
        // Show empty chart state if no data
        const chartContainer = document.querySelector('.trend-chart');
        if (chartContainer) {
            chartContainer.innerHTML = '<p style="text-align: center; color: #888; padding: 2rem;">No trend data available</p>';
        }
    }
}

// Initialize trend chart
function initializeTrendChart(trendData) {
    const ctx = document.getElementById('trendChart');
    if (!ctx || !trendData) return;
    
    // Destroy existing chart if it exists
    if (window.reportsTrendChart) {
        window.reportsTrendChart.destroy();
    }
    
    // Format labels for better display
    const formattedLabels = (trendData.labels || []).map(label => {
        const date = new Date(label);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    window.reportsTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedLabels,
            datasets: [{
                label: 'Analyses',
                data: trendData.analysis_counts || [],
                borderColor: '#f5576c',
                backgroundColor: 'rgba(245, 87, 108, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#f5576c',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const originalLabel = trendData.labels[context[0].dataIndex];
                            const date = new Date(originalLabel);
                            return date.toLocaleDateString('en-US', { 
                                weekday: 'short', 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                            });
                        },
                        label: function(context) {
                            return `Analyses: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#8892b0',
                        maxTicksLimit: 7
                    }
                },
                y: {
                    grid: {
                        color: '#3a3f5c'
                    },
                    ticks: {
                        color: '#8892b0',
                        beginAtZero: true
                    }
                }
            }
        }
    });
}

// Setup reports handlers
function setupReportsHandlers() {
    const generateReportBtn = document.getElementById('generate-report-btn');
    if (generateReportBtn) {
        generateReportBtn.addEventListener('click', generateReport);
    }
    
    // Add filter change handlers
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const reportTypeFilter = document.getElementById('report-type-filter');
    const statusFilter = document.getElementById('status-filter');
    
    if (startDateInput) {
        startDateInput.addEventListener('change', () => {
            loadReportsData(); // Reload data when filters change
        });
    }
    
    if (endDateInput) {
        endDateInput.addEventListener('change', () => {
            loadReportsData(); // Reload data when filters change
        });
    }
    
    if (reportTypeFilter) {
        reportTypeFilter.addEventListener('change', () => {
            loadReportsData(); // Reload data when filters change
        });
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', () => {
            loadReportsData(); // Reload data when filters change
        });
    }
}

// Generate report
async function generateReport() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const reportType = document.getElementById('report-type-filter').value;
    const status = document.getElementById('status-filter').value;
    
    showNotification('Generating report...', 'info');
    
    try {
        const response = await fetch('/api/reports/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                report_type: 'compliance_summary',
                format: 'pdf',
                start_date: startDate,
                end_date: endDate,
                analysis_type: reportType
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Report generated successfully!', 'success');
            
            // Show report details
            setTimeout(() => {
                showReportDetails(result);
            }, 1000);
        } else {
            const errorData = await response.json();
            showNotification(`Failed to generate report: ${errorData.detail || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error generating report:', error);
        showNotification('Error generating report', 'error');
    }
}

// Show report details
function showReportDetails(reportData) {
    const details = [];
    
    if (reportData.summary) {
        details.push(`Total Analyses: ${reportData.summary.total_analyses}`);
        details.push(`Average Compliance: ${reportData.summary.average_compliance_score}%`);
        details.push(`Issues Found: ${reportData.summary.issues_found}`);
        details.push(`Compliance Rate: ${reportData.summary.compliance_rate}%`);
    }
    
    if (reportData.trends) {
        details.push(`Trend Period: ${reportData.trends.period}`);
        details.push(`Data Points: ${reportData.trends.labels.length} days`);
    }
    
    const message = `Report Generated:\n• ${details.join('\n• ')}\n• Format: ${reportData.format}\n• Generated: ${new Date(reportData.exported_at).toLocaleString()}`;
    showNotification(message, 'info', 8000);
}

// ===== SETTINGS SECTION FUNCTIONS =====

// Load settings data
async function loadSettingsData() {
    try {
        // Load settings from API
        const response = await fetch('/api/settings');
        const settings = await response.json();
        updateSettingsUI(settings);
        setupSettingsHandlers();
    } catch (error) {
        console.error('Error loading settings:', error);
        // Fallback to localStorage if API fails
        const settings = JSON.parse(localStorage.getItem('musicPoliceSettings') || '{}');
        updateSettingsUI(settings);
        setupSettingsHandlers();
    }
}

// Update settings UI
function updateSettingsUI(settings) {
    // Map database keys to frontend element IDs
    const keyMappings = {
        'default_priority': 'default-priority',
        'auto_delete_days': 'auto-delete',
        'email_notifications': 'email-notifications',
        'api_rate_limit': 'rate-limit',
        'max_file_size_mb': 'max-file-size',
        'api_logging': 'api-logging',
        'require_auth': 'require-auth',
        'encrypt_files': 'encrypt-files',
        'session_timeout_minutes': 'session-timeout'
    };
    
    // Update form fields with saved settings
    Object.keys(keyMappings).forEach(dbKey => {
        const frontendKey = keyMappings[dbKey];
        const element = document.getElementById(frontendKey);
        if (element && settings[dbKey] !== undefined) {
            if (element.type === 'checkbox') {
                element.checked = settings[dbKey];
            } else {
                element.value = settings[dbKey];
            }
        }
    });
}

// Setup settings handlers
function setupSettingsHandlers() {
    const saveSettingsBtn = document.getElementById('save-settings-btn');
    const resetSettingsBtn = document.getElementById('reset-settings-btn');
    const clearCacheBtn = document.getElementById('clear-cache-btn');
    
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }
    
    if (resetSettingsBtn) {
        resetSettingsBtn.addEventListener('click', resetSettings);
    }
    
    if (clearCacheBtn) {
        clearCacheBtn.addEventListener('click', clearCache);
    }
}

// Save settings
async function saveSettings() {
    const settings = {
        'default-priority': document.getElementById('default-priority').value,
        'auto-delete': document.getElementById('auto-delete').value,
        'email-notifications': document.getElementById('email-notifications').checked,
        'rate-limit': document.getElementById('rate-limit').value,
        'max-file-size': document.getElementById('max-file-size').value,
        'api-logging': document.getElementById('api-logging').checked,
        'require-auth': document.getElementById('require-auth').checked,
        'encrypt-files': document.getElementById('encrypt-files').checked,
        'session-timeout': document.getElementById('session-timeout').value
    };
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('✅ Settings saved successfully to database!', 'success');
        } else {
            throw new Error('Failed to save settings');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        // Fallback to localStorage
        localStorage.setItem('musicPoliceSettings', JSON.stringify(settings));
        showNotification('⚠️ Settings saved locally (database unavailable)', 'warning');
    }
}

// Reset settings
async function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
        // Reset UI to default values
        document.getElementById('default-priority').value = 'normal';
        document.getElementById('auto-delete').value = '7';
        document.getElementById('email-notifications').checked = true;
        document.getElementById('rate-limit').value = '100';
        document.getElementById('max-file-size').value = '100';
        document.getElementById('api-logging').checked = true;
        document.getElementById('require-auth').checked = true;
        document.getElementById('encrypt-files').checked = true;
        document.getElementById('session-timeout').value = '60';
        
        // Save the reset values
        await saveSettings();
        showNotification('Settings reset to default values and saved', 'success');
    }
}

// Clear cache
function clearCache() {
    if (confirm('Are you sure you want to clear the cache? This will remove all temporary data.')) {
        // Clear localStorage cache
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('musicPolice_')) {
                localStorage.removeItem(key);
            }
        });
        showNotification('Cache cleared successfully!', 'success');
    }
}

// ===== AUDIO PLAYBACK FUNCTIONS =====

// Global audio player state
let currentAudio = null;
let currentAnalysisId = null;

// Play audio for a specific analysis
function playAudio(analysisId) {
    // Stop current audio if playing
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    
    // Update play buttons
    updatePlayButtons(analysisId, 'playing');
    
    // Create new audio element
    currentAudio = new Audio(`/api/analyses/${analysisId}/audio`);
    currentAnalysisId = analysisId;
    
    // Show global audio player
    showGlobalAudioPlayer(analysisId);
    
    // Set up audio event listeners
    currentAudio.addEventListener('loadstart', () => {
        showNotification('Loading audio...', 'info', 2000);
    });
    
    currentAudio.addEventListener('canplay', () => {
        showNotification('Audio ready to play', 'success', 2000);
        // Initialize progress display
        updateAudioProgress();
    });
    
    // Add progress tracking
    currentAudio.addEventListener('timeupdate', () => {
        updateAudioProgress();
    });
    
    currentAudio.addEventListener('loadedmetadata', () => {
        updateAudioProgress();
    });
    
    currentAudio.addEventListener('error', (e) => {
        console.error('Audio error:', e);
        let errorMessage = 'Error loading audio file';
        
        if (currentAudio.error) {
            switch (currentAudio.error.code) {
                case 1: // MEDIA_ERR_ABORTED
                    errorMessage = 'Audio playback was aborted';
                    break;
                case 2: // MEDIA_ERR_NETWORK
                    errorMessage = 'Network error loading audio file';
                    break;
                case 3: // MEDIA_ERR_DECODE
                    errorMessage = 'Audio file format not supported';
                    break;
                case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
                    errorMessage = 'Audio file not found or not supported';
                    break;
                default:
                    errorMessage = `Audio error: ${currentAudio.error.message}`;
            }
        }
        
        showNotification(errorMessage, 'error');
        updatePlayButtons(analysisId, 'stopped');
        hideGlobalAudioPlayer();
        currentAudio = null;
        currentAnalysisId = null;
    });
    
    currentAudio.addEventListener('ended', () => {
        updatePlayButtons(analysisId, 'stopped');
        hideGlobalAudioPlayer();
        currentAudio = null;
        currentAnalysisId = null;
    });
    
    // Set timeout for loading
    const loadTimeout = setTimeout(() => {
        if (currentAudio && currentAudio.readyState < 2) {
            showNotification('Audio file not found or cannot be loaded', 'error');
            updatePlayButtons(analysisId, 'stopped');
            hideGlobalAudioPlayer();
            currentAudio = null;
            currentAnalysisId = null;
        }
    }, 10000); // 10 second timeout
    
    currentAudio.addEventListener('canplay', () => {
        clearTimeout(loadTimeout);
    });
    
    // Start playing
    currentAudio.play().catch(error => {
        console.error('Playback error:', error);
        clearTimeout(loadTimeout);
        showNotification('Error playing audio: ' + error.message, 'error');
        updatePlayButtons(analysisId, 'stopped');
        hideGlobalAudioPlayer();
        currentAudio = null;
        currentAnalysisId = null;
    });
}

// Update play button states
function updatePlayButtons(analysisId, state) {
    const playButtons = document.querySelectorAll('.play-button');
    playButtons.forEach(btn => {
        const btnAnalysisId = btn.getAttribute('onclick').match(/playAudio\((\d+)\)/);
        if (btnAnalysisId && parseInt(btnAnalysisId[1]) === analysisId) {
            const icon = btn.querySelector('i');
            if (state === 'playing') {
                btn.classList.add('playing');
                icon.className = 'fas fa-pause';
                btn.title = 'Pause audio';
            } else {
                btn.classList.remove('playing');
                icon.className = 'fas fa-play';
                btn.title = 'Play audio';
            }
        } else if (state === 'playing') {
            // Reset other buttons
            btn.classList.remove('playing');
            const icon = btn.querySelector('i');
            icon.className = 'fas fa-play';
            btn.title = 'Play audio';
        }
    });
}

// Show global audio player
function showGlobalAudioPlayer(analysisId) {
    let player = document.getElementById('global-audio-player');
    if (!player) {
        player = createGlobalAudioPlayer();
        document.body.appendChild(player);
    }
    
    // Update player content
    const title = player.querySelector('h5');
    const filename = document.querySelector(`[onclick="playAudio(${analysisId})"]`)?.closest('.table-row')?.querySelector('span')?.textContent || 'Unknown';
    title.textContent = `Now Playing: ${filename}`;
    
    // Reset progress display
    const currentTimeDisplay = document.getElementById('current-time');
    const totalTimeDisplay = document.getElementById('total-time');
    const progressBar = document.getElementById('audio-progress');
    const progressFill = document.getElementById('progress-bar-fill');
    
    if (currentTimeDisplay) currentTimeDisplay.textContent = '0:00';
    if (totalTimeDisplay) totalTimeDisplay.textContent = '0:00';
    if (progressBar) progressBar.value = 0;
    if (progressFill) progressFill.style.width = '0%';
    
    player.classList.add('show');
}

// Hide global audio player
function hideGlobalAudioPlayer() {
    const player = document.getElementById('global-audio-player');
    if (player) {
        player.classList.remove('show');
    }
}

// Create global audio player element
function createGlobalAudioPlayer() {
    const player = document.createElement('div');
    player.id = 'global-audio-player';
    player.className = 'global-audio-player';
    player.innerHTML = `
        <h5>Now Playing</h5>
        <div class="audio-progress-container">
            <span class="time-display" id="current-time">0:00</span>
            <div class="progress-bar-container">
                <input type="range" id="audio-progress" min="0" max="100" value="0" onchange="seekAudio(this.value)">
                <div class="progress-bar-fill" id="progress-bar-fill"></div>
            </div>
            <span class="time-display" id="total-time">0:00</span>
        </div>
        <div class="global-audio-controls">
            <button onclick="togglePlayPause()">
                <i class="fas fa-pause"></i>
            </button>
            <button onclick="stopAudio()">
                <i class="fas fa-stop"></i>
            </button>
            <button onclick="hideGlobalAudioPlayer()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    return player;
}

// Toggle play/pause
function togglePlayPause() {
    if (currentAudio) {
        if (currentAudio.paused) {
            currentAudio.play();
            updatePlayButtons(currentAnalysisId, 'playing');
        } else {
            currentAudio.pause();
            updatePlayButtons(currentAnalysisId, 'paused');
        }
    }
}

// Stop audio
function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        updatePlayButtons(currentAnalysisId, 'stopped');
        hideGlobalAudioPlayer();
        currentAudio = null;
        currentAnalysisId = null;
    }
}

// Seek audio to specific position
function seekAudio(percentage) {
    if (currentAudio && currentAudio.duration) {
        const seekTime = (percentage / 100) * currentAudio.duration;
        currentAudio.currentTime = seekTime;
    }
}

// Format time in MM:SS format
function formatTime(seconds) {
    if (isNaN(seconds) || !isFinite(seconds)) return '0:00';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Update progress bar and time display
function updateAudioProgress() {
    if (!currentAudio) return;
    
    const progressBar = document.getElementById('audio-progress');
    const progressFill = document.getElementById('progress-bar-fill');
    const currentTimeDisplay = document.getElementById('current-time');
    const totalTimeDisplay = document.getElementById('total-time');
    
    if (currentAudio.duration && isFinite(currentAudio.duration)) {
        const progress = (currentAudio.currentTime / currentAudio.duration) * 100;
        
        if (progressBar) {
            progressBar.value = progress;
        }
        
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
        
        if (currentTimeDisplay) {
            currentTimeDisplay.textContent = formatTime(currentAudio.currentTime);
        }
        
        if (totalTimeDisplay) {
            totalTimeDisplay.textContent = formatTime(currentAudio.duration);
        }
    }
}

// ===== UTILITY FUNCTIONS =====

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Handle multi-line messages
    const formattedMessage = message.replace(/\n/g, '<br>');
    
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${formattedMessage}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after specified duration
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, duration);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Get notification color
function getNotificationColor(type) {
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196F3'
    };
    return colors[type] || '#2196F3';
}

// Initialize all event handlers

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Modal functions

function showLyrics(analysisId) {
    currentAnalysisId = analysisId;
    const modal = document.getElementById('lyrics-modal');
    const content = document.getElementById('lyrics-content');
    
    content.innerHTML = '<p>Loading lyrics and audio...</p>';
    modal.style.display = 'flex';
    
    // Fetch lyrics and analysis details from API
    Promise.all([
        fetch(`/api/analyses/${analysisId}/lyrics`).then(r => r.json()),
        fetch(`/api/analyses/${analysisId}`).then(r => r.json())
    ])
    .then(([lyricsData, analysisData]) => {
        let html = '';
        
        
        // Add lyrics section
        html += `
            <div class="lyrics-section">
                <div class="lyrics-header">
                    <h4>Lyrics</h4>
                    <button id="edit-lyrics-btn" class="btn btn-secondary">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
                <p style="color: #8892b0; font-size: 0.9rem; margin-bottom: 1rem; font-style: italic; padding: 0.75rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; border-left: 3px solid #667eea;">
                    💡 Use the play button in the analysis table to start audio playback
                </p>
                <div id="lyrics-display" class="lyrics-content">
        `;
        
        if (lyricsData.lyrics) {
            // Format lyrics with better spacing and readability
            const formattedLyrics = lyricsData.lyrics
                .replace(/\n\n/g, '\n\n') // Preserve double line breaks
                .replace(/\n/g, '\n') // Keep single line breaks
                .trim();
            html += `<div style="white-space: pre-wrap; line-height: 1.8; font-size: 1rem; color: #e2e8f0;">${formattedLyrics}</div>`;
        } else {
            html += '<p style="color: #8892b0; font-style: italic; text-align: center; padding: 2rem;">No lyrics available for this analysis.</p>';
        }
        
        html += `
                </div>
                <div id="lyrics-editor" class="lyrics-editor" style="display: none;">
                    <textarea id="lyrics-textarea" rows="12" placeholder="Enter or edit lyrics here...">${lyricsData.lyrics || ''}</textarea>
                    <div class="editor-controls">
                        <button id="save-lyrics-btn" class="btn btn-success">
                            <i class="fas fa-save"></i> Save Changes
                        </button>
                        <button id="cancel-edit-btn" class="btn btn-secondary">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        
        // Setup lyrics editing
        setupLyricsEditing(analysisId);
        
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        content.innerHTML = '<p>Error loading data. Please try again.</p>';
    });
}

function closeLyricsModal() {
    const modal = document.getElementById('lyrics-modal');
    modal.style.display = 'none';
    currentAnalysisId = null;
}

// Setup lyrics editing functionality
function setupLyricsEditing(analysisId) {
    const editBtn = document.getElementById('edit-lyrics-btn');
    const saveBtn = document.getElementById('save-lyrics-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    const lyricsDisplay = document.getElementById('lyrics-display');
    const lyricsEditor = document.getElementById('lyrics-editor');
    const lyricsTextarea = document.getElementById('lyrics-textarea');
    
    if (!editBtn) return;
    
    // Edit button
    editBtn.addEventListener('click', () => {
        lyricsDisplay.style.display = 'none';
        lyricsEditor.style.display = 'block';
        lyricsTextarea.focus();
    });
    
    // Cancel button
    cancelBtn.addEventListener('click', () => {
        lyricsEditor.style.display = 'none';
        lyricsDisplay.style.display = 'block';
    });
    
    // Save button
    saveBtn.addEventListener('click', async () => {
        const newLyrics = lyricsTextarea.value.trim();
        
        try {
            showNotification('Saving lyrics...', 'info');
            
            const response = await fetch(`/api/analyses/${analysisId}/lyrics`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ lyrics: newLyrics })
            });
            
            if (response.ok) {
                showNotification('✅ Lyrics saved successfully!', 'success');
                
                // Update display
                const formattedLyrics = newLyrics
                    .replace(/\n\n/g, '\n\n') // Preserve double line breaks
                    .replace(/\n/g, '\n') // Keep single line breaks
                    .trim();
                lyricsDisplay.innerHTML = `<div style="white-space: pre-wrap; line-height: 1.8; font-size: 1rem; color: #e2e8f0;">${formattedLyrics}</div>`;
                
                // Switch back to display mode
                lyricsEditor.style.display = 'none';
                lyricsDisplay.style.display = 'block';
            } else {
                const errorData = await response.json();
                showNotification(`❌ Failed to save lyrics: ${errorData.detail || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error saving lyrics:', error);
            showNotification('❌ Network error while saving lyrics', 'error');
        }
    });
}

function copyLyrics() {
    const content = document.getElementById('lyrics-content');
    const text = content.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Lyrics copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy lyrics:', err);
        showNotification('Failed to copy lyrics', 'error');
    });
}

function showAnalysisDetails(analysisId) {
    currentAnalysisId = analysisId;
    const modal = document.getElementById('analysis-modal');
    const content = document.getElementById('analysis-content');
    
    content.innerHTML = '<p>Loading analysis details...</p>';
    modal.style.display = 'flex';
    
    // Fetch analysis details from API
    fetch(`/api/analyses/${analysisId}`)
        .then(response => response.json())
        .then(data => {
            displayAnalysisDetails(data);
        })
        .catch(error => {
            console.error('Error fetching analysis details:', error);
            content.innerHTML = '<p>Error loading analysis details. Please try again.</p>';
        });
}

function closeAnalysisModal() {
    const modal = document.getElementById('analysis-modal');
    modal.style.display = 'none';
    currentAnalysisId = null;
}

function displayAnalysisDetails(analysis) {
    const content = document.getElementById('analysis-content');
    
    let html = `
        <div class="analysis-detail">
            <h4>📁 File Information</h4>
            <p><strong>Filename:</strong> ${analysis.filename}</p>
            <p><strong>Compliance Score:</strong> ${(analysis.compliance_score * 100).toFixed(1)}%</p>
            <p><strong>Analysis Date:</strong> ${new Date(analysis.created_at).toLocaleString()}</p>
            <p><strong>Analysis ID:</strong> ${analysis.id}</p>
        </div>
    `;
    
    // Similar Songs Section
    if (analysis.similar_songs && analysis.similar_songs.length > 0) {
        html += `
            <div class="analysis-detail">
                <h4>🎵 Similar Songs Found</h4>
                <p>This song appears to be similar to the following previously uploaded songs:</p>
        `;
        
        analysis.similar_songs.forEach(song => {
            html += `
                <div class="similar-song">
                    <h5>${song.filename}</h5>
                    <p><strong>Similarity Score:</strong> <span class="similarity-score">${(song.similarity_score * 100).toFixed(1)}%</span></p>
                    <p><strong>Uploaded:</strong> ${new Date(song.created_at).toLocaleDateString()}</p>
                    <p><strong>Compliance Score:</strong> ${(song.compliance_score * 100).toFixed(1)}%</p>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    // Issues Section
    if (analysis.issues && analysis.issues.length > 0) {
        html += `
            <div class="analysis-detail">
                <h4>⚠️ Issues Detected</h4>
        `;
        
        analysis.issues.forEach(issue => {
            const severityClass = issue.severity || 'medium';
            const severityIcon = severityClass === 'high' ? '🔴' : severityClass === 'medium' ? '🟡' : '🟢';
            html += `
                <div class="issue-item ${severityClass}">
                    <p><strong>${severityIcon} ${issue.type}:</strong> ${issue.detail || issue.description}</p>
                    ${issue.confidence ? `<p><em>Confidence: ${(issue.confidence * 100).toFixed(1)}%</em></p>` : ''}
                </div>
            `;
        });
        
        html += '</div>';
    } else {
        html += `
            <div class="analysis-detail">
                <h4>✅ No Issues Detected</h4>
                <p>This audio file passed all compliance checks successfully.</p>
            </div>
        `;
    }
    
    // Recommendations Section
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        html += `
            <div class="analysis-detail">
                <h4>💡 Recommendations</h4>
        `;
        
        analysis.recommendations.forEach(rec => {
            html += `
                <div class="recommendation-item">
                    <p>${rec}</p>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    // Metadata Section
    if (analysis.metadata) {
        const plagiarismScore = (analysis.metadata.plagiarism_score || 0) * 100;
        const biasScore = (analysis.metadata.bias_score || 0) * 100;
        const fileSize = (analysis.metadata.file_size || 0) / 1024 / 1024;
        
        html += `
            <div class="analysis-detail">
                <h4>📊 Analysis Metadata</h4>
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <strong>Plagiarism Score:</strong> 
                        <span class="score-badge ${plagiarismScore > 70 ? 'high' : plagiarismScore > 40 ? 'medium' : 'low'}">
                            ${plagiarismScore.toFixed(1)}%
                        </span>
                    </div>
                    <div class="metadata-item">
                        <strong>Bias Score:</strong> 
                        <span class="score-badge ${biasScore > 60 ? 'high' : biasScore > 30 ? 'medium' : 'low'}">
                            ${biasScore.toFixed(1)}%
                        </span>
                    </div>
                    <div class="metadata-item">
                        <strong>File Size:</strong> ${fileSize.toFixed(2)} MB
                    </div>
                    <div class="metadata-item">
                        <strong>Lyrics Source:</strong> 
                        <span class="source-badge ${analysis.metadata.lyrics_source}">
                            ${analysis.metadata.lyrics_source || 'none'}
                        </span>
                    </div>
                    ${analysis.metadata.has_lyrics ? `
                    <div class="metadata-item">
                        <strong>Lyrics Available:</strong> 
                        <span class="status-badge success">✅ Yes</span>
                    </div>
                    ` : `
                    <div class="metadata-item">
                        <strong>Lyrics Available:</strong> 
                        <span class="status-badge warning">❌ No</span>
                    </div>
                    `}
                </div>
            </div>
        `;
    }
    
    content.innerHTML = html;
}

// Close modals when clicking outside
window.onclick = function(event) {
    const lyricsModal = document.getElementById('lyrics-modal');
    const analysisModal = document.getElementById('analysis-modal');
    
    if (event.target === lyricsModal) {
        closeLyricsModal();
    }
    if (event.target === analysisModal) {
        closeAnalysisModal();
    }
}


