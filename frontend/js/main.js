// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Navigation menu toggle for mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const authButtons = document.querySelector('.auth-buttons');

    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            authButtons.classList.toggle('active');
            
            // Style changes for mobile menu
            if (navMenu.classList.contains('active')) {
                navMenu.style.display = 'flex';
                navMenu.style.flexDirection = 'column';
                navMenu.style.position = 'absolute';
                navMenu.style.top = '80px';
                navMenu.style.left = '0';
                navMenu.style.width = '100%';
                navMenu.style.backgroundColor = 'var(--dark)';
                navMenu.style.padding = '1rem';
                navMenu.style.boxShadow = 'var(--shadow-md)';
                navMenu.style.zIndex = '100';
                
                authButtons.style.display = 'flex';
                authButtons.style.flexDirection = 'column';
                authButtons.style.position = 'absolute';
                authButtons.style.top = navMenu.scrollHeight + 80 + 'px';
                authButtons.style.left = '0';
                authButtons.style.width = '100%';
                authButtons.style.backgroundColor = 'var(--dark)';
                authButtons.style.padding = '1rem';
                authButtons.style.boxShadow = 'var(--shadow-md)';
                authButtons.style.gap = '0.5rem';
                authButtons.style.zIndex = '100';
            } else {
                navMenu.style = '';
                authButtons.style = '';
            }
        });
    }

    // Pricing toggle between monthly and yearly
    const pricingSwitch = document.querySelector('.pricing-toggle .switch');
    const pricingSlider = document.querySelector('.pricing-toggle .slider');
    const priceAmounts = document.querySelectorAll('.amount');
    const originalPrices = Array.from(priceAmounts).map(el => parseInt(el.textContent));
    let yearlyPricing = false;

    if (pricingSwitch) {
        // Create hidden checkbox for toggle functionality
        const toggleCheckbox = document.createElement('input');
        toggleCheckbox.type = 'checkbox';
        toggleCheckbox.id = 'pricing-toggle';
        pricingSwitch.prepend(toggleCheckbox);

        pricingSwitch.addEventListener('click', function() {
            yearlyPricing = !yearlyPricing;
            toggleCheckbox.checked = yearlyPricing;
            
            if (yearlyPricing) {
                // Yearly pricing (20% discount)
                priceAmounts.forEach((el, index) => {
                    const yearlyPrice = Math.round(originalPrices[index] * 0.8);
                    el.textContent = yearlyPrice;
                });

                // Change period text
                document.querySelectorAll('.period').forEach(el => {
                    el.textContent = '/yr';
                });
                
                // Move slider to right
                pricingSlider.style.transform = 'translateX(26px)';
                pricingSlider.style.backgroundColor = 'var(--primary)';
            } else {
                // Monthly pricing
                priceAmounts.forEach((el, index) => {
                    el.textContent = originalPrices[index];
                });

                // Change period text
                document.querySelectorAll('.period').forEach(el => {
                    el.textContent = '/mo';
                });
                
                // Move slider to left
                pricingSlider.style.transform = '';
                pricingSlider.style.backgroundColor = '';
            }
        });
    }

    // Market Analysis Form
    const analyzeBtn = document.getElementById('analyze-btn');
    const marketAnalysisForm = document.querySelector('.market-analysis-form');
    const analysisResults = document.querySelector('.analysis-results');
    const marketSegmentSelect = document.getElementById('market-segment');
    const businessPreferenceSelect = document.getElementById('business-preference');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            // Validate form
            const marketSegment = marketSegmentSelect.value;
            const businessPreference = businessPreferenceSelect.value;
            
            if (!marketSegment) {
                shake(marketSegmentSelect);
                return;
            }
            
            if (!businessPreference) {
                shake(businessPreferenceSelect);
                return;
            }

            // Show loading state
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            analyzeBtn.disabled = true;

            // Simulate API call with timeout
            setTimeout(() => {
                // Hide the form and show results
                marketAnalysisForm.style.display = 'none';
                analysisResults.classList.remove('hidden');

                // Generate dynamic content based on selections
                const resultsHeader = analysisResults.querySelector('.results-header h3');
                const resultsBadge = analysisResults.querySelector('.results-header .badge');
                const businessModelsContainer = analysisResults.querySelector('.business-models');
                
                // Update header based on selection
                resultsHeader.textContent = `Market Analysis Results: ${marketSegmentSelect.options[marketSegmentSelect.selectedIndex].text}`;
                
                // Create some dynamic business models based on selection
                const models = generateBusinessModels(marketSegment, businessPreference);
                resultsBadge.textContent = `${models.length} Business Models Found`;
                
                // Clear existing models
                businessModelsContainer.innerHTML = '';
                
                // Add new models
                models.forEach(model => {
                    businessModelsContainer.appendChild(createBusinessModelCard(model));
                });
                
                // Reset button
                analyzeBtn.innerHTML = 'Analyze Market <i class="fas fa-arrow-right"></i>';
                analyzeBtn.disabled = false;
                
                // Add back button
                const backButton = document.createElement('button');
                backButton.className = 'btn btn-secondary';
                backButton.style.marginTop = '1rem';
                backButton.innerHTML = '<i class="fas fa-arrow-left"></i> Back to Analysis';
                backButton.addEventListener('click', function() {
                    analysisResults.classList.add('hidden');
                    marketAnalysisForm.style.display = 'block';
                    this.remove();
                });
                
                analysisResults.appendChild(backButton);
            }, 2000);
        });
    }
    
    // Generate business models based on selections
    function generateBusinessModels(marketSegment, preference) {
        const models = [];
        let count = Math.floor(Math.random() * 2) + 2; // 2-3 models
        
        const modelTypes = {
            'digital-products': ['Membership Site', 'Digital Course Platform', 'Template Marketplace', 'eBook Publishing'],
            'e-commerce': ['Dropshipping Store', 'Print on Demand', 'Subscription Box', 'Niche Marketplace'],
            'saas': ['Productivity Tool', 'Marketing Automation', 'Analytics Platform', 'Customer Support System'],
            'online-education': ['Cohort-Based Course', 'On-Demand Training', 'Expert Community', 'Certification Program'],
            'affiliate-marketing': ['Review Website', 'Comparison Platform', 'Deal Aggregator', 'Niche Content Hub']
        };
        
        const preferenceData = {
            'highest-revenue': { revenueFactor: 1.5, implementationFactor: 0.8 },
            'lowest-effort': { revenueFactor: 0.8, implementationFactor: 1.5 },
            'fastest-implementation': { revenueFactor: 0.7, implementationFactor: 1.7 },
            'lowest-startup-cost': { revenueFactor: 0.6, implementationFactor: 1.2 }
        };
        
        // Get models for the selected market segment
        const availableModels = modelTypes[marketSegment] || modelTypes['digital-products'];
        const factors = preferenceData[preference] || preferenceData['highest-revenue'];
        
        // Create random selection of models
        for (let i = 0; i < count; i++) {
            if (i < availableModels.length) {
                const baseRevenue = Math.floor(Math.random() * 3000) + 1000;
                const adjustedRevenue = Math.floor(baseRevenue * factors.revenueFactor);
                
                const implementation = Math.floor(Math.random() * 3) + 6;
                const automation = Math.floor(Math.random() * 3) + 7;
                
                models.push({
                    name: availableModels[i],
                    revenue: adjustedRevenue,
                    implementation: implementation, 
                    automation: automation,
                    description: getDescription(availableModels[i])
                });
            }
        }
        
        // Sort by revenue if highest-revenue was selected
        if (preference === 'highest-revenue') {
            models.sort((a, b) => b.revenue - a.revenue);
        }
        
        return models;
    }
    
    // Get description for business model
    function getDescription(modelType) {
        const descriptions = {
            'Membership Site': 'Recurring membership site with premium digital content and tiered access levels.',
            'Digital Course Platform': 'Educational platform with automated course delivery and student management.',
            'Template Marketplace': 'Marketplace selling digital templates with instant delivery and no inventory.',
            'eBook Publishing': 'Digital publishing platform with automated delivery and marketing.',
            'Dropshipping Store': 'E-commerce store with products shipped directly from suppliers to customers.',
            'Print on Demand': 'Custom product store with items printed and shipped as orders come in.',
            'Subscription Box': 'Recurring delivery service with curated products sent monthly to subscribers.',
            'Niche Marketplace': 'Specialized marketplace connecting buyers and sellers in a specific niche.',
            'Productivity Tool': 'SaaS solution that helps businesses improve workflow efficiency.',
            'Marketing Automation': 'Platform that automates repetitive marketing tasks and campaigns.',
            'Analytics Platform': 'Data analysis tool that provides actionable business insights.',
            'Customer Support System': 'Automated customer service solution with ticketing and knowledge base.',
            'Cohort-Based Course': 'Time-limited learning program where students progress together as a group.',
            'On-Demand Training': 'Self-paced educational content available 24/7 to subscribers.',
            'Expert Community': 'Paid membership community with access to industry experts and peers.',
            'Certification Program': 'Educational system that provides verified credentials upon completion.',
            'Review Website': 'Content site monetized through affiliate commissions from reviewed products.',
            'Comparison Platform': 'Website that compares similar products and earns commissions on referrals.',
            'Deal Aggregator': 'Platform that collects and displays the best deals with affiliate links.',
            'Niche Content Hub': 'Specialized content website with in-depth articles and affiliate promotions.'
        };
        
        return descriptions[modelType] || 'A business model with automation and passive income potential.';
    }
    
    // Create business model card
    function createBusinessModelCard(model) {
        const card = document.createElement('div');
        card.className = 'business-model-card';
        
        const modelHeader = document.createElement('div');
        modelHeader.className = 'model-header';
        
        const modelTitle = document.createElement('h4');
        modelTitle.textContent = model.name;
        
        const revenueBadge = document.createElement('span');
        revenueBadge.className = 'revenue-badge';
        revenueBadge.textContent = `$${model.revenue}/mo`;
        
        modelHeader.appendChild(modelTitle);
        modelHeader.appendChild(revenueBadge);
        
        const description = document.createElement('p');
        description.textContent = model.description;
        
        const modelMetrics = document.createElement('div');
        modelMetrics.className = 'model-metrics';
        
        // Implementation metric
        const implMetric = document.createElement('div');
        implMetric.className = 'metric';
        
        const implLabel = document.createElement('span');
        implLabel.className = 'metric-label';
        implLabel.textContent = 'Implementation';
        
        const implBar = document.createElement('div');
        implBar.className = 'metric-bar';
        
        const implFill = document.createElement('div');
        implFill.className = 'metric-fill';
        implFill.style.width = `${model.implementation * 10}%`;
        
        const implValue = document.createElement('span');
        implValue.className = 'metric-value';
        implValue.textContent = `${model.implementation}/10`;
        
        implBar.appendChild(implFill);
        implMetric.appendChild(implLabel);
        implMetric.appendChild(implBar);
        implMetric.appendChild(implValue);
        
        // Automation metric
        const autoMetric = document.createElement('div');
        autoMetric.className = 'metric';
        
        const autoLabel = document.createElement('span');
        autoLabel.className = 'metric-label';
        autoLabel.textContent = 'Automation';
        
        const autoBar = document.createElement('div');
        autoBar.className = 'metric-bar';
        
        const autoFill = document.createElement('div');
        autoFill.className = 'metric-fill';
        autoFill.style.width = `${model.automation * 10}%`;
        
        const autoValue = document.createElement('span');
        autoValue.className = 'metric-value';
        autoValue.textContent = `${model.automation}/10`;
        
        autoBar.appendChild(autoFill);
        autoMetric.appendChild(autoLabel);
        autoMetric.appendChild(autoBar);
        autoMetric.appendChild(autoValue);
        
        modelMetrics.appendChild(implMetric);
        modelMetrics.appendChild(autoMetric);
        
        const selectBtn = document.createElement('button');
        selectBtn.className = 'btn btn-primary btn-select';
        selectBtn.textContent = 'Select & Implement';
        
        card.appendChild(modelHeader);
        card.appendChild(description);
        card.appendChild(modelMetrics);
        card.appendChild(selectBtn);
        
        return card;
    }

    // Authentication buttons and modals
    const loginBtn = document.querySelector('.btn-login');
    const signUpBtn = document.querySelector('.btn-primary');
    const loginModal = document.getElementById('login-modal');
    const appModal = document.getElementById('app-modal');

    // Login button functionality
    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function() {
            openModal(loginModal);
        });
    }
    
    // Sign up button functionality
    if (signUpBtn && appModal) {
        signUpBtn.addEventListener('click', function() {
            // Set content for sign up
            const modalBody = appModal.querySelector('.modal-body');
            modalBody.innerHTML = `
                <form class="auth-form">
                    <div class="input-group">
                        <label for="signup-name">Full Name</label>
                        <input type="text" id="signup-name" class="form-input" placeholder="Your name">
                    </div>
                    <div class="input-group">
                        <label for="signup-email">Email</label>
                        <input type="email" id="signup-email" class="form-input" placeholder="your@email.com">
                    </div>
                    <div class="input-group">
                        <label for="signup-password">Password</label>
                        <input type="password" id="signup-password" class="form-input" placeholder="••••••••••">
                    </div>
                    <div class="input-group">
                        <label for="signup-confirm">Confirm Password</label>
                        <input type="password" id="signup-confirm" class="form-input" placeholder="••••••••••">
                    </div>
                    <button type="submit" class="btn btn-primary btn-full">Create Account</button>
                    <div class="auth-divider">
                        <span>or continue with</span>
                    </div>
                    <div class="social-login">
                        <button type="button" class="btn btn-social btn-google">
                            <i class="fab fa-google"></i> Google
                        </button>
                        <button type="button" class="btn btn-social btn-github">
                            <i class="fab fa-github"></i> GitHub
                        </button>
                    </div>
                </form>
            `;
            
            // Set header title
            appModal.querySelector('.modal-header h3').textContent = 'Sign Up for Decision Points AI';
            
            // Add event listener to the form
            const form = modalBody.querySelector('form');
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const name = document.getElementById('signup-name').value;
                const email = document.getElementById('signup-email').value;
                const password = document.getElementById('signup-password').value;
                const confirm = document.getElementById('signup-confirm').value;
                
                // Validate
                if (!name || !email || !password || !confirm) {
                    alert('Please fill out all fields');
                    return;
                }
                
                if (password !== confirm) {
                    alert('Passwords do not match');
                    return;
                }
                
                // Success message
                modalBody.innerHTML = `
                    <div class="success-message">
                        <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
                        <h3>Account Created!</h3>
                        <p>Welcome to Decision Points AI, ${name}! You can now log in to access your dashboard.</p>
                        <button class="btn btn-primary btn-full" id="goto-login">Go to Login</button>
                    </div>
                `;
                
                // Add event listener to the login button
                document.getElementById('goto-login').addEventListener('click', function() {
                    closeModal(appModal);
                    setTimeout(() => {
                        openModal(loginModal);
                    }, 300);
                });
            });
            
            openModal(appModal);
        });
    }

    // Add login form submission handler
    const loginForm = loginModal.querySelector('.auth-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                alert('Please enter both email and password');
                return;
            }
            
            // Simulate login success
            closeModal(loginModal);
            
            // Show success notification
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fas fa-check-circle"></i> Login successful! Redirecting to dashboard...
                </div>
            `;
            
            // Style the notification
            notification.style.position = 'fixed';
            notification.style.bottom = '20px';
            notification.style.right = '20px';
            notification.style.backgroundColor = 'var(--success)';
            notification.style.color = 'white';
            notification.style.padding = '12px 20px';
            notification.style.borderRadius = 'var(--radius-md)';
            notification.style.boxShadow = 'var(--shadow-md)';
            notification.style.zIndex = '2000';
            notification.style.display = 'flex';
            notification.style.alignItems = 'center';
            notification.style.gap = '10px';
            notification.style.animation = 'slideIn 0.3s ease';
            
            // Add animation
            const styleSheet = document.createElement("style");
            styleSheet.textContent = `
                @keyframes slideIn {
                    0% { transform: translateX(100%); opacity: 0; }
                    100% { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    0% { transform: translateX(0); opacity: 1; }
                    100% { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(styleSheet);
            
            document.body.appendChild(notification);
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease';
                notification.addEventListener('animationend', function() {
                    notification.remove();
                });
            }, 3000);
        });
    }

    // Close modals when clicking the close button
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });

    // Close modals when clicking outside the content
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target);
        }
    });
    
    // Close modals when ESC key is pressed
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (modal.style.display === 'flex') {
                    closeModal(modal);
                }
            });
        }
    });

    // Testimonial slider controls
    const testimonialDots = document.querySelectorAll('.testimonial-dots .dot');
    const prevButton = document.querySelector('.testimonial-control.prev');
    const nextButton = document.querySelector('.testimonial-control.next');
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    let currentTestimonial = 0;

    if (testimonialDots.length > 0 && testimonialCards.length > 0) {
        // Hide all testimonials except the first one
        testimonialCards.forEach((card, index) => {
            if (index !== 0) {
                card.style.display = 'none';
            }
        });
        
        // Initialize dots click events
        testimonialDots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentTestimonial = index;
                updateTestimonialSlider();
            });
        });

        // Previous/Next buttons
        if (prevButton) {
            prevButton.addEventListener('click', () => {
                currentTestimonial = (currentTestimonial - 1 + testimonialDots.length) % testimonialDots.length;
                updateTestimonialSlider();
            });
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => {
                currentTestimonial = (currentTestimonial + 1) % testimonialDots.length;
                updateTestimonialSlider();
            });
        }

        // Auto-transition testimonials
        const autoSlideInterval = setInterval(() => {
            currentTestimonial = (currentTestimonial + 1) % testimonialDots.length;
            updateTestimonialSlider();
        }, 5000);

        // Pause auto-transition when hovering over testimonials
        const testimonialSlider = document.querySelector('.testimonial-slider');
        if (testimonialSlider) {
            testimonialSlider.addEventListener('mouseenter', () => {
                clearInterval(autoSlideInterval);
            });
            
            testimonialSlider.addEventListener('mouseleave', () => {
                clearInterval(autoSlideInterval); // Clear existing interval
                autoSlideInterval = setInterval(() => {
                    currentTestimonial = (currentTestimonial + 1) % testimonialDots.length;
                    updateTestimonialSlider();
                }, 5000);
            });
        }

        // Update slider based on current index
        function updateTestimonialSlider() {
            // Update active dot
            testimonialDots.forEach((dot, index) => {
                if (index === currentTestimonial) {
                    dot.classList.add('active');
                } else {
                    dot.classList.remove('active');
                }
            });

            // Update visible testimonial with fade effect
            testimonialCards.forEach((testimonial, index) => {
                if (index === currentTestimonial) {
                    testimonial.style.opacity = '0';
                    testimonial.style.display = 'block';
                    setTimeout(() => {
                        testimonial.style.transition = 'opacity 0.5s ease';
                        testimonial.style.opacity = '1';
                    }, 50);
                } else {
                    testimonial.style.display = 'none';
                    testimonial.style.opacity = '0';
                }
            });
        }

        // Run on initial load
        updateTestimonialSlider();
    }

    // Business model selection
    const selectButtons = document.querySelectorAll('.btn-select');
    selectButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Show confirmation modal or navigate to implementation
            const modelName = this.closest('.business-model-card').querySelector('h4').textContent;
            alert(`You selected: ${modelName}. Starting implementation process.`);
            // Here you'd redirect or open the implementation flow
        });
    });

    // Helper functions
    function openModal(modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    function shake(element) {
        element.classList.add('shake');
        element.style.borderColor = 'var(--danger)';
        setTimeout(() => {
            element.classList.remove('shake');
            element.style.borderColor = '';
        }, 600);
    }

    // Add animation class
    const shakeKeyframes = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }

        .shake {
            animation: shake 0.6s ease;
        }
    `;

    const styleSheet = document.createElement("style");
    styleSheet.textContent = shakeKeyframes;
    document.head.appendChild(styleSheet);

    // Smooth scroll for navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Adjust for navbar height
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    authButtons.classList.remove('active');
                }
            }
        });
    });
});
