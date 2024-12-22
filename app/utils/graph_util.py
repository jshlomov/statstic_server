import base64
import io
import os

from matplotlib import pyplot as plt


def create_graph_x_y(labels, values, xlabel, ylabel, title):
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='skyblue')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body>
        <div>
            <img src="data:image/png;base64,{plot_data}" alt="Fatal Attacks by Group Plot">
        </div>
    </body>
    </html>
    """

    with open(os.path.join('static', 'map.html'), 'w') as file:
        file.write(html_content)