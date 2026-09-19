from flask import Flask, flash, jsonify, redirect, render_template, request, session
#from flask_session import Session

import os
import subprocess
import re
import json
import datetime
app = Flask(__name__)

@app.route('/')
def index():
    current_session =  os.environ.get("SESSION") if "SESSION" in os.environ else "6b2cbf7c-ba48-4cff-9fd4-cd22974fe756"
    return redirect(f"/{current_session}", code=302)    

@app.route("/<session>", methods=["GET"])
def get_domain(session):
    workers = []
    is_aws  = True if os.environ.get("AWS_DEFAULT_REGION") else False
    current_session = session
    path    =  "/tricarros_commons/olx_spider" if is_aws else "./tricarros_commons/olx_spider"

    directory = f"{path}/{current_session}"

    if not os.path.exists(directory):
        return f"{directory} not found"
    files = [f.name for f in os.scandir(directory) if (os.path.isfile(f)) and (f.name[:18] == 'page_crawled_times')] 
    sessions = [f"{f.name} @ " + datetime.datetime.fromtimestamp(os.lstat(f"{path}/{f.name}").st_mtime).isoformat() for f in os.scandir(f'{path}') if (f.is_dir()) and (f.name[-1:] != ')')] 
    sessions = [{"id": f.name, "timestamp": datetime.datetime.fromtimestamp(os.lstat(f"{path}/{f.name}").st_mtime).isoformat()} for f in os.scandir(f'{path}') if (f.is_dir()) and (f.name[-1:] != ')')]     
    sessions = sorted(sessions, key=lambda d: d['timestamp']) 
    print(sessions)
    page_detail = {
                        "start_crawling_time": "2023-11-02 21:39:45.365756",
                        "current_time": f"{datetime.datetime.now()}",
                        "elapsed_crawling_time": "0:24:51.140971",
                        "estimated_crawling_time": "0:24:51.140971",
                        "remaining_crawling_time": "0:00:00",
                        "crawled_pages": "0",
                        "total_pages": "0",
                        "percentage": "100",
                        "page_speed": "",
                        "page_duplicated_filtered": "0"
                    }
    for file in files:
        taskno  = re.findall(r'([a-z\-]+).json$', file)[0]
        with open(f"{directory}/page_crawled_times_{taskno}.json") as user_file:
            parsed_page_crawled_times_json = json.load(user_file)
            page_detail['total_pages'] = int(page_detail['total_pages']) + int(parsed_page_crawled_times_json['total_pages'])
            page_detail['crawled_pages'] = int(page_detail['crawled_pages']) + int(parsed_page_crawled_times_json['crawled_pages'])
        output = json.dumps(parsed_page_crawled_times_json, indent=4)
        #subprocess.check_output(f"python3 {directory}/summary.py {taskno}", shell=True)
        workers.append({"id": taskno, "pre": output, "data": parsed_page_crawled_times_json})
  
    elapsed_crawling_time = datetime.datetime.now() - datetime.datetime.fromisoformat(page_detail["current_time"])     
    estimated_crawling_time = elapsed_crawling_time / (int(page_detail['crawled_pages'])/int(page_detail['total_pages']))   
    remaining_crawling_time = estimated_crawling_time - elapsed_crawling_time


    return render_template("home.html", current_session=current_session, sessions=sessions, workers=workers, summary={"OK": page_detail['crawled_pages'], "pending": int(page_detail['total_pages']) - int(page_detail['crawled_pages']), "total": page_detail['total_pages']})


@app.route('/hello')
def hello():
    files = [f for f  in os.scandir("/")]
    try:
        files_tricarros = [f for f  in os.scandir("/tricarros_commons")]
    except:
        files_tricarros = "erro"
    return f"World (env: {str(os.environ)}, dir: {str(files)}, files_tricarros: {str(files_tricarros)})"

app.run(host='0.0.0.0', port=80)