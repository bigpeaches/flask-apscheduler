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

"""Utility module."""

import json
import dateutil.parser

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from collections import OrderedDict
from flask import Response


def job_to_dict(job):
    """Converts a job to an OrderedDict."""

    data = OrderedDict()
    data['id'] = job.id
    data['name'] = job.name
    data['func'] = job.func_ref
    data['args'] = job.args
    data['kwargs'] = job.kwargs

    data.update(trigger_to_dict(job.trigger))

    if not job.pending:
        data['misfire_grace_time'] = job.misfire_grace_time
        data['max_instances'] = job.max_instances
        data['next_run_time'] = None if job.next_run_time is None else job.next_run_time.isoformat()

    return data


def trigger_to_dict(trigger):
    """Converts a trigger to an OrderedDict."""

    data = OrderedDict()

    if isinstance(trigger, DateTrigger):
        data['trigger'] = 'date'
        data['run_date'] = trigger.run_date.isoformat()
    elif isinstance(trigger, IntervalTrigger):
        data['trigger'] = 'interval'
        data['start_date'] = trigger.start_date.isoformat()

        if trigger.end_date:
            data['end_date'] = trigger.end_date.isoformat()

        w, d, hh, mm, ss = extract_timedelta(trigger.interval)

        if w > 0:
            data['weeks'] = w
        if d > 0:
            data['days'] = d
        if hh > 0:
            data['hours'] = hh
        if mm > 0:
            data['minutes'] = mm
        if ss > 0:
            data['seconds'] = ss
    elif isinstance(trigger, CronTrigger):
        data['trigger'] = 'cron'

        if trigger.start_date:
            data['start_date'] = trigger.start_date.isoformat()

        if trigger.end_date:
            data['end_date'] = trigger.end_date.isoformat()

        for field in trigger.fields:
            if not field.is_default:
                data[field.name] = int(str(field))
    else:
        data['trigger'] = str(trigger)

    return data


def jsonify(data, status=None):
    return Response(json.dumps(data, indent=2), status=status, mimetype='application/json')


def fix_job_def(job_def):
    if isinstance(job_def.get('start_date'), str):
        job_def['start_date'] = dateutil.parser.parse(job_def.get('start_date'))

    if isinstance(job_def.get('end_date'), str):
        job_def['end_date'] = dateutil.parser.parse(job_def.get('end_date'))

    if isinstance(job_def.get('run_date'), str):
        job_def['run_date'] = dateutil.parser.parse(job_def.get('run_date'))

    # it keeps compatibility backward
    if isinstance(job_def.get('trigger'), dict):
        trigger = job_def.pop('trigger')
        job_def['trigger'] = trigger.pop('type', 'date')
        job_def.update(trigger)


def extract_timedelta(delta):
    w, d = divmod(delta.days, 7)
    mm, ss = divmod(delta.seconds, 60)
    hh, mm = divmod(mm, 60)
    return w, d, hh, mm, ss
