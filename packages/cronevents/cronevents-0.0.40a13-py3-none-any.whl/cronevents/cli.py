import argparse
import os
import sys
import time

import cronevents.event_manager
import cronevents.register


service_name = 'cronevents-manager.service'
suggested_service_path = f'/etc/systemd/system/{service_name}'
system_service_config = '''
[Unit]
Description=Handler to manaage Cron Events using the cronevents package
After=network.target

[Service]
WorkingDirectory={{path}}
ExecStart=/bin/bash -c 'source venv/bin/activate && cronevents manager'
Type=simple
RemainAfterExit=no
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
'''

reload_command = 'sudo systemctl daemon-reload'
start_service_command = f'sudo systemctl start {service_name}'
stop_service_command = f'sudo systemctl stop {service_name}'
enable_service_command = f'sudo systemctl enable {service_name}'
status_service_command = f'sudo systemctl status {service_name}'
follow_service_command = f'sudo journalctl -fau {service_name}'
restart_service_command = f'sudo systemctl restart {service_name}'

service_commands = f'''
First , create a service file at {suggested_service_path} with the following content:
run: `cronevents service-file --path {"{{path}}"} > {suggested_service_path}`

Then make changes as needed:
run: `sudo nano {suggested_service_path}`

Then reload the systemd daemon:
run: `{reload_command}`

Then start the service:
run: `{start_service_command }`

To check the status of the service:
run: `{status_service_command}`

To enable the service on boot:
run: `{enable_service_command}`
'''


def cli():
    parser = argparse.ArgumentParser(description='Buelon command-line interface')
    parser.add_argument('-v', '--version', action='version', version='Cron Events 0.0.40-alpha13')

    subparsers = parser.add_subparsers(title='Commands', dest='command', required=False)

    # Hub command
    hub_parser = subparsers.add_parser('manager', help='Run the hub')
    hub_parser.add_argument('-p', '--postgres', required=False, help='Postgres connection (host:port:user:password:database)')

    # Register command
    register_parser = subparsers.add_parser('register', help='Register a new event')
    register_parser.add_argument('-p', '--postgres', required=False, help='Postgres connection (host:port:user:password:database)')
    register_parser.add_argument('-f', '--file', required=True, help='Python file path with event decorators')

    #  Service command
    service_parser = subparsers.add_parser('service-file', help='Prints service file')
    service_parser.add_argument('-p', '--path', help='Path to project')

    # #  Service command
    # service_parser = subparsers.add_parser('service', help='Prints service commands')

    # Service Display command
    service_display_parser = subparsers.add_parser('display-service', help='Display service commands')
    service_display_parser.add_argument('-p', '--path', help='Path to project')

    # Service Create command
    service_display_parser = subparsers.add_parser('create-service', help='Create service')
    service_display_parser.add_argument('-p', '--path', help='Path to project')

    # Service Follow command
    service_display_parser = subparsers.add_parser('follow-service', help='Follow service')

    # Service Status command
    service_display_parser = subparsers.add_parser('status-service', help='Status service')

    # Service Restart command
    service_display_parser = subparsers.add_parser('restart-service', help='Restart service')

    # Service Stop command
    service_display_parser = subparsers.add_parser('stop-service', help='Stop service')


    # Test Query command
    test_query_parser = subparsers.add_parser('test', help='Test a Query')
    test_query_parser.add_argument('-q', '--query', required=True, help='The cronevent query')

    init_parser = subparsers.add_parser('init', help='Create the initial finals needed in the `.cronevents` folder')

    display_cronevents_parser = subparsers.add_parser('cronevents', help='Show recent cronevents')
    # display_cronevents_parser.add_argument('-n', '-l', '--limit', required=False, help='The number of cronevents to show', default=10)

    display_triggers_parser = subparsers.add_parser('triggers', help='Show recent triggers for a certain cronevent')
    display_triggers_parser.add_argument('-c', '--cronevent-id', required=True, help='The cronevent id of the cronevent')
    display_triggers_parser.add_argument('-n', '-l', '--limit', required=False, help='The number of triggers to show', default=10)

    display_logs_parser = subparsers.add_parser('logs', help='Show logs of a triggered cronevent')
    display_logs_parser.add_argument('-t', '--trigger-id', required=True, help='The trigger id of the logs')


    # Parse arguments
    args, remaining_args = parser.parse_known_args()

    # Handle the commands
    if args.command == 'init':
        from cronevents.settings import get_settings
        get_settings()
        print('Initialized')
        sys.exit(0)
    elif args.command == 'manager':
        if args.postgres:
            os.environ['CRON_EVENTS_USING_POSTGRES'] = 'true'
            (os.environ['POSTGRES_HOST'], os.environ['POSTGRES_PORT'], os.environ['POSTGRES_USER'],
             os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DATABASE']) = args.postgres.split(':')
        cronevents.event_manager.main()
        sys.exit(0)
    elif args.command == 'register':
        if args.postgres:
            os.environ['CRON_EVENTS_USING_POSTGRES'] = 'true'
            (os.environ['POSTGRES_HOST'], os.environ['POSTGRES_PORT'], os.environ['POSTGRES_USER'],
             os.environ['POSTGRES_PASSWORD'], os.environ['POSTGRES_DATABASE']) = args.postgres.split(':')

        cronevents.register.register_events(args.file, args.postgres)
        sys.exit(0)
    elif args.command == 'test':
        cronevents.event_manager.query_syntax_checker(args.query)
        print('Valid query')
        sys.exit(0)
    elif args.command == 'service-file':
        print(system_service_config.replace('{{path}}', args.path or os.getcwd()))
        sys.exit(0)
    elif args.command == 'service-display':
        print(service_commands.replace('{{path}}', args.path or os.getcwd()))
        sys.exit(0)
    elif args.command == 'create-service':
        path = args.path or os.getcwd()

        with open(suggested_service_path, 'w') as f:
            f.write(system_service_config.replace('{{path}}', path))

        os.system(reload_command)
        os.system(start_service_command)
        os.system(enable_service_command)
        time.sleep(.01)
        os.system(restart_service_command)
        print(f'\nService created at {suggested_service_path}')
        sys.exit(0)
    elif args.command == 'follow-service':
        os.system(follow_service_command)
        sys.exit(0)
    elif args.command == 'status-service':
        os.system(status_service_command)
        sys.exit(0)
    elif args.command == 'restart-service':
        os.system(restart_service_command)
        sys.exit(0)
    elif args.command == 'stop-service':
        os.system(stop_service_command)
        sys.exit(0)
    elif args.command == 'cronevents':
        from cronevents.settings import get_settings
        s = get_settings()
        for cr in s.cronevents.list():
            print(cr.display())
        sys.exit(0)
    elif args.command == 'triggers':
        from cronevents.settings import get_settings
        s = get_settings()
        i = 0
        for t in s.trigger.list(stream=True, cronevent_id=args.cronevent_id):
            if i < int(args.limit):
                print(t.display())
                i += 1
        sys.exit(0)
    elif args.command == 'logs':
        from cronevents.settings import get_settings
        s = get_settings()
        for l in s.logger(args.trigger_id).list(stream=True):
            # print(l.display())
            print(l.line)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    cli()
