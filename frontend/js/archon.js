// Archon Agent Integration
class ArchonService {
    constructor() {
        this.baseUrl = '/api/archon';
    }

    /**
     * Get all income streams
     * @returns {Promise<Array>} List of income streams
     */
    async getIncomeStreams() {
        try {
            const response = await fetch(`${this.baseUrl}/income-streams`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to get income streams');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error fetching income streams:', error);
            throw error;
        }
    }

    /**
     * Create a new income stream
     * @param {Object} data Income stream data
     * @param {string} data.stream_type Type of income stream (membership, digital_product, etc.)
     * @param {string} data.name Name of the income stream
     * @param {string} data.description Description of the income stream
     * @param {number} [data.automation_level=8] Level of automation (1-10)
     * @param {Array<string>} [data.required_services=[]] Required services
     * @returns {Promise<Object>} Created income stream
     */
    async createIncomeStream(data) {
        try {
            const response = await fetch(`${this.baseUrl}/income-streams`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to create income stream');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error creating income stream:', error);
            throw error;
        }
    }

    /**
     * Create a new subscription tier
     * @param {Object} data Subscription tier data
     * @param {string} data.name Name of the tier
     * @param {number} data.price Price of the tier
     * @param {Array<string>} data.features Features included in this tier
     * @param {string} [data.billing_cycle='monthly'] Billing cycle (monthly, yearly, quarterly)
     * @returns {Promise<Object>} Created subscription tier
     */
    async createSubscriptionTier(data) {
        try {
            const response = await fetch(`${this.baseUrl}/subscription-tiers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to create subscription tier');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error creating subscription tier:', error);
            throw error;
        }
    }

    /**
     * Integrate Stripe payment processing
     * @param {Object} data Stripe integration data
     * @param {string} data.api_key Stripe API key
     * @param {string} [data.webhook_secret] Stripe webhook secret
     * @returns {Promise<Object>} Integration status
     */
    async integrateStripe(data) {
        try {
            const response = await fetch(`${this.baseUrl}/stripe/integrate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to integrate Stripe');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error integrating Stripe:', error);
            throw error;
        }
    }

    /**
     * Generate revenue forecast
     * @param {Object} data Forecast parameters
     * @param {number} [data.months=12] Number of months to forecast
     * @param {number} [data.growth_rate=5.0] Monthly growth rate percentage
     * @returns {Promise<Object>} Revenue forecast
     */
    async generateForecast(data = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/forecast`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to generate forecast');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error generating forecast:', error);
            throw error;
        }
    }

    /**
     * Implement an income stream
     * @param {number} incomeStreamId ID of the income stream to implement
     * @returns {Promise<Object>} Implementation details
     */
    async implementIncomeStream(incomeStreamId) {
        try {
            const response = await fetch(`${this.baseUrl}/income-streams/${incomeStreamId}/implement`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to implement income stream');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error implementing income stream:', error);
            throw error;
        }
    }

    /**
     * Generate a deployment guide for an income stream
     * @param {number} incomeStreamId ID of the income stream
     * @param {Object} [implementationResult] Optional Archon implementation result
     * @returns {Promise<Object>} Deployment guide
     */
    async generateDeploymentGuide(incomeStreamId, implementationResult = null) {
        try {
            const response = await fetch(`${this.baseUrl}/income-streams/${incomeStreamId}/deployment-guide`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    implementation_result: implementationResult
                })
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to generate deployment guide');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error generating deployment guide:', error);
            throw error;
        }
    }

    /**
     * @param {string} agentParams JSON string of agent parameters
     * @returns {Promise<Object>} Archon agent configuration and status
     */
    async runArchonAgent(incomeStreamId, agentParams = '{}') {
        try {
            const response = await fetch(`${this.baseUrl}/run-agent`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    income_stream_id: incomeStreamId,
                    agent_parameters: agentParams // Include agent parameters in request body
                })
            });
            
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error || 'Failed to run Archon agent');
            }
            
            return result.data;
        } catch (error) {
            console.error('Error running Archon agent:', error);
            throw error;
        }
    }
}

// Initialize the ArchonService
const archonService = new ArchonService();

// DOM elements for Archon UI
let archonContainer;
let incomeStreamsList;
let incomeStreamForm;
let runAgentButton;
let deploymentGuideContainer;
let forecastContainer;

// Initialize the Archon UI
document.addEventListener('DOMContentLoaded', function() {
    // Check if the Archon UI container exists
    archonContainer = document.getElementById('archon-container');
    if (!archonContainer) {
        // Create the Archon UI container if it doesn't exist
        createArchonUI();
    } else {
        // Initialize existing UI elements
        initializeArchonUIElements();
    }
});

/**
 * Create the Archon UI dynamically
 */
function createArchonUI() {
    // Create main container
    archonContainer = document.createElement('div');
    archonContainer.id = 'archon-container';
    archonContainer.className = 'archon-container';
    
    // Create UI content
    archonContainer.innerHTML = `
        <div class="archon-header">
            <h2>Archon Passive Income Generator</h2>
            <p>Create automated income streams with minimal human intervention</p>
        </div>
        
        <div class="archon-content">
            <div class="archon-sidebar">
                <div class="archon-section">
                    <h3>Income Streams</h3>
                    <div id="income-streams-list" class="income-streams-list">
                        <p>No income streams created yet.</p>
                    </div>
                    <button id="new-income-stream-btn" class="btn btn-primary">Create New Income Stream</button>
                </div>
            </div>
            
            <div class="archon-main">
                <div id="income-stream-form-container" class="archon-section hidden">
                    <h3>Create Income Stream</h3>
                    <form id="income-stream-form">
                        <div class="input-group">
                            <label for="stream-name">Name</label>
                            <input type="text" id="stream-name" class="form-input" placeholder="Name your income stream" required>
                        </div>
                        
                        <div class="input-group">
                            <label for="stream-type">Type</label>
                            <select id="stream-type" class="form-input" required>
                                <option value="">Select a type</option>
                                <option value="membership">Membership Site</option>
                                <option value="digital_product">Digital Product</option>
                                <option value="affiliate">Affiliate Marketing</option>
                                <option value="saas">Software as a Service</option>
                                <option value="marketplace">Marketplace</option>
                            </select>
                        </div>
                        
                        <div class="input-group">
                            <label for="stream-description">Description</label>
                            <textarea id="stream-description" class="form-input" placeholder="Describe your income stream" required></textarea>
                        </div>
                        
                        <div class="input-group">
                            <label for="automation-level">Automation Level (1-10)</label>
                            <input type="range" id="automation-level" class="form-range" min="1" max="10" value="8">
                            <div class="range-value"><span id="automation-value">8</span>/10</div>
                        </div>
                        
                        <div class="input-group">
                            <label>Required Services</label>
                            <div class="checkbox-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" name="required-services" value="stripe"> Stripe
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="required-services" value="shopify"> Shopify
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="required-services" value="mailchimp"> MailChimp
                                </label>
                                <label class="checkbox-label">
                                    <input type="checkbox" name="required-services" value="wordpress"> WordPress
                                </label>
                            </div>
                        </div>
                        
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">Create Income Stream</button>
                            <button type="button" id="cancel-form" class="btn btn-secondary">Cancel</button>
                        </div>
                    </form>
                </div>
                
                <div id="income-stream-details" class="archon-section hidden">
                    <div id="income-stream-header"></div>
                    
                    <div class="archon-tabs">
                        <button class="tab-btn active" data-tab="overview">Overview</button>
                        <button class="tab-btn" data-tab="implement">Implement</button>
                        <button class="tab-btn" data-tab="forecast">Revenue Forecast</button>
                        <button class="tab-btn" data-tab="deploy">Deployment Guide</button>
                    </div>
                    
                    <div class="tab-content active" id="overview-tab">
                        <div class="income-stream-overview"></div>
                    </div>
                    
                    <div class="tab-content" id="implement-tab">
                        <div class="implement-actions">
                            <p>Use the Archon Agent to implement this income stream with minimal human intervention.</p>
                            <div class="input-group">
                                <label for="agent-params">Agent Parameters (JSON)</label>
                                <textarea id="agent-params" class="form-input" placeholder="Enter agent parameters"></textarea>
                            </div>
                            <button id="run-agent-btn" class="btn btn-primary">Run Archon Agent</button>
                        </div>
                        <div id="agent-result" class="agent-result hidden"></div>
                    </div>
                    
                    <div class="tab-content" id="forecast-tab">
                        <div class="forecast-controls">
                            <div class="input-group inline">
                                <label for="forecast-months">Months</label>
                                <input type="number" id="forecast-months" class="form-input" min="1" max="60" value="12">
                            </div>
                            <div class="input-group inline">
                                <label for="growth-rate">Monthly Growth (%)</label>
                                <input type="number" id="growth-rate" class="form-input" min="0" max="100" value="5" step="0.1">
                            </div>
                            <button id="generate-forecast-btn" class="btn btn-primary">Generate Forecast</button>
                        </div>
                        <div id="forecast-result" class="forecast-result"></div>
                    </div>
                    
                    <div class="tab-content" id="deploy-tab">
                        <div class="deployment-actions">
                            <p>Generate a comprehensive deployment guide for this income stream.</p>
                            <button id="generate-guide-btn" class="btn btn-primary">Generate Deployment Guide</button>
                        </div>
                        <div id="deployment-guide" class="deployment-guide"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add to document body or a specific container
    const mainContainer = document.querySelector('.main-content') || document.body;
    mainContainer.appendChild(archonContainer);
    
    // Initialize UI elements
    initializeArchonUIElements();
    
    // Add CSS styles
    addArchonStyles();
}

/**
 * Initialize Archon UI elements and event listeners
 */
function initializeArchonUIElements() {
    // Get UI elements
    incomeStreamsList = document.getElementById('income-streams-list');
    incomeStreamForm = document.getElementById('income-stream-form');
    const newIncomeStreamBtn = document.getElementById('new-income-stream-btn');
    const cancelFormBtn = document.getElementById('cancel-form');
    const formContainer = document.getElementById('income-stream-form-container');
    const detailsContainer = document.getElementById('income-stream-details');
    const automationRange = document.getElementById('automation-level');
    const automationValue = document.getElementById('automation-value');
    const tabButtons = document.querySelectorAll('.tab-btn');
    runAgentButton = document.getElementById('run-agent-btn');
    deploymentGuideContainer = document.getElementById('deployment-guide');
    forecastContainer = document.getElementById('forecast-result');
    
    // Load income streams
    loadIncomeStreams();
    
    // Event listeners
    if (newIncomeStreamBtn) {
        newIncomeStreamBtn.addEventListener('click', function() {
            formContainer.classList.remove('hidden');
            detailsContainer.classList.add('hidden');
        });
    }
    
    if (cancelFormBtn) {
        cancelFormBtn.addEventListener('click', function() {
            formContainer.classList.add('hidden');
            incomeStreamForm.reset();
        });
    }
    
    if (incomeStreamForm) {
        incomeStreamForm.addEventListener('submit', handleIncomeStreamFormSubmit);
    }
    
    if (automationRange && automationValue) {
        automationRange.addEventListener('input', function() {
            automationValue.textContent = this.value;
        });
    }
    
    // Tab switching
    if (tabButtons) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                
                // Update active tab button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Update active tab content
                const tabContents = document.querySelectorAll('.tab-content');
                tabContents.forEach(content => content.classList.remove('active'));
                document.getElementById(`${tabName}-tab`).classList.add('active');
            });
        });
    }
    
    // Run agent button
    if (runAgentButton) {
        runAgentButton.addEventListener('click', handleRunAgent);
    }
    
    // Generate forecast button
    const generateForecastBtn = document.getElementById('generate-forecast-btn');
    if (generateForecastBtn) {
        generateForecastBtn.addEventListener('click', handleGenerateForecast);
    }
    
    // Generate deployment guide button
    const generateGuideBtn = document.getElementById('generate-guide-btn');
    if (generateGuideBtn) {
        generateGuideBtn.addEventListener('click', handleGenerateDeploymentGuide);
    }
}

/**
 * Add CSS styles for the Archon UI
 */
function addArchonStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .archon-container {
            font-family: var(--font-family, 'Inter', sans-serif);
            color: var(--text-color, #333);
            background-color: var(--bg-color, #f9f9f9);
            border-radius: var(--radius-lg, 8px);
            box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.1));
            margin: 2rem 0;
            overflow: hidden;
        }
        
        .archon-header {
            background: linear-gradient(135deg, var(--primary, #4a6cf7) 0%, var(--primary-dark, #2546b5) 100%);
            color: white;
            padding: 1.5rem 2rem;
            text-align: center;
        }
        
        .archon-header h2 {
            margin: 0 0 0.5rem;
            font-size: 1.8rem;
        }
        
        .archon-header p {
            margin: 0;
            opacity: 0.8;
        }
        
        .archon-content {
            display: flex;
            min-height: 500px;
        }
        
        .archon-sidebar {
            width: 300px;
            background-color: var(--bg-color-light, #f1f1f1);
            border-right: 1px solid var(--border-color, #ddd);
            padding: 1.5rem;
        }
        
        .archon-main {
            flex: 1;
            padding: 1.5rem;
        }
        
        .archon-section {
            margin-bottom: 2rem;
        }
        
        .archon-section h3 {
            margin-top: 0;
            font-size: 1.3rem;
            border-bottom: 1px solid var(--border-color, #ddd);
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .income-streams-list {
            margin-bottom: 1rem;
        }
        
        .income-stream-item {
            padding: 0.75rem;
            background-color: white;
            border-radius: var(--radius-md, 6px);
            border: 1px solid var(--border-color, #ddd);
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .income-stream-item:hover {
            border-color: var(--primary, #4a6cf7);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .income-stream-item.active {
            border-color: var(--primary, #4a6cf7);
            box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
        }
        
        .income-stream-item h4 {
            margin: 0 0 0.25rem;
            font-size: 1rem;
        }
        
        .income-stream-item p {
            margin: 0;
            font-size: 0.85rem;
            color: var(--text-muted, #666);
        }
        
        .income-stream-badge {
            display: inline-block;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            background-color: var(--primary-light, #eef1fe);
            color: var(--primary, #4a6cf7);
            margin-top: 0.5rem;
        }
        
        .form-input {
            width: 100%;
            padding: 0.75rem;
            font-size: 0.95rem;
            border: 1px solid var(--border-color, #ddd);
            border-radius: var(--radius-sm, 4px);
            background-color: white;
            transition: border-color 0.2s ease;
        }
        
        .form-input:focus {
            border-color: var(--primary, #4a6cf7);
            outline: none;
            box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
        }
        
        .input-group {
            margin-bottom: 1.25rem;
        }
        
        .input-group.inline {
            display: inline-block;
            margin-right: 1rem;
            width: calc(50% - 0.5rem);
        }
        
        .input-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            font-size: 0.95rem;
        }
        
        .form-range {
            width: 100%;
            height: 6px;
            -webkit-appearance: none;
            background: var(--border-color, #ddd);
            border-radius: 3px;
            outline: none;
        }
        
        .form-range::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--primary, #4a6cf7);
            cursor: pointer;
        }
        
        .range-value {
            text-align: center;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }
        
        .checkbox-label {
            display: flex;
            align-items: center;
            cursor: pointer;
        }
        
        .checkbox-label input {
            margin-right: 0.5rem;
        }
        
        .form-actions {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .hidden {
            display: none !important;
        }
        
        .archon-tabs {
            display: flex;
            border-bottom: 1px solid var(--border-color, #ddd);
            margin-bottom: 1.5rem;
        }
        
        .tab-btn {
            background: none;
            border: none;
            padding: 0.75rem 1.25rem;
            font-size: 0.95rem;
            cursor: pointer;
            position: relative;
            color: var(--text-color, #333);
            transition: color 0.2s ease;
        }
        
        .tab-btn:hover {
            color: var(--primary, #4a6cf7);
        }
        
        .tab-btn.active {
            color: var(--primary, #4a6cf7);
            font-weight: 500;
        }
        
        .tab-btn.active::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            width: 100%;
            height: 2px;
            background-color: var(--primary, #4a6cf7);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .income-stream-header {
            margin-bottom: 1.5rem;
        }
        
        .income-stream-header h3 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
        }
        
        .income-stream-header .badge {
            font-size: 0.75rem;
            padding: 0.3rem 0.6rem;
            border-radius: 12px;
            margin-left: 0.75rem;
            background-color: var(--primary-light, #eef1fe);
            color: var(--primary, #4a6cf7);
        }
        
        .income-stream-overview {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
        }
        
        .overview-card {
            background-color: white;
            border-radius: var(--radius-md, 6px);
            border: 1px solid var(--border-color, #ddd);
            padding: 1.25rem;
        }
        
        .overview-card h4 {
            margin-top: 0;
            margin-bottom: 1rem;
            font-size: 1.1rem;
            color: var(--text-muted, #666);
        }
        
        .overview-item {
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
        }
        
        .overview-item .label {
            color: var(--text-muted, #666);
            font-size: 0.95rem;
        }
        
        .overview-item .value {
            font-weight: 500;
        }
        
        .implement-actions, .deployment-actions, .forecast-controls {
            background-color: white;
            border-radius: var(--radius-md, 6px);
            border: 1px solid var(--border-color, #ddd);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .agent-result, .deployment-guide, .forecast-result {
            background-color: white;
            border-radius: var(--radius-md, 6px);
            border: 1px solid var(--border-color, #ddd);
            padding: 1.5rem;
        }
        
        .result-section {
            margin-bottom: 1.5rem;
        }
        
        .result-section h4 {
            margin-top: 0;
            margin-bottom: 0.75rem;
            font-size: 1.1rem;
        }
        
        .code-block {
            background-color: var(--bg-code, #f5f7ff);
            border-radius: var(--radius-sm, 4px);
            padding: 1rem;
            font-family: monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            font-size: 0.9rem;
        }
        
        .step-list {
            counter-reset: step-counter;
            list-style-type: none;
            padding-left: 0;
        }
        
        .step-list li {
            position: relative;
            padding-left: 2.5rem;
            margin-bottom: 1rem;
            counter-increment: step-counter;
        }
        
        .step-list li::before {
            content: counter(step-counter);
            position: absolute;
            left: 0;
            top: 0;
            width: 1.75rem;
            height: 1.75rem;
            background-color: var(--primary-light, #eef1fe);
            color: var(--primary, #4a6cf7);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .forecast-chart {
            width: 100%;
            height: 250px;
            margin: 1.5rem 0;
        }
        
        .forecast-summary {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .forecast-metric {
            background-color: var(--bg-color-light, #f1f1f1);
            border-radius: var(--radius-md, 6px);
            padding: 1rem;
            text-align: center;
        }
        
        .forecast-metric .value {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary, #4a6cf7);
            margin-bottom: 0.5rem;
        }
        
        .forecast-metric .label {
            font-size: 0.85rem;
            color: var(--text-muted, #666);
        }
    `;
    
    document.head.appendChild(styleElement);
}

/**
 * Load income streams from the API
 */
async function loadIncomeStreams() {
    try {
        const streams = await archonService.getIncomeStreams();
        
        if (!incomeStreamsList) return;
        
        if (streams && streams.length > 0) {
            // Clear the list
            incomeStreamsList.innerHTML = '';
            
            // Add each income stream to the list
            streams.forEach(stream => {
                const streamElement = document.createElement('div');
                streamElement.className = 'income-stream-item';
                streamElement.dataset.id = stream.id;
                
                streamElement.innerHTML = `
                    <h4>${stream.name}</h4>
                    <p>${stream.description.substring(0, 80)}${stream.description.length > 80 ? '...' : ''}</p>
                    <span class="income-stream-badge">${stream.type}</span>
                `;
                
                streamElement.addEventListener('click', () => showIncomeStreamDetails(stream));
                
                incomeStreamsList.appendChild(streamElement);
            });
            
            // Show the first income stream details by default
            if (streams.length > 0) {
                showIncomeStreamDetails(streams[0]);
            }
        } else {
            incomeStreamsList.innerHTML = '<p>No income streams created yet.</p>';
        }
    } catch (error) {
        console.error('Error loading income streams:', error);
        if (incomeStreamsList) {
            incomeStreamsList.innerHTML = '<p>Error loading income streams. Please try again.</p>';
        }
    }
}

/**
 * Show income stream details
 * @param {Object} stream Income stream data
 */
function showIncomeStreamDetails(stream) {
    const detailsContainer = document.getElementById('income-stream-details');
    const formContainer = document.getElementById('income-stream-form-container');
    const headerContainer = document.getElementById('income-stream-header');
    const overviewContainer = document.querySelector('.income-stream-overview');
    
    // Set the active income stream
    document.querySelectorAll('.income-stream-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.id) === stream.id) {
            item.classList.add('active');
        }
    });
    
    // Update header
    headerContainer.innerHTML = `
        <h3>${stream.name} <span class="badge">${stream.type}</span></h3>
        <p>${stream.description}</p>
    `;
    
    // Update overview
    overviewContainer.innerHTML = `
        <div class="overview-card">
            <h4>Details</h4>
            <div class="overview-item">
                <span class="label">Type</span>
                <span class="value">${stream.type}</span>
            </div>
            <div class="overview-item">
                <span class="label">Automation Level</span>
                <span class="value">${stream.automation_level}/10</span>
            </div>
            <div class="overview-item">
                <span class="label">Automated Percentage</span>
                <span class="value">${stream.automated_percentage}%</span>
            </div>
            <div class="overview-item">
                <span class="label">Status</span>
                <span class="value">${stream.status}</span>
            </div>
        </div>
        
        <div class="overview-card">
            <h4>Revenue Potential</h4>
            <div class="overview-item">
                <span class="label">Monthly Revenue</span>
                <span class="value">$${stream.monthly_revenue.toFixed(2)}</span>
            </div>
            <div class="overview-item">
                <span class="label">Annual Revenue</span>
                <span class="value">$${(stream.monthly_revenue * 12).toFixed(2)}</span>
            </div>
            <div class="overview-item">
                <span class="label">Required Services</span>
                <span class="value">${stream.required_services.join(', ') || 'None'}</span>
            </div>
        </div>
    `;
    
    // Update run agent button with the stream ID
    if (runAgentButton) {
        runAgentButton.dataset.id = stream.id;
    }
    
    // Show the details container and hide the form
    detailsContainer.classList.remove('hidden');
    formContainer.classList.add('hidden');
}

/**
 * Handle income stream form submission
 * @param {Event} event Form submission event
 */
async function handleIncomeStreamFormSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const name = document.getElementById('stream-name').value;
    const type = document.getElementById('stream-type').value;
    const description = document.getElementById('stream-description').value;
    const automationLevel = parseInt(document.getElementById('automation-level').value);
    
    // Get selected required services
    const requiredServices = [];
    document.querySelectorAll('input[name="required-services"]:checked').forEach(checkbox => {
        requiredServices.push(checkbox.value);
    });
    
    // Create income stream data
    const streamData = {
        name,
        stream_type: type,
        description,
        automation_level: automationLevel,
        required_services: requiredServices
    };
    
    try {
        // Show loading state
        const submitButton = incomeStreamForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.textContent = 'Creating...';
        submitButton.disabled = true;
        
        // Create the income stream
        const stream = await archonService.createIncomeStream(streamData);
        
        // Reset form
        incomeStreamForm.reset();
        document.getElementById('income-stream-form-container').classList.add('hidden');
        
        // Reload income streams
        loadIncomeStreams();
        
        // Show the new income stream details
        setTimeout(() => {
            showIncomeStreamDetails(stream);
        }, 100);
        
        // Reset button
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    } catch (error) {
        console.error('Error creating income stream:', error);
        alert('Failed to create income stream. Please try again.');
        
        // Reset button
        const submitButton = incomeStreamForm.querySelector('button[type="submit"]');
        submitButton.textContent = 'Create Income Stream';
        submitButton.disabled = false;
    }
}

/**
 * Handle running the Archon agent
 */
async function handleRunAgent() {
    const streamId = parseInt(runAgentButton.dataset.id);
    if (!streamId) return;

    const agentParams = document.getElementById('agent-params').value;
    
    // Show loading state
    const originalText = runAgentButton.textContent;
    runAgentButton.textContent = 'Running Agent...';
    runAgentButton.disabled = true;
    
    const agentResult = document.getElementById('agent-result');
    agentResult.classList.remove('hidden');
    agentResult.innerHTML = '<p>Running Archon Agent, please wait...</p>';
    
    try {
        const result = await archonService.runArchonAgent(streamId, agentParams);
        
        // Display the result
        agentResult.innerHTML = `
            <div class="result-section">
                <h4>Archon Agent Configuration</h4>
                <p>The Archon agent has been configured to implement the income stream with the following parameters:</p>
                <div class="code-block">${JSON.stringify(result.archon_run_agent_json, null, 2)}</div>
            </div>
            
            <div class="result-section">
                <h4>Next Steps</h4>
                <ul class="step-list">
                    <li>Archon agent is analyzing and implementing the income stream</li>
                    <li>Once implementation is complete, you can generate a detailed deployment guide</li>
                    <li>You can then forecast the revenue and monitor the performance of your income stream</li>
                </ul>
            </div>
        `;
    } catch (error) {
        console.error('Error running Archon agent:', error);
        agentResult.innerHTML = `<p>Failed to run Archon agent: ${error.message}</p>`;
    } finally {
        // Reset button
        runAgentButton.textContent = originalText;
        runAgentButton.disabled = false;
    }
}

/**
 * Handle generating a revenue forecast
 */
async function handleGenerateForecast() {
    const streamId = document.querySelector('.income-stream-item.active')?.dataset.id;
    if (!streamId) return;
    
    // Get forecast parameters
    const months = parseInt(document.getElementById('forecast-months').value);
    const growthRate = parseFloat(document.getElementById('growth-rate').value);
    
    // Show loading state
    const generateButton = document.getElementById('generate-forecast-btn');
    const originalText = generateButton.textContent;
    generateButton.textContent = 'Generating...';
    generateButton.disabled = true;
    
    forecastContainer.innerHTML = '<p>Generating forecast, please wait...</p>';
    
    try {
        // Generate forecast
        const forecast = await archonService.generateForecast({
            months,
            growth_rate: growthRate
        });
        
        // Display the forecast
        forecastContainer.innerHTML = `
            <div class="forecast-summary">
                <div class="forecast-metric">
                    <div class="value">$${forecast.average_monthly_revenue.toFixed(2)}</div>
                    <div class="label">Avg Monthly Revenue</div>
                </div>
                <div class="forecast-metric">
                    <div class="value">$${forecast.total_projected_revenue.toFixed(2)}</div>
                    <div class="label">Total ${months} Month Revenue</div>
                </div>
                <div class="forecast-metric">
                    <div class="value">${forecast.growth_rate_monthly}%</div>
                    <div class="label">Monthly Growth Rate</div>
                </div>
            </div>
            
            <div class="forecast-table">
                <h4>Monthly Projections</h4>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Revenue</th>
                            <th>Growth</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${forecast.monthly_projections.map(month => `
                            <tr>
                                <td>Month ${month.month}</td>
                                <td>$${month.revenue.toFixed(2)}</td>
                                <td>${month.growth}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        console.error('Error generating forecast:', error);
        forecastContainer.innerHTML = `<p>Failed to generate forecast: ${error.message}</p>`;
    } finally {
        // Reset button
        generateButton.textContent = originalText;
        generateButton.disabled = false;
    }
}

/**
 * Handle generating a deployment guide
 */
async function handleGenerateDeploymentGuide() {
    const streamId = document.querySelector('.income-stream-item.active')?.dataset.id;
    if (!streamId) return;
    
    // Show loading state
    const generateButton = document.getElementById('generate-guide-btn');
    const originalText = generateButton.textContent;
    generateButton.textContent = 'Generating...';
    generateButton.disabled = true;
    
    deploymentGuideContainer.innerHTML = '<p>Generating deployment guide, please wait...</p>';
    
    try {
        // Generate deployment guide
        const guide = await archonService.generateDeploymentGuide(parseInt(streamId));
        
        // Display the deployment guide
        deploymentGuideContainer.innerHTML = `
            <div class="guide-section">
                <h4>Deployment Steps</h4>
                <ol class="step-list">
                    ${guide.deployment.steps.map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
            
            <div class="guide-section">
                <h4>Technical Requirements</h4>
                <ul>
                    ${guide.deployment.technical_requirements.map(req => `<li>${req}</li>`).join('')}
                </ul>
                <p>Estimated setup time: ${guide.deployment.estimated_setup_time}</p>
            </div>
            
            <div class="guide-section">
                <h4>Maintenance</h4>
                <ul>
                    ${guide.maintenance.recurring_tasks.map(task => `<li>${task}</li>`).join('')}
                </ul>
                <p>Estimated weekly effort: ${guide.maintenance.estimated_weekly_effort}</p>
            </div>
            
            <div class="guide-section">
                <h4>Profitability</h4>
                <p>Estimated monthly revenue: $${guide.profitability.estimated_monthly_revenue.toFixed(2)}</p>
                <p>Estimated annual revenue: $${guide.profitability.estimated_annual_revenue.toFixed(2)}</p>
                <p>Estimated profit margin: ${guide.profitability.estimated_profit_margin}</p>
                
                <h5>Expected Expenses</h5>
                <ul>
                    ${guide.profitability.expected_expenses.map(expense => `
                        <li>${expense.name}: ${expense.amount}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    } catch (error) {
        console.error('Error generating deployment guide:', error);
        deploymentGuideContainer.innerHTML = `<p>Failed to generate deployment guide: ${error.message}</p>`;
    } finally {
        // Reset button
        generateButton.textContent = originalText;
        generateButton.disabled = false;
    }
}
