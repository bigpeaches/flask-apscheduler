# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from collections import OrderedDict
from flask import current_app, request, Response
from .utils import job_to_dict, jsonify


def get_scheduler_info():
    """Gets the scheduler info."""

    scheduler = current_app.apscheduler

    d = OrderedDict([
        ('current_host', scheduler.host_name),
        ('allowed_hosts', scheduler.allowed_hosts),
        ('running', scheduler.running)
    ])

    return jsonify(d)


def add_job():
    """Adds a new job."""

    data = request.get_data(as_text=True)

    try:
        data = json.loads(data)
        job = current_app.apscheduler.add_job(**data)
        return jsonify(job_to_dict(job))
    except ConflictingIdError:
        return jsonify(dict(error_message='Job %s already exists.' % data.get('id')), status=409)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def delete_job(job_id):
    """Deletes the specified job."""

    try:
        current_app.apscheduler.delete_job(job_id)
        return Response(status=204)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def get_job(job_id):
    """Gets the specified job."""

    job = current_app.apscheduler.scheduler.get_job(job_id)

    if not job:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)

    return jsonify(job_to_dict(job))


def get_jobs():
    """Gets all jobs scheduled."""

    jobs = current_app.apscheduler.scheduler.get_jobs()

    job_states = []

    for job in jobs:
        job_states.append(job_to_dict(job))

    return jsonify(job_states)


def pause_job(job_id):
    """Pauses the specified job."""

    try:
        current_app.apscheduler.pause_job(job_id)
        job = current_app.apscheduler.scheduler.get_job(job_id)
        return jsonify(job_to_dict(job))
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def resume_job(job_id):
    """Resumes the specified job."""

    try:
        current_app.apscheduler.resume_job(job_id)
        job = current_app.apscheduler.scheduler.get_job(job_id)
        return jsonify(job_to_dict(job))
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def run_job(job_id):
    """Executes the specified job."""

    try:
        current_app.apscheduler.run_job(job_id)
        job = current_app.apscheduler.scheduler.get_job(job_id)
        return jsonify(job_to_dict(job))
    except LookupError:
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)
