from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,RadioField,IntegerField
from wtforms.validators import DataRequired, Email, EqualTo,NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
import razorpay
import razorpay.errors
from datetime import datetime
import random
from googleapiclient.discovery import build
from google.oauth2 import service_account


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

key = "6Kto5LxwDqchjAc0"
uri = "mongodb+srv://abhirajbanerjee02:6Kto5LxwDqchjAc0@cluster-chronotunes.pkxxz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-ChronoTunes"

RAZORPAY_KEY_ID = "rzp_test_iXumXBu7UMOLEf"
RAZORPAY_KEY_SECRET = "DbnMUMaSxdlLkTNCZ0ruZb7R"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))
# Create a new client and connect to the server
mongoClient = MongoClient(uri, server_api=ServerApi('1'))
database = mongoClient['users']
collection = database['chronoTunes']
users = collection.find()
contact = mongoClient['contact']
customer = contact['chronoTunes']
song_db=mongoClient['songs']
questions = [
    "I felt miserable or unhappy.",
    "I didn’t enjoy anything at all.",
    "I felt so tired I just sat around and did nothing.",
    "I was very restless.",
    "I felt I was no good anymore.",
    "I cried a lot.",
    "I found it hard to think properly or concentrate.",
    "I hated myself.",
    "I was a bad person.",
    "I felt lonely.",
    "I thought nobody really loved me.",
    "I thought I could never be as good as other people.",
    "I did everything wrong."
]
classical_link = "https://drive.google.com/drive/folders/11gCZK8C4lWcAX77tCuYRbi5jC8cbMhnW"
bengali_link = "https://drive.google.com/drive/folders/1gifXb2IjlJoIYs9mCZW1-0XITQ6qr1J4"
hindi_retro_link = "https://drive.google.com/drive/folders/1VAV9M8cYo9ZMAkBoMZrJpe4Kupx8Jst3"
hindi_modern_link="https://drive.google.com/drive/folders/1Ai-dpQ6s2_E_ShWifMHLoOvypZoBzymR"

info = {'Bilawal': {"benefits":['Gives healthy mind and body', 'Control sound and sonorous sleep'],
                  "time":'12-24'},
          'Kalyan':{"benefits": ['Reduce mental tension', 'Relief from headache'],
                    "time":'18-21'},
          'Khamaj': {"benefits":['Control sound and sonorous sleep', 'Reduce mental tension'],
                "time":'21-24'},
          'Kafi': {"benefits":['Brings joy', 'Mitigate insomina', 'Reduces anxiety', 'Reduces hypertension'],
          "time":'21-24'},
          'Asavari': ['Brings Creativity and Happiness', 'builds confidence'],
          'Todi': {"benefits":['Reduces anxiety', 'Brings serenity'],
                "time":'9-12'},
          'Poorvi': {"benefits":['Reduce mental tension', 'Mitigate insomina'],
          "time":'15-21'},
          'Marva': {"benefits":['Enhances compassion and patience'],
          "time":'15-24'},
          'Bhairavi': {"benefits":['Brings Creativity and Happiness', 'Enhances compassion and patience'],
                   "time":'0-9'},
          'Bhairav': {"benefits":['Brings serenity', 'Emotional strength', 'Peace', 'Tranquility', 'Relaxation & Rest'],
          "time":'6-9'},
          }

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    messege = StringField('messege', validators=[DataRequired()])

class PlaylistForm(FlaskForm):
    genre=RadioField('Select your preferred genre:', choices=[
       ('Hindi-Retro', 'Hindi-Retro'),
       ('Hindi-Modern', 'Hindi-Modern'),
       ('Classical','Classical')
   ], validators=[DataRequired()])
    playlist_length = IntegerField('Length of Playlist (1-30 songs):', 
                                   validators=[DataRequired(),NumberRange(1,30)])

class User(UserMixin):

    def __init__(self, id):
        self.id = id
# Function to authenticate and create the Google Drive service
def create_drive_service():
    SERVICE_ACCOUNT_FILE = 'C:\\Users\\chand\\OneDrive\\Desktop\\ide\\ChronoTunes\\credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    # Create credentials using the service account file
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # Build the Drive service
    return build('drive', 'v3', credentials=creds)

service = create_drive_service()
def get_folder_id(genre):
    if genre=='bengali':
        return bengali_link.split('/')[-1]
    elif genre=='classical':
        return classical_link.split('/')[-1]
    elif genre=='hindi-retro':
        return hindi_retro_link.split('/')[-1]
    elif genre=='hindi-modern':
        return hindi_modern_link.split('/')[-1]

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/')
@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('about.html')
    else:
        return redirect(url_for('login'))


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    score = 0
    if request.method == 'POST':
        # Process the form data
        responses = {question: request.form.get(question) for question in questions}
        for value in responses.values():
            score += int(value)
        collection.update_one({"email": session['email']}, {"$set": {"score": score}}) 
        session['score']=score
        flash("Thank you for completing the questionnaire!", "success")
        return redirect(url_for('home'))

    return render_template('questionnaire.html', questions=questions)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = collection.find_one({'email': form.email.data})
        if existing_user is None:
            hashed_password = generate_password_hash(form.password.data)
            collection.insert_one({
                'username': form.username.data,
                'email': form.email.data,
                'password': hashed_password,
                'score': 0,
                'admin': False,
                'membership':False,
                'genre':[],
                'playlist':[],
                'time_created':[]
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists!', 'danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = collection.find_one({'email': form.email.data})
        if user and check_password_hash(user['password'], form.password.data):
            c_user = User(user['username'])
            login_user(c_user)
            session['loggedin'] = True
            session['username'] = user['username']
            session['email'] = user['email']
            session['password'] = user['password']
            session['score'] = user['score']
            session['admin'] = user['admin']
            session['membership']=user['membership']
            session['genres']=user['genre']
            session['playlists']=user['playlist']
            session['time_created']=user['time_created']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/view_songs/<int:index>')
def view_songs(index):
    # Assuming you have a global or session variable that holds the combined playlists
    combined_playlists = session['playlists'] # Replace with your actual method to get playlists

    if index < 0 or index >= len(combined_playlists):
        return "Invalid index", 404  # Handle invalid index

    # Get the selected playlist
    selected_playlist = combined_playlists[index]
    songs = selected_playlist['playlist']
    folder_id=get_folder_id(selected_playlist['genre'].lower())
    query = f"'{folder_id}' in parents and mimeType='audio/mpeg'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    filter_items=[]
    for file in items:
        if file['name'].replace('.mp3', '.pickle') in songs:
            filter_items.append({'name':file['name'],'url':f"https://drive.google.com/file/d/{file['id']}/view"})
    #print(songs,filter_items)
    return render_template('playlist.html', genre=selected_playlist['genre'], audio_files=filter_items)
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    results = collection.find({"email":session['email']}, {'genre': 1, 'playlist': 1, 'time_created':1,'_id': 0 })
    results=list(results)
    if results[0]:
        # Initialize empty lists
        times = []
        genres = []
        playlists = []
# Iterate through the data and extend the lists
        for item in results:
            times.extend(item['time_created'])
            genres.extend(item['genre'])
            playlists.extend(item['playlist'])
        combined_playlists = []

        for i in range(len(genres)):
            combined_playlists.append({
            'genre': genres[i],
            'playlist': playlists[i],
            'time_created': times[i].strftime('%Y-%m-%d %H:%M:%S')  # Format the datetime as a string
            })
        session['playlists']=combined_playlists
        if request.method == 'POST':
            current_password = request.form['currentPassword']
            new_password = request.form['newPassword']
            confirm_password = request.form['confirmPassword']

            if new_password != confirm_password:
                flash("New passwords do not match!", "error")
            elif not check_password_hash(session['password'], current_password):
                flash("Current password is incorrect!", "error")
            else:
                users[current_user.id] = generate_password_hash(new_password)
                collection.update_one({'email': session['email']},{'$set': {'password': new_password }})
                flash("Password updated successfully!", "success")
                return redirect(url_for('profile'))
    else:
        return render_template('profile.html', username=session['username'],is_member=session['membership'])

    return render_template('profile.html', username=session['username'], combined_playlists=session['playlists'],is_member=session['membership'])

@app.route('/contactUs', methods=['POST', 'GET'])
@login_required
def contactUs():
    form = ContactForm()
    if form.validate_on_submit():
        customer.insert_one({"name":form.name.data, "email":form.email.data, "message":form.messege.data,"time":datetime.now()})
        flash("Sent Message Succesfully!", "success")
        return redirect(url_for('home'))
    return render_template('contact.html', form=form)

@app.route('/get_playlist', methods=['GET', 'POST'])
def get_playlist():
    form = PlaylistForm()
    if form.validate_on_submit() and session["loggedin"]:
        genre = form.genre.data
        playlist_length = int(form.playlist_length.data)
        if not session['score'] or session['score']<=12:
            songs = song_db[genre.lower()].find({}, {'filename': 1})
        else:
            thaat=['Bhairavi','Bhairav','Kafi','Bilawal','Todi']
            songs=song_db[genre.lower()].find({"thaat": {"$in": thaat}}, {'filename': 1})

        filenames = [song['filename'] for song in songs if 'filename' in song]

        if not filenames:
            flash("No songs found for the genre:", 'success')
            return render_template('getplaylist.html', form=form, error="No songs found.")

        filtered_songs = random.sample(filenames, playlist_length)

        user_id = session['email'] 
        collection.update_one(
            {"email": user_id},
            {   "$push": {"playlist": filtered_songs,
                "genre":genre,
                "time_created": datetime.now()}
            },
            upsert=True
        )
        folder_id=get_folder_id(genre.lower())
        query = f"'{folder_id}' in parents and mimeType='audio/mpeg'"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        filter_items=[]
        for file in items:
            if file['name'].replace('.mp3', '.pickle') in filtered_songs:
                filter_items.append({'name':file['name'],'url':f"https://drive.google.com/file/d/{file['id']}/view"})
        #print(songs,filter_items)
        return render_template('playlist.html',audio_files=filter_items)

    return render_template('getplaylist.html', form=form)

@app.route('/membership', methods=['POST'])
def membership():
        if request.method == 'POST':    
            return render_template('membership.html',key_id=RAZORPAY_KEY_ID)

@app.route('/verify', methods=['POST'])
def verify_payment():
    #Get Data From Razorpay checkout
        payment_id = request.form.get("razorpay_payment_id")
        order_id = request.form.get("razorpay_order_id")
        signature = request.form.get("razorpay_signature")
        #Verify signature
        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id,
                "razorpay_signature": signature
            })
            #Update membership status
            user_id = session['email']
            collection.update_one({'email': user_id},{"$set": {"membership": True}})
            session['membership'] = True
            flash("Membership activated successfully!", "success")
            return redirect(url_for('profile'))
        except razorpay.errors.SignatureVerificationError:
            flash("Signature verification failed", "error")
            return render_template('membership.html',key_id=RAZORPAY_KEY_ID)
  
@app.route('/order', methods=['POST'])
def create_order():
    if 'loggedin' in session:
        amount = 12900 #In Paise
        currency = "INR"
        order_data = {"amount":amount,
                      "currency":currency }
        razorpay_order = razorpay_client.order.create(data=order_data)
        return{"order_id":razorpay_order['id'],"amount":amount}
    else:
        flash('Please log in to purchase membership.', 'error')
        return redirect(url_for('login.html'))


@app.route('/admin', methods=['GET'])
def admin():
    if session['admin']:
        responses = customer.find({})
        return render_template('admin.html', responses=responses)
    flash('Not an Admin User!', 'error')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
