import networkx as nx
from pyvis.network import Network
from utils.github_api import search_issues

def generate_graph():
    """Genera un grafo interactivo usando pyvis"""
    issues = search_issues()
    G = nx.DiGraph()
    
    # Añadir nodos
    for issue in issues:
        G.add_node(issue["id"], 
                 label=issue["title"],
                 group=issue["type"],
                 title=issue["content"])
    
    # Añadir conexiones (ejemplo básico)
    for i in range(len(issues)-1):
        G.add_edge(issues[i]["id"], issues[i+1]["id"])
    
    # Configurar visualización
    net = Network(height="750px", width="100%", notebook=False)
    net.from_nx(G)
    
    # Guardar en docs/ para GitHub Pages
    net.save_graph("docs/index.html")