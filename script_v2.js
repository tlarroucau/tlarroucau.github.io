document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn.querySelector('i');
    const htmlElement = document.documentElement;

    // Check for saved user preference, if any, on load of the website
    const savedTheme = localStorage.getItem('theme');
    
    // If saved theme is light, apply it
    if (savedTheme === 'light') {
        htmlElement.setAttribute('data-theme', 'light');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    }

    themeToggleBtn.addEventListener('click', () => {
        // Add rotation animation class
        themeToggleBtn.classList.add('rotate');
        
        // Remove animation class after transition ends
        setTimeout(() => {
            themeToggleBtn.classList.remove('rotate');
        }, 500);

        if (htmlElement.getAttribute('data-theme') === 'light') {
            // Switch to Dark
            htmlElement.removeAttribute('data-theme');
            localStorage.setItem('theme', 'dark');
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        } else {
            // Switch to Light
            htmlElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    });

    // Scroll Animation (Intersection Observer)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    document.querySelectorAll('section').forEach(section => {
        observer.observe(section);
    });

    // Navigation Active State
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('#sidebar nav ul li a');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= (sectionTop - sectionHeight / 3)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').includes(current)) {
                link.classList.add('active');
            }
        });
    });

    // Modal Logic
    const modal = document.getElementById('paper-modal');
    const modalContent = document.getElementById('modal-body');
    const closeModal = document.querySelector('.close-modal');

    // Data for popups (extracted from original HTML structure)
    // We will populate this dynamically or hardcode based on the link clicks
    
    document.querySelectorAll('a[href^="#popup"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const popupId = link.getAttribute('href').substring(1);
            const sourcePopup = document.getElementById(popupId);
            
            if (sourcePopup) {
                // Clone content to modal
                const content = sourcePopup.querySelector('.popup-inner').innerHTML;
                modalContent.innerHTML = content;
                
                // Re-initialize carousels inside the modal
                initCarousels(modalContent);
                
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // Prevent background scrolling
            }
        });
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        // Stop any playing carousels
        stopAllCarousels();
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            stopAllCarousels();
        }
    });

    // Carousel Logic
    function initCarousels(container) {
        const carousels = container.querySelectorAll('.popupphoto.carousel');
        
        carousels.forEach(carousel => {
            // Transform old structure to new if needed, or just apply logic
            // The old structure: div.popupphoto.carousel > img, img...
            
            const images = carousel.querySelectorAll('img');
            if (images.length === 0) return;

            // Wrap images in a container if not already
            let wrapper = carousel.querySelector('.carousel-container');
            if (!wrapper) {
                wrapper = document.createElement('div');
                wrapper.className = 'carousel-container';
                
                // Move images into wrapper
                images.forEach(img => {
                    img.classList.add('carousel-slide');
                    wrapper.appendChild(img);
                });
                
                // Add buttons
                const prevBtn = document.createElement('button');
                prevBtn.className = 'carousel-btn prev';
                prevBtn.innerHTML = '&#10094;';
                
                const nextBtn = document.createElement('button');
                nextBtn.className = 'carousel-btn next';
                nextBtn.innerHTML = '&#10095;';
                
                wrapper.appendChild(prevBtn);
                wrapper.appendChild(nextBtn);
                
                carousel.innerHTML = ''; // Clear old
                carousel.appendChild(wrapper);
                
                // Logic
                let currentIndex = 0;
                let interval;
                const slides = wrapper.querySelectorAll('.carousel-slide');
                
                function showSlide(index) {
                    slides.forEach(slide => slide.classList.remove('active'));
                    slides[index].classList.add('active');
                }
                
                function nextSlide() {
                    currentIndex = (currentIndex + 1) % slides.length;
                    showSlide(currentIndex);
                }
                
                function prevSlide() {
                    currentIndex = (currentIndex - 1 + slides.length) % slides.length;
                    showSlide(currentIndex);
                }
                
                function startAutoPlay() {
                    interval = setInterval(nextSlide, 4000);
                }
                
                function stopAutoPlay() {
                    clearInterval(interval);
                }
                
                // Event Listeners
                nextBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    stopAutoPlay();
                    nextSlide();
                    startAutoPlay();
                });
                
                prevBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    stopAutoPlay();
                    prevSlide();
                    startAutoPlay();
                });
                
                wrapper.addEventListener('mouseenter', stopAutoPlay);
                wrapper.addEventListener('mouseleave', startAutoPlay);
                
                // Init
                showSlide(0);
                startAutoPlay();
                
                // Store interval to clear later
                carousel.dataset.intervalId = interval;
            }
        });
    }

    function stopAllCarousels() {
        document.querySelectorAll('.popupphoto.carousel').forEach(c => {
            if (c.dataset.intervalId) {
                clearInterval(c.dataset.intervalId);
            }
        });
    }
});
