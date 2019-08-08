# Cloudlens CLI
Author: Michael Wan


## Dependencies
- Kubectl ([Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/))
- Python3
- PyYaml (Pip Package)


## Overview
- Cloudlens is a CLI prompted by the command ```cloudlens```
- It offers the following functionalities:
	- Starting / shutting down webhook and deployments that require Cloudlens auto injection
	- Configuring different Cloudlens projects per namespace (by specifying a specific API key per each namespace)
	- Checking the status of webhook and pods with Cloudlens injected


## Installation
- Run ```install.sh``` as root user in a UNIX shell
- Cloudlens is now properly installed


## Usage
### Starting the webhook
The webhook is what's responsible for Cloudlens being automatically injected. The source code for the webhook is [here](https://github.com/OpenIxia/Cloudlens-k8s-webhook.git). To start the webhook, we run:
```console
root@ubuntu:~$ cloudlens start webhook
Successfully created webhook.
```
The webhook is now successfully running, and we can check for its status by running:
```console
root@ubuntu:~$ cloudlens status
Webhook running with no issues.
```
### Starting a deployment
We can now start our deployments, which will automatically have Cloudlens agents injected into them. To start a deployment, we run:
```console
root@ubuntu:~$ cloudlens start deployment --yaml [YAML file path]
```

We can also pass in additional optional arguments such as labels and a namespace to deploy in (the default is the "default" namespace):
```console
root@ubuntu:~$ cloudlens start deployment --yaml [YAML file path] --labels label1=Hi label2="Hello World" --namespace [NAMESPACE]
```

Running ```cloudlens status``` again will allow us to view the status of the pods from the deployment:
```console
root@ubuntu:~$ cloudlens status
Webhook running with no issues.
1 pod running with cloudlens containers installed:
	test-deployment-5d477fc6d8-229gb (default)
```
### Shutting down a deployment
There are many different ways to shut down a deployment:
```console
root@ubuntu:~$ cloudlens shutdown deployment [DEPLOYMENT NAME] # Specifying deployment name
root@ubuntu:~$ cloudlens shutdown deployment --labels label1=Hi # Shutting down deployments using a label selector
root@ubuntu:~$ cloudlens shutdown deployment [DEPLOYMENT NAME] --namespace default # Specifying a specific namespace to target
root@ubuntu:~$ cloudlens shutdown deployment [DEPLOYMENT NAME] --all-namespaces # Deleting the deployment in all namespaces
```
### Shutting down the webhook
```console
root@ubuntu:~$ cloudlens shutdown webhook
```


## Demo
For the demo shown during the CLI presentation, a DSVW app was deployed with Cloudlens automatically injected. In the background, there were two apps running: a sensor app to snort for attacks, and a ELK stack to allow for users to visualize and analyze the data.

The sensor and ELK apps exist under the Open Ixia [sample-cloud-ids](https://github.com/OpenIxia/sample-cloud-ids) repo in the respective folders ```sensor/``` and ```events_ui/```. Follow the instructions in the READMEs of both directories to successfully launch the apps.

Thus, for simplicity, the CLI tool will only be used to deploy the DSVW app with cloudlens injection.

The demo consists of 3 portions:
1. Deploying webhook and app
2. Online Cloudlens configuration
3. Traffic simulation and visualization

### 1. Deploying webhook and app

First, the webhook needs to be started:
```console
root@ubuntu:~$ cloudlens start webhook
Successfully created webhook.
```
Before we continue, we must properly configure our Cloudlens project API key. If you haven't already, access the online [hub](https://ixia-sandbox.cloud) and create a project. We'll work in the default namespace in Kubernetes.
```console
root@ubuntu:~$ cloudlens config key [ENTER YOUR CLOUDLENS PROJECT API KEY] --namespace default
Successfully configured key for namespace default.
```
Now, the DSVW app can be deployed:
```console
root@ubuntu:~$ cloudlens start deployment --yaml demo/test-dsvw.yaml --labels workload=dsvw --namespace default
Successfully created deployment demo/test-dsvw.yaml
```
Status check:
```console
root@ubuntu:~$ cloudlens status
Webhook running with no issues.
5 pods running with cloudlens containers installed:
	dsvw-deployment-5d477fc6d8-229gb (default)
	dsvw-deployment-5d477fc6d8-2w6kn (default)
	dsvw-deployment-5d477fc6d8-fhg6c (default)
	dsvw-deployment-5d477fc6d8-ldhpz (default)
	dsvw-deployment-5d477fc6d8-ztm8j (default)
```
Don't worry if the IDs aren't the same, they're randomly generated.

Lastly, to expose our app so that we can access it, we must deploy the following service:
```console
root@ubuntu~$ kubectl apply -f demo/test-dsvw-service.yaml
``` 

### 2. Online Cloudlens configuration
Now that the cloudlens agents are up, we need to configure them on the online hub so that they'll pass their traffic to the cloudlens agent sitting inside the sensor app.

We need our online hub to be able to determine between the Cloudlens agents sitting inside the DSVW app versus those inside the sensor app. Click "Define A Group" inside your project on the hub and create a filter such that the group consisting of agents with the tag "workload" set to "dsvw". Create another group that filters agents with the tag "workload" set to "sample_snort_sensor".

Now, connect these two groups so that they can communicate.

### 3. Traffic simulation and visualization
If everything is set up correctly, you should be able to view the DSVW app at [localhost:31418](localhost:31418). The Kibana is available at [localhost:5601](localhost:5601)

To simulate real life traffic, run the following script to generate attack traffic:
```console
root@ubuntu:~$ python demo/test-traffic.py
```

The Kibana visualization graphs should be able to capture the various attacks.



