from flask import Flask, render_template, request, session, redirect, url_for
import requests
import re
from os import environ
from dotenv import load_dotenv

# firebase info
from db.db import firebase
auth = firebase.auth()

app = Flask(__name__)

# load environment vars
load_dotenv()

# Food API information
app_id = environ.get('EDUMAM_FOOD_API_ID')
app_key = environ.get('EDUMAM_FOOD_API_KEY')

allergies = ['sodium benzoate', 'benzoate', 'shellfish']

@app.route('/')
def home():
    error_msg = ""

    if 'userToken' not in session:
        redirect(url_for('login_page'))

    return render_template('index.html', error_msg=error_msg)


@app.route('/login_page')
def login_page():
    error_msg = ""

    if 'userToken' in session:
        return redirect(url_for('home'))

    return render_template('login.html', error_msg=error_msg)

@app.route('/login', methods=['POST'])
def login():
    try:
        user_id = session['userToken']
    except KeyError:
        user_id = False

    if user_id:
        return redirect(url_for('home'))
    else:
        if request.method == 'POST':
            error_msg = ''
            email = request.form['email-login']
            password = request.form['password-login']

            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user = auth.refresh(user['refreshToken'])
                session['userToken'] = user['idToken']
                session['username'] = auth.get_account_info(session['userToken'])['users'][0]['email']
                return redirect(url_for('home'))
            except:
                error_msg = 'Incorrect email or password'
                return render_template('login.html', error_msg=error_msg)


@app.route('/logout')
def logout():
    auth.current_user = None
    session.clear()
    return redirect(url_for('home'))

@app.route('/food_search', methods=['POST'])
def food_search():
    if request.method == 'POST':
        food_search_query = request.form["food"]

        if len(food_search_query) < 1:
            error_msg = "Search field cannot be empty."
            return render_template('index.html', error_msg=error_msg)

        foods_with_ingredient_label = ["generic meals", "packaged foods"]
        food_items = []

        # get rid of multiple white spaces and make them only 1 whitespace
        food_search_query = re.sub(" +", " ", food_search_query)

        # replace white space with '%20'
        food_search_query = food_search_query.replace(" ", "%20")

        api_request = f'https://api.edamam.com/api/food-database/parser?ingr={food_search_query}&app_id={app_id}&app_key={app_key}'

        res = requests.get(api_request).json()

        # Error out if user entered invalid food item
        error = res.get('error')

        if error:
            error_msg = "Please enter a valid food item."
            return render_template('index.html', error_msg=error_msg)

        for food in res["hints"]:
            id = food["food"]["foodId"]
            label = food["food"]["label"]
            category = food["food"]["category"].lower()

            if category in foods_with_ingredient_label:
                food_items.append({
                    "id": id,
                    "label": label,
                    "category": category,
                    "foodContentsLabel": food["food"]["foodContentsLabel"].lower(),
                    "containsAllergens": False,
                    "allergens": [],
                })

        for allergen in allergies:
            for food_item in food_items:
                # If an allergen is found in the food ingredients
                if food_item["foodContentsLabel"].find(allergen) != -1:
                    food_item["containsAllergens"] = True
                    food_item["allergens"].append(allergen)

        return render_template('food_search.html', response=res, food_items=food_items)


if __name__ == '__main__' and environ.get('LOCAL_DEV'):
    app.secret_key = 'yg732g72362g8ihoqwu'
    app.run(debug=True)
