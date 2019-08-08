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

#### Examples
```console
root@ubuntu:~$ cloudlens start webhook
Successfully created webhook.
```
The webhook is now successfully running, and we can check for its status by running
```console
root@ubuntu:~$ cloudlens status
Webhook running with no issues.
```


