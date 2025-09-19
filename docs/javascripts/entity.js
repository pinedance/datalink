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

    // Use existing gallery functionality from gallery.js
    window.initializeGalleryForEntity = function() {
        // Check if ImageGallery class is available
        if (typeof ImageGallery !== 'undefined' && window.gallery) {
            // Update existing gallery instance for new content
            window.gallery.setupLazyLoading();
            window.gallery.updateImages();
        } else if (typeof ImageGallery !== 'undefined') {
            // Create new gallery instance if none exists
            window.gallery = new ImageGallery();
        }
    };

    // Initial load
    await loadAndDisplayEntity();
});