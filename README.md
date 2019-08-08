## Cloudlens CLI
Author: Michael Wan

### Installation
- Run ```install.sh``` as root user in a UNIX shell
- Cloudlens is now properly installed

### Usage
- Cloudlens is a CLI prompted by the command ```cloudlens```
- It offers the following functionalities:
	- Starting / shutting down webhook and deployments that require Cloudlens auto injection
	- Configuring different Cloudlens projects per namespace (by specifying a specific API key per each namespace)
	- Checking the status of webhook and pods with Cloudlens injected

#### Example Usage
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
We can now start our deployments, which will automatically have Cloudlens agents injected into them. To start a deployment, we run:
```cloudlens start deployment --yaml [YAML file path]```

We can also pass in additional optional arguments such as labels and a namespace to deploy in (the default is the "default" namespace):
```cloudlens start deployment --yaml [YAML file path] --labels label1=Hi label2="Hello World" --namespace [NAMESPACE]```

Running ```cloudlens status``` again will allow us to view the status of the pods from the deployment:
```console
root@ubuntu:~$ cloudlens status
Webhook running with no issues.
1 pod running with cloudlens containers installed:
	test-deployment-5d477fc6d8-229gb (default)
```

Shutting down deployments is very similar to starting them:
```cloudlens shutdown deployment [DEPLOYMENT NAME]```
We can also shut down deployments using a label selector
```cloudlens shutdown deployment --labels label1=Hi```
Also, we can shut down deployments in specific namespaces, or in all namespaces:
```cloudlens shutdown deployment [DEPLOYMENT NAME] --namespace default```
Or
```cloudlens shutdown deployment [DEPLOYMENT NAME] --all-namespaces```

### Demo