document.addEventListener('DOMContentLoaded', function() {
    // Check if network data is available
    if (typeof networkData === 'undefined') {
        console.error('Network data not found');
        return;
    }

    // Get the container element
    const container = document.getElementById('network-graph');
    if (!container) {
        console.error('Network container not found');
        return;
    }

    // Remove loading message
    container.classList.add('loaded');

    // Configure vis-network options
    const options = {
        nodes: {
            borderWidth: 2,
            borderWidthSelected: 4,
            chosen: true,
            font: {
                size: 14,
                color: '#333333'
            },
            scaling: {
                min: 10,
                max: 30
            },
            shadow: {
                enabled: true,
                color: 'rgba(0,0,0,0.2)',
                size: 6,
                x: 2,
                y: 2
            }
        },
        edges: {
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 1.2
                }
            },
            color: {
                inherit: false
            },
            font: {
                size: 11,
                color: '#666666',
                strokeWidth: 2,
                strokeColor: '#ffffff'
            },
            smooth: {
                enabled: true,
                type: 'dynamic',
                roundness: 0.5
            },
            width: 2,
            selectionWidth: 4
        },
        physics: {
            enabled: true,
            stabilization: {
                enabled: true,
                iterations: 100,
                updateInterval: 50
            },
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.3,
                springLength: 120,
                springConstant: 0.04,
                damping: 0.4,
                avoidOverlap: 0.2
            }
        },
        layout: {
            randomSeed: 42,  // 고정된 시드로 일관된 레이아웃
            improvedLayout: true,
            clusterThreshold: 150
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            hideEdgesOnDrag: false,
            hideNodesOnDrag: false
        },
        layout: {
            improvedLayout: true,
            clusterThreshold: 150
        }
    };

    // Create network
    const network = new vis.Network(container, networkData, options);

    // Add event listeners
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            // Navigate to entity detail page
            window.location.href = `entities/${nodeId}.html`;
        }
    });

    // Hover effects - simplified to avoid constant redrawing
    network.on('hoverNode', function(params) {
        container.style.cursor = 'pointer';
    });

    network.on('blurNode', function(params) {
        container.style.cursor = 'default';
    });

    // Add loading indicator
    network.on('stabilizationProgress', function(params) {
        const maxWidth = 496;
        const minWidth = 20;
        const widthFactor = params.iterations / params.total;
        const width = Math.max(minWidth, maxWidth * widthFactor);
        
        // You can add a progress bar here if needed
        console.log(`Stabilization progress: ${Math.round(widthFactor * 100)}%`);
    });

    network.on('stabilizationIterationsDone', function() {
        console.log('Network stabilization complete');
    });

    // Fit network to container on window resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            network.fit();
        }, 250);
    });

    // Initial fit
    setTimeout(function() {
        network.fit();
    }, 500);
});