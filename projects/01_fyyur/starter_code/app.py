#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import truediv
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from sqlalchemy.orm import backref
from forms import *
import sys
from werkzeug.datastructures import ImmutableMultiDict
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# migration
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String)
    website_link = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    artists = db.relationship('Artist', secondary='shows')
    shows = db.relationship('Show', cascade="all,delete", backref = 'venue')

    def to_dict(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'genres': self.genres.split(','),  # convert string to list
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website_link': self.website_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
      }

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
    

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO FINISHED: implement any missing fields, as a database migration using Flask-Migrate
    # according to form.py
    website_link = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)

    venues = db.relationship('Venue', secondary='shows')
    shows = db.relationship('Show', cascade="all,delete", backref = 'artist')

    def to_dict(self):
      return {
        'name': self.name,
        'city': self.city,
        'state': self.city,
        'phone': self.phone,
        'genres': self.genres.split(','),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website_link': self.website_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description
      }

    def __repr__(self):
      return f'<Artist {self.id} {self.name}'

# TODO FINISHED: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    # venue = db.relationship(Venue, backref='venues.name')
    # artist =db.relationship(Artist, backref='artists.name')

    def show_artist(self):
      return {
          'artist_id': self.artist_id,
          'artist_name': self.artist.name,
          'artist_image_link': self.artist.image_link,
            # convert datetime to string
          'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }
    
    def show_venue(self):
      return {
        'venue_id': self.venue_id,
        'venue_name': self.venue.name,
        'venue_image_link': self.venue.image_link,
        # convert datetime to string
        'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S')
      }
      
    def __repr__(self):
      return f'<Show <self.id> by artist <self.artist>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  locations = set()
  # get all venues 
  venues = Venue.query.order_by(Venue.state, Venue.city).all()
  
  for venue in venues:
    locations.add((venue.city, venue.state))
  
  for location in locations:
    data.append({
      'city': location[0],
      'state': location[1],
      'venues': []
    }) 


  for venue in venues:
    for venue_location in data:
      if venue_location['city'] == venue.city and venue_location['state'] == venue.state:
        venue_location['venues'].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.today(), venue.shows)))
        })
  # -Lin's commment, is there any easy way to achieve this?
  sorted(data, key = lambda d: (d['state'], d['city']))
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  count = 0 # count the returned result
  for venue in venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': len(list(filter(lambda x: x.start_time > datetime.today(), venue.shows)))
    })
    count += 1
  
  response = {'count': count, 'data': data}


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  past_shows = list(filter(lambda x: x.start_time < datetime.today(), venue.shows))
  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), venue.shows))

  past_shows = list(map(lambda x: x.show_artist(), past_shows))
  upcoming_shows = list(map(lambda x: x.show_artist(), upcoming_shows))

  data = venue.to_dict()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  if 'seeking_talent' in request.form:
    seeking_talent = True 
  else:
    seeking_talent = False
  try:
    venue  = Venue(
      name = request.form['name'],
      city = request.form['city'],
      state = request.form['state'],
      address = request.form['address'],
      phone = request.form['phone'],
      image_link = request.form['image_link'],
      facebook_link = request.form['facebook_link'],
      genres = request.form.getlist('genres'),
      website_link = request.form['website_link'],
      seeking_talent = seeking_talent,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    # TODO: on unsuccessful db insert, flash an error instead.
    if error:
      flash('Venue ' + request.form['name'] + ' could not be listed!')
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  error = False 
  try: 
    venue = Venue.query.get(venue_id)
    venue_name = venue.name 
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('Venue ' + venue_name + ' cannot be deleted')
    else:
      flash('Venue ' + venue_name + " has been!")


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  ALTERNATIVE Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue_post(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  error = False 
  try: 
    venue = Venue.query.get(venue_id)
    print(venue.shows[0].id)
    venue_name = venue.name 
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('Venue ' + venue_name + ' cannot be deleted!')
    else:
      flash('Venue ' + venue_name + " has been deleted!")


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))


#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  

  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  # populate the form with SQLAlchemy
  form = VenueForm(obj=venue)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False 

  try:
    venue = Venue.query.filter_by(id = venue_id)
    tmp_genres = request.form.getlist('genres')
    if 'seeking_talent' in request.form:
      seeking_talent = True 
    else:
      seeking_talent = False
    data_to_update = {
      'name': request.form['name'],
      'city': request.form['city'],
      'state': request.form['state'],
      'address': request.form['address'],
      'phone': request.form['phone'],
      'genres': ','.join(tmp_genres),
      'facebook_link': request.form['facebook_link'],
      'image_link': request.form['image_link'],
      'website_link': request.form['website_link'],
      'seeking_talent': seeking_talent,
      'seeking_description': request.form['seeking_description']
    }

    venue.update(data_to_update)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')    

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Artist
#  ----------------------------------------------------------------

#  Read Artist
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist.name, Artist.id).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), artist.shows))
  past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows))

  upcoming_shows = list(map(lambda x: x.show_venue(), upcoming_shows))
  past_shows = list(map(lambda x: x.show_venue(), past_shows))

  data = artist.to_dict()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  print(data)
  return render_template('pages/show_artist.html', artist=data)


#  Search Artist
#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  data = []
  count = 0
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': len(list(filter(lambda x: x.start_time >= datetime.today(), artist.shows)))
    })
    count += 1
  
  response ={'count': count, 'data': data}


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


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
  error = False 
  try:
    data = request.form.to_dict(flat=True)
    if 'seeking_venue' in data:
      data['seeking_venue'] = True 
    else:
      data['seeking_venue'] = False 
    artist = Artist(**data)
    db.session.add(artist)
    db.session.commit() 
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # TODO: populate form with fields from artist with ID <artist_id>

  artist = Artist.query.get(artist_id)
  # populate the form with SQLAlchemy
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

# Update artist
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False 
  artist = Artist.query.filter_by(id = artist_id)
  try:
    data_to_update = request.form.to_dict(flat = True)
    if 'seeking_venue' in data_to_update:
      data_to_update['seeking_venue'] = True 
    else:
      data_to_update['seeking_venue'] = False 
    artist.update(data_to_update)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated!')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

# display shows
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all() 
  data = []
  for show in shows:
    data.append({
      'venue_id': show.venues.id,
      'venue_name': show.venues.name,
      'artist_id': show.artists.id,
      'artist_name': show.artists.name,
      'artist_image_link': show.artists.image_link,
      'start_time': show.start_time.isoformat()
    })
  
  return render_template('pages/shows.html', shows=data)

# Render shows forms
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# Create shows
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
  error = False 
  try:
    data = request.form.to_dict(flat=True)
    print(data)
    show = Show(**data)
    db.session.add(show)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
    else:
    # on successful db insert, flash success
      flash('Show was successfully listed!')
    return render_template('pages/home.html')

# Handlers
#  ----------------------------------------------------------------
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
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
