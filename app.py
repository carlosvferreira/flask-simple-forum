from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Thread(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  date_created = db.Column(db.DateTime, default=datetime.now)
  comments = db.relationship('Comment', backref="thread", cascade="all, delete, delete-orphan")
  
  def __repr__(self):
    return '<Thread %r>' % self.title

class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=False)
  date_created = db.Column(db.DateTime, default=datetime.now)
  thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

  def __repr__(self):
    return '<Comment %r>' % self.content

@app.route('/')
def index():
  threads = Thread.query.order_by(Thread.date_created.desc()).all()
  return render_template('index.html', threads=threads)

@app.route('/new', methods=['GET', 'POST'])
def new():

  new_thread = None

  if request.method == 'POST' and request.form['content'] != "" and request.form['title'] != "":
    thread_content = request.form['content']
    thread_title = request.form['title']
    new_thread = Thread(content=thread_content, title=thread_title)

    try:
      db.session.add(new_thread)
      db.session.commit()
      return redirect('/') #correct this code to redirect to created thread page if possible

    except:
      return 'Tere was an error while creating the thread'

  elif request.method == 'POST' and request.form['content' or 'title'] == "":
    return 'Please insert a title and content to create a new thread'

  else:
    return render_template('new.html', new_thread=new_thread)

@app.route('/delete/<int:id>')
def delete(id):
  thread_to_delete = Thread.query.get_or_404(id)

  db.session.delete(thread_to_delete)
  db.session.commit()
  return redirect('/')


@app.route('/view/<int:id>', methods=['GET', 'POST'])
def view(id):
  thread = Thread.query.get_or_404(id)
  new_comment = None
  comment = Comment.query.filter(Comment.thread_id == thread.id).order_by(Comment.date_created).all()

  if request.method == 'POST' and request.form['content'] != "":
    comment_content = request.form['content']
    thread_parent = thread
    new_comment = Comment(content=comment_content, thread=thread_parent)

    try:  
      db.session.add(new_comment)
      thread.comments.append(new_comment)
      db.session.commit()
      return redirect(request.url)
    except:
      return 'There was an error while creating the comment'


  else:
    return render_template('view.html', thread=thread, comment=comment)

if __name__ == "__main__":
  app.run(debug=True)
  db.create_all()