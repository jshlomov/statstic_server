import base64
import io
import os

import folium
import pandas as pd
from matplotlib import pyplot as plt
from app.db.neo4j_database import driver
from app.utils.graph_util import put_graph_in_html


def get_grouped_data(filter_by="country"):
    query = f"""
    MATCH (g:Group)-[:CONDUCTED]->(a:Attack)-[:OCCURRED_AT]->(l:Location)
    WITH l.{filter_by} AS location_group, 
         COLLECT(DISTINCT g.name) AS groups, 
         AVG(l.latitude) AS lat, 
         AVG(l.longitude) AS lon
    RETURN location_group, groups, lat, lon, SIZE(groups) AS group_count
    ORDER BY group_count DESC
    """
    with driver.session() as session:
        result = session.run(query)
        return result.data()

def create_shared_targets_map(filter_by="country"):
    data = get_grouped_data(filter_by=filter_by)
    m = folium.Map(location=[0, 0], zoom_start=2)

    for record in data:
        lat = record.get('lat')
        lon = record.get('lon')
        location_group = record.get('location_group', 'Unknown Location')
        group_count = record.get('group_count', 0)
        groups = record.get('groups', [])

        if lat is not None and lon is not None:
            popup_html = f"""
                <div style="max-height: 150px; overflow-y: auto;">
                    <strong>Location:</strong> {location_group}<br>
                    <strong>Group Count:</strong> {group_count}<br>
                    <strong>Groups:</strong><br>
                    {'<br>'.join(groups)}
                </div>
            """
            popup = folium.Popup(popup_html, max_width=300)

            folium.Marker(
                location=[lat, lon],
                popup=popup,
                tooltip=f"{location_group} - {group_count} groups"
            ).add_to(m)

    map_path = os.path.join('static', 'map.html')
    m.save(map_path)


def plot_group_activity(filter_by="country"):
    query = f"""
    MATCH (g:Group)-[:CONDUCTED]->(a:Attack)-[:OCCURRED_AT]->(l:Location)
    WITH l.{filter_by} AS location_group, g.name AS group, a.date AS attack_date
    RETURN location_group, group, date(attack_date).year AS year, COUNT(*) AS attack_count
    ORDER BY year
    """
    with driver.session() as session:
        result = session.run(query)
        data = pd.DataFrame(result.data())

    if data.empty:
        print("No data returned from the query.")
        return

    grouped = data.groupby(["location_group", "year"])
    for (location, year), group_data in grouped:
        plt.plot(
            group_data["year"],
            group_data["attack_count"],
            label=f"{location}"
        )
    plt.xlabel("Year")
    plt.ylabel("Attack Count")
    title = "Group Activity Over Time by Location"
    plt.title(title)
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()

    put_graph_in_html(title, plot_data)

#1
def create_attack_strategies_map(filter_by="region"):
    query = f"""
    MATCH (g:Group)-[:CONDUCTED]->(a:Attack)-[:USED]->(at:AttackType),
          (a)-[:OCCURRED_AT]->(l:Location)
    WITH l.{filter_by} AS location_group, 
         COLLECT(DISTINCT at.name) AS attack_types, 
         COLLECT(DISTINCT g.name) AS groups, 
         AVG(l.latitude) AS lat, 
         AVG(l.longitude) AS lon
    WITH location_group, attack_types, groups, lat, lon, SIZE(attack_types) AS attack_types_count
    RETURN location_group, attack_types, groups, lat, lon, attack_types_count
    ORDER BY attack_types_count DESC
    """
    with driver.session() as session:
        data = session.run(query).data()

    m = folium.Map(location=[0, 0], zoom_start=2)

    for record in data:
        if record["lat"] is not None or record["lon"] is not None:
            popup_content = f"""
            <div style="width: 200px; height: 150px; overflow-y: auto;">
                Location: {record['location_group']}<br>
                Attack Types: {', '.join(record['attack_types'][:5])}<br>
                Groups: {', '.join(record['groups'][:5])}<br>
                attack_types Count: {record['attack_types_count']}
            </div>
            """
            folium.Marker(
                location=[record["lat"], record["lon"]],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"{record['location_group']} - {record['attack_types_count']} attack_types"
            ).add_to(m)

    map_path = os.path.join('static', 'map.html')
    m.save(map_path)


create_attack_strategies_map()


def create_high_activity_map(filter_by="region"):
    data = get_grouped_data(filter_by=filter_by)
    m = folium.Map(location=[0, 0], zoom_start=2)

    for record in data:
        location_group = record.get('location_group', 'Unknown Location')
        group_count = record.get('group_count', 0)
        groups = record.get('groups', [])
        popup_html = f"""
            <div style="max-height: 150px; overflow-y: auto;">
                <strong>Location:</strong> {location_group}<br>
                <strong>Group Count:</strong> {group_count}<br>
                <strong>Groups:</strong><br>
                {'<br>'.join(groups)}
            </div>
        """
        popup = folium.Popup(popup_html, max_width=300)
        folium.Marker(
            location=[record["lat"], record["lon"]],
            popup=popup,
            tooltip=f"{record['location_group']} - {record['group_count']} unique groups"
        ).add_to(m)

    map_path = os.path.join('static', 'map.html')
    m.save(map_path)
