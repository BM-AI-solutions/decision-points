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
        });
    }

    // Pricing toggle between monthly and yearly
    const pricingToggle = document.getElementById('pricing-toggle');
    const priceAmounts = document.querySelectorAll('.amount');
    const originalPrices = Array.from(priceAmounts).map(el => parseInt(el.textContent));

    if (pricingToggle) {
        pricingToggle.addEventListener('change', function() {
            if (this.checked) {
                // Yearly pricing (20% discount)
                priceAmounts.forEach((el, index) => {
                    const yearlyPrice = Math.round(originalPrices[index] * 0.8);
                    el.textContent = yearlyPrice;
                });

                // Change period text
                document.querySelectorAll('.period').forEach(el => {
                    el.textContent = '/yr';
                });
            } else {
                // Monthly pricing
                priceAmounts.forEach((el, index) => {
                    el.textContent = originalPrices[index];
                });

                // Change period text
                document.querySelectorAll('.period').forEach(el => {
                    el.textContent = '/mo';
                });
            }
        });
    }

    // Market Analysis Form
    const analyzeBtn = document.getElementById('analyze-btn');
    const marketAnalysisForm = document.querySelector('.market-analysis-form');
    const analysisResults = document.querySelector('.analysis-results');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            // Validate form
            const marketSegment = document.getElementById('market-segment').value;
            if (!marketSegment) {
                shake(document.getElementById('market-segment'));
                return;
            }

            // Show loading state
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

            // Simulate API call with timeout
            setTimeout(() => {
                // Hide the form and show results
                marketAnalysisForm.style.display = 'none';
                analysisResults.style.display = 'block';

                // Reset button
                analyzeBtn.innerHTML = 'Analyze Market <i class="fas fa-arrow-right"></i>';
            }, 2000);
        });
    }

    // Login button and modal
    const loginBtn = document.querySelector('.btn-login');
    const loginModal = document.getElementById('login-modal');

    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function() {
            openModal(loginModal);
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

    // Testimonial slider controls
    const testimonialDots = document.querySelectorAll('.testimonial-dots .dot');
    const prevButton = document.querySelector('.testimonial-control.prev');
    const nextButton = document.querySelector('.testimonial-control.next');
    let currentTestimonial = 0;

    if (testimonialDots.length > 0) {
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
        setInterval(() => {
            currentTestimonial = (currentTestimonial + 1) % testimonialDots.length;
            updateTestimonialSlider();
        }, 5000);

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

            // Update visible testimonial
            const testimonials = document.querySelectorAll('.testimonial-card');
            testimonials.forEach((testimonial, index) => {
                if (index === currentTestimonial) {
                    testimonial.style.display = 'block';
                } else {
                    testimonial.style.display = 'none';
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