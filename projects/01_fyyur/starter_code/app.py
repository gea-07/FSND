#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Done: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Done: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
    __tablename__ = 'shows'
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    start_time = db.Column(db.DateTime(), primary_key=True)

class Venue(db.Model):
  __tablename__ = 'venues'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # Done: implement any missing fields, as a database migration using Flask-Migrate
  genres = db.Column(db.ARRAY(db.String()))
  website = db.Column(db.String())
  seeking_talent = db.Column(db.Boolean, default=True)
  seeking_description = db.Column(db.String())
  show = db.relationship('Shows', backref=db.backref('venues_table', lazy=True))

  def __repr__(self):
        return f'<Venue \
        {self.id}, \
        {self.name},\
        {self.city},\
        {self.state},\
        {self.address},\
        {self.phone},\
        {self.image_link},\
        {self.facebook_link},\
        {self.genres},\
        {self.website},\
        {self.seeking_talent},\
        {self.seeking_description}\
        >'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Done: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String())
    show = db.relationship('Shows', backref=db.backref('artists', lazy=True))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  try:
    query = Venue.query.order_by(Venue.state).order_by(Venue.city).all()
    for venue in query:
      data_exists = next((item for item in data if item["city"] == venue.city and item['state']==venue.state), False)  
      if not data_exists:
        recordObject = {
          "city": venue.city,
          "state": venue.state,
          "venues": []}

        #find all the venues in the city and state
        query2 = Venue.query.filter(Venue.city==venue.city, Venue.state==venue.state).all()

        for cityStateVenue in query2:
          recordDetailObject = {
            "id": cityStateVenue.id,
            "name": cityStateVenue.name,
            "num_upcoming_shows": Shows.query.filter(
              Shows.venue_id == cityStateVenue.id,
              Shows.start_time > datetime.utcnow()).count()
          }
          recordObject['venues'].append(recordDetailObject)

        data.append(recordObject)  
  except:
    db.session.rollback()
  finally:
    db.session.commit()

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue_name= '%{0}%'.format(request.form.get('search_term'))
  query = Venue.query.filter(Venue.name.ilike(venue_name)).all()
  data = []
  response = {
    "count": len(query),
    "data": []
  }
  for venue in query:
    venueObject = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Shows.query.filter(
            Shows.venue_id == venue.id,
            Shows.start_time > datetime.utcnow()).count()
    }
    response['data'].append(venueObject)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  try:
    error = False
    data = []
    past_shows = []
    upcoming_shows = []
    venue = Venue.query.get(venue_id)

    if venue:
      #get all the shows for this venue, shows is an array of Show objects
      shows = venue.show
      for show in shows:    
        past_artist = Artist.query.filter(Artist.id == show.artist_id, show.start_time < datetime.utcnow()).first()
        upcoming_artist = Artist.query.filter(Artist.id == show.artist_id, show.start_time > datetime.utcnow()).first()
        artist = past_artist if past_artist != None else upcoming_artist
        show_detail = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        if past_artist != None:
          past_shows.append(show_detail)
        else:
          upcoming_shows.append(show_detail)
        
      recordObject = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      }
      data.append(recordObject)
  except:
    error = True
    db.session.rollback()
    len(upcoming_shows)
  finally:
    db.session.close 
  if not error:
    return render_template('pages/show_venue.html', venue=data[0])
  else:
    return render_template('pages/show_venue.html', {})


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Done: insert form data as a new Venue record in the db, instead
  error = False
  form = VenueForm()
  # Done: modify data to be the data object returned from db insertion
  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      genres = form.genres.data,
      website = form.website.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
      )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if not error:  
     # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('forms/new_venue.html', form=form)
  else:
    # Done: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('Venue ' + request.form['name'] + ' could not listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # Done: BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({'success':True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  data = []
  query = Artist.query.all()
  for artist in query:
    recordObject = {
      "id": artist.id,
      "name": artist.name,
    }
    data.append(recordObject)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist_name= '%{0}%'.format(request.form.get('search_term'))
  query = Artist.query.filter(Artist.name.ilike(artist_name)).all()
  data = []
  response = {
    "count": len(query),
    "data": []
  }
  for artist in query:
    artistObject = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Shows.query.filter(
            Shows.artist_id == artist.id,
            Shows.start_time > datetime.utcnow()).count()
    }
    response['data'].append(artistObject)
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # Done: replace with real venue data from the venues table, using venue_id
  try:
    error = False
    data = []
    past_shows = []
    upcoming_shows = []
    artist = Artist.query.get(artist_id)
    if artist:
      shows = artist.show
      for show in shows:
        past_venue = Venue.query.filter(Venue.id == show.venue_id, show.start_time < datetime.utcnow()).first()
        upcoming_venue = Venue.query.filter(Venue.id == show.venue_id, show.start_time > datetime.utcnow()).first()
        venue = past_venue if past_venue != None else upcoming_venue
   
        show_detail = {
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        if show.start_time < datetime.utcnow():
          past_shows.append(show_detail)
        else:
          upcoming_shows.append(show_detail)

    artistObject = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    }
    data.append(artistObject)
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if not error:
    return render_template('pages/show_artist.html', artist=data[0])
  else:
    return render_template('pages/show_artist.html', artist={})

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  try:
    artist = {}
    form = ArtistForm()
    artist_from_db = Artist.query.get(artist_id)
    if (artist_from_db):
      artist={
        "id": artist_from_db.id,
        "name": artist_from_db.name,
        "genres": artist_from_db.genres,
        "city": artist_from_db.city,
        "state": artist_from_db.state,
        "phone": artist_from_db.phone,
        "website": artist_from_db.website,
        "facebook_link": artist_from_db.facebook_link,
        "seeking_venue": artist_from_db.seeking_venue,
        "seeking_description": artist_from_db.seeking_description,
        "image_link": artist_from_db.image_link
      }
      # Done: populate form with fields from artist with ID <artist_id>
      #form.populate_obj(artist) #this doesn't work! so I have to manually populate the form
      
      form.name.data = artist_from_db.name
      form.genres.data = artist_from_db.genres
      form.city.data = artist_from_db.city
      form.state.data = artist_from_db.state
      form.phone.data = artist_from_db.phone
      form.website.data = artist_from_db.website
      form.facebook_link.data = artist_from_db.facebook_link
      form.seeking_venue.data = artist_from_db.seeking_venue
      form.seeking_description.data = artist_from_db.seeking_description
      form.image_link.data = artist_from_db.image_link
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()  
    
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = {}
    form = ArtistForm()
    print(form)
    artist = Artist.query.get(artist_id)
    if artist:
      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.facebook_link = form.facebook_link.data
      db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  try:
    venue = {}
    form = VenueForm()
    venue_from_db = Venue.query.get(venue_id)
    if venue_from_db:
      venue={
        "id": venue_from_db.id,
        "name": venue_from_db.name,
        "genres": venue_from_db.genres,
        "address": venue_from_db.address,
        "city": venue_from_db.city,
        "state": venue_from_db.state,
        "phone": venue_from_db.phone,
        "website": venue_from_db.website,
        "facebook_link": venue_from_db.facebook_link,
        "seeking_talent": venue_from_db.seeking_talent,
        "seeking_description": venue_from_db.seeking_description,
        "image_link": venue_from_db.image_link
      }
      # Done: populate form with values from venue with ID <venue_id>
      form.name.data = venue_from_db.name
      form.city.data = venue_from_db.city
      form.state.data = venue_from_db.state
      form.address.data = venue_from_db.address
      form.phone.data = venue_from_db.phone
      form.image_link.data = venue_from_db.image_link
      form.genres.data = venue_from_db.genres
      form.facebook_link.data = venue_from_db.facebook_link
      form.website.data = venue_from_db.website
      form.seeking_talent = venue_from_db.seeking_talent
      form.seeking_description = venue_from_db.seeking_description
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Populate DB with initial data.
#----------------------------------------------------------------------------#
def populate_database():
  try:
    if Artist.query.count() == 0:
      artist1 = Artist(
        id = 4,
        name = "Guns N Petals",
        genres = ["Rock n Roll"],
        city = "San Francisco",
        state = "CA",
        phone = "326-123-5000",
        website = "https://www.gunsnpetalsband.com",
        facebook_link = "https://www.facebook.com/GunsNPetals",
        seeking_venue = True,
        seeking_description = "Looking for shows to perform at in the San Francisco Bay Area!",
        image_link = "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
      )

      artist2 = Artist(
        id = 5,
        name = "Matt Quevedo",
        genres = ["Jazz"],
        city = "New York",
        state = "NY",
        phone = "300-400-5000",
        facebook_link = "https://www.facebook.com/mattquevedo923251523",
        seeking_venue = False,
        image_link = "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"
      )

      artist3 = Artist(
        id = 6,
        name = "The Wild Sax Band",
        genres = ["Jazz", "Classical"],
        city = "San Francisco",
        state = "CA",
        phone = "432-325-5432",
        seeking_venue = False,
        image_link = "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
      )

      db.session.add_all([artist1, artist2, artist3])

    if Venue.query.count() == 0:
      venue1 = Venue(
        id = 1,
        name = "The Musical Hop",
        genres = ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        address = "1015 Folsom Street",
        city = "San Francisco",
        state = "CA",
        phone = "123-123-1234",
        website = "https://www.themusicalhop.com",
        facebook_link = "https://www.facebook.com/TheMusicalHop",
        seeking_talent = True,
        seeking_description = "We are on the lookout for a local artist to play every two weeks. Please call us.",
        image_link = "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
      )

      venue2 = Venue(
        id = 2,
        name = "The Dueling Pianos Bar",
        genres = ["Classical", "R&B", "Hip-Hop"],
        address = "335 Delancey Street",
        city = "New York",
        state = "NY",
        phone = "914-003-1132",
        website = "https://www.theduelingpianos.com",
        facebook_link = "https://www.facebook.com/theduelingpianos",
        seeking_talent = False,
        image_link = "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
      )

      venue3 = Venue(
        id = 3,
        name = "Park Square Live Music & Coffee",
        genres = ["Rock n Roll", "Jazz", "Classical", "Folk"],
        address = "34 Whiskey Moore Ave",
        city = "San Francisco",
        state = "CA",
        phone = "415-000-1234",
        website = "https://www.parksquarelivemusicandcoffee.com",
        facebook_link = "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        seeking_talent = False,
        image_link = "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
      )

      db.session.add_all([venue1, venue2, venue3])

      if Shows.query.count() == 0:
        show1 = Shows(
          start_time = datetime.strptime("2019-05-21T21:30:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ'),
          venue_id = 1,
          artist_id = 4
        )

        show2 = Shows(
          start_time = datetime.strptime("2019-06-15T23:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ'),
          venue_id = 3,
          artist_id = 5
        )
        show3 = Shows(
          start_time = datetime.strptime("2035-04-01T20:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ'),
          venue_id = 3,
          artist_id = 6
        )
        show4 = Shows(
          start_time = datetime.strptime("2035-04-08T20:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ'),
          venue_id = 3,
          artist_id = 6
        )
        show5 = Shows(
          start_time = datetime.strptime("2035-04-15T20:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ'),
          venue_id = 3,
          artist_id = 6
        )
        db.session.add_all([show1, show2, show3, show4, show5])

      db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

def test_data():
  try:
    data = []
    past_shows = []
    upcoming_shows = []
    venue = Venue.query.get(3)

    if venue:
      #get all the shows for this venue, shows is an array of Show objects
      shows = venue.show
      for show in shows:    
        past_artist = Artist.query.filter(Artist.id == show.artist_id, show.start_time < datetime.utcnow()).first()
        upcoming_artist = Artist.query.filter(Artist.id == show.artist_id, show.start_time > datetime.utcnow()).first()
        artist =past_artist if past_artist != None else upcoming_artist
        show_detail = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time,
        }
        if past_artist != None:
          past_shows.append(show_detail)
        else:
          upcoming_shows.append(show_detail)
        
      recordObject = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": Shows.query.filter(
                  Shows.venue_id == venue.id,
                  Shows.start_time < datetime.utcnow()).count(),
        "upcoming_shows_count": Shows.query.filter(
                  Shows.venue_id == venue.id,
                  Shows.start_time > datetime.utcnow()).count(),
      }
      data.append(recordObject)
  except:
    db.session.rollback()
  finally:
    db.session.close  
    
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    #initialize the database if empty
    populate_database()
    test_data()
    app.run(host="localhost", port=8000, debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
