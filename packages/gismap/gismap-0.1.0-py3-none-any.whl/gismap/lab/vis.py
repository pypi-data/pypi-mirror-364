from string import Template
import uuid
import json


vis_template = Template("""
<div id="${container_id}"></div>
<div id="${modal_id}" class="modal">
  <div class="modal-content">
    <span class="close" id="${modal_close_id}">&times;</span>
    <div id="${modal_body_id}"></div>
  </div>
</div>
<style>
  /* Styles adaptatifs pour dark/light */
  #${container_id} {
    width: 1200px; height: 800px; border: 1px solid #444;
    background: #181818;
  }
  .modal {
    display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%;
    overflow: auto; background-color: rgba(10,10,10,0.85);
  }
  .modal-content {
    background-color: #23272e; color: #f0f0f0;
    margin: 10% auto; padding: 24px; border: 1px solid #888;
    width: 50%; border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0,0,0,.6);
  }
  .close {
    color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer;
  }
  .close:hover, .close:focus { color: #fff; text-decoration: none; cursor: pointer; }
  @media (prefers-color-scheme: light) {
    #${container_id} { background: #fff; border: 1px solid #ccc; }
    .modal { background-color: rgba(220,220,220,0.85); }
    .modal-content { background: #fff; color: #222; border: 1px solid #888; }
    .close { color: #222; }
    .close:hover, .close:focus { color: #555; }
  }
</style>
<script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<script type="text/javascript">
(function() {
  // Détection du thème
  function getTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function getVisOptions(theme) {
    if (theme === 'dark') {
      return {
        nodes: {
          shape: 'circle', size: 20,
          font: { size: 16, color: '#f0f0f0' },
          color: {
            background: '#222e3c',
            border: '#5d90f5',
            highlight: { background: '#2f3d4d', border: '#f5a25d' }
          },
          borderWidth: 2
        },
        edges: {
          width: 2,
          color: { color: '#888', highlight: '#f5a25d' },
          smooth: { type: 'continuous' }
        },
        interaction: { hover: true }
      };
    } else {
      return {
        nodes: {
          shape: 'circle', size: 20,
          font: { size: 16, color: '#222' },
          color: {
            background: '#e3eaff',
            border: '#3d6cf7',
            highlight: { background: '#fffbe6', border: '#f5a25d' }
          },
          borderWidth: 2
        },
        edges: {
          width: 2,
          color: { color: '#848484', highlight: '#f5a25d' },
          smooth: { type: 'continuous' }
        },
        interaction: { hover: true }
      };
    }
  }
  const nodes = new vis.DataSet(${nodes_json});
  const edges = new vis.DataSet(${edges_json});
  const container = document.getElementById('${container_id}');
  let network = null;
  function renderNetwork() {
    const theme = getTheme();
    const options = getVisOptions(theme);
    network = new vis.Network(container, { nodes: nodes, edges: edges }, options);
    // Tooltip survol
    network.on("hoverNode", function(params) {
      const node = nodes.get(params.node);
      network.body.container.title = node.hover || '';
    });
    network.on("blurNode", function(params) {
      network.body.container.title = '';
    });
    network.on("hoverEdge", function(params) {
      const edge = edges.get(params.edge);
      network.body.container.title = edge.hover || '';
    });
    network.on("blurEdge", function(params) {
      network.body.container.title = '';
    });
    // Modal overlay
    const modal = document.getElementById('${modal_id}');
    const modalBody = document.getElementById('${modal_body_id}');
    const modalClose = document.getElementById('${modal_close_id}');
    network.on("click", function(params) {
      if (params.nodes.length === 1) {
        const node = nodes.get(params.nodes[0]);
        modalBody.innerHTML = node.overlay || '';
        modal.style.display = "block";
      } else if (params.edges.length === 1) {
        const edge = edges.get(params.edges[0]);
        modalBody.innerHTML = edge.overlay || '';
        modal.style.display = "block";
      } else {
        modal.style.display = "none";
      }
    });
    modalClose.onclick = function() { modal.style.display = "none"; };
    window.onclick = function(event) {
      if (event.target == modal) { modal.style.display = "none"; }
    };
  }
  renderNetwork();
  // Adapter dynamiquement si le thème change
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
    renderNetwork();
  });
})();
</script>
""")


def generate_html(nodes, edges):
    """
    Parameters
    ----------
    nodes: :class:`list`
    edges: :class:`list`

    Returns
    -------
    :class:`str`
    """
    uid = str(uuid.uuid4())[:8]  # identifiant unique pour éviter les collisions
    container_id = f"mynetwork_{uid}"
    modal_id = f"modal_{uid}"
    modal_body_id = f"modal_body_{uid}"
    modal_close_id = f"modal_close_{uid}"
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    dico = {
        "container_id": container_id,
        "modal_id": modal_id,
        "modal_body_id": modal_body_id,
        "modal_close_id": modal_close_id,
        "nodes_json": nodes_json,
        "edges_json": edges_json,
    }
    return vis_template.substitute(dico)  # html_template
