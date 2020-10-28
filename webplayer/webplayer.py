'''main flask app setup'''
from flask import Flask
from webplayer.file_handler import mod as mod_file_handler
from webplayer.bookmarks import mod as mod_bookmarks
from webplayer.list_handler import mod as mod_list_handler
from webplayer.config import mod as mod_config_handler

app = Flask(__name__, instance_relative_config=True)

app.config.from_object('config')
app.config.from_pyfile('webplayer.cfg', silent=True)

app.register_blueprint(mod_file_handler)
app.register_blueprint(mod_bookmarks)
app.register_blueprint(mod_list_handler)
app.register_blueprint(mod_config_handler)
