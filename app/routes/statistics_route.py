from flask import Blueprint, jsonify, request, render_template
import app.services.statistic_service as service
statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/fatal-attacktype/', methods=['POST'])
def fatal_attacktype():
    try:
        top = request.form.get('top_value')
        if top == '': top = None
        else: top = int(top)
        result = service.get_fatal_attack_types(top_num=top)
        # return jsonify(result), 200
        return render_template('index.html', result=result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@statistics_bp.route('/percentage_of_casualties_by_region/', methods=['GET','POST'])
def percentage_of_casualties_by_region():
    try:
        print(request.form)
        top = request.form.get('top_value')
        if top == '': top = None
        else: top = int(top)
        print(top)
        filter_location_value = request.form.get('filter_value')
        filter_location_type = request.form.get('filter_type')

        result = service.percentage_of_casualties_by_region(filter_location_type, top_num=top)
        # return jsonify(result), 200
        return render_template('index.html', result=result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@statistics_bp.route('/get_top_five_attackers/', methods=['GET','POST'])
def get_top_five_attackers():
    try:
        print(request.form)
        top = request.form.get('top_value')
        if top == '': top = None
        else: top = int(top)
        print(top)
        filter_location_value = request.form.get('filter_value')
        filter_location_type = request.form.get('filter_type')

        result = service.get_top_five_attackers()

        return render_template('index.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


