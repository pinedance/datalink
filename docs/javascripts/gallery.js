/**
 * Image Gallery with Lazy Loading and Lightbox
 */
class ImageGallery {
    constructor() {
        this.currentImageIndex = 0;
        this.images = [];
        this.lightbox = null;
        this.observer = null;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupGallery());
        } else {
            this.setupGallery();
        }
    }
    
    setupGallery() {
        this.setupLazyLoading();
        this.setupLightbox();
        this.bindEvents();
    }
    
    setupLazyLoading() {
        // Create intersection observer for lazy loading
        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                }
            });
        }, options);

        // Observe all gallery items (including dynamically added ones)
        const galleryItems = document.querySelectorAll('.gallery-item:not([data-observer-added])');
        galleryItems.forEach(item => {
            this.observer.observe(item);
            item.setAttribute('data-observer-added', 'true');
        });
    }
    
    loadImage(galleryItem) {
        const placeholder = galleryItem.querySelector('.gallery-placeholder');
        const img = galleryItem.querySelector('.gallery-image');
        const src = placeholder.getAttribute('data-src');
        
        if (!src || img.classList.contains('loaded')) return;
        
        // Create a new image to preload
        const imageLoader = new Image();
        
        imageLoader.onload = () => {
            // Image loaded successfully
            img.src = src;
            img.classList.remove('hidden');
            img.classList.add('loaded');
            placeholder.style.display = 'none';
            
            // Stop observing this item
            this.observer.unobserve(galleryItem);
        };
        
        imageLoader.onerror = () => {
            // Image failed to load
            placeholder.innerHTML = '<div class="error-message">Image failed to load</div>';
            placeholder.style.background = '#f0f0f0';
            this.observer.unobserve(galleryItem);
        };
        
        imageLoader.src = src;
    }
    
    setupLightbox() {
        this.lightbox = document.getElementById('lightbox-modal');
        if (!this.lightbox) return;

        // Update images array dynamically when needed
        this.updateImages();
    }

    updateImages() {
        // Collect all images for lightbox navigation
        const galleryItems = document.querySelectorAll('.gallery-item');
        this.images = Array.from(galleryItems).map(item => {
            const placeholder = item.querySelector('.gallery-placeholder');
            const img = item.querySelector('.gallery-image');
            return {
                src: placeholder.getAttribute('data-src'),
                alt: img.getAttribute('alt') || 'Gallery image',
                element: item
            };
        });

        // Update counter total
        if (this.lightbox) {
            const totalCounter = this.lightbox.querySelector('.lightbox-total');
            if (totalCounter) {
                totalCounter.textContent = this.images.length;
            }
        }
    }
    
    bindEvents() {
        // Gallery item click events (using event delegation for dynamic content)
        document.addEventListener('click', (e) => {
            const galleryItem = e.target.closest('.gallery-item');
            if (galleryItem && !galleryItem.hasAttribute('data-click-bound')) {
                e.preventDefault();
                const galleryItems = document.querySelectorAll('.gallery-item');
                const index = Array.from(galleryItems).indexOf(galleryItem);
                this.openLightbox(index);
            }
        });

        // Keyboard navigation for accessibility
        document.addEventListener('keydown', (e) => {
            const galleryItem = e.target.closest('.gallery-item');
            if (galleryItem && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                const galleryItems = document.querySelectorAll('.gallery-item');
                const index = Array.from(galleryItems).indexOf(galleryItem);
                this.openLightbox(index);
            }
        });

        // Make items focusable
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList.contains('gallery-item')) {
                        node.setAttribute('tabindex', '0');
                    } else if (node.nodeType === 1) {
                        const galleryItems = node.querySelectorAll('.gallery-item');
                        galleryItems.forEach(item => item.setAttribute('tabindex', '0'));
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
        
        // Lightbox controls
        if (this.lightbox) {
            // Close button
            const closeBtn = this.lightbox.querySelector('.lightbox-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => this.closeLightbox());
            }
            
            // Overlay click to close
            const overlay = this.lightbox.querySelector('.lightbox-overlay');
            if (overlay) {
                overlay.addEventListener('click', () => this.closeLightbox());
            }
            
            // Previous/Next buttons
            const prevBtn = this.lightbox.querySelector('.lightbox-prev');
            const nextBtn = this.lightbox.querySelector('.lightbox-next');
            
            if (prevBtn) {
                prevBtn.addEventListener('click', () => this.previousImage());
            }
            
            if (nextBtn) {
                nextBtn.addEventListener('click', () => this.nextImage());
            }
            
            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (!this.lightbox.classList.contains('active')) return;
                
                switch (e.key) {
                    case 'Escape':
                        this.closeLightbox();
                        break;
                    case 'ArrowLeft':
                        this.previousImage();
                        break;
                    case 'ArrowRight':
                        this.nextImage();
                        break;
                }
            });
            
            // Touch/swipe support for mobile
            this.setupTouchEvents();
        }
    }
    
    setupTouchEvents() {
        let startX = 0;
        let startY = 0;
        const threshold = 50; // Minimum swipe distance
        
        const lightboxContent = this.lightbox.querySelector('.lightbox-content');
        if (!lightboxContent) return;
        
        lightboxContent.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        lightboxContent.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Check if it's a horizontal swipe
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > threshold) {
                if (deltaX > 0) {
                    this.previousImage();
                } else {
                    this.nextImage();
                }
            }
        }, { passive: true });
    }
    
    openLightbox(index) {
        if (!this.lightbox) return;

        // Update images array before opening lightbox
        this.updateImages();

        if (!this.images.length) return;

        this.currentImageIndex = index;
        this.updateLightboxImage();
        this.lightbox.classList.remove('hidden');
        this.lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling

        // Focus the lightbox for keyboard navigation
        this.lightbox.focus();
    }
    
    closeLightbox() {
        if (!this.lightbox) return;
        
        this.lightbox.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    previousImage() {
        if (this.currentImageIndex > 0) {
            this.currentImageIndex--;
            this.updateLightboxImage();
        }
    }
    
    nextImage() {
        if (this.currentImageIndex < this.images.length - 1) {
            this.currentImageIndex++;
            this.updateLightboxImage();
        }
    }
    
    updateLightboxImage() {
        if (!this.lightbox || !this.images.length) return;
        
        const currentImage = this.images[this.currentImageIndex];
        const lightboxImg = this.lightbox.querySelector('.lightbox-image');
        const currentCounter = this.lightbox.querySelector('.lightbox-current');
        const prevBtn = this.lightbox.querySelector('.lightbox-prev');
        const nextBtn = this.lightbox.querySelector('.lightbox-next');
        
        if (lightboxImg) {
            lightboxImg.src = currentImage.src;
            lightboxImg.alt = currentImage.alt;
        }
        
        if (currentCounter) {
            currentCounter.textContent = this.currentImageIndex + 1;
        }
        
        // Update button states
        if (prevBtn) {
            prevBtn.disabled = this.currentImageIndex === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentImageIndex === this.images.length - 1;
        }
    }
    
    // Cleanup method
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        
        // Remove event listeners
        document.removeEventListener('keydown', this.keydownHandler);
    }
}

// Initialize gallery when script loads and make it globally accessible
window.gallery = new ImageGallery();