import flask
import json
from flask import render_template, request
from flask import jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import requests
import os

app = flask.Flask(__name__, template_folder='Templates')

#code for connection
app.config['MYSQL_HOST'] = 'localhost'#hostname
app.config['MYSQL_USER'] = 'root'#username
app.config['MYSQL_PASSWORD'] = ''#password
app.config['MYSQL_DB'] = 'travelguide'#database name

df = pd.read_csv("Data/mahat.csv")
df1 = pd.read_csv("Data/mahat.csv")
df = df.dropna(subset=['Best_time_to_visit', 'Type', 'DistanceFromCity', 'Place'])
label_encoders = {}
for col in ['Best_time_to_visit', 'Type', 'DistanceFromCity', 'Place', 'City']:
    label_encoders[col] = LabelEncoder()
    df[col] = label_encoders[col].fit_transform(df[col])
X = df[['City', 'Type']]
y = df['Place']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)



df1['Ratings_x'] = df1['Ratings_x'].astype(str)
df1['DistanceFromCity'] = df1['DistanceFromCity'].astype(str)
df1['features'] = df1['City'] + ' ' + df1['Ratings_x'] + ' ' + df1['DistanceFromCity']
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df1['features'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

mysql = MySQL(app)
@app.route('/')


@app.route('/main', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
    
@app.route('/predictionpage', methods=['GET', 'POST'])
def predictionpage():
    if flask.request.method == 'GET':
        return(flask.render_template('predictionpage.html'))

def recommendtour(place, cosine_sim=cosine_sim):
    places = df1[df1['Place'].str.contains(place, case=False)]
    
    if places.empty:
        print(f"Error: Place '{place}' not found in the dataset.")
        return
    
    idx = places.index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]
    place_indices = [i[0] for i in sim_scores]
    return df1['Place'].iloc[place_indices]

@app.route('/travelpage', methods=['GET', 'POST'])
def travelpage():
    if flask.request.method == 'GET':
        return(flask.render_template('travelpage.html'))
    
@app.route('/about', methods=['GET', 'POST'])
def about():
    if flask.request.method == 'GET':
        return(flask.render_template('about.html'))
    

@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    if flask.request.method == 'GET':
        return(flask.render_template('blogs.html'))
    
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if flask.request.method == 'GET':
        return(flask.render_template('contacts.html'))
    
@app.route('/routemap', methods=['GET', 'POST'])
def routemap():
    if flask.request.method == 'GET':
        return(flask.render_template('routemap.html'))
    
@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if flask.request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        age = '0'
        city = '0'
        state = '0'
        nationality = '0'
        password = request.form['password']
        insert_query = 'INSERT INTO user_detail (username, email, phone, age, city, state, nationality, password) VALUES ("'+username+'", "'+email+'", "'+phone+'", '+age+', "'+city+'", "'+state+'", "'+nationality+'", "'+password+'")'
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(insert_query)
        mysql.connect.commit()
        msg = '1'
        
        return msg
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        phone           = request.form['phone']
        password        = request.form['password']
        
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        qry = 'SELECT * FROM user_detail WHERE phone="'+phone+'" AND password="'+password+'"'
        result = cursor.execute(qry)
        result = cursor.fetchone();
        if result:
            msg = "1"
        else:
           msg = "0"
    return msg

def download_image(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'Downloaded {filename}')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}:', e)

def download_images(query, download_path, max_images=10):
    api_key = 'ZuRric8BOJ8AAptcBDkHoRh67qJ6XA6bGcTSteBh76vTBv1d3Xo1r42O'
    url = f'https://api.pexels.com/v1/search?query={query}&per_page={max_images}'

    headers = {'Authorization': api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for index, photo in enumerate(data['photos']):
            if index >= max_images:
                break
            image_url = photo['src']['medium']
            image_filename = os.path.join(download_path, f'images_{index}.jpg')
            download_image(image_url, image_filename)
    except requests.exceptions.RequestException as e:
        print('Error fetching images:', e)
        raise
        
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if flask.request.method == 'GET':
        
        traveltype      = request.args['traveltype']
        distance        = request.args['distance']
        inpcity        = request.args['city']
        
        user_input = {'City':inpcity, 'Type': traveltype}
        user_input_encoded = {col: label_encoders[col].transform([user_input[col]])[0] if user_input[col] in label_encoders[col].classes_ else -1 for col in user_input}
        predicted_place_encoded = clf.predict([list(user_input_encoded.values())])[0]
        predicted_place = label_encoders['Place'].inverse_transform([predicted_place_encoded])[0]
        print("Recommended place to visit:", predicted_place)
        
        predicted_row = df1[df1['Place'] == predicted_place]
        print(predicted_row)
        
        recommended_city = predicted_row['City'].iloc[0]
        recommended_place_desc = predicted_row['Place_desc'].iloc[0]
        recommended_place_ratings = predicted_row['Ratings_y'].iloc[0]
        
        # Assuming recommendtour() returns a Series object named recommendations_series
        recommendations_series = recommendtour(predicted_place)
        
        # Convert Series to dictionary
        recommendations_dict = recommendations_series.to_dict()
        
        # Serialize the dictionary to JSON
        recommendations_json = json.dumps(recommendations_dict)
        
        if inpcity == recommended_city:
            placeavl = 1
        else:
            placeavl = 0
            
        query = predicted_place  
        download_path = 'static/predimages'  
        max_images = 6  
        download_images(query, download_path, max_images)      
       
        # Create the returndata dictionary
        preddata = {
            "type":traveltype,
            "predicted_place": predicted_place,
            "recommended_city": recommended_city,
            "recommended_place_desc": recommended_place_desc,
            "recommended_place_ratings": recommended_place_ratings,
            "recommendations": recommendations_dict,
            "placeavl":placeavl
        }
        
        # Return the returndata as JSON
    return render_template('predictionpage.html', preddata=preddata)

@app.route('/searchdata', methods=['GET', 'POST'])
def searchdata():
    if flask.request.method == 'GET':
        predicted_place      = request.args['searchdata']
        
        predicted_row = df1[df1['Place'].str.contains(predicted_place, case=False)]
        print(predicted_row)
        # Retrieve the corresponding City and Place_desc
        recommended_city = predicted_row['City'].iloc[0]
        recommended_place_desc = predicted_row['Place_desc'].iloc[0]
        recommended_place_ratings = predicted_row['Ratings_y'].iloc[0]
        
        # Assuming recommendtour() returns a Series object named recommendations_series
        recommendations_series = recommendtour(predicted_place)
        
        # Convert Series to dictionary
        recommendations_dict = recommendations_series.to_dict()
        
        # Serialize the dictionary to JSON
        recommendations_json = json.dumps(recommendations_dict)
        
        
        query = predicted_place  
        download_path = 'static/predimages'  
        max_images = 6  
        download_images(query, download_path, max_images)
        
        # Create the returndata dictionary
        preddata = {

            "predicted_place": predicted_place,
            "recommended_city": recommended_city,
            "recommended_place_desc": recommended_place_desc,
            "recommended_place_ratings": recommended_place_ratings,
            "recommendations": recommendations_dict,

        }
        
    # Return the returndata as JSON
    return render_template('predictionpage.html', preddata=preddata)


    
if __name__ == '__main__':
    app.run(debug=False)