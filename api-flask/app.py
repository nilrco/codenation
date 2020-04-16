#!/usr/bin/venv python3

from flask import Flask, request, jsonify
from loguru import logger

from statsapi import data_store, operation


app = Flask(__name__)


@app.route("/data", methods=['POST'])
def save_data():
    logger.info(f"Saving data...")

    content = request.get_json()

    uuid = data_store.save(content["data"])

    logger.info(f"Data saved with uuid '{uuid}' succesfully")

    return jsonify({"status": "success", "message": "data saved with succesfully", "uuid": uuid})


@app.route("/data/<uuid>", methods=["GET"])
def retrieve_data(uuid):
    logger.info(f"Retrieving data associetad with uuid '{uuid}' ....")

    try:
        stored_data = data_store.get(uuid)
    except KeyError:
        logger.warning(f"Cannot retrieve data associetad with UUID '{uuid}'")

        return jsonify({"status": "failed", "message": "data cannot be retrieved", "data": []})

    logger.info(f"Data associetad with UUID '{uuid}' retrieved with succesfully")

    return jsonify({"status": "sucess", "message": "data retrieved succesfully", "data": stored_data})


@app.route("/data/<uuid>/<operation>", methods=["GET"])
def process_operation(uuid, operation):
    logger.info(f"Processing operation '{operation}' on data associeated with UUID: '{uuid}'...")

    try:
        stored_data = data_store.get(uuid)

        operation_func = get_operation(operation)

        result = operation_func(stored_data)
    except KeyError:
        logger.warning(f"Cannot retrieve data associetad with UUID '{uuid}'")

        return jsonify({"status": "failed", "message": "data cannot be retrieved", "results": None})
    except NoSuchOperationError:
        logger.warning(f"Cannot find operation '{operation}'")

        return jsonify({"status": "failed", "message": f"no such '{operation}' ", "results": None})

    logger.info(f"Operation '{operation}' on data with UUID '{uuid}' finished succesfully")

    return jsonify({"status": "sucess", "message": "resulted completed.", "result": result})


class NoSuchOperationError(Exception):
    pass


def get_operation(operation_name):
    if operation_name == 'min':
        return operation.op_min
    elif operation_name == 'max':
        return operation.op_max
    elif operation_name == 'mean':
        return operation.op_mean
    else:
        raise NoSuchOperationError


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
