# autopep8: off
import traceback
import socketio
import argparse
import asyncio
from urllib.parse import urlparse, urlunparse
import warnings

import websockets
warnings.simplefilter(action='ignore', category=FutureWarning)
import subprocess
import threading
import time
from dotenv import dotenv_values
import glob
import os
import sys
import json
import shutil
from flask import Blueprint, request, jsonify, send_file, Flask, abort

from .utils.system_utils import getCurrentCommitHash, getSystemInfo
from .task_executor import TaskExecutor
from .constant import ExecutorRegInfo, TaskExecution, ExecutorType

from .xai_sdk import *

from flask_cors import CORS
# autopep8: on


def create_tmp_dir(service_init_path):
    basedir = os.path.abspath(os.path.dirname(service_init_path))
    tmpdir = os.path.join(basedir, "tmp")
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)


def load_env(mode, **kwargs):
    os.environ["ENV"] = mode
    print("CWD:", os.getcwd())
    print("App Mode: ", os.environ["ENV"])
    env_file = os.path.join(os.getcwd(), f".env.{os.environ['ENV']}")

    for k, v in kwargs.items():
        os.environ[k] = v

    print("Env file: ", env_file)
    config = dotenv_values(env_file)
    for k in config.keys():
        if os.getenv(k) == None:
            os.environ[k] = config[k]


def set_app(app: Flask):
    # cors
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.static_folder = os.environ['COMPONENT_STATIC_PATH']


class ExecutorBluePrint(Blueprint):

    def __init__(
        self, init_file_name, component_path, *args, mongo=False, **kwargs
    ) -> None:
        print(sys.argv)
        if not sys.argv[0].endswith("flask"):
            self.app = 'dummy'
            print("Not in flask environment, skip the initialization, please use the 'flask --app ...' command to start the service")
            return
        load_env(os.environ.get("ENV", "dev"))

        self.te = TaskExecutor(
            component_path=component_path,
            mongo=mongo,
        )

        super().__init__(
            self.te.component_name,
            init_file_name,
            url_prefix=os.environ['CONTEXT_PATH'],
            *args, **kwargs
        )

        self.tmp_path = self.te.tmp_path

        executor_reg_infos = self.te.executor_reg_info_tb.all()
        if len(executor_reg_infos) > 0:
            self.te.sio = self.connect_central_ws(
                executor_reg_infos[0][ExecutorRegInfo.publisher_endpoint_url],
                executor_reg_infos[0][ExecutorRegInfo.executor_id],
                executor_reg_infos[0][ExecutorRegInfo.executor_endpoint_url],
            )

        @self.route("/reset", methods=["GET"])
        def reset():
            self.te.reset()
            return ""

        @self.route("/register_to_central", methods=["POST"])
        def register_to_central():
            if request.method == "POST":
                data = request.json
                central_url = data["central_url"]
                service_url = data["service_url"]

                self.publisher_endpoint_url = central_url
                self.te.component_info[ExecutorRegInfo.executor_endpoint_url] = service_url + \
                    os.environ['CONTEXT_PATH']
                resp = register_executor(
                    central_url, **self.te.component_info, sys_info=getSystemInfo())
                if resp.get(ExecutorRegInfo.executor_id) is not None:
                    resp[ExecutorRegInfo.publisher_endpoint_url] = self.publisher_endpoint_url
                    self.te.keep_reg_info(**resp)
                    self.te.sio = self.connect_central_ws(
                        self.publisher_endpoint_url,
                        resp[ExecutorRegInfo.executor_id],
                        resp[ExecutorRegInfo.executor_endpoint_url],
                    )
                    return resp

        @self.route("/get_available_task_function_key", methods=["GET"])
        def available_task_function_key():
            return jsonify(list(self.te.task_func_map.keys()))

        @self.route("/task_execution_result", methods=["GET"])
        def task_result():
            if request.method == "GET":
                task_ticket = request.args["task_ticket"]

                exp_rs_path = self.te.get_exp_rs_path(task_ticket)
                zip_path = os.path.join(
                    self.te.static_path, "rs", f"{task_ticket}.zip")

                if not os.path.exists(zip_path):
                    shutil.make_archive(
                        zip_path.replace('.zip', ''),
                        "zip",
                        exp_rs_path,
                    )

                if os.path.exists(zip_path):
                    return send_file(zip_path, as_attachment=True)
                else:
                    # TODO: should follow the restful specification
                    return "no such task"

        @self.route("/task_result_present", methods=["GET"])
        def task_result_present():
            if request.method == "GET":
                task_ticket = request.args["task_ticket"]
                pre = self.te.get_task_rs_presentation(task_ticket)
                return jsonify(pre)
            return ""

        @self.route("/task_status", methods=["GET", "POST"])
        def task_status():
            if request.method == "GET":
                task_ticket = request.args["task_ticket"]
                return jsonify(
                    {TaskExecution.task_status: self.te.get_task_actual_staus(
                        task_ticket)}
                )

        @self.route("/task_execution", methods=["GET", "POST"])
        def task():
            if request.method == "GET":
                pass
            else:
                form_data = request.form
                act = form_data["act"]
                # stop a task
                if act == "stop":
                    task_ticket = form_data[TaskExecution.task_ticket]
                    self.te.terminate_process(task_ticket)

                # execute a task which assigned by the central
                if act == "execute":
                    task_execution = json.loads(form_data["task_execution"])
                    pipeline_ticket = form_data.get("pipeline_ticket")
                    self.te.start_a_task(task_execution, pipeline_ticket)

                if act == "delete":
                    task_ticket = form_data[TaskExecution.task_ticket]
                    self.te.delete_the_task(task_ticket)

                if act == "run_sync":
                    task_function_key = form_data[TaskSheet.task_function_key]
                    task_parameters = json.loads(
                        form_data[TaskExecution.task_parameters])
                    task_parameters['request'] = request
                    task_parameters['run_mode'] = "run_sync"
                    publisher_endpoint_url = self.te.get_publisher_endpoint_url()
                    return jsonify(get_task_function(self.te.task_func_map, task_function_key)(
                        None,
                        publisher_endpoint_url,
                        task_parameters
                    ))

            return ""

        # @self.route("/executor", methods=["POST"])
        # def exe():
        #     return ""

        if self.te.component_info['executor_type'] == ExecutorType.dataset:
            @self.route("/dataset_source_file", methods=['GET'])
            def dataset_source_file():
                dataset_file = os.path.join(
                    self.te.component_path_parent, "dataset.py")
                if os.path.exists(dataset_file):
                    with open(dataset_file) as f:
                        content = f.read()
                        return content
                else:
                    abort(404)

        if self.te.component_info['executor_type'] == ExecutorType.model:
            @self.route("/model_source_file", methods=['GET'])
            def model_source_file():
                dataset_file = os.path.join(
                    self.te.component_path_parent, "model.py")
                if os.path.exists(dataset_file):
                    with open(dataset_file) as f:
                        content = f.read()
                        return content
                else:
                    abort(404)

        self.app = create_service(self)

    def get_task_executor(self):
        return self.te

    def connect_central_ws(self, central_url, executor_id, executor_endpoint_url):
        ws_url = central_url.replace('http', 'ws')
        print("executor_endpoint_url:", executor_endpoint_url)
        try:
            sio = socketio.Client()
            print(
                f"Trying to connect to central ws {ws_url} with id {executor_id}")
            sio.connect(
                ws_url,
                headers=dict(
                    Authorization=executor_endpoint_url,
                    EID=executor_id
                ),
                transports=['websocket']
            )

            print(f"Connected to central ws {ws_url} with id {executor_id}")

            @sio.on('ping')
            def on_message(data):
                if os.environ.get("SHOW_CLIENT_WS_PING", "0") == '1':
                    print('I received a ping!')
                sio.emit('ping', 'pong')

            @sio.on('message')
            def on_message(data):
                print('I received a message!')
                # ... connect to a server and use the client
                # ... no need to manually disconnect!

            return sio
        except Exception as e:
            print("Central ws connection failed")
            traceback.print_exc()


def create_service(bp: ExecutorBluePrint):
    context_path = os.environ["CONTEXT_PATH"]
    static_url_path = context_path + "/static"

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_url_path=static_url_path
    )

    set_app(app)
    app.register_blueprint(bp)

    bp.te.component_info[ExecutorRegInfo.executor_info]['code_version_hash'] = getCurrentCommitHash()
    print("Current code version hash: ",
          bp.te.component_info[ExecutorRegInfo.executor_info]['code_version_hash'])

    return app
