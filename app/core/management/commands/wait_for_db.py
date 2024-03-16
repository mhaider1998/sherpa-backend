'''
Make Django wait for the database to be available.
'''

import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Write a message to the screen while waiting for the database to be available.
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                # Try to execute a simple query against the database.
                # If it fails, an exception will be raised.
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
