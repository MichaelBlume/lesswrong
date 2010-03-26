#!/usr/bin/env python

from subprocess import Popen, PIPE
import os

LESSWRONG_DIR='/home/mike/production/lesswrong/' #You should change this.

PORT=8080
INI_FILE='development.ini'
LOGFILE='lesswrong.log'
POSTGRES_RUNFILE='/var/run/postgresql/.s.PGSQL.5432'
POSTGRES_BIN='/usr/lib/postgresql/8.2/bin/postgres'
POSTGRES_DATA='/usr/local/pgsql/data'
MEMCACHED_BIN='/etc/init.d/memcached'
POSTGRES_USER='postgres'
POSTGRES_READY_STRING='database system is ready'

lesswronglog=open(LESSWRONG_DIR+LOGFILE, 'w')

memcached=Popen(['sudo', MEMCACHED_BIN, 'restart'], stdout=PIPE)
lesswronglog.write('Restarting memcached...\n')
lesswronglog.write('sudo ' + MEMCACHED_BIN + ' restart\n')
memcached.wait()
lesswronglog.write('memcached ready.\n')

if not os.path.exists(POSTGRES_RUNFILE):
    lesswronglog.write('postgres not running. Starting now.\n')
    postgres=Popen(['sudo', '-u', POSTGRES_USER, POSTGRES_BIN, '-D',
                     POSTGRES_DATA], stderr=PIPE)
    lesswronglog.write('sudo -u ' + POSTGRES_USER + ' ' + POSTGRES_BIN
                        + ' -D ' + POSTGRES_DATA)
    lesswronglog.write('Waiting for postgres to be ready...\n')
    line='thisishacky'
    while line:
        line=postgres.stderr.readline()
        lesswronglog.write(line)
        if POSTGRES_READY_STRING in line:
            break
    else:
        postgres.kill()
        raise Exception('Database Fail!')
else:
    lesswronglog.write('postgres already running. Leaving it alone.\n')

lesswronglog.write('switching to LW directory: ' + LESSWRONG_DIR + 'r2\n')
os.chdir(LESSWRONG_DIR + 'r2')

lesswrong=Popen(['lesswrongd','serve','--reload', INI_FILE, 'port='+str(PORT)],
                stdout=lesswronglog, stderr=lesswronglog, executable='paster')
lesswronglog.write('starting up Less Wrong on port ' + str(PORT) + '\n')
lesswronglog.write('lesswrongd serve --reload ' + INI_FILE + 'port=' + str(PORT) + '\n')

print "Less Wrong running on port " + str(PORT) + " and PID " + str(lesswrong.pid)
print "Type 'sudo kill " + str(lesswrong.pid) + "' to stop it."
