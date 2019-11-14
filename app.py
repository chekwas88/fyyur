#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.dialects.postgresql import ARRAY
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    seeking_artist = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='venues', cascade='all, delete-orphan', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artists', cascade='all, delete-orphan', lazy=True)


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
def string_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False

today = datetime.now()
now = today.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def index():
    artists = Artist.query.order_by(db.desc('id')).limit(10).all()
    venues = Venue.query.order_by(db.desc('id')).limit(10).all()
    return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
    venues = []
    try:
        venues = Venue.query.distinct(Venue.city).all()
        for venue in venues:
            venue.venues = Venue.query.filter_by(city=venue.city).all()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally: 
        db.session.close()
    return render_template('pages/venues.html', areas=venues)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {}
    try:
        name = request.form['search_term']
        response['data'] = Venue.query.filter(Venue.name.ilike('%'+ name + '%')).all()
        response['count'] = Venue.query.filter(Venue.name.ilike('%'+ name + '%')).count()
    except:
        print(sys.exc_info())
        flash('error occured')

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    venue = []
    upcoming_show = []
    past_show = []
    try:
        venue = Venue.query.get(venue_id)
        for show in venue.shows:
            artist = Artist.query.get(show.artist_id)
            
            if show.start_time > today:
                upcoming_show.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'artist_image_link': artist.image_link,
                    "start_time": str(show.start_time)
                })
                
            else:
                past_show.append({
                    'artist_id': artist.id,
                    'artist_name': artist.name,
                    'artist_image_link': artist.image_link,
                    "start_time": str(show.start_time)
                })

        setattr(venue, 'past_shows', past_show)
        setattr(venue, 'upcoming_shows', upcoming_show)
        setattr(venue, 'past_shows_count', len(past_show))
        setattr(venue, 'upcoming_shows_count', len(upcoming_show))
    except:
        print(sys.exc_info())
    return render_template('pages/show_venue.html', venue=venue)

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
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing
    try:
        data = request.form
        genres = data.getlist('genres')
        venue = Venue(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            address=data['address'],
            phone=data['phone'],
            genres=genres,
            facebook_link=data['facebook_link'],
            image_link=data['image_link'],
            seeking_artist=string_to_bool(data['seeking_talent']),
            seeking_description=data['seeking_description']
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + data['name'] + ' was successfully listed!')  
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('venues'))


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue has been deleted sucessfully')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Venue could not deleted')
    finally:
        db.session.close()
    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    artists = []
    try:
        artists = Artist.query.all()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally: 
        db.session.close()
    return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {}
    try:
        name = request.form['search_term']
        response['data'] = Artist.query.filter(Artist.name.ilike('%'+ name + '%')).all()
        response['count'] = Artist.query.filter(Artist.name.ilike('%'+ name + '%')).count()
    except:
        print(sys.exc_info())
        flash('An error occured while searching for artist')

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    artist = []
    upcoming_show = []
    past_show = []
    try:
        artist = Artist.query.get(artist_id)
        for show in artist.shows:
            venue = Venue.query.get(show.venue_id)
            if show.start_time > today:
                upcoming_show.append({
                    'venue_id': venue.id,
                    'venue_name': venue.name,
                    'venue_image_link': venue.image_link,
                    "start_time": str(show.start_time)
                })
                
            else:
                past_show.append({
                    'venue_id': venue.id,
                    'venue_name': venue.name,
                    'venue_image_link': venue.image_link,
                    "start_time": str(show.start_time)
                })

        setattr(artist, 'past_shows', past_show)
        setattr(artist, 'upcoming_shows', upcoming_show)
        setattr(artist, 'past_shows_count', len(past_show))
        setattr(artist, 'upcoming_shows_count', len(upcoming_show))
    except:
        print(sys.exc_info())
    return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        data = request.form
        artist = Artist.query.get(artist_id)
        for entry in data:
            if entry == 'genres':
                genres = data.getlist('genres')
                setattr(artist, entry, genres)
            else:
                setattr(artist, entry, data[entry])
        flash('artist ' + data['name'] + ' has been updated')
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error ocurred while updating artist ' + data['name'])
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    try:
        data = request.form
        venue = Venue.query.get(venue_id)
        for entry in data:
            if entry == 'genres':
                genres = data.getlist('genres')
                setattr(venue, entry, genres)
            else:
                setattr(venue, entry, data[entry])
        flash('venue ' + data['name'] + ' has been updated')
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error ocurred while updating venue ' + data['name'])
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
        flash('Artist has been deleted sucessfully')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Artist could not deleted')
    finally:
        db.session.close()
    return redirect(url_for('artists'))

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
    try:
        data = request.form
        genres = data.getlist('genres')
        artist = Artist(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            address=data['address'],
            phone=data['phone'],
            genres=genres,
            facebook_link=data['facebook_link'],
            image_link=data['image_link'],
            seeking_venue=string_to_bool(data['seeking_shows']),
            seeking_description=data['seeking_description']
        )
        print(artist)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + data['name'] + ' was successfully listed!')  
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('artists'))

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
    try:
        shows = Show.query.order_by('start_time').all()
        data = []
        for show in shows:
            data.append ({
                "venue_id": show.venue_id,
                 "venue_name": show.venues.name,
                "artist_id": show.artist_id,
                "artist_name": show.artists.name,
                "artist_image_link": show.artists.image_link,
                "start_time": str(show.start_time)
            })
    except:
        print(sys.exc_info())
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
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    try:
        data = request.form
        show = Show(
            artist_id=data['artist_id'],
            venue_id=data['venue_id'],
            start_time=data['start_time']
        )
        db.session.add(show)
        db.session.commit()
        flash('Show has been created successfully')  
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred while trying to list a show')
    finally:
        db.session.close()
    return redirect(url_for('shows'))

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
