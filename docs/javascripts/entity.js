/**
 * Entity Page Handler
 *
 * This module manages the individual entity viewer page with hash-based routing.
 * It loads entity data dynamically and renders detailed information including
 * properties, relationships, image galleries, and external links.
 *
 * Features:
 * - Hash-based routing (#entity_id)
 * - Dynamic entity data loading via AJAX
 * - Image gallery integration with lightbox functionality
 * - Relationship visualization with navigation links
 * - Error handling and loading states
 * - Browser history support (back/forward navigation)
 */

document.addEventListener('DOMContentLoaded', async function() {
    // DOM element references
    const entityContainer = document.getElementById('entity-container');
    const entityLoading = document.getElementById('entity-loading');
    const entityContent = document.getElementById('entity-content');
    const entityError = document.getElementById('entity-error');

    // Global data cache to avoid repeated API calls
    let entitiesMetaData = null;
    let relationshipsData = null;

    // Extract entity ID from URL hash parameter
    function getEntityIdFromHash() {
        return window.location.hash.slice(1); // Remove the # symbol
    }

    /**
     * Load shared metadata and relationships data
     * This data is cached to avoid repeated API calls when navigating between entities
     */
    async function loadSharedData() {
        try {
            // Load entities metadata and relationships data in parallel
            const [entitiesResponse, relationshipsResponse] = await Promise.all([
                fetch('../data/entities-meta.json'),    // Entity metadata (name, type, etc.)
                fetch('../data/relationships.json')     // All relationship connections
            ]);

            if (!entitiesResponse.ok || !relationshipsResponse.ok) {
                throw new Error('Failed to load shared data');
            }

            // Cache the data for subsequent use
            entitiesMetaData = await entitiesResponse.json();
            relationshipsData = await relationshipsResponse.json();

        } catch (error) {
            console.error('Error loading shared data:', error);
            throw error;
        }
    }

    /**
     * Load detailed data for a specific entity
     * @param {string} entityId - The unique identifier for the entity
     * @returns {Object} Complete entity data including properties, images, etc.
     */
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

    /**
     * Main rendering function that populates the entity page with data
     * @param {Object} entity - Complete entity data
     * @param {Array} relationships - All relationship data for filtering
     */
    function renderEntity(entity, relationships) {
        // Update page header with entity information
        document.getElementById('entity-name').textContent = entity.name;
        document.getElementById('entity-type').textContent = entity.type;

        // Display entity description if available
        const descriptionElement = document.getElementById('entity-description');
        if (entity.description) {
            descriptionElement.innerHTML = `<p>${entity.description}</p>`;
        } else {
            descriptionElement.style.display = 'none';
        }

        // Render different sections of the entity page
        renderProperties(entity.properties);
        renderExternalLinks(entity.external_links);
        renderImageGallery(entity);
        renderRelationships(entity.id, relationships);
    }

    /**
     * Render entity properties section
     * @param {Object} properties - Key-value pairs of entity properties
     */
    function renderProperties(properties) {
        const propertiesContainer = document.getElementById('properties-list');
        if (!properties || Object.keys(properties).length === 0) {
            document.getElementById('entity-properties').style.display = 'none';
            return;
        }

        let html = '';
        for (const [key, value] of Object.entries(properties)) {
            // Format property keys for display (snake_case -> Title Case)
            const displayKey = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            if (Array.isArray(value)) {
                html += `<p><strong>${displayKey}:</strong> ${value.join(', ')}</p>`;
            } else {
                html += `<p><strong>${displayKey}:</strong> ${value}</p>`;
            }
        }
        propertiesContainer.innerHTML = html;
    }

    /**
     * Render external links section
     * @param {Array} links - Array of external link objects with url and name properties
     */
    function renderExternalLinks(links) {
        const linksContainer = document.getElementById('external-links-list');
        if (!links || links.length === 0) {
            document.getElementById('entity-external-links').style.display = 'none';
            return;
        }

        let html = '<ul>';
        for (const link of links) {
            // Add security attributes for external links
            html += `<li><a href="${link.url}" target="_blank" rel="noopener">${link.name}</a></li>`;
        }
        html += '</ul>';
        linksContainer.innerHTML = html;
    }

    /**
     * Render image gallery section with lazy loading and lightbox support
     * Combines external image URLs and local image files
     * @param {Object} entity - Entity data containing image_links and local_images
     */
    function renderImageGallery(entity) {
        const galleryContainer = document.getElementById('image-gallery');
        const images = [];

        // Collect external image links (support both old string format and new object format)
        if (entity.image_links) {
            for (const imgItem of entity.image_links) {
                if (typeof imgItem === 'string') {
                    // Old format: simple string URL
                    images.push({
                        src: imgItem,
                        type: 'external',
                        alt: `${entity.name} image`,
                        source: 'Unknown',
                        description: ''
                    });
                } else if (typeof imgItem === 'object' && imgItem.url) {
                    // New format: object with url, source, description
                    images.push({
                        src: imgItem.url,
                        type: 'external',
                        alt: imgItem.alt || `${entity.name} image`,
                        source: imgItem.source || 'Unknown',
                        description: imgItem.description || ''
                    });
                }
            }
        }

        // Collect local image files
        if (entity.local_images) {
            for (const img of entity.local_images) {
                images.push({
                    src: img.path,
                    type: 'local',
                    alt: img.alt,
                    source: 'Local',
                    description: img.description || `Local image: ${img.filename}`
                });
            }
        }

        // Hide gallery section if no images available
        if (images.length === 0) {
            document.getElementById('entity-gallery').style.display = 'none';
            return;
        }

        // Generate gallery HTML with placeholder and lazy loading structure
        let galleryHtml = '<div class="image-gallery">';
        images.forEach((img, index) => {
            galleryHtml += `
                <div class="gallery-item" data-index="${index}">
                    <div class="gallery-placeholder"
                         data-src="${img.src}"
                         data-source="${img.source || 'Unknown'}"
                         data-description="${img.description || ''}">
                        <div class="placeholder-shimmer"></div>
                    </div>
                    <img class="gallery-image hidden"
                         data-src="${img.src}"
                         alt="${img.alt}"
                         loading="lazy">
                </div>
            `;
        });
        galleryHtml += '</div>';

        galleryContainer.innerHTML = galleryHtml;

        // Update lightbox counter for navigation
        const lightboxTotal = document.querySelector('.lightbox-total');
        if (lightboxTotal) {
            lightboxTotal.textContent = images.length;
        }

        // Initialize gallery functionality for the dynamically loaded content
        initializeGalleryForEntity();
    }

    /**
     * Render relationships section showing incoming and outgoing connections
     * @param {string} entityId - Current entity ID
     * @param {Array} relationships - All relationship data for filtering
     */
    function renderRelationships(entityId, relationships) {
        const relationshipsContainer = document.getElementById('relationships-content');

        // Filter relationships where this entity is either source or target
        const incoming = relationships.filter(r => r.to === entityId);
        const outgoing = relationships.filter(r => r.from === entityId);

        // Hide section if no relationships exist
        if (incoming.length === 0 && outgoing.length === 0) {
            document.getElementById('entity-relationships').style.display = 'none';
            return;
        }

        let html = '';

        // Render incoming relationships (other entities pointing to this one)
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

        // Render outgoing relationships (this entity pointing to others)
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

    /**
     * Display error state when entity loading fails
     */
    function showError() {
        entityLoading.style.display = 'none';
        entityContent.classList.add('hidden');
        entityError.classList.remove('hidden');
    }

    /**
     * Display content state when entity loads successfully
     */
    function showContent() {
        entityLoading.style.display = 'none';
        entityError.classList.add('hidden');
        entityContent.classList.remove('hidden');
    }

    /**
     * Main controller function that orchestrates entity loading and display
     * Handles the complete flow from hash parsing to content rendering
     */
    async function loadAndDisplayEntity() {
        const entityId = getEntityIdFromHash();

        // Validate that an entity ID is provided in the hash
        if (!entityId) {
            showError();
            return;
        }

        try {
            // Load shared metadata if not already cached
            if (!entitiesMetaData || !relationshipsData) {
                await loadSharedData();
            }

            // Verify entity exists in the metadata
            if (!entitiesMetaData[entityId]) {
                showError();
                return;
            }

            // Load detailed entity-specific data
            const entity = await loadEntityData(entityId);

            // Populate the page with entity information
            renderEntity(entity, relationshipsData);

            // Transition from loading to content display
            showContent();

            // Update browser tab title
            document.title = `${entity.name} - DataLink`;

        } catch (error) {
            console.error('Error loading entity:', error);
            showError();
        }
    }

    // Browser navigation event handling
    // Listen for hash changes to support browser back/forward buttons
    window.addEventListener('hashchange', loadAndDisplayEntity);

    /**
     * Initialize gallery functionality for dynamically loaded entity content
     * Integrates with the existing gallery.js ImageGallery class
     * Creates new instance or updates existing one as needed
     */
    window.initializeGalleryForEntity = function() {
        // Check if ImageGallery class is available from gallery.js
        if (typeof ImageGallery !== 'undefined' && window.gallery) {
            // Update existing gallery instance for new content
            window.gallery.setupLazyLoading();
            window.gallery.updateImages();
        } else if (typeof ImageGallery !== 'undefined') {
            // Create new gallery instance if none exists
            window.gallery = new ImageGallery();
        }
    };

    // Start the application by loading the initial entity
    await loadAndDisplayEntity();
});