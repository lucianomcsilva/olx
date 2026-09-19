import subprocess
import uuid
import json
import os
from time import sleep

total_pages = 1000
workers = [                 'AC',
                            'AL',
                            'AP',
                            'AM',
                            'BA',
                            'CE',
                            'DF',
                            'ES',
                            'GO',
                            'MA',
                            'MS',
                            'MT',
                            'MG',
                            'PA',
                            'PB',
                            'PR',
                            'PE',
                            'PI',
                            'RJ',
                            'RN',
                            'RS',
                            'RO',
                            'RR',
                            'SC',
                            'SP',
                            'SE',
                            'TO',
                        ]

workers_sul = ['PR', 'RS', 'SC']
workers_sudeste = ['SP', 'RJ', 'ES', 'MG']
# workers_co = ['GO', 'MS', 'MT', 'DF']
# workers_norte = ['TO', 'RR', 'RO', 'AM', 'AP', 'PA', 'AC']
workers_nordeste = ['AL', 'BA', 'CE', 'MA', 'PA', 'PE', 'PI', 'RN', 'SE', 'PB', 'ES' #sei que nao é
                    ]

workers = workers_nordeste

session = uuid.uuid4()
session = "abcd1234"
for port, taskno in enumerate(workers, 8081):
    """
    network_config = {
                        "awsvpcConfiguration": {
                            "assignPublicIp": "ENABLED",
                            "securityGroups": ["sg-05c9b3a0217ee5857"],
                            "subnets": ["subnet-05b3091efed4c75b3"]
                        }
                    } 
    overrides = {
                "containerOverrides": [
                    {
                        "name": "tricarros",
                        "command": [
                            "usr/local/bin/scrapy",
                            "crawl",
                            "webmotors"
                        ],
                        "environment": [
                            {
                                "name": "START_PAGE",
                                "value": f"{(taskno) * pages_per_worker + 1}"
                            },
                            {
                                "name": "END_PAGE",
                                "value": f"{(taskno+1) * pages_per_worker}"
                            },
                            {
                                "name": "AWS_DEFAULT_REGION",
                                "value": "us-east-1"
                            },
                            {
                                "name": "SESSION",
                                "value": str(session)
                            },
                            {
                                "name": "TASKNO",
                                "value": str(taskno)
                            }
                        ]
                    }
                ]
            }
    """
    #command = f"aws ecs run-task --cluster TricarrosCluster --task-definition TriCarrosScrapWebmotors:9  --launch-type='FARGATE'  --network-configuration '{json.dumps(network_config)}' --overrides '{json.dumps(overrides)}'"
    command = f"docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION='docker' -e TASKNO={taskno.lower()} -e SESSION={session} --name='worker-{taskno.lower()}' --rm -p {port}:80 --volume '/Users/lucianomcesilva/apps/olx/tricarros_commons:/tricarros_commons' -v '/Users/lucianomcesilva/apps/olx/data:/data' -v '/Users/lucianomcesilva/.aws:/.aws:ro'  tricarros-olx-arm64 &"
    #print(command)
    
    my_env = os.environ.copy()
    my_env["TASKNO"] = taskno.lower()
    #print(my_env)
    sleep(20 * 60)

    with open(f'./logs/estado-{taskno.lower()}.log', 'w') as fd:        
        subprocess.Popen("scrapy crawl olx_spider", shell=True, env=my_env, stdout=fd)
        
    #subprocess.Popen(command, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    
#docker run -e AWS_DEFAULT_REGION='docker' -e TASKNO=ac -e SESSION=123456789 --name='worker-ac' --rm -p 8081:80 --volume '/tricarros_commons:/Users/lucianomcesilva/apps/olx/tricarros_commons' -v '/data:/Users/lucianomcesilva/apps/olx/data'  tricarros-olx-arm64

#docker run -e AWS_DEFAULT_REGION='docker' -e TASKNO=ac -e SESSION=123456789 --name='worker-ac' --rm -p 8081:80 --volume '/Users/lucianomcesilva/apps/olx/tricarros_commons:/tricarros_commons'  tricarros-olx-arm64
