from ast import Call
import random
import sys
import time
from turtle import clear
import requests
from newspaper import Article
from bs4 import BeautifulSoup
import os
import platform
from flask import Flask, render_template, request, redirect
import mysql.connector

def clear_terminal():
    os_name = platform.system().lower()
    if os_name == 'windows':
        os.system('cls')
    elif os_name in ['linux', 'darwin']:
        os.system('clear')
    else:
        print("Operating system not supported for clearing terminal.")
def webscrape(search_query):
    URL = f"https://www.bing.com/search?q={search_query.replace(' ', '+')}"

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
    ]
    headers = {
        "User-Agent": random.choice(user_agents)
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        exit()

    soup = BeautifulSoup(response.text, "lxml")

    results = soup.find_all("li", class_="b_algo")
    i = 0
    links = []
    for i, result in enumerate(results[:10]):
        title_tag = result.find("h2")
        if title_tag and title_tag.a:
            title = title_tag.text.strip()
            link = title_tag.a["href"]
            links.append({"title": title, "link": link})
    return links

def webscrapeURL(url):
    article = Article(url)
    article.download()
    article.parse()
    formatted_content = article.text.replace('\n\n', '</p><p>').replace('\n', '<br>')
    formatted_content = f'<p>{formatted_content}</p>'
    return article.title, formatted_content
        
class Recipe:
    title = ""
    prepTime = ""
    cookTime = ""
    servings = ""
    course = ""
    calories = ""
    ingredients = []
    directions = []
    notes = []
    
    def display(self):
        print(self.title)
        print("Prep time: " + self.prepTime)
        print("Cook time: " + self.cookTime)
        print("Servings: " + self.servings)
        print("Course: " + self.course)
        print("Calories: " + self.calories + " kcal")
        print("Ingredients:")
        for i in range(len(self.ingredients)):
            print("- " + self.ingredients[i])
        
        print("Instructions:")
        for i in range(len(self.directions)):
            print(str(i+1) + ". " + self.directions[i])
            
        print("Notes:")
        for i in range(len(self.notes)):
            print("* " + self.notes[i])
        return None
    
    def makeFile(self):
        fileName = self.title + ".txt"
        f = open(fileName, "w")
        titleLine = "Tt " + self.title + "\n"
        prepLine = "Pp " + self.prepTime + "\n"
        cookLine = "Ct " + self.cookTime + "\n"
        servLine = "Sv " + self.servings + "\n"
        courseLine = "Cs " + self.course + "\n"
        calLine = "Kc " + self.calories + "\n"
        f.write(titleLine)
        f.write(prepLine)
        f.write(cookLine)
        f.write(servLine)
        f.write(courseLine)
        f.write(calLine)
        
        for ingred in self.ingredients:
            f.write("Ii " + ingred + "\n")
            
        for instruct in self.directions:
            f.write("Dd " + instruct + "\n")
            
        for note in self.notes:
            f.write("Nn " + note + "\n")
            
        f.close()
        return None
        
            
def newRecipe():
    name = input("Enter recipe name: ")
    prep = input("Enter prep time: ")
    cook = input("Enter cook time: ")
    servs = input("Enter recipe yield: ")
    meal = input("Enter course: ")
    cals = input("Enter calories per serving: ")
        
    ingreds = []
    ingredient = ""
    while ingredient != "q":
        ingredient = input("Enter ingredient (Press q to quit): ")
        if ingredient != "q":
            ingreds.append(ingredient)
    instructs = []
    instruct = ""
    while instruct != "q":
        instruct = input("Enter instruction (Press q to quit): ")
        if instruct != "q":
            instructs.append(instruct)
    addlNotes = []
    note = ""
    while note != "q":
        note = input("Enter note (Press q to quit): ")
        if note != "q":
            addlNotes.append(note)
            
    recipe = Recipe()
    recipe.title = name
    recipe.prepTime = prep
    recipe.cookTime = cook
    recipe.servings = servs
    recipe.course = meal
    recipe.calories = cals
    recipe.ingredients = ingreds
    recipe.directions = instructs
    recipe.notes = addlNotes
    return recipe

def recipeFromFile(file):
    name = ""
    prep = ""
    cook = ""
    serv = ""
    meal = ""
    cals = ""
    ingreds = []
    dirs = []
    addlNotes = []
    try:
        f = open(file, 'r')
        if f:
            # file opened
            for x in f:
                if x[0:2] == "Tt":
                   title = x[3:]
                elif x[0:2] == "Pp":
                    prep = x[3:]
                elif x[0:2] == "Ct":
                    cook = x[3:]
                elif x[0:2] == "Sv":
                    serv = x[3:]
                elif x[0:2] == "Kc":
                    cals = x[3:]
                elif x[0:2] == "Ii":
                    ingreds.append(x[3:])
                elif x[0:2] == "Dd":
                    dirs.append(x[3:])
                elif x[0:2] == "Nn":
                    addlNotes.append(x[3:])
                else:
                    continue
        else:
            print(f"File '{file}' could not be opened.")
    except IOError as e:
        print(f"An error occurred: {e}")
    if name == "":
        print("File parsing failed")
        return None
    recipe = Recipe()
    recipe.title = name
    recipe.prepTime = prep
    recipe.cookTime = cook
    recipe.servings = serv
    recipe.course = meal
    recipe.calories = cals
    recipe.ingredients = ingreds
    recipe.directions = dirs
    recipe.notes = addlNotes
    return recipe

database = mysql.connector.connect(host="localhost", user="kiara", password="Prince$1don")
mycursor = database.cursor()
try:
    database = mysql.connector.connect(host="localhost", user="kiara", password="Prince$1don", database="recipebook")
except:
    mycursor.execute("CREATE DATABASE recipebook")
    database = mysql.connector.connect(host="localhost", user="kiara", password="Prince$1don", database="recipebook")


recipes = []
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        prep = request.form["prep"]
        cook = request.form["cook"]
        serv = request.form["serv"]
        meal = request.form["meal"]
        cals = request.form["cals"]
    
        ingreds = request.form["ingredients"]
        ingredients = ingreds.splitlines()

        dirs = request.form["instructions"]
        directions = dirs.splitlines()
    
        addlNotes = request.form["notes"]
        notes = addlNotes.splitlines()
    
        recipe = Recipe()
        recipe.title = name
        recipe.prepTime = prep
        recipe.cookTime = cook
        recipe.servings = serv
        recipe.course = meal
        recipe.calories = cals
        recipe.ingredients = ingredients
        recipe.directions = directions
        recipe.notes = notes
    
        # make file and add to database
        recipe.makeFile()
        recipes.append(recipe)
        return render_template("index.html")
    else:
        return render_template("newRecipe.html")

@app.route('/search')
def search():
    return render_template('searchRecipes.html')

@app.route('/noresults')
def noResults():
    return render_template('noresults.html')

@app.route('/results')
def showResults():
    return render_template("results.html")

@app.route("/discover", methods =["GET", "POST"])
def discover():
    if request.method == "POST":
        query = request.form["query"]
        results = webscrape(query)
        if not results:
            return render_template("noresults.html")
        return render_template("results.html", results=results)
    else:
        return render_template("discoverRecipes.html")
    
@app.route("/article", methods=["GET", "POST"])
def showRecipe():
    if request.method == "POST":
        websiteURL = request.form["url"]
        if not websiteURL:
            return render_template("noresults.html")
        title, content = webscrapeURL(websiteURL)
        return render_template("article.html", title=title, content=content)
    else:
        return render_template("discoverRecipes.html")

if __name__ == '__main__':
    app.run(debug=True)
    


    
    




