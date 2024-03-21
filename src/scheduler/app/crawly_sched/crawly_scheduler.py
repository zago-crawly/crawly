from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined
import six

from apscheduler.job import Job
from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from apscheduler.events import (JobEvent, EVENT_JOB_ADDED)
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.events import (
    SchedulerEvent, JobEvent, EVENT_SCHEDULER_START)

# #: constant indicating a scheduler's stopped state
STATE_STOPPED = 0
# #: constant indicating a scheduler's running state (started and processing jobs)
STATE_RUNNING = 1
# #: constant indicating a scheduler's paused state (started but not processing jobs)
# STATE_PAUSED = 2


class CrawlyScheduler(BackgroundScheduler):
    def add_job(self, func, template_uuid: str, schema_uuid: str,
                trigger=None, args=None, kwargs=None, id=None, name=None,
                misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined,
                next_run_time=undefined, jobstore='default', executor='default',
                replace_existing=False, **trigger_args):

        job_kwargs = {
            'trigger': self._create_trigger(trigger, trigger_args),
            'executor': executor,
            'func': func,
            'args': tuple(args) if args is not None else (),
            'kwargs': dict(kwargs) if kwargs is not None else {},
            'id': id,
            'name': name,
            'misfire_grace_time': misfire_grace_time,
            'coalesce': coalesce,
            'max_instances': max_instances,
            'next_run_time': next_run_time
        }
        job_kwargs = dict((key, value) for key, value in six.iteritems(job_kwargs) if
                          value is not undefined)
        job = Job(self, **job_kwargs)

        # Don't really add jobs to job stores before the scheduler is up and running
        with self._jobstores_lock:
            if self.state == STATE_STOPPED:
                self._pending_jobs.append((job, jobstore, replace_existing))
                self._logger.info('Adding job tentatively -- it will be properly scheduled when '
                                  'the scheduler starts')
            else:
                self._real_add_job(job,
                                   jobstore,
                                   replace_existing,
                                   template_uuid=template_uuid,
                                   schema_uuid=schema_uuid)

        return job
  
    def _real_add_job(self, job, jobstore_alias, replace_existing, template_uuid: str, schema_uuid: str):
        
        # Fill in undefined values with defaults
        replacements = {}
        for key, value in six.iteritems(self._job_defaults):
            if not hasattr(job, key):
                replacements[key] = value

        # Calculate the next run time if there is none defined
        if not hasattr(job, 'next_run_time'):
            now = datetime.now(self.timezone)
            replacements['next_run_time'] = job.trigger.get_next_fire_time(None, now)

        # Apply any replacements
        job._modify(**replacements)

        # Add the job to the given job store
        store = self._lookup_jobstore(jobstore_alias)
        try:
            store.add_job(job, template_uuid, schema_uuid)
        except ConflictingIdError:
            if replace_existing:
                store.update_job(job)
            else:
                raise

        # Mark the job as no longer pending
        job._jobstore_alias = jobstore_alias

        # Notify listeners that a new job has been added
        event = JobEvent(EVENT_JOB_ADDED, job.id, jobstore_alias)
        self._dispatch_event(event)

        self._logger.info('Added job "%s" to job store "%s"', job.name, jobstore_alias)

        # Notify the scheduler about the new job
        if self.state == STATE_RUNNING:
            self.wakeup()

    def get_job_by_template(self, job_id, jobstore=None):
        """
        Returns the Job that matches the given ``job_id``.

        :param str|unicode job_id: the identifier of the job
        :param str|unicode jobstore: alias of the job store that most likely contains the job
        :return: the Job by the given ID, or ``None`` if it wasn't found
        :rtype: Job

        """
        with self._jobstores_lock:
            try:
                return self._lookup_job(job_id, jobstore)[0]
            except JobLookupError:
                return
            
    def _lookup_jobs_by_condition(self, condition, jobstore_alias):
        """
        Finds a job by some condition.

        :type job_id: str
        :param str jobstore_alias: alias of a job store to look in
        :return tuple[Job, str]: a tuple of job, jobstore alias (jobstore alias is None in case of
            a pending job)
        :raises JobLookupError: if no job by the given ID is found.

        """
        # Look in all job stores
        for alias, store in six.iteritems(self._jobstores):
            if jobstore_alias in (None, alias):
                job = store.lookup_job_with_condition(condition)
                if job is not None:
                    return job, alias

        raise JobLookupError(condition)