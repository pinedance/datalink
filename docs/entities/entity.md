---
hide:
#   - navigation
#   - toc
  - footer
---

<style>
.hidden {
    display: none !important;
}
.loading {
    text-align: center;
    padding: 2rem;
    color: hsla(0, 0%, 40%, 1);
}
.error {
    text-align: center;
    padding: 2rem;
    color: hsla(0, 73%, 50%, 1);
}
</style>

<div id="entity-container">
    <div id="entity-loading">Loading entity data...</div>
    <div id="entity-content" class="hidden">
        <div id="entity-header">
            <h1 id="entity-name"></h1>
            <p id="entity-type"></p>
        </div>

        <div id="entity-description"></div>

        <div id="entity-properties">
            <h2>Properties</h2>
            <div id="properties-list"></div>
        </div>

        <div id="entity-external-links">
            <h2>External Links</h2>
            <div id="external-links-list"></div>
        </div>

        <div id="entity-gallery">
            <h2>Image Gallery</h2>
            <div id="image-gallery"></div>
        </div>

        <div id="entity-relationships">
            <h2>Relationships</h2>
            <div id="relationships-content"></div>
        </div>

        <div id="entity-navigation">
            <p><a href="../index.html">← Back to Home</a></p>
        </div>
    </div>

    <div id="entity-error" class="hidden">
        <h1>Entity Not Found</h1>
        <p>The requested entity could not be found.</p>
        <p><a href="../index.html">← Back to Home</a></p>
    </div>
</div>

<!-- Lightbox Modal -->
<div id="lightbox-modal" class="lightbox-modal hidden">
    <div class="lightbox-overlay"></div>
    <div class="lightbox-content">
        <button class="lightbox-close">&times;</button>
        <button class="lightbox-prev">&#8249;</button>
        <img class="lightbox-image" src="" alt="">
        <button class="lightbox-next">&#8250;</button>
        <div class="lightbox-counter">
            <span class="lightbox-current">1</span> / <span class="lightbox-total">1</span>
        </div>
    </div>
</div>

<script src="../javascripts/entity.js"></script>
<script src="../javascripts/gallery.js"></script>

<script>
// Entity data and relationships will be loaded dynamically
let entityData = null;
let relationshipsData = null;
let entitiesMetaData = null;
</script>
