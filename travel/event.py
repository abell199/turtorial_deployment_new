from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import *
from .forms import CreateEvent, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from datetime import date

bp = Blueprint('event', __name__,)


@bp.route('/<id>')
def eventDetails(id):
     event = db.session.scalar(db.select(event).where(event.id==id))
     form = CommentForm()
     return render_template('event.html', event=event, form=form)

@bp.route('/createevent', methods = ['GET', 'POST'])
@login_required
def createEvent():
  print('Method type: ', request.method)
  form = CreateEvent()
  if form.validate_on_submit():
    #call the function that checks and returns image
    db_file_path = check_upload_file(form)
    event = event(
    event_name=form.event_name.data,
    artist_name=form.artist_name.data,
    genre=form.genre.data,
    image = db_file_path,
    location=form.location.data,
    date=form.date.data,
    total_tickets=form.total_tickets.data,
    price=form.price.data,
    description=form.description.data)

    # add the object to the db session
    db.session.add(event)

    # commit to the database
    db.session.commit()
    flash('Successfully created new Event', 'success')
    return redirect(url_for('event.createEvent'))
  return render_template('create.html', form=form)

@bp.route('/<id>/comment', methods=['GET', 'POST'])  
@login_required
def comment(id):  
    form = CommentForm()  
    #get the destination object associated to the page and the comment
    event = db.session.scalar(db.select(event).where(event.id==id))
    if form.validate_on_submit():  
      #read the comment from the form
      comment = Comment(comment=form.text.data, event=event,
                        user=current_user) 
      #here the back-referencing works - comment.destination is set
      # and the link is created
      db.session.add(comment) 
      db.session.commit() 
      #flashing a message which needs to be handled by the html
      flash('Your comment has been added', 'success')  
      # print('Your comment has been added', 'success') 
    # using redirect sends a GET request to destination.show
    return redirect(url_for('event.eventDetails', id=id))

def check_upload_file(form):
  #get file data from form  
  fp = form.image.data
  filename = fp.filename
  #get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  #upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH,'static/image',secure_filename(filename))
  #store relative path in DB as image location in HTML is relative
  db_upload_path = 'static/image' + secure_filename(filename)
  #save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path

def checkAvailability(eventid):
   event = event.query.filter_by(eventid)
   eventTickets = event.total_tickets
   eventTicketsSold = event.tickets_sold
   tickets_remaining = eventTickets-eventTicketsSold
   return tickets_remaining