document.addEventListener('DOMContentLoaded', async function() {
    const entityContainer = document.getElementById('entity-container');
    const entityLoading = document.getElementById('entity-loading');
    const entityContent = document.getElementById('entity-content');
    const entityError = document.getElementById('entity-error');

    // Get entity ID from hash
    function getEntityIdFromHash() {
        return window.location.hash.slice(1); // Remove the # symbol
    }

    // Load shared data
    async function loadSharedData() {
        try {
            const [entitiesResponse, relationshipsResponse] = await Promise.all([
                fetch('../data/entities-meta.json'),
                fetch('../data/relationships.json')
            ]);

            if (!entitiesResponse.ok || !relationshipsResponse.ok) {
                throw new Error('Failed to load shared data');
            }

            entitiesMetaData = await entitiesResponse.json();
            relationshipsData = await relationshipsResponse.json();

        } catch (error) {
            console.error('Error loading shared data:', error);
            throw error;
        }
    }

    // Load detailed entity data
    async function loadEntityData(entityId) {
        try {
            const response = await fetch(`../data/entities/${entityId}.json`);
            if (!response.ok) {
                throw new Error(`Entity ${entityId} not found`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error loading entity ${entityId}:`, error);
            throw error;
        }
    }

    // Render entity content
    function renderEntity(entity, relationships) {
        // Update header
        document.getElementById('entity-name').textContent = entity.name;
        document.getElementById('entity-type').textContent = entity.type;

        // Update description
        const descriptionElement = document.getElementById('entity-description');
        if (entity.description) {
            descriptionElement.innerHTML = `<p>${entity.description}</p>`;
        } else {
            descriptionElement.style.display = 'none';
        }

        // Render properties
        renderProperties(entity.properties);

        // Render external links
        renderExternalLinks(entity.external_links);

        // Render image gallery
        renderImageGallery(entity);

        // Render relationships
        renderRelationships(entity.id, relationships);
    }

    function renderProperties(properties) {
        const propertiesContainer = document.getElementById('properties-list');
        if (!properties || Object.keys(properties).length === 0) {
            document.getElementById('entity-properties').style.display = 'none';
            return;
        }

        let html = '';
        for (const [key, value] of Object.entries(properties)) {
            const displayKey = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            if (Array.isArray(value)) {
                html += `<p><strong>${displayKey}:</strong> ${value.join(', ')}</p>`;
            } else {
                html += `<p><strong>${displayKey}:</strong> ${value}</p>`;
            }
        }
        propertiesContainer.innerHTML = html;
    }

    function renderExternalLinks(links) {
        const linksContainer = document.getElementById('external-links-list');
        if (!links || links.length === 0) {
            document.getElementById('entity-external-links').style.display = 'none';
            return;
        }

        let html = '<ul>';
        for (const link of links) {
            html += `<li><a href="${link.url}" target="_blank" rel="noopener">${link.name}</a></li>`;
        }
        html += '</ul>';
        linksContainer.innerHTML = html;
    }

    function renderImageGallery(entity) {
        const galleryContainer = document.getElementById('image-gallery');
        const images = [];

        // Add external image links
        if (entity.image_links) {
            for (const imgUrl of entity.image_links) {
                images.push({
                    src: imgUrl,
                    type: 'external',
                    alt: `${entity.name} image`
                });
            }
        }

        // Add local images
        if (entity.local_images) {
            for (const img of entity.local_images) {
                images.push({
                    src: img.path,
                    type: 'local',
                    alt: img.alt
                });
            }
        }

        if (images.length === 0) {
            document.getElementById('entity-gallery').style.display = 'none';
            return;
        }

        let galleryHtml = '<div class="image-gallery">';
        images.forEach((img, index) => {
            galleryHtml += `
                <div class="gallery-item" data-index="${index}">
                    <div class="gallery-placeholder" data-src="${img.src}">
                        <div class="placeholder-shimmer"></div>
                    </div>
                    <img class="gallery-image hidden" data-src="${img.src}" alt="${img.alt}" loading="lazy">
                </div>
            `;
        });
        galleryHtml += '</div>';

        galleryContainer.innerHTML = galleryHtml;

        // Update lightbox total count
        const lightboxTotal = document.querySelector('.lightbox-total');
        if (lightboxTotal) {
            lightboxTotal.textContent = images.length;
        }

        // Reinitialize gallery functionality for dynamically loaded content
        initializeGalleryForEntity();
    }

    function renderRelationships(entityId, relationships) {
        const relationshipsContainer = document.getElementById('relationships-content');

        // Filter relationships for this entity
        const incoming = relationships.filter(r => r.to === entityId);
        const outgoing = relationships.filter(r => r.from === entityId);

        if (incoming.length === 0 && outgoing.length === 0) {
            document.getElementById('entity-relationships').style.display = 'none';
            return;
        }

        let html = '';

        if (incoming.length > 0) {
            html += '<h3>Incoming Relationships</h3><ul>';
            for (const rel of incoming) {
                const fromEntity = entitiesMetaData[rel.from];
                if (fromEntity) {
                    html += `<li><strong><a href="#${fromEntity.id}">${fromEntity.name}</a></strong> ${rel.type} this entity</li>`;
                }
            }
            html += '</ul>';
        }

        if (outgoing.length > 0) {
            html += '<h3>Outgoing Relationships</h3><ul>';
            for (const rel of outgoing) {
                const toEntity = entitiesMetaData[rel.to];
                if (toEntity) {
                    html += `<li>This entity ${rel.type} <strong><a href="#${toEntity.id}">${toEntity.name}</a></strong></li>`;
                }
            }
            html += '</ul>';
        }

        relationshipsContainer.innerHTML = html;
    }

    // Show error state
    function showError() {
        entityLoading.style.display = 'none';
        entityContent.classList.add('hidden');
        entityError.classList.remove('hidden');
    }

    // Show content
    function showContent() {
        entityLoading.style.display = 'none';
        entityError.classList.add('hidden');
        entityContent.classList.remove('hidden');
    }

    // Main function to load and display entity
    async function loadAndDisplayEntity() {
        const entityId = getEntityIdFromHash();

        if (!entityId) {
            showError();
            return;
        }

        try {
            // Load shared data if not already loaded
            if (!entitiesMetaData || !relationshipsData) {
                await loadSharedData();
            }

            // Check if entity exists in meta data
            if (!entitiesMetaData[entityId]) {
                showError();
                return;
            }

            // Load detailed entity data
            const entity = await loadEntityData(entityId);

            // Render the entity
            renderEntity(entity, relationshipsData);

            // Show content
            showContent();

            // Update page title
            document.title = `${entity.name} - DataLink`;

        } catch (error) {
            console.error('Error loading entity:', error);
            showError();
        }
    }

    // Handle hash changes (browser back/forward)
    window.addEventListener('hashchange', loadAndDisplayEntity);

    // Function to initialize gallery for dynamically loaded content
    window.initializeGalleryForEntity = function() {
        // Setup lazy loading for new gallery items
        const galleryItems = document.querySelectorAll('.gallery-item:not([data-observer-added])');

        if (galleryItems.length === 0) return;

        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loadImageForEntity(entry.target, observer);
                }
            });
        }, options);

        galleryItems.forEach(item => {
            observer.observe(item);
            item.setAttribute('data-observer-added', 'true');
        });

        // Setup click events for lightbox
        setupLightboxForEntity(galleryItems);
    };

    function loadImageForEntity(galleryItem, observer) {
        const placeholder = galleryItem.querySelector('.gallery-placeholder');
        const img = galleryItem.querySelector('.gallery-image');
        const src = placeholder.getAttribute('data-src');

        if (!src || img.classList.contains('loaded')) return;

        const imageLoader = new Image();

        imageLoader.onload = () => {
            img.src = src;
            img.classList.remove('hidden');
            img.classList.add('loaded');
            placeholder.style.display = 'none';
            observer.unobserve(galleryItem);
        };

        imageLoader.onerror = () => {
            placeholder.innerHTML = '<div class="error-message">Image failed to load</div>';
            placeholder.style.background = '#f0f0f0';
            observer.unobserve(galleryItem);
        };

        imageLoader.src = src;
    }

    function setupLightboxForEntity(galleryItems) {
        const lightbox = document.getElementById('lightbox-modal');
        if (!lightbox) return;

        galleryItems.forEach((item, index) => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                openEntityLightbox(index);
            });

            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openEntityLightbox(index);
                }
            });

            item.setAttribute('tabindex', '0');
        });
    }

    function openEntityLightbox(index) {
        const lightbox = document.getElementById('lightbox-modal');
        const galleryItems = document.querySelectorAll('.gallery-item');

        if (!lightbox || !galleryItems.length) return;

        const images = Array.from(galleryItems).map(item => {
            const placeholder = item.querySelector('.gallery-placeholder');
            const img = item.querySelector('.gallery-image');
            return {
                src: placeholder.getAttribute('data-src'),
                alt: img.getAttribute('alt') || 'Gallery image'
            };
        });

        let currentIndex = index;
        const lightboxImg = lightbox.querySelector('.lightbox-image');
        const currentCounter = lightbox.querySelector('.lightbox-current');
        const totalCounter = lightbox.querySelector('.lightbox-total');

        function updateLightboxImage() {
            if (lightboxImg) {
                lightboxImg.src = images[currentIndex].src;
                lightboxImg.alt = images[currentIndex].alt;
            }
            if (currentCounter) {
                currentCounter.textContent = currentIndex + 1;
            }
            if (totalCounter) {
                totalCounter.textContent = images.length;
            }
        }

        updateLightboxImage();
        lightbox.classList.remove('hidden');
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Setup lightbox navigation
        const closeBtn = lightbox.querySelector('.lightbox-close');
        const overlay = lightbox.querySelector('.lightbox-overlay');
        const prevBtn = lightbox.querySelector('.lightbox-prev');
        const nextBtn = lightbox.querySelector('.lightbox-next');

        function closeLightbox() {
            lightbox.classList.add('hidden');
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }

        if (closeBtn) closeBtn.onclick = closeLightbox;
        if (overlay) overlay.onclick = closeLightbox;

        if (prevBtn) {
            prevBtn.onclick = () => {
                if (currentIndex > 0) {
                    currentIndex--;
                    updateLightboxImage();
                }
            };
        }

        if (nextBtn) {
            nextBtn.onclick = () => {
                if (currentIndex < images.length - 1) {
                    currentIndex++;
                    updateLightboxImage();
                }
            };
        }

        // Keyboard navigation
        function handleKeydown(e) {
            switch (e.key) {
                case 'Escape':
                    closeLightbox();
                    document.removeEventListener('keydown', handleKeydown);
                    break;
                case 'ArrowLeft':
                    if (currentIndex > 0) {
                        currentIndex--;
                        updateLightboxImage();
                    }
                    break;
                case 'ArrowRight':
                    if (currentIndex < images.length - 1) {
                        currentIndex++;
                        updateLightboxImage();
                    }
                    break;
            }
        }

        document.addEventListener('keydown', handleKeydown);
    }

    // Initial load
    await loadAndDisplayEntity();
});