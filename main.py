from flask import Flask, render_template, request, redirect, url_for
import requests
import re
from os import environ

app = Flask(__name__)

# Food API information
app_id = environ.get('EDUMAM_FOOD_API_ID')
app_key = environ.get('EDUMAM_FOOD_API_KEY')

allergies = ['sodium benzoate', 'benzoate', 'shellfish']

@app.route('/')
def home():
    error_msg = ""
    return render_template('index.html', error_msg=error_msg)

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
                if food_item["foodContentsLabel"].find(allergen) is not -1:
                    food_item["containsAllergens"] = True
                    food_item["allergens"].append(allergen)

        return render_template('food_search.html', response=res, food_items=food_items)


if __name__ == '__main__' and not environ.get('IN_PROD'):
    app.run(debug=True)
