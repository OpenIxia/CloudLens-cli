# Cloudlens CLI
Author: Michael Wan

## Dependencies
- Kubectl ([Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/))
- Python3
- PyYaml (Pip Package)


## Installation
- Run ```install.sh``` as root user in a UNIX shell
- Cloudlens is now properly installed

## Overview
- Cloudlens is a CLI prompted by the command ```cloudlens```
- It offers the following functionalities:
	- Starting / shutting down webhook and deployments that require Cloudlens auto injection
	- Configuring different Cloudlens projects per namespace (by specifying a specific API key per each namespace)
	- Checking the status of webhook and pods with Cloudlens injected

## Usage
### Starting a webhook
First, let's start the webhook:
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
cloudlens start deployment --yaml [YAML file path]
```

We can also pass in additional optional arguments such as labels and a namespace to deploy in (the default is the "default" namespace):
```console
cloudlens start deployment --yaml [YAML file path] --labels label1=Hi label2="Hello World" --namespace [NAMESPACE]
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
cloudlens shutdown deployment [DEPLOYMENT NAME]
cloudlens shutdown deployment --labels label1=Hi # Shutting down deployments using a label selector
cloudlens shutdown deployment [DEPLOYMENT NAME] --namespace default # Specifying a specific namespace to target
cloudlens shutdown deployment [DEPLOYMENT NAME] --all-namespaces # Deleting the deployment in all namespaces
```
### Shutting down the webhook
```console
cloudlens shutdown webhook
```

## Demo
For the demo shown during the CLI presentation, a DSVW app was deployed with Cloudlens automatically injected. In the background, there were two apps running: a sensor app to snort for attacks, and a ELK stack to allow for users to visualize and analyze the data.

The sensor and ELK apps exist under the Open Ixia [sample-cloud-ids](https://github.com/OpenIxia/sample-cloud-ids) repo in the respective folders ```sensor/``` and ```events_ui/```. Follow the instructions in the READMEs of both directories to successfully launch the apps.

Thus, for simplicity, the CLI tool will only be used to deploy the DSVW app with cloudlens injection.

First, the webhook needs to be started:
```console
root@ubuntu:~$ cloudlens start webhook
Successfully created webhook.
```
Now, the DSVW app can be deployed:
```console
root@ubuntu:~$ cloudlens start deployment --yaml demo/test-dsvw.yaml --labels workload=dsvw
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


