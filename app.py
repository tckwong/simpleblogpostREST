import dbcreds
import mariadb
from flask import Flask, request, Response
import json
import sys
from flask_cors import CORS

#instantiate Flask object
app = Flask(__name__)

def connectDB():
    conn = None
    cursor = None

    try:
        conn=mariadb.connect(
                            user=dbcreds.user,
                            password=dbcreds.password,
                            host=dbcreds.host,
                            port=dbcreds.port,
                            database=dbcreds.database
                            )
        cursor = conn.cursor()
    except:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.close()
        raise ConnectionError("Failed to connect to the database")
    return (conn, cursor)

def getPosts():
    conn = None
    cursor = None
    
    try:
        (conn, cursor) = connectDB()
        cursor.execute("SELECT * FROM posts")
        list = cursor.fetchall()
        content_list = []
        content = {}
        for result in list:
            created_at = result[2]
            created_at_serialized = created_at.strftime("%Y-%m-%d")
            content = {
                "id": result[0],
                "content": result[1],
                "created_at": created_at_serialized
                }
            content_list.append(content)

        return Response(json.dumps(content_list), mimetype="application/json", status=200)
    except ConnectionError:
        print("Error while attempting to connect to the database")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()
    
def createPost():
    conn = None
    cursor = None
    try:
        (conn, cursor) = connectDB()
        data = request.json
        
        from datetime import datetime
        cur_date = datetime.today().strftime('%Y-%m-%d')
        client_content = data.get('content')

        if (client_content is not None):    
            
            resp = {
                "content": client_content,
            }
            cursor.execute("INSERT INTO posts (content, created_at) VALUES(?,?)", [client_content,cur_date])
            conn.commit()
        return Response(json.dumps(resp), mimetype="application/json", status=200)
    
    except ConnectionError:
        print("Error while attempting to connect to the database")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()

def updatePost():
    conn = None
    cursor = None
    try:
        (conn, cursor) = connectDB()
        data = request.json
        client_id = data.get('id')
        client_content = data.get('content')

        if (client_content is not None):
            
            resp = {
                "id": client_id,
                "content": client_content
            }
            cursor.execute("UPDATE posts SET content = ? WHERE id = ?", [client_content, client_id])
            conn.commit()
        
        return Response(json.dumps(resp), mimetype="application/json", status=200)
    except ConnectionError:
        print("Error while attempting to connect to the database")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()

def deletePost():
    conn = None
    cursor = None
    try:
        (conn, cursor) = connectDB()
        data = request.json
        client_id = data.get('id')

        if (client_id is not None):
            resp = {
                "id": client_id,
            }
            cursor.execute("DELETE FROM posts WHERE id = ?", [client_id])
            conn.commit()
        return Response(json.dumps(resp), mimetype="application/json", status=200)
    except ConnectionError:
        print("Error while attempting to connect to the database")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    finally:
        if (cursor != None):
            cursor.close()

        if (conn != None):
            conn.rollback()
            conn.close()

@app.route('/')
def homepage():
    return "<h1>Hello World</h1>"

@app.route('/api/posts', methods=['GET', 'POST', 'PATCH', 'DELETE'])

def blogPostsApi():
    if (request.method == 'GET'):
        return getPosts()
    elif (request.method == 'POST'):
        return createPost()
    elif (request.method == 'PATCH'):
        return updatePost() 
    elif (request.method == 'DELETE'):
        return deletePost() 
    else:
        print("Something went wrong.")

#Debug / production environments
if (len(sys.argv) > 1):
    mode = sys.argv[1]
    if (mode == "production"):
        from flask_cors import CORS
        CORS(app)
        import bjoern
        host = '0.0.0.0'
        port = 5005
        print("Server is running in production mode")
        bjoern.run(app, host, port)
    elif (mode == "testing"):
        from flask_cors import CORS
        CORS(app)
        print("Server is running in testing mode")
        app.run(debug=True)
        #Should not have CORS open in production
    else:
        print("Invalid mode arugement, exiting")
        exit()
else:
    print ("No arguement was provided")
    exit()

