---
hide:
  - navigation
  - toc
  - footer
---

# Data Link

{% set data = load_datalink() %}
<p class="stats-summary">Entities: {{ data.entities | length }} | Relations: {{ data.relationships | length }} | {% for entity_type in data.entities | map(attribute='type') | unique %}{{ entity_type.title() }} {{ data.entities | selectattr('type', 'equalto', entity_type) | list | length }}개{% if not loop.last %}, {% endif %}{% endfor %}</p>

<div id="network-container">
    <div id="network-graph"></div>
</div>

<script src="javascripts/vis-network.min.js"></script>
<script src="javascripts/network.js"></script>
<script>
// Network data will be loaded via AJAX in network.js
let networkData = null;
</script>
