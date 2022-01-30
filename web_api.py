import flask

from flask import request, jsonify

import config
import api_handler


app = flask.Flask(__name__)
app.config['DEBUG'] = config.DEBUG


@app.route('/<requestType>', methods=['GET'])
def getRequest(requestType):  
    handler = api_handler.APIHandler(request, requestType)
    result = handler.get_result()
    return jsonify(result)

@app.route('/help', methods=['GET'])
def _help():
    return config.HELP_HTML

def main():
    app.run(port=config.PORT)


if __name__ == '__main__':
    main()
