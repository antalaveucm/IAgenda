import click
import os
import yaml
from utils.github_api import create_issue, search_issues
from utils.graph_generator import generate_graph
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
from datetime import datetime

# Configuración de modelo de IA
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

@click.group()
def cli():
    """CLI para gestionar la agenda inteligente"""
    pass

@cli.command()
@click.argument('title')
@click.option('--content', required=True, help='Contenido detallado')
@click.option('--type', type=click.Choice(['idea', 'proyecto', 'entregable']), default='idea')
@click.option('--tags', help='Etiquetas separadas por comas')
def add(title, content, type, tags):
    """Añade un nuevo elemento a la agenda"""
    tags_list = tags.split(',') if tags else []
    
    # Crear issue en GitHub
    issue_data = {
        "title": title,
        "content": content,
        "type": type,
        "tags": tags_list
    }
    response = create_issue(issue_data)
    click.echo(f"✅ Issue creado: {response['html_url']}")

@cli.command()
@click.argument('query')
def search(query):
    """Busca elementos relacionados usando IA"""
    issues = search_issues()
    query_embedding = model.encode(query)
    
    # Cargar embeddings existentes
    if os.path.exists('embeddings/embeddings.pkl'):
        with open('embeddings/embeddings.pkl', 'rb') as f:
            embeddings = pickle.load(f)
    else:
        embeddings = {}
    
    # Calcular similitudes
    results = []
    for issue in issues:
        if issue['id'] not in embeddings:
            embeddings[issue['id']] = model.encode(issue['content'])
        similarity = np.dot(query_embedding, embeddings[issue['id']])
        results.append((similarity, issue))
    
    # Guardar embeddings
    with open('embeddings/embeddings.pkl', 'wb') as f:
        pickle.dump(embeddings, f)
    
    # Mostrar top 3
    for score, item in sorted(results, reverse=True)[:3]:
        click.echo(f"📌 {item['title']} (Similitud: {score:.2f})")
        click.echo(f"   {item['content']}\n")

@cli.command()
def visualize():
    """Genera la visualización del grafo"""
    generate_graph()
    click.echo("🌐 Grafo generado en docs/index.html")

@cli.command()
def resumen():
    """Muestra un resumen de tareas pendientes"""
    issues = search_issues()
    
    if not issues:
        click.secho("\n✅ ¡No hay tareas pendientes!", fg="green")
        return

    # Agrupar por tipo
    categorias = {
        "idea": [],
        "proyecto": [],
        "entregable": []
    }
    
    for issue in issues:
        categorias[issue["type"]].append(issue)
    
    # Mostrar resumen
    click.secho("\n📊 RESUMEN DE TAREAS PENDIENTES", bold=True)
    click.secho("==================================\n", fg="blue")
    
    for tipo, items in categorias.items():
        if not items:
            continue
            
        color = {
            "idea": "cyan",
            "proyecto": "yellow",
            "entregable": "magenta"
        }[tipo]
        
        click.secho(f"  {tipo.upper()} ({len(items)})", fg=color, bold=True)
        
        for idx, item in enumerate(items, 1):
            fecha = datetime.strptime(item["created_at"], "%Y-%m-%d").strftime("%d/%m/%Y")
            click.echo(f"    {idx}. {item['title']} ({fecha})")
            click.secho(f"       » {item['content']}", fg="white")
        
        click.echo()

if __name__ == '__main__':
    cli()