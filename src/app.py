from flask import Flask, render_template, jsonify, request, redirect, url_for
import database
ph = database.get_placeholder()

app = Flask(__name__)

# Routes

@app.route("/")
def dashboard():
    conn = database.get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT * FROM game_risk 
        WHERE id IN (
            SELECT MAX(id) 
            FROM game_risk 
            GROUP BY team
        )
        ORDER BY risk_score DESC
    '''

    cursor.execute(query)
    games = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", games=games)

# Handle the Search Form Submission
@app.route('/search', methods=['POST'])
def search_team():
    query = request.form.get('team_query')
    # Redirect the user to the specific team URL
    return redirect(url_for('show_team', team_name=query))

# Team Details Page
@app.route('/team/<team_name>')
def show_team(team_name):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Use SQL LIKE to find matches
    # The % symbols allow partial matching
    query = f'''SELECT * FROM game_risk WHERE team LIKE {ph}'''
    cursor.execute(query, ('%' + team_name + '%',))
    game = cursor.fetchone()
    conn.close()

    return render_template("team.html", game=game, search_term=team_name)

@app.route('/api/risk')
def api_risk():
    conn = database.get_db_connection()
    cursor = conn.cursor()
    # CORRECT (Postgres Safe)
    query = '''
        SELECT * FROM game_risk 
        WHERE id IN (
            SELECT MAX(id) FROM game_risk GROUP BY team
        )
        ORDER BY risk_score DESC
    '''
    cursor.execute(query)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)