#!/usr/bin/python3
# TODO: PID.lockfile
# TODO: continue processing on export failure -> error handler

import os
import logging
import asyncio
import concurrent.futures
from datetime import datetime
from enum import IntEnum
# import gzip
import psycopg2

dsn = "dbname='geonaturedb' host='localhost' user='geonatuser' password='monpassachanger'"  # noqa
exports_path = '/home/pat/geonature/backend/static/exports/export_{id}.{ext}'
num_workers = max(1, len(os.sched_getaffinity(0)) - 1)
queue = asyncio.Queue(maxsize=0)

logger = logging.getLogger(__name__)
console_logger = logging.StreamHandler()
logger.addHandler(console_logger)
logger.setLevel(logging.DEBUG)
asyncio_logger = logging.getLogger('asyncio')
asyncio_logger.setLevel(logging.DEBUG)
asyncio_console_logger = logging.StreamHandler()
asyncio_logger.addHandler(asyncio_console_logger)
loop = asyncio.get_event_loop()
loop.set_debug = True


def export_csv():
    return "COPY (SELECT {} FROM gn_intero.v_export) TO STDOUT WITH CSV HEADER DELIMITER ',';"


def export_json():
    return "COPY (select json_agg(t) from (select {} from gn_intero.v_export) as t) TO STDOUT;"


def export_rdf():
    raise NotImplementedError


class Format(IntEnum):
    CSV = 1
    JSON = 2
    RDF = 4


format_map_ext = {
    Format.CSV: 'csv',
    Format.JSON: 'json',
    Format.RDF: 'rdf'
}


format_map_func = {
    Format.CSV: export_csv,
    Format.JSON: export_json,
    Format.RDF: export_rdf
}


class Standard(IntEnum):
    DRWC = 1
    ABCD = 2
    EML = 4


def export(ts, columns, format):
    def ts_to_export_fname(ts):
        return (datetime.strptime(str(ts), '%Y-%m-%d %H:%M:%S.%f') - datetime.utcfromtimestamp(0)).total_seconds()

    with psycopg2.connect(dsn) as db:
        with db.cursor() as cursor:

            fname = ts_to_export_fname(ts)

            if isinstance(columns, str):
                columns = columns.split(',')

            extension = format_map_ext[format]
            statement = format_map_func[format]()
            statement = statement.format(
                ','.join(['"{}"'.format(column) for column in columns])
                if len(columns) > 1 else '"{}"'.format(columns[0]))

            # with gzip.open
            with open(exports_path.format(id=fname, ext=extension), 'wb') as export_file:
                # log_start
                cursor.execute('UPDATE gn_intero.t_exports SET start=NOW() WHERE id=%s', (ts,))
                try:

                    cursor.copy_expert(statement, export_file)

                    # log_end
                    cursor.execute('UPDATE gn_intero.t_exports SET ("end", "log", "status")=(NOW(), %s, %s) WHERE id=%s',
                                   (cursor.rowcount, 0, ts))
                except (psycopg2.InternalError, psycopg2.ProgrammingError, Exception) as e:
                    db.rollback()
                    # log_fault
                    cursor.execute('UPDATE gn_intero.t_exports SET ("end", "log", "status")=(NULL, %s, -1) WHERE id=%s',
                                   (str(e), ts))
                finally:
                    db.commit()


async def process(executor, queue=queue, loop=loop):
        if queue.empty():
            return None
        task = await queue.get()
        return loop.run_in_executor(executor, task['func'], task['args'])


async def run(queue=queue, num_workers=num_workers):
    with psycopg2.connect(dsn) as db:
        with db.cursor() as cursor:
            cursor.execute('SELECT id, selection, format FROM gn_intero.t_exports WHERE "start" IS NULL AND status=-2 ORDER BY id ASC;')
            for record in cursor.fetchall():
                queue.put_nowait({'func': export, 'args': (record)})

    with concurrent.futures.ProcessPoolExecutor() as executor:
        while not queue.empty():
            tasks = [process(executor, queue) for i in range(num_workers)]
            for future in asyncio.as_completed(tasks):
                result = await future
                logger.debug('%s', result)


if __name__ == '__main__':

    loop.run_until_complete(run())
