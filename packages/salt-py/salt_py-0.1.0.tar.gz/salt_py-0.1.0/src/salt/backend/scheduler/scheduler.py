"""The scheduler component takes care of iterating through workflows and eventually trigger them."""

import time
import json

import redis
import pika

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from salt import settings

from loguru import logger


class Scheduler:
    def __init__(self):
        self._redis = redis.Redis(
            host=settings.redis_settings.redis_url,
            port=settings.redis_settings.redis_port,
            db=settings.redis_settings.redis_workflow_db,
        )
        self._rabbit = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.rabbit_settings.rabbit_url,
            credentials=pika.PlainCredentials(settings.rabbit_settings.rabbit_user, settings.rabbit_settings.rabbit_password)
        ))

    def loop(self):
        sched = BackgroundScheduler()
        sched.start()

        logger.info("Scanning Redis for active workflows...")
        while True:
            for key in self._redis.scan_iter(f"*"):
                workflow_json = self._redis.get(key)
                if not workflow_json:
                    continue

                workflow_data = json.loads(workflow_json)
                if workflow_data.get("paused"):
                    continue

                self.schedule_workflow(sched, workflow_data)

            time.sleep(5)

    def queue_workflow(self, workflow_data):
        """Once a workflow reaches this point, it will be queued using the workflow.queue field.

        The workflow.queue is used to set the rabbitmq queue to use to post the workflow schedule request.

        Once the workflow is in the queue, it will be picked by a Worker, which will execute it.
        TODO The handling of KILL signal (e.g. to stop the workflow) is handled using Kafka.
          Once the job is picked by a worker, the worker starts listening for KILL signals through Kafka or similar.
        """
        channel = self._rabbit.channel()
        queue = workflow_data.get("queue", "default")
        queue = "workflows" if queue == "default" else queue

        channel.queue_declare(queue="workflows", durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(workflow_data),
            properties=pika.BasicProperties(
                delivery_mode=2  # Make message persistent
            )
        )

        logger.debug(f"Queued [{workflow_data['workflow_id']}] v{workflow_data['version']} to queue: {queue}")


    def schedule_workflow(self, scheduler, workflow_data):
        schedule = workflow_data.get("schedule", {})
        workflow_id = workflow_data["workflow_id"]

        if schedule.get("type") == "interval":
            scheduler.add_job(
                func=self.queue_workflow,
                trigger=IntervalTrigger(seconds=int(schedule["every_seconds"])),
                id=workflow_data.get("id"),
                args=[workflow_data],
                replace_existing=True
            )
        elif schedule.get("type") == "cron":
            scheduler.add_job(
                func=self.queue_workflow,
                trigger=CronTrigger.from_crontab(schedule["cron"]),
                id=workflow_data.get("id"),
                args=[workflow_data],
                replace_existing=True
            )
        else:
            print(f"Unknown schedule type for workflow {workflow_id}")
