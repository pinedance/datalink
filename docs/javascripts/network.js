/**
 * Network Graph Visualization
 *
 * This module initializes and manages the vis-network graph that displays
 * the linked data relationships from the DataLink project.
 *
 * Features:
 * - Loads network data dynamically via AJAX from JSON files
 * - Creates interactive network graph with hover and click events
 * - Handles navigation to individual entity pages
 * - Responsive layout with window resize support
 * - Loading states and error handling
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Get the container element where the network graph will be rendered
    const container = document.getElementById('network-graph');
    if (!container) {
        console.error('Network container not found');
        return;
    }

    // Show loading message while data is being fetched
    container.innerHTML = '<div class="loading">Loading network data...</div>';

    try {
        // Load network data via AJAX from the generated JSON file
        // This file is created by generate_pages.py during build process
        const response = await fetch('data/network.json');
        if (!response.ok) {
            throw new Error(`Failed to load network data: ${response.status}`);
        }

        const networkData = await response.json();

        // Clear loading message and prepare container for network rendering
        container.innerHTML = '';
        container.classList.add('loaded');

        // Function to get current theme-aware colors
        function getThemeColors() {
            const isDarkMode = document.body.getAttribute('data-md-color-scheme') === 'slate';

            if (isDarkMode) {
                return {
                    nodeText: 'hsla(0, 0%, 85%, 1)',
                    nodeShadow: 'hsla(0, 0%, 0%, 0.4)',
                    edgeText: 'hsla(0, 0%, 75%, 1)',
                    edgeStroke: 'hsla(0, 0%, 15%, 0.8)'
                };
            } else {
                return {
                    nodeText: 'hsla(0, 0%, 20%, 1)',
                    nodeShadow: 'hsla(0, 0%, 0%, 0.2)',
                    edgeText: 'hsla(0, 0%, 40%, 1)',
                    edgeStroke: 'hsla(0, 0%, 100%, 1)'
                };
            }
        }

        // Get theme colors
        const themeColors = getThemeColors();

        // Configure vis-network options for optimal visualization
        const options = {
            // Node appearance and behavior settings
            nodes: {
                borderWidth: 2,           // Default border width
                borderWidthSelected: 4,   // Border width when selected
                chosen: true,             // Enable selection highlighting
                font: {
                    size: 14,
                    color: themeColors.nodeText
                },
                scaling: {
                    min: 10,             // Minimum node size
                    max: 30              // Maximum node size
                },
                shadow: {
                    enabled: true,
                    color: themeColors.nodeShadow,
                    size: 6,
                    x: 2,
                    y: 2
                }
            },
            // Edge appearance and behavior settings
            edges: {
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 1.2  // Arrow size multiplier
                    }
                },
                color: {
                    inherit: false        // Don't inherit color from nodes
                },
                font: {
                    size: 11,
                    color: themeColors.edgeText,
                    strokeWidth: 2,       // Text outline width
                    strokeColor: themeColors.edgeStroke
                },
                smooth: {
                    enabled: true,
                    type: 'dynamic',      // Dynamic curve smoothing
                    roundness: 0.5
                },
                width: 2,                 // Default edge width
                selectionWidth: 4         // Edge width when selected
            },
            // Physics simulation settings for node positioning
            physics: {
                enabled: true,
                stabilization: {
                    enabled: true,
                    iterations: 100,      // Max iterations for initial layout
                    updateInterval: 50    // Update frequency during stabilization
                },
                barnesHut: {             // Force-directed layout algorithm
                    gravitationalConstant: -2500,
                    centralGravity: 0.8,
                    // springLength: 120,    // Preferred edge length
                    // springConstant: 0.04, // Edge stiffness
                    // damping: 0.4,         // Movement damping
                    // avoidOverlap: 0.8     // Node overlap prevention
                }
            },
            // Layout configuration
            layout: {
                randomSeed: 42,          // Fixed seed for consistent layout
                improvedLayout: true,    // Enhanced layout algorithm
                clusterThreshold: 150    // Clustering threshold for large graphs
            },
            // User interaction settings
            interaction: {
                hover: true,             // Enable hover effects
                tooltipDelay: 200,       // Hover tooltip delay (ms)
                hideEdgesOnDrag: false,  // Keep edges visible during drag
                hideNodesOnDrag: false   // Keep nodes visible during drag
            }
        };

        // Create the vis-network instance with loaded data and options
        const network = new vis.Network(container, networkData, options);

        // Function to update network colors when theme changes
        function updateNetworkTheme() {
            const newColors = getThemeColors();
            const newOptions = {
                nodes: {
                    font: { color: newColors.nodeText },
                    shadow: { color: newColors.nodeShadow }
                },
                edges: {
                    font: {
                        color: newColors.edgeText,
                        strokeColor: newColors.edgeStroke
                    }
                }
            };
            network.setOptions(newOptions);
        }

        // Watch for theme changes
        const themeObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
                    updateNetworkTheme();
                }
            });
        });

        themeObserver.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-md-color-scheme']
        });

        // Event Handlers

        // Handle node clicks - navigate to entity detail page
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const url = `entities/${nodeId}.html`;

                // Check if ctrl key is pressed for new tab
                if (params.event.srcEvent.ctrlKey) {
                    // Open in new tab
                    window.open(url, '_blank');
                } else {
                    // Navigate in current window
                    window.location.href = url;
                }
            }
        });

        // Mouse cursor feedback for hoverable nodes
        network.on('hoverNode', function(params) {
            container.style.cursor = 'pointer';
        });

        network.on('blurNode', function(params) {
            container.style.cursor = 'default';
        });

        // Physics stabilization progress tracking
        network.on('stabilizationProgress', function(params) {
            const maxWidth = 496;
            const minWidth = 20;
            const widthFactor = params.iterations / params.total;
            const width = Math.max(minWidth, maxWidth * widthFactor);

            // Log progress for debugging (can be extended to show progress bar)
            console.log(`Stabilization progress: ${Math.round(widthFactor * 100)}%`);
        });

        network.on('stabilizationIterationsDone', function() {
            console.log('Network stabilization complete');
        });

        // Responsive layout handling

        // Debounced window resize handler to prevent excessive redraws
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(function() {
                network.fit(); // Adjust network view to fit container
            }, 250); // 250ms debounce delay
        });

        // Initial network fit after DOM and physics stabilization
        setTimeout(function() {
            network.fit();
        }, 500); // 500ms delay to ensure proper initialization

    } catch (error) {
        // Error handling for network data loading failures
        console.error('Error loading network data:', error);
        container.innerHTML = '<div class="error">Failed to load network data. Please try refreshing the page.</div>';
    }
});