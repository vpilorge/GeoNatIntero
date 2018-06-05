#!/usr/bin/python3
import os
import logging
import asyncio
import concurrent.futures
from datetime import datetime
# import gzip
import psycopg2

dsn = "dbname='geonaturedb' host='localhost' user='geonatuser' password='monpassachanger'"
exports_path='/home/pat/geonature/backend/static/exports/export_{id}.{ext}'
selector = "COPY (SELECT {} FROM gn_intero.v_export) TO STDOUT WITH CSV HEADER DELIMITER ',';"
num_workers = max(1, len(os.sched_getaffinity(0)) - 1)
queue = asyncio.Queue(maxsize=0)

asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.setLevel(logging.DEBUG)
console_logger = logging.StreamHandler()
asyncio_logger.addHandler(console_logger)
loop = asyncio.get_event_loop()
loop.set_debug = True


def export_csv(args):
    with psycopg2.connect(dsn) as db:
        with db.cursor() as cursor:
            submission_ts, columns = args

            submissionID = (
                datetime.strptime(str(submission_ts), '%Y-%m-%d %H:%M:%S.%f') -
                datetime.utcfromtimestamp(0)).total_seconds()

            if (isinstance(columns, str) or isinstance(columns, unicode)):
                columns = columns.split(',')

            statement = selector.format(
                ','.join(['"{}"'.format(column) for column in columns])
                if len(columns) > 1 else '"{}"'.format(columns[0]))

            # with gzip.open
            with open(exports_path.format(id=submissionID, ext='csv'), 'wb') as export:
                cursor.execute('UPDATE gn_intero.t_exports SET start=NOW() WHERE submission=%s', (submission_ts,))
                try:
                    cursor.copy_expert(statement, export)
                    cursor.execute('UPDATE gn_intero.t_exports SET ("end", "log", "status")=(NOW(), %s, %s) WHERE submission=%s',
                              (cursor.rowcount, 0, submission_ts))
                except (Exception, psycopg2.InternalError) as e:
                    db.rollback()
                    print('EXCEPTION CAUGHT:', submission_ts)
                    cursor.execute('UPDATE gn_intero.t_exports SET ("end", "log", "status")=(NULL, %s, -1) WHERE submission=%s',
                              (str(e), submission_ts))
                finally:
                    db.commit()


async def process(queue=queue, loop=loop):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        if queue.empty():
            return None
        task = await queue.get()
        func = task['func']
        args = task['args']
        return loop.run_in_executor(executor, func, args)


async def run(queue=queue, num_workers=num_workers):
    with psycopg2.connect(dsn) as db:
        with db.cursor() as cursor:
            cursor.execute('SELECT submission, selection FROM gn_intero.t_exports WHERE "start" IS NULL AND status=-2 ORDER BY submission ASC;')
            for record in cursor.fetchall():
                submissionID = (
                    datetime.strptime(str(record[0]), '%Y-%m-%d %H:%M:%S.%f') -
                    datetime.utcfromtimestamp(0)).total_seconds()
                queue.put_nowait({'func': export_csv, 'args': (record)})
    while not queue.empty():
        tasks = [process(queue) for i in range(num_workers)]
        for future in asyncio.as_completed(tasks):
            result = await future


if __name__ == '__main__':

    loop.run_until_complete(run())
