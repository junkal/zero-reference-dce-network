import flask
import cv2, io, os, base64, json
import argparse
import numpy as np
import uuid
import jwt
import datetime
import tensorflow as tf
from model.dce_model import ZeroDCE
from PIL import Image
from tensorflow import keras
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = flask.Flask(__name__)
app.config['SECRET_KEY']='dtu4efv@$7hio8jkp=+.39caGWLbdzx'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.abspath(os.getcwd())+"//database//database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

zero_dce_model = None
db = SQLAlchemy(app)

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.Integer)
  username = db.Column(db.String(50))
  password = db.Column(db.String(50))

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if "X-Access-Tokens" in flask.request.headers:
			token = flask.request.headers["X-Access-Tokens"]
		else:
			return flask.jsonify({'message': 'Token is missing'}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
			current_user = Users.query.filter_by(public_id=data['public_id']).first()
		except jwt.DecodeError:
			return flask.jsonify({'message': 'Decode Failure'}), 401

		except jwt.exceptions.ExpiredSignatureError:
			return flask.jsonify({'message': 'Token has expired'}), 401

		return f(current_user, *args, **kwargs)
	return decorated


@app.route('/register', methods=['GET', 'POST'])
def register_user():
	data = flask.request.get_json()

	hashed_password = generate_password_hash(data['password'], method='sha256')
	new_user = Users(public_id = str(uuid.uuid4()),
					 username = data['username'],
					 password = hashed_password)

	try:
		db.session.add(new_user)
		db.session.commit()
	except exc.SQLAlchemyError:
		print("[Error] Add user error")
		return flask.jsonify({'message': 'register user failed!'})

	return flask.jsonify({'message': 'registered successfully'})

@app.route('/login', methods=['GET', 'POST'])
def login_user():

	auth = flask.request.authorization

	if not auth or not auth.username or not auth.password:
		return flask.jsonify('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

	user = Users.query.filter_by(username=auth.username).first()

	if user is not None:
		if check_password_hash(user.password, auth.password):
			token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

			return flask.jsonify({"message": "login OK!", "token" : token})
	else:
		return flask.jsonify({"message" : "[Error] Unknown username {}".format(auth.username)})

	return flask.jsonify({"message" : "Fail to login"})


@app.route("/predict", methods=["POST"])
@token_required
def predict(current_user):

	data = {"success": False}

	if flask.request.files.get("image"):
		# read the image in PIL format
		filename = flask.request.files["filename"].read().decode("utf-8")
		file_ext = os.path.splitext(filename)[1]

		if file_ext in ['.jpg', '.png', '.jpeg']:
			image = flask.request.files["image"].read()
			image = Image.open(io.BytesIO(image))
			image = keras.preprocessing.image.img_to_array(image)
			image = image.astype("float32") / 255.0
			image = np.expand_dims(image, axis=0)

			enhanced_image = zero_dce_model(image)
			enhanced_image = tf.cast((enhanced_image[0, :, :, :] * 255), dtype=np.uint8)
			enhanced_image = Image.fromarray(enhanced_image.numpy())

			img_byte_arr = io.BytesIO()
			enhanced_image.save(img_byte_arr, format="jpeg")
			im_b64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

			data['filename'] = filename
			data['image'] = im_b64
			data["size"] = enhanced_image.size
			data["success"] = True
		else:
			print("[ERROR] Unacceptable image file extension {}".format(file_ext))

	return flask.jsonify(data) #or return json.dumps(data)

if __name__ == '__main__':
	print("[INFO] *** Loading ZeroDCE Keras model and Flask starting server..."
		  "please wait until server has fully started ***")

	if not os.path.exists("database"):
		os.makedirs("database")

	db.create_all()

	print("[INFO] Remember to set environment variable ENV using: export ENV=<variable name>")
	zero_dce_model = ZeroDCE()
	zero_dce_model.load_weights("./model/model_last_weights.h5")
u
	environment = os.getenv('ENV')
	if environment == "local":
	 	app.run(host="127.0.0.1", port=4000, debug=True)
	elif environment == "webservice":
	 	app.run(host="0.0.0.0", port=4000, debug=True)
	else:
		print("[ERROR] Unknown environment, default to local IP")
		app.run(host="127.0.0.1", port=4000, debug=True)
