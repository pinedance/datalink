---
hide:
  - navigation
  - toc
  - footer
---

{% set data = load_datalink() %}
<p class="stats-summary">총 {{ data.entities | length }}개 엔터티, {{ data.relationships | length }}개 관계 | 유형별: {% for entity_type in data.entities | map(attribute='type') | unique %}{{ entity_type.title() }} {{ data.entities | selectattr('type', 'equalto', entity_type) | list | length }}개{% if not loop.last %}, {% endif %}{% endfor %}</p>

<div id="network-container">
    <div id="network-graph"></div>
</div>

<script>
// 네트워크 데이터를 JavaScript로 전달
const networkData = {{ generate_network_data() | tojson }};
</script>