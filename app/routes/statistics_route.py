from flask import Blueprint, jsonify, request, render_template
import app.services.statistic_mongo_service as service
import app.repository.neo4j_repository as neo4j_repo
statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/fatal-attacktype/', methods=['POST'])
def fatal_attacktype():
    try:
        top = request.form.get('top_value')
        if top == '': top = None
        else: top = int(top)
        result = service.get_fatal_attack_types(top_num=top)
        return render_template('index.html', result=result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@statistics_bp.route('/percentage_of_casualties_by_region/', methods=['GET','POST'])
def percentage_of_casualties_by_region():
    try:
        top = request.form.get('top_value')
        if top == '': top = None
        else: top = int(top)
        filter_location_type = request.form.get('filter_type')
        result = service.percentage_of_casualties_by_region(filter_location_type, top_num=top)
        return render_template('index.html', result=result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_top_five_attackers/', methods=['GET','POST'])
def get_top_five_attackers():
    try:
        top = request.form.get('top_value')
        if top == '': top = None
        else: top = int(top)
        result = service.get_top_five_attackers()
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_geographical_attacks_hotspots/', methods=['GET','POST'])
def get_geographical_attacks_hotspots():
    try:
        years_ago = request.form.get('years_ago')
        if years_ago == '' or years_ago is None: years_ago = None
        else: years_ago = int(years_ago)
        result = service.get_geographical_attacks_hotspots(years_ago)
        return render_template('index.html')
        # return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_most_active_groups_per_country/', methods=['GET','POST'])
def get_most_active_groups_per_country():
    try:
        filter_value = request.form.get('filter_value')
        if filter_value == '' or filter_value is None:
            filter_value = None
        result = service.get_most_active_groups_per_country(filter_value)
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_shared_targets_by_location/', methods=['POST'])
def get_shared_targets_by_location():
    try:
        filter_location_type = request.form.get('filter_type')
        result = neo4j_repo.create_shared_targets_map(filter_location_type)
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/track_group_activity_over_time/', methods=['POST'])
def track_group_activity_over_time():
    try:
        filter_location_type = request.form.get('filter_type')
        result = neo4j_repo.plot_group_activity(filter_location_type)
        # return jsonify(result), 200
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_attack_strategies_by_location/', methods=['POST'])
def get_attack_strategies_by_location():
    try:
        filter_location_type = request.form.get('filter_type')
        result = neo4j_repo.create_attack_strategies_map(filter_location_type)
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_high_group_activity_locations/', methods=['POST'])
def get_high_group_activity_locations():
    try:
        filter_location_type = request.form.get('filter_type')
        result = neo4j_repo.create_high_activity_map(filter_location_type)
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_groups_with_shared_targets_by_year/', methods=['POST'])
def get_groups_with_shared_targets_by_year():
    try:
        filter_location_type = request.form.get('filter_type')
        result = neo4j_repo.plot_common_targets_graph(filter_location_type)
        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
