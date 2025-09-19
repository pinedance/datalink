# DataLink Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow](#data-flow)
3. [Component Reference](#component-reference)
4. [API Documentation](#api-documentation)
5. [Development Workflow](#development-workflow)
6. [Build Process](#build-process)
7. [Frontend Architecture](#frontend-architecture)
8. [Performance Considerations](#performance-considerations)
9. [Troubleshooting](#troubleshooting)

## Architecture Overview

### High-Level Architecture

DataLink follows a static site generation pattern with dynamic frontend components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YAML Data     │───▶│  Build Process   │───▶│  Static Site    │
│   (Source)      │    │  (Python)        │    │  (HTML/JS/CSS)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   JSON Data      │
                       │   (Runtime)      │
                       └──────────────────┘
```

### Technology Stack

- **Static Site Generator**: MkDocs + Material Theme
- **Data Processing**: Python 3.x (PyYAML, pathlib)
- **Frontend**: Vanilla JavaScript ES6+ (no frameworks)
- **Visualization**: vis-network.js
- **Build Tools**: mkdocs-gen-files, mkdocs-macros-plugin
- **Styling**: CSS3 with Material Design principles

### Core Principles

1. **Build-time Data Processing**: Heavy data processing happens during build, not runtime
2. **Client-side Routing**: Hash-based routing for entity navigation without server requests
3. **Progressive Enhancement**: Core functionality works without JavaScript
4. **Performance First**: Lazy loading, efficient data structures, minimal bundle size

## Data Flow

### Build-time Flow

```mermaid
graph TD
    A[YAML Files] --> B[core_datalink.py]
    B --> C[generate_pages.py]
    C --> D[network.json]
    C --> E[entities-meta.json]
    C --> F[relationships.json]
    C --> G[entity/{id}.json files]
    C --> H[Entity index pages]
    I[MkDocs] --> J[Static HTML]
    D --> K[Client Browser]
    E --> K
    F --> K
    G --> K
```

### Runtime Flow

```mermaid
graph TD
    A[Page Load] --> B{Page Type?}
    B -->|Index| C[Load network.json]
    B -->|Entity| D[Load entities-meta.json]
    C --> E[Render Network Graph]
    D --> F[Load entity/{id}.json]
    F --> G[Render Entity Page]
    G --> H[Initialize Image Gallery]
    E --> I[Handle Node Clicks]
    I --> J[Navigate to Entity Page]
```

## Component Reference

### Backend Components

#### `core_datalink.py`
**Purpose**: Core data loading utilities

**Key Functions**:
- `load_datalink()`: Loads and merges YAML files
- `get_entity_by_id(data, entity_id)`: Retrieves specific entity
- `get_entity_relationships(data, entity_id)`: Gets entity relationships

**Usage**:
```python
from core_datalink import load_datalink
data = load_datalink()
```

#### `generate_pages.py`
**Purpose**: Build-time page and JSON generation

**Key Functions**:
- `export_json_data(data)`: Generates all JSON files
- `main()`: Orchestrates build process

**Generated Files**:
- `data/network.json`: Network graph data
- `data/entities-meta.json`: Entity metadata
- `data/relationships.json`: All relationships
- `data/entities/{id}.json`: Individual entity data

#### `main.py`
**Purpose**: MkDocs macro definitions

**Key Macros**:
- `load_datalink()`: Template access to data

### Frontend Components

#### `network.js`
**Purpose**: Network graph visualization

**Key Features**:
- vis-network integration
- Dynamic data loading
- Node click handling
- Responsive layout
- Physics simulation

**API**:
```javascript
// Network loads automatically on DOMContentLoaded
// Configuration in options object
// Event handlers for user interaction
```

#### `entity.js`
**Purpose**: Entity page management

**Key Features**:
- Hash-based routing
- Dynamic content loading
- Relationship rendering
- Image gallery integration

**API**:
```javascript
// Main functions
getEntityIdFromHash()           // Extract entity ID from URL hash
loadAndDisplayEntity()          // Load and render entity
renderEntity(entity, relationships) // Render entity content
initializeGalleryForEntity()    // Setup image gallery
```

#### `gallery.js`
**Purpose**: Image gallery with lightbox

**Key Features**:
- Lazy loading with Intersection Observer
- Lightbox modal
- Touch/swipe support
- Keyboard navigation
- Dynamic content support

**API**:
```javascript
// Class instantiation
const gallery = new ImageGallery()

// Key methods
gallery.setupLazyLoading()      // Setup lazy loading
gallery.updateImages()          // Refresh image list
gallery.openLightbox(index)     // Open lightbox
gallery.destroy()               // Cleanup
```

### Data Structures

#### Entity Object
```json
{
  "id": "unique_identifier",
  "name": "Entity Name",
  "type": "entity_type",
  "description": "Optional description",
  "properties": {
    "key": "value",
    "array_key": ["item1", "item2"]
  },
  "external_links": [
    {
      "name": "Link Name",
      "url": "https://example.com"
    }
  ],
  "image_links": ["url1", "url2"],
  "local_images": [
    {
      "filename": "image.jpg",
      "path": "/images/entity_id/image.jpg",
      "alt": "Alt text"
    }
  ]
}
```

#### Relationship Object
```json
{
  "from": "source_entity_id",
  "to": "target_entity_id",
  "type": "relationship_type",
  "properties": {}
}
```

#### Network Node Object
```json
{
  "id": "entity_id",
  "label": "Display Name",
  "title": "Hover tooltip",
  "color": "hsla(217, 92%, 73%, 0.9)",
  "shape": "dot",
  "size": 25,
  "font": {"size": 14},
  "type": "entity_type"
}
```

#### Network Edge Object
```json
{
  "from": "source_id",
  "to": "target_id",
  "label": "relationship_type",
  "color": "hsla(328, 78%, 64%, 1)",
  "arrows": "to",
  "font": {"size": 12}
}
```

## API Documentation

### REST Endpoints (Static JSON Files)

All data is served as static JSON files generated during build:

#### `GET /data/network.json`
Returns network graph data for visualization.

**Response**:
```json
{
  "nodes": [/* array of node objects */],
  "edges": [/* array of edge objects */]
}
```

#### `GET /data/entities-meta.json`
Returns metadata for all entities (lightweight).

**Response**:
```json
{
  "entity_id": {
    "id": "entity_id",
    "name": "Entity Name",
    "type": "entity_type",
    // ... metadata only
  }
}
```

#### `GET /data/relationships.json`
Returns all relationship data.

**Response**:
```json
[
  {
    "from": "entity1",
    "to": "entity2",
    "type": "relationship_type",
    "properties": {}
  }
]
```

#### `GET /data/entities/{id}.json`
Returns complete data for specific entity.

**Parameters**:
- `id`: Entity identifier

**Response**: Complete entity object with all properties and local images.

### JavaScript Events

#### Network Graph Events
```javascript
// Node click - fired when network node is clicked
network.on('click', function(params) {
  // params.nodes[0] contains clicked node ID
})

// Hover events
network.on('hoverNode', function(params) {})
network.on('blurNode', function(params) {})
```

#### Hash Change Events
```javascript
// Browser navigation
window.addEventListener('hashchange', loadAndDisplayEntity)
```

#### Gallery Events
```javascript
// Image load events
gallery.observer // IntersectionObserver instance
// Touch events for mobile
// Keyboard events for accessibility
```

## Development Workflow

### Setup Development Environment

1. **Install Dependencies**:
   ```bash
   # Install Python dependencies
   pip install mkdocs mkdocs-material mkdocs-gen-files mkdocs-macros-plugin PyYAML

   # Or using uv
   uv sync
   ```

2. **Project Structure**:
   ```
   datalink/
   ├── data/datalink/          # YAML data files
   ├── docs/                   # MkDocs source
   │   ├── images/            # Local images
   │   ├── javascripts/       # JS components
   │   ├── stylesheets/       # CSS files
   │   └── entities/          # Entity pages
   ├── core_datalink.py       # Data utilities
   ├── generate_pages.py      # Build script
   └── main.py               # MkDocs macros
   ```

3. **Start Development Server**:
   ```bash
   uv run mkdocs serve
   # or
   mkdocs serve
   ```

### Adding New Data

1. **Create YAML File**:
   ```yaml
   # data/datalink/example.yaml
   entities:
     - id: new_entity
       name: "New Entity"
       type: "example_type"
       description: "Entity description"
       properties:
         key: "value"
       external_links:
         - name: "Website"
           url: "https://example.com"
       image_links:
         - "https://example.com/image.jpg"

   relationships:
     - from: new_entity
       to: existing_entity
       type: "related_to"
   ```

2. **Add Images** (optional):
   ```
   docs/images/new_entity/
   ├── image1.jpg
   └── image2.png
   ```

3. **Build and Test**:
   ```bash
   uv run mkdocs build
   # Check generated files in site/
   ```

### Modifying Frontend Components

1. **JavaScript Changes**:
   - Edit files in `docs/javascripts/`
   - Follow existing patterns and comment conventions
   - Test across different browsers and devices

2. **CSS Changes**:
   - Edit files in `docs/stylesheets/`
   - Maintain responsive design
   - Consider dark mode compatibility

3. **Testing**:
   - Test network graph functionality
   - Test entity page navigation
   - Test image gallery on mobile devices
   - Verify accessibility features

## Build Process

### MkDocs Build Pipeline

1. **Pre-build Phase**:
   - `mkdocs-gen-files` executes `generate_pages.py`
   - YAML data loaded via `core_datalink.py`
   - JSON files generated in `site/data/`

2. **Build Phase**:
   - MkDocs processes Markdown files
   - `mkdocs-macros-plugin` processes templates
   - Static assets copied to output

3. **Post-build Phase**:
   - HTML, CSS, JavaScript bundled
   - Service worker generated (if configured)
   - Static site ready for deployment

### Generated File Structure

```
site/
├── data/
│   ├── network.json
│   ├── entities-meta.json
│   ├── relationships.json
│   └── entities/
│       ├── entity1.json
│       └── entity2.json
├── javascripts/
├── stylesheets/
├── images/
└── *.html
```

### Performance Optimization

- **Data splitting**: Large datasets split into smaller JSON files
- **Lazy loading**: Images loaded only when visible
- **Efficient queries**: Pre-indexed data for fast lookups
- **Caching**: Browser caching for static JSON files

## Frontend Architecture

### Module System

DataLink uses ES6+ modules with careful dependency management:

```javascript
// No build step - direct browser module loading
// Careful ordering of script tags in HTML
// Event-driven communication between modules
```

### State Management

- **Global State**: Minimal global variables
- **Component State**: Each component manages its own state
- **Data Caching**: Loaded data cached to avoid repeated requests
- **URL State**: Entity ID stored in URL hash

### Responsive Design

- **Mobile-first**: CSS designed for mobile first
- **Touch Support**: Gallery supports touch/swipe gestures
- **Accessibility**: Keyboard navigation and ARIA labels
- **Performance**: Optimized for slower mobile connections

### Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest)
- **ES6+ Features**: Arrow functions, async/await, modules
- **Fallbacks**: Graceful degradation where needed
- **Testing**: Cross-browser testing recommended

## Performance Considerations

### Data Loading

- **Lazy Loading**: Entity data loaded only when needed
- **Prefetching**: Critical data loaded on page load
- **Caching**: Browser caching for static JSON files
- **Compression**: Server should enable gzip compression

### Image Optimization

- **Lazy Loading**: Images loaded when entering viewport
- **Progressive Loading**: Placeholder → Image transition
- **Format Support**: WebP, AVIF for modern browsers
- **Responsive Images**: Multiple sizes for different devices

### Network Graph

- **Physics Simulation**: Limited iterations for faster stabilization
- **Node Simplification**: Simplified rendering for large graphs
- **Event Throttling**: Debounced resize and interaction events
- **Memory Management**: Proper cleanup of vis-network instances

### Bundle Size

- **No Framework**: Vanilla JavaScript keeps bundle small
- **Minimal Dependencies**: Only essential external libraries
- **Code Splitting**: Features loaded only when needed
- **Tree Shaking**: Unused code eliminated during build

## Troubleshooting

### Common Issues

#### Entity Page Not Loading

**Symptoms**: Hash navigation doesn't load entity content

**Causes**:
- Entity JSON file not generated
- Invalid entity ID in URL
- JavaScript errors in console

**Solutions**:
1. Check if `data/entities/{id}.json` exists
2. Verify entity ID matches YAML data
3. Check browser console for JavaScript errors
4. Ensure proper MkDocs build completion

#### Network Graph Not Rendering

**Symptoms**: Blank network container or loading message persists

**Causes**:
- `network.json` file missing or invalid
- vis-network library not loaded
- Container element not found

**Solutions**:
1. Verify `data/network.json` exists and contains valid data
2. Check vis-network.js is loaded before network.js
3. Ensure network-graph container exists in HTML
4. Check browser console for errors

#### Images Not Loading in Gallery

**Symptoms**: Gallery shows placeholders but images don't load

**Causes**:
- Incorrect image paths
- CORS issues with external images
- Lazy loading not triggering

**Solutions**:
1. Verify image paths in entity JSON files
2. Check external image URLs and CORS headers
3. Test Intersection Observer support
4. Manually trigger gallery.setupLazyLoading()

#### Build Errors

**Symptoms**: MkDocs build fails or generates incorrect JSON

**Causes**:
- Invalid YAML syntax
- Missing Python dependencies
- Path issues in generate_pages.py

**Solutions**:
1. Validate YAML files with online validators
2. Install required Python packages
3. Check file paths and permissions
4. Review build logs for specific errors

### Debug Mode

Enable detailed logging by modifying JavaScript files:

```javascript
// Add at the top of JS files for debugging
const DEBUG = true;
const log = DEBUG ? console.log : () => {};

// Use throughout code
log('Debug message', data);
```

### Performance Monitoring

Monitor performance using browser developer tools:

1. **Network Tab**: Check JSON file sizes and load times
2. **Performance Tab**: Profile JavaScript execution
3. **Memory Tab**: Monitor memory usage and leaks
4. **Console**: Watch for errors and warnings

---

This technical documentation should be updated as the system evolves. For questions or issues not covered here, please check the project repository or create an issue for discussion.