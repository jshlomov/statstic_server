import os
import folium
import toolz as tz
from folium.plugins import HeatMap
from toolz.curried import partial
from app.db.mongo_database import db_url, db_name, collection_name
from app.repository.mongo_repository import AttackRepository
import app.repository.neo4j_repository  as neo4j_repo
from app.utils.graph_util import create_graph_x_y

mongo_repository = AttackRepository(db_url, db_name, collection_name)

def get_fatal_attack_types(top_num):
    result = mongo_repository.get_all_fatal_attacks_by_group(top_num)
    labels = [item["_id"] for item in result]
    values = [item["total_points"] for item in result]
    create_graph_x_y(labels, values, "Attack Types", "Total Points", "Fatal Attacks by Group")

    return result


def percentage_of_casualties_by_region(location_type, top_num):
    result = mongo_repository.percentage_of_casualties_by_region(location_type, top_num)

    m = folium.Map(location=[0, 0], zoom_start=2)
    for entry in result:
        if entry["lat"] is not None and entry["lon"] is not None:
            folium.Marker(
                location=[entry["lat"], entry["lon"]],
                popup=f"Region: {entry['_id']}<br>Avg Casualties: {entry['avgCasualties']:.2f}",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
    map_path = os.path.join('static', 'map.html')
    m.save(map_path)

    return result

def get_top_five_attackers():
    result = mongo_repository.top_five_attackers()
    labels = [item["_id"] for item in result]
    values = [item["sum"] for item in result]
    create_graph_x_y(labels, values,  "Group", "Fatalities", "Fatal Attacks by Attacker")
    return result

def get_geographical_attacks_hotspots(years_ago):
    result = mongo_repository.get_all_attacks_by_years(years_ago)

    m = folium.Map(location=[0, 0], zoom_start=2)
    heat_list = tz.pipe(
        result,
        partial(
            tz.filter,
            lambda x: "location" in x and x["location"].get("lat") is not None and x["location"].get("lon") is not None
        ),
        partial(tz.map, lambda x: [x["location"]['lat'], x["location"]['lon']]),
        list
    )
    HeatMap(heat_list, radius=15, blur=20).add_to(m)
    map_path = os.path.join('static', 'map.html')
    m.save(map_path)

    return result
def get_most_active_groups_per_country(country_name):
    result = mongo_repository.get_most_active_groups_per_country(country_name)

    world_map = folium.Map(location=[0, 0], zoom_start=2)

    for country_data in result:
        country_name = country_data["_id"]
        top_groups = country_data["top_groups"]

        if top_groups:
            top_group = top_groups[0]
            lat = top_group["lat"]
            lon = top_group["lon"]

            popup_content = f"<b>Country:</b> {country_name}<br><b>Top Groups:</b><ul>"
            for group in top_groups:
                popup_content += f"<li>{group['group']}: {group['sum']} incidents</li>"
            popup_content += "</ul>"

            if lat is not None and lon is not None:
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(world_map)

    map_path = os.path.join('static', 'map.html')
    world_map.save(map_path)

    return result