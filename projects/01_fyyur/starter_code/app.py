#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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
    try:
        # Query all venues from the database
        venues = Venue.query.all()

        # Create a dictionary to store venue data grouped by city and state
        areas = {}

        # Iterate over each venue
        for venue in venues:
            key = (venue.city, venue.state)

            # If the city-state combination does not exist in the dictionary, add it
            if key not in areas:
                areas[key] = {
                    "city": venue.city,
                    "state": venue.state,
                    "venues": []
                }

            # Query upcoming shows for the current venue
            upcoming_shows_count = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > db.func.now()).count()

            print("upcoming shows count = ", upcoming_shows_count)

            # Append venue data to the corresponding city-state entry in the dictionary
            areas[key]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "upcoming_shows_count": upcoming_shows_count
            })

        # Convert the dictionary into a list of values
        data = list(areas.values())

        # Render the template with the venue data
        return render_template('pages/venues.html', areas=data)
    except Exception as e:
        # Handle any exceptions
        print(f"Error retrieving venues: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')

from sqlalchemy import func  # Import SQLAlchemy function for case-insensitive search

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Get the search term from the form data
    search_term = request.form.get('search_term', '')

    # Perform case-insensitive partial string search for venues containing the search term
    venues = Venue.query.filter(func.lower(Venue.name).contains(search_term.lower())).all()

    # Format the response data
    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "upcoming_shows_count": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > db.func.now()).count()
        } for venue in venues]
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Query the venue with the given venue_id from the database
    venue = Venue.query.get_or_404(venue_id)

    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
        temp_show = {
            'artist_id' : show.artist_id,
            'artist_name' : show.artist.name,
            'artist_image_link' : show.artist.image_link,
            'start_time' : show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # Format venue data
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,  # Assuming genres is a list attribute of the Venue model
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.looking_for_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,  # Initialize empty lists for past_shows and upcoming_shows
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    # Populate past_shows and upcoming_shows if available in your Venue model

    return render_template('pages/show_venue.html', venue=data)



#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    print(request.form)  # This will print the whole form data to console
    venue_name = request.form.get('name')
    print("venue_name received: ", venue_name)
    if form.validate():
        try:
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                looking_for_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(new_venue)
            db.session.commit()
            # Flash a success message
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
            
        except Exception as e:
            db.session.rollback()
            # Flash an error message
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            print(e)
        finally:
            db.session.close()
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. Form validation failed.')
    
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # Query the venue from the database using its ID
    venue = Venue.query.get_or_404(venue_id)

    try:
        # Delete the venue record from the database
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        # Handle potential errors during deletion
        db.session.rollback()
        print(f"Error deleting venue with ID {venue_id}: {str(e)}")
        abort(500)  # Return a 500 Internal Server Error response

    return redirect(url_for('index'))  # Redirect the user to the homepage after successful deletion


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    try:
        # Query the database to get all artists
        artists = Artist.query.all()

        # Convert the queried data into the format required by the template
        data = [{'id': artist.id, 'name': artist.name} for artist in artists]

        # Render the template with the artists data
        return render_template('pages/artists.html', artists=data)
    except Exception as e:
        # Handle any exceptions
        print(f"Error retrieving artists: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('error.html')

@app.route('/artists/search', methods=['POST'])
def search_artists():
    try:
        # Get the search term from the request form data
        search_term = request.form.get('search_term', '').strip()

        # Perform a case-insensitive partial string search on artist names in the database
        # Here, we use ILIKE for case-insensitive search and '%' for partial matching
        artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

        # Prepare the response data
        response = {
            "count": len(artists),
            "data": [{
                "id": artist.id,
                "name": artist.name,
                "upcoming_shows_count": Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > db.func.now()).count(),  # You can populate this field based on your application logic
            } for artist in artists]
        }

        # Render the template with the search results and the search term
        return render_template('pages/search_artists.html', results=response, search_term=search_term)
    except Exception as e:
        # Handle any exceptions
        print(f"Error searching artists: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        # Query the database to get the artist with the given artist_id
        artist = Artist.query.get_or_404(artist_id)

        # If artist is not found, return a 404 error
        if not artist:
            return render_template('errors/404.html'), 404
        
        past_shows = []
        upcoming_shows = []

        for show in artist.shows:
          temp_show = {
            'artist_id' : show.artist_id,
            'artist_name' : show.artist.name,
            'artist_image_link' : show.artist.image_link,
            'start_time' : show.start_time.strftime("%m/%d/%Y, %H:%M")
            }
          if show.start_time <= datetime.now():
            past_shows.append(temp_show)
          else:
            upcoming_shows.append(temp_show)


        # Convert the queried data into the format required by the template
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.looking_for_venues,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

        # Render the template with the artist data
        return render_template('pages/show_artist.html', artist=data)
    except Exception as e:
        # Handle any exceptions
        print(f"Error retrieving artist: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        # Get the artist record from the database based on the artist_id
        artist = Artist.query.get(artist_id)

        # Create an instance of the ArtistForm and populate it with the artist data
        form = ArtistForm(obj=artist)

        # Render the edit artist form template with the form and artist data
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    except Exception as e:
        # Handle any exceptions
        print(f"Error editing artist: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        # Get the artist record from the database based on the artist_id
        artist = Artist.query.get(artist_id)

        # Create an instance of the ArtistForm and populate it with the form data
        form = ArtistForm(request.form)

        # Update the artist record with the new attributes from the form
        form.populate_obj(artist)

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the artist page after successful submission
        return redirect(url_for('show_artist', artist_id=artist_id))
    except Exception as e:
        # Handle any exceptions
        db.session.rollback()
        print(f"Error editing artist submission: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        # Get the venue record from the database based on the venue_id
        venue = Venue.query.get(venue_id)

        # Create an instance of the VenueForm and populate it with the venue data
        form = VenueForm(obj=venue)

        # Render the edit venue form template with the form and venue data
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    except Exception as e:
        # Handle any exceptions
        print(f"Error editing venue: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        # Get the venue record from the database based on the venue_id
        venue = Venue.query.get(venue_id)

        # Create an instance of the VenueForm and populate it with the form data
        form = VenueForm(request.form)

        # Update the venue record with the new attributes from the form
        form.populate_obj(venue)

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the venue page after successful submission
        return redirect(url_for('show_venue', venue_id=venue_id))
    except Exception as e:
        # Handle any exceptions
        db.session.rollback()
        print(f"Error editing venue submission: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Extract form data
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    looking_for_venues = True if request.form.get('looking_for_venues') == 'y' else False
    seeking_description = request.form['seeking_description']

    print("Adding artist to db : " + name)

    try:
        # Create a new Artist instance with the form data
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                        image_link=image_link, facebook_link=facebook_link, website_link=website_link,
                        looking_for_venues=looking_for_venues, seeking_description=seeking_description)
        # Add the new artist to the session
        db.session.add(artist)
        # Commit the session to insert the new artist into the database
        db.session.commit()

        # Flash a success message
        flash('Artist ' + name + ' was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        # Flash an error message
        flash('An error occurred. Artist ' + name + ' could not be listed.')
        print(f"Error inserting artist: {str(e)}")
        return render_template('pages/home.html')
    finally:
        # Close the session
        db.session.close()

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    try:
        # Query the database to retrieve all show records
        shows = db.session.query(Show).all()

        # Create a list to store the formatted show data
        data = []

        # Iterate over each show record and format its data
        for show in shows:
            venue = Venue.query.get(show.venue_id)
            artist = Artist.query.get(show.artist_id)

            show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "artist_id": artist.id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time)  # Convert datetime to string
            }
            data.append(show_data)

        # Render the template with the show data
        return render_template('pages/shows.html', shows=data)
    except Exception as e:
        # Handle any exceptions
        print(f"Error retrieving shows: {str(e)}")
        # Flash an error message or handle it in your preferred way
        return render_template('errors/500.html')



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    
  form = ShowForm(request.form)
  print(request.form)  # This will print the whole form data to console
  #show_name = request.form.get('name')
  #print("show_name received: ", show_name)
  if form.validate():
      try:
          new_show = Show(
              start_time = form.start_time.data,
              artist_id = form.artist_id.data,
              venue_id = form.venue_id.data
          )
          db.session.add(new_show)
          db.session.commit()
          # Flash a success message
          flash('Show was successfully listed!')
          
      except Exception as e:
          db.session.rollback()
          # Flash an error message
          flash('An error occurred. Show could not be listed.')
          print(e)
      finally:
          db.session.close()
  else:
      flash('An error occurred. Show could not be listed. Form validation failed.')
  
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
