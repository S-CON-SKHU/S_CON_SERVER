import os
import werkzeug
from flask import Flask, jsonify, Response, request
from flask_restful import Resource, Api, reqparse
import makeJson
from web import makeJsonForios
from flask_cors import CORS, cross_origin
import DB
import openpyxl as oxl

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, resources={r'*': {'origins': 'http://localhost:3000'}})
api = Api(app)


@app.route('/web/<part>/<int:year>', methods=['GET', 'POST'])
def webGet(part, year):
    '''
    if part == "all":
        temp = readJson.read_json()
    elif year == 0:
        temp = readJson.read_json(part, year)
    else:
        temp = readJson.read_json()
    '''
    temp = makeJson.makejson(part, year)
    return jsonify(temp)

@app.route('/ios/<part>/<int:year>', methods=['GET', 'POST'])
def iosGet(part, year):
    temp = makeJsonForios.makejson(part, year)
    return jsonify(temp)


class Upload(Resource):
    def post(self):
        my_res = Response()
        http_method = request.method
        if http_method == "POST":
            print("--사전 요청(Preflight Request)--")
            my_res.headers.add("Access-Control-Allow-Origin", "*")
            my_res.headers.add('Access-Control-Allow-Headers', "*")
            my_res.headers.add('Access-Control-Allow-Methods', "*")

        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()

        file_object = args['file']

        if file_object is None:
            return jsonify({'result': 'false'})
        else:
            file_path = os.path.join(os.getcwd(), file_object.filename)
            fileName = file_object.filename
            file_object.save(dst=file_object.filename)

            temp = oxl.load_workbook(fileName)
            temp = temp['Sheet1']
            #2 ~ 18까지 데이터 있음.
            for column in temp.columns:
                #2번 행이 비었다는건 비어있는 열이라는 뜻이므로 스톱
                if column[0].value == None:
                    continue

                elif column[1].value == None:
                    break

                text = column[1:19]
                DB.insertToDB(text)


            return jsonify({'result':file_path})


api.add_resource(Upload, '/upload')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

