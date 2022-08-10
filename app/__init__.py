import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *


from models import setup_db, Venue, Artist, Show, db


def create_app():
    app = Flask(__name__)
    setup_db(app)

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
        venues = Venue.query.distinct(Venue.city).all()
        
        # TODO: replace with real venues data.
        #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
        data = []
        for venue in venues:
            vens = []
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": vens
            })
            city_venues = Venue.query.filter(Venue.city==venue.city, Venue.state==venue.state).all()
            for v in city_venues:
                vens.append({
                    "id": v.id,
                    "name": v.name,
                    "num_upcoming_shows": Show.query.filter(Show.start_time >= datetime.now()).count(),
                })
    
        return render_template('pages/venues.html', areas=data);

    @app.route('/venues/search', methods=['POST'])
    def search_venues():
        search_term = request.form['search_term']
        venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
        
        # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
        # seach for Hop should return "The Musical Hop".
        # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
        data = []
        for venue in venues.all():
            data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Venue.query.filter(Venue.id==venue.id, Show.start_time >= datetime.now()),
            })
        response={
            "count": venues.count(),
            "data": data
        }
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

    @app.route('/venues/<int:venue_id>')
    def show_venue(venue_id):
        # shows the venue page with the given venue_id
        # TODO: replace with real venue data from the venues table, using venue_id
        venue = Venue.query.get(venue_id)

        upcoming_sql = Show.query.filter(Show.start_time >= datetime.now(), Show.venue_id==venue.id)
        upcoming_show = []
        for show in upcoming_sql.all():
            upcoming_show.append({
                "venue_id": show.venue_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })

        past_sql = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue.id)
        past_shows = []
        for show in past_sql.all():
            past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
            })
        data={
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres.replace('{','').replace('}', '').split(','),
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website_link": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_show,
            "past_shows_count": past_sql.count(),
            "upcoming_shows_count": upcoming_sql.count(),
        }
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
        if request.method == 'POST' and form.validate():
            error = False
            try:
                venue = Venue(
                    name = form.name.data,
                    city = form.city.data,
                    state = form.state.data,
                    address = form.address.data,
                    phone = form.phone.data,
                    genres = form.genres.data,
                    image_link = form.image_link.data,
                    facebook_link = form.facebook_link.data,
                    website_link = form.website_link.data,
                    seeking_talent = form.seeking_talent.data,
                    seeking_description = form.seeking_description.data,
                )
                db.session.add(venue)
                db.session.commit()
                flash('Venue ' + request.form['name'] + ' was successfully listed!')
            except:
                db.session.rollback()
                error = True
                print(sys.exc_info())
                flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
            finally:
                db.session.close()
            if error:
                abort(500)
            return render_template('pages/home.html')

    @app.route('/venues/<venue_id>', methods=['DELETE'])
    def delete_venue(venue_id):
        error = False
        try:
            Venue.query.filter(Venue.id==venue_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()
        if error:
            abort(500)
        # TODO: Complete this endpoint for taking a venue_id, and using
        # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
        return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
    @app.route('/artists')
    def artists():
        artists = Artist.query.all()
        # TODO: replace with real data returned from querying the database
        data=[]
        for artist in artists:
            data.append({
            "id": artist.id,
            "name": artist.name,
        })
        return render_template('pages/artists.html', artists=data)

    @app.route('/artists/search', methods=['POST'])
    def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
        search_term = request.form['search_term']
        artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%"))
        data = []
        for artist in artists.all():
            data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": Show.query.filter(Show.artist_id==artist.id, Show.start_time >= datetime.now()).count(),
            })
        response={
            "count": artists.count(),
            "data": data
        }
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

    @app.route('/artists/<int:artist_id>')
    def show_artist(artist_id):
        # shows the artist page with the given artist_id
        # TODO: replace with real artist data from the artist table, using artist_id
        artist = Artist.query.get(artist_id)
        genres =  artist.genres.replace('{', '').replace('}', '').split(',')

        past_shows_query = Show.query.filter(Show.start_time < datetime.now(), Show.artist_id==artist_id)
        past_shows = []
        for show in past_shows_query.all():
            past_shows.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time)
            })

        upcoming_query = Show.query.filter(Show.start_time>=datetime.now(), Show.artist_id==artist_id)
        upcoming_shows = []
        for show in upcoming_query.all():
            upcoming_shows.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time),
            })
        data={
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": past_shows_query.count(),
            "upcoming_shows_count": upcoming_query.count(),
        }
        return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
    @app.route('/artists/<int:artist_id>/edit', methods=['GET'])
    def edit_artist(artist_id):
        artist = Artist.query.get(artist_id)
        form = ArtistForm()
        
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website_link
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

        # TODO: populate form with fields from artist with ID <artist_id>
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    @app.route('/artists/<int:artist_id>/edit', methods=['POST'])
    def edit_artist_submission(artist_id):
        form = ArtistForm(request.form)
        if request.method == 'POST' and form.validate():
            error = False
            try:
                artist = Artist.query.get(artist_id)
                artist.name = form.name.data
                artist.genres = form.genres.data
                artist.city = form.city.data
                artist.state = form.state.data
                artist.phone = form.phone.data
                artist.website_link = form.website_link.data
                artist.facebook_link = form.facebook_link.data
                artist.seeking_venue = form.seeking_venue.data
                artist.seeking_description = form.seeking_description.data
                artist.image_link = form.image_link.data
                db.session.commit()
            except:
                db.session.rollback()
                error = True
                print(sys.exc_info())
            finally:
                db.session.close()
            if error:
                abort(500)

        # TODO: take values from the form submitted, and update existing
        # artist record with ID <artist_id> using the new attributes

            return redirect(url_for('show_artist', artist_id=artist_id))

    @app.route('/venues/<int:venue_id>/edit', methods=['GET'])
    def edit_venue(venue_id):
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website_link
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link
        # TODO: populate form with values from venue with ID <venue_id>
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    @app.route('/venues/<int:venue_id>/edit', methods=['POST'])
    def edit_venue_submission(venue_id):
        # TODO: take values from the form submitted, and update existing
        # venue record with ID <venue_id> using the new attributes
        form = VenueForm(request.form)
        if request.method == 'POST' and form.validate():
            error = False
            try:
                venue = Venue.query.get(venue_id)
                venue.name = form.name.data
                venue.genres = form.genres.data
                venue.address = form.address.data
                venue.city = form.city.data
                venue.state = form.state.data
                venue.phone = form.phone.data
                venue.website_link = form.website_link.data
                venue.facebook_link = form.facebook_link.data
                venue.seeking_talent = form.seeking_talent.data
                venue.seeking_description = form.seeking_description.data
                venue.image_link = form.image_link.data
                db.session.commit()
            except:
                db.session.rollback()
                error = True
                print(sys.exc_info())
            finally:
                db.session.close()
            if error:
                abort(500)
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
        form = ArtistForm(request.form)
        if request.method == 'POST' and form.validate():
            error = False
            try:
                artist = Artist(
                    name=form.name.data,
                    city=form.city.data,
                    state=form.state.data,
                    phone=form.phone.data,
                    genres=form.genres.data,
                    image_link=form.image_link.data,
                    facebook_link=form.facebook_link.data,
                    website_link=form.website_link.data,
                    seeking_venue=form.seeking_venue.data,
                    seeking_description=form.seeking_description.data,
                )
                db.session.add(artist)
                db.session.commit()
                flash('Artist ' + request.form['name'] + ' was successfully listed!')
            except:
                db.session.rollback()
                error = True
                print(sys.exc_info())
                flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
            finally:
                db.session.close()

            if error:
                abort(500)

        # on successful db insert, flash success
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

    @app.route('/shows')
    def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
        shows = Show.query.all()
        data=[]
        for show in shows:
            data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
        print(data)
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
        form = ShowForm(request.form)
        if request.method == 'POST' and form.validate():
            error = False
            try:
                show = Show(
                    venue_id = form.venue_id.data,
                    artist_id = form.artist_id.data,
                    start_time = form.start_time.data,
                )
                db.session.add(show)
                db.session.commit()
                # on successful db insert, flash success
                flash('Show was successfully listed!')
            except:
                db.session.rollback()
                error = True
                print(sys.exc_info)
                flash('An error occurred. Show could not be listed.')
            finally:
                db.session.close()
            if error:
                abort(500)
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
    return app

