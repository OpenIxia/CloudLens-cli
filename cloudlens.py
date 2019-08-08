#!/usr/bin/env python3
"""Cloudlens CLI
@author Michael Wan

Usage:
cloudlens [-h] {start,shutdown,config,uninstall,status} ...
cloudlens start [-h] [--yaml YAML] [--namespace NAMESPACE]
                       [--labels LABELS [LABELS ...]]
                       {webhook,testapp,deployment}
cloudlens shutdown [-h] [--namespace NAMESPACE]
                          [--labels LABELS [LABELS ...]] [--all-namespaces]
                          {webhook,testapp,deployment} [name]
cloudlens config [-h] --namespace NAMESPACE {key} apikey


Able to deploy webhook to automatically inject cloudlens sidecar containers as well as
facilitating functionalities
"""

import os
import re
import argparse
import subprocess
import shlex
import json
import yaml

DIR_NAME = "cloudlens-cli"
WEBHOOK_NS = "default"


def colorize(text, color="default"):
    """Returns colorized text"""
    reset = '\033[0m'
    colormap = {
        "black": '\033[30m',
        "red": '\033[31m',
        "green": '\033[32m',
        "orange": '\033[33m',
        "blue": '\033[34m',
        "purple": '\033[35m',
        "cyan": '\033[36m',
        "lightgrey": '\033[37m',
        "darkgrey": '\033[90m',
        "lightred": '\033[91m',
        "lightgreen": '\033[92m',
        "yellow": '\033[93m',
        "lightblue": '\033[94m',
        "pink": '\033[95m',
        "lightcyan": '\033[96m',
    }
    colormap['error'] = colormap['lightred']
    colormap['success'] = colormap['green']
    colormap['warning'] = colormap['yellow']
    colormap['info'] = colormap['lightcyan']
    if color != "default" and color in colormap:
        return colormap[color] + text + reset
    return text


def log(text, color="default"):
    """Prints with color option"""
    print(colorize(text, color))


def cloudlens_cli_parser():
    """Creates argument parser"""
    parser = argparse.ArgumentParser(
        description=
        'Cloudlens CLI that facilitates webhook admission controller deployment.'
    )
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')

    start_handler = subparsers.add_parser('start', help='start help')
    start_handler.add_argument(
        'object',
        choices=['webhook', 'testapp', 'deployment'],
        help='object to be acted on')
    start_handler.add_argument(
        '--yaml', dest='yaml', help='specify yaml file of deployment')
    start_handler.add_argument(
        '--namespace',
        dest='namespace',
        help='specify namespace to start deployment')
    start_handler.add_argument(
        '--labels', dest='labels', nargs='+', help='specify custom labels')

    shutdown_handler = subparsers.add_parser('shutdown', help='shutdown help')
    shutdown_handler.add_argument(
        'object',
        choices=['webhook', 'testapp', 'deployment'],
        help='object to be acted on')
    shutdown_handler.add_argument('name', nargs='?', const=None)
    shutdown_handler.add_argument(
        '--namespace',
        dest='namespace',
        help='specify namespace to shutdown deployment')
    shutdown_handler.add_argument(
        '--labels', dest='labels', nargs='+', help='specify labels of deployment(s) to shutdown')
    shutdown_handler.add_argument(
        '--all-namespaces', dest='all_namespaces', action='store_true')

    config_handler = subparsers.add_parser('config', help='config help')
    config_handler.add_argument(
        'object', choices=['key'], help='object to be acted on')
    config_handler.add_argument(
        'apikey', help='key value / file containing key')
    config_handler.add_argument('--namespace', dest='namespace', required=True)
    subparsers.add_parser('uninstall', help='uninstall help')
    subparsers.add_parser('status', help='status help')
    return parser


def handle_parse_errors(args, parser):
    """Handles errors in arguments"""
    if args.action == "start":
        if args.object == 'webhook' and "namespace" in args and args.namespace:
            parser.error(
                colorize(
                    "Namespace should not be specified for webhook.",
                    "error"))
        if args.object in ['webhook', 'testapp'] and args.yaml is not None:
            parser.error(
                colorize(
                    "YAML file should not be specified when starting webhook or testapp.",
                    "error"))
        if args.object == "deployment" and args.yaml is None:
            parser.error(
                colorize(
                    "Please specify a YAML file with the file flag to start an deployment.",
                    "error"))
    if args.action == "shutdown":
        if args.object == "deployment":
            if ("name" not in args or args.name is None) and ("labels" not in args or args.labels is None):
                parser.error(
                    colorize("Please specify either the name or the labels of the deployment to shutdown",
                             "error"))
            if "name" in args and args.name and "labels" in args and args.labels:
                parser.error(
                    colorize("Please specify only one of the options 'name' and 'label'",
                             "error"))
        if args.object in ['webhook', 'testapp'] and "name" in args and args.name:
            parser.error(
                colorize(
                    "Name should not be specified when shutting down webhook or testapp",
                    "error"))
        if args.all_namespaces and args.object == 'webhook':
            parser.error(
                colorize("Cannot use all namespace flag for webhook", "error"))
        if args.object in ['webhook', 'testapp'] and "labels" in args and args.labels:
            parser.error(
                colorize("Labels should not be specified for generic webhook or testapp.",
                    "error"))


def read_yaml(file):
    """Reads in a YAML file as specified by CLI"""
    fullpath = os.path.join(os.getcwd(), file)
    contents = None
    with open(fullpath, "r") as stream:
        try:
            contents = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            log("Error upon reading %s" % file, "error")
            log(str(err), "error")
    return contents


def bash(cmd, keep_format=False, silent=False, display_err=True):
    """Method to facilitate running bash commands."""
    try:
        if keep_format:
            if not silent:
                ret = subprocess.run(cmd, shell=True)
            else:
                ret = subprocess.run(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        else:
            if not silent:
                ret = subprocess.run(" ".join(shlex.split(cmd)), shell=True)
            else:
                ret = subprocess.run(
                    " ".join(shlex.split(cmd)),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        if silent and display_err and ret.returncode != 0:
            if ret.stderr:
                log("Error. %s" % ret.stderr.decode("utf-8").strip(), "error")
            elif ret.stdout:
                log("Error. %s" % ret.stdout.decode("utf-8").strip(), "error")
            else:
                log("Error. Reason unknown", "error")
        return ret.returncode == 0
    except Exception as err:
        log("*** Error ***", "error")
        log(str(err), "error")
        return False


def check_kubectl_installation():
    """Check whether Kubectl is installed on machine."""
    try:
        subprocess.check_output(["which", "kubectl"])
        return True
    except Exception as err:
        log("*** Error ***", "error")
        log(str(err), "error")
        return False


def get_all_namespaces():
    """Gets all namespaces"""
    try:
        ret = subprocess.check_output("kubectl get namespace", shell=True)
        ret = ret.decode("utf-8").strip().split("\n")
        for i in range(len(ret)):
            ret[i] = ret[i].split()[0]
        ret = ret[1:]
        return ret
    except Exception as err:
        log("*** Error ***", "error")
        log(str(err), "error")
        return None


def get_current_namespace():
    """Returns the current namespace name"""
    try:
        ret = subprocess.check_output(
            "kubectl config view --minify --output \
                                      'jsonpath={..namespace}'",
            shell=True)
        ret = ret.decode("utf-8")
        return ret
    except Exception as err:
        log("*** Error ***", "error")
        log(str(err), "error")
        return None


def api_config_exists(namespace):
    """Look for api secret config"""
    try:
        ret = subprocess.check_output(
            "kubectl get secrets --namespace=%s \
                                      -o json" % namespace,
            shell=True)
        ret = json.loads(ret.decode("utf-8"))
        for secret in ret["items"]:
            if secret["metadata"]["name"] == "cloudlens-config-secret":
                return True
        return False
    except Exception as err:
        log("*** Error ***", "error")
        log(str(err), "error")
        return False


def switch_namespace(namespace, silent=True):
    """Switches namespace"""
    if bash(
            "kubectl config set-context --current --namespace=%s" % namespace,
            silent=True):
        if not silent:
            log("Successfully switched to namespace %s" % namespace, "success")
        return True
    if not silent:
        log("Error upon switching to namespace %s" % namespace, "error")
    return False


def config_secret(apikey, namespace):
    """Configure API secret for given namespace"""
    if api_config_exists(namespace):
        log("Namespace key config already exists... Overwriting...", "warning")
        bash("kubectl delete secret cloudlens-config-secret", silent=True)
    create_secret_cmd = "kubectl create secret generic \
                         cloudlens-config-secret \
                         --from-literal=apikey=\"%s\" \
                         --namespace %s" % (apikey, namespace)
    if bash(create_secret_cmd, silent=True):
        log("Successfully configured key for namespace %s" % namespace,
            "success")
        return True
    log("Error upon key configuration for namespace %s" % namespace, "error")
    return False


def pods_status():
    """Gets the status of all deployed pods with cloudlens containers"""
    try:
        running = []
        ret = subprocess.check_output(
            'kubectl get pods -o=custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace \
            --all-namespaces',
            shell=True)
        ret = ret.decode("utf-8").strip().split("\n")
        for i in range(len(ret)):
            ret[i] = tuple(ret[i].split())
        ret = ret[1:]
        for pod, namespace in ret:
            try:
                containers = subprocess.check_output(
                    'kubectl get pods %s --namespace=%s -o \
                                                     jsonpath="{.spec.containers[*].image}"'
                    % (pod, namespace),
                    shell=True)
                containers = containers.decode("utf-8").split(' ')
                for container in containers:
                    if 'ixiacom/cloudlens-agent' in container:
                        running.append((pod, namespace))
                        break
            except Exception as c_err:
                log("*** Error ***", "error")
                log(str(c_err), "error")
        if running:
            log(
                "%s pods running with cloudlens containers installed:" % str(
                    len(running)), "success")
            for pod, namespace in running:
                log("\t%s (%s)" % (pod, namespace), "info")
            return len(running)
        log("No pods with cloudlens containers are running at the moment.",
            "success")
        return 0
    except Exception as p_err:
        log("*** Error ***", "error")
        log(str(p_err), "error")
        return -1


def webhook_status():
    """Check if webhook is successfully deployed"""
    namespace = get_current_namespace()
    if namespace != WEBHOOK_NS:
        log("Not in %s namespace... auto switching" % WEBHOOK_NS, "warning")
        switch_namespace(WEBHOOK_NS)
    check_exists = {
        "deployment":
        bash(
            "kubectl get deployment sidecar-injector-webhook-deployment",
            silent=True,
            display_err=False),
        "configmap":
        bash(
            "kubectl get configmap sidecar-injector-webhook-configmap",
            silent=True,
            display_err=False),
        "service":
        bash(
            "kubectl get service sidecar-injector-webhook-svc",
            silent=True,
            display_err=False),
        "mutatingwebhook":
        bash(
            "kubectl get mutatingwebhookconfiguration sidecar-injector-webhook-cfg",
            silent=True,
            display_err=False),
    }
    if namespace != WEBHOOK_NS:
        log("Switching back to namespace %s" % namespace, "warning")
        switch_namespace(namespace)
    webhook_errors = []
    for component in check_exists:
        if not check_exists[component]:
            webhook_errors.append(component)
    if webhook_errors:
        if len(webhook_errors) == 4:
            log("The webhook is not running.", "success")
        else:
            log(
                "%s errors. The following do not exist: %s" %
                (len(webhook_errors), ", ".join(webhook_errors)), "error")
        return False
    log("Webhook running with no issues.", "success")
    return True


def create_webhook():
    """Creates and deploys webhook in default namespace."""
    starting_ns = get_current_namespace()
    path_to_cur_dir = os.path.dirname(os.path.realpath(__file__))
    if starting_ns != WEBHOOK_NS:
        log("Not in namespace %s... switching" % starting_ns, "warning")
        switch_namespace(WEBHOOK_NS)
    gen_cert_cmd = "%s/deployment/webhook-create-signed-cert.sh \
                    --service sidecar-injector-webhook-svc \
                    --secret sidecar-injector-webhook-certs \
                    --namespace %s" % (path_to_cur_dir, WEBHOOK_NS)
    patch_cert_cmd = "cat %s/deployment/mutatingwebhook.yaml | \
                      %s/deployment/webhook-patch-ca-bundle.sh > \
                      %s/deployment/mutatingwebhook-ca-bundle.yaml" % \
             (path_to_cur_dir, path_to_cur_dir, path_to_cur_dir)
    apply_yamls = [
        "kubectl create -f %s/deployment/configmap.yaml" % path_to_cur_dir,
        "kubectl create -f %s/deployment/deployment.yaml" % path_to_cur_dir,
        "kubectl create -f %s/deployment/service.yaml" % path_to_cur_dir,
        "kubectl create -f %s/deployment/mutatingwebhook-ca-bundle.yaml" %
        path_to_cur_dir
    ]
    cmds = [gen_cert_cmd, patch_cert_cmd]
    cmds.extend(apply_yamls)
    ret = all([bash(cmd, silent=True) for cmd in cmds])
    if WEBHOOK_NS != starting_ns:
        log("Switching back to namespace %s" % starting_ns, "warning")
        switch_namespace(starting_ns)
    if ret:
        log("Successfully created webhook.", "success")
    else:
        log("Error upon webhook creation.", "error")


def remove_webhook():
    """Shutsdown the webhook and deletes all deployments used to configure webhook."""
    starting_ns = get_current_namespace()
    if starting_ns != WEBHOOK_NS:
        log("Not in namespace %s... switching" % WEBHOOK_NS, "warning")
        switch_namespace(WEBHOOK_NS)
    cmds = [
        "kubectl delete deployment sidecar-injector-webhook-deployment",
        "kubectl delete service sidecar-injector-webhook-svc",
        "kubectl delete configmap --all",
        "kubectl delete mutatingwebhookconfiguration --all",
    ]
    ret = all([bash(cmd, silent=True) for cmd in cmds])
    if WEBHOOK_NS != starting_ns:
        log("Switching back to namespace %s" % starting_ns, "warning")
        switch_namespace(starting_ns)
    if ret:
        log("Successfully removed webhook", "success")
    else:
        log("Error upon webhook deletion.", "error")


def start(file, labels=None, target_namespace=None):
    """Starts a deployment from a given file"""
    starting_ns = get_current_namespace()
    if target_namespace:
        if target_namespace not in get_all_namespaces():
            log("Error. Specified namespace is not a valid namespace", "error")
            return
        log("Namespace %s specified" % target_namespace, "warning")
        if target_namespace != starting_ns:
            log("Switching to target namespace",
                "warning")
            switch_namespace(target_namespace)
    else:
        log("No namespace specified. Using default", "warning")
        if starting_ns != "default":
            switch_namespace("default")
        target_namespace = "default"
    if not api_config_exists(target_namespace):
        log(
            "Warning. No API key secret stored in current namespace %s. \
            Learn more by running 'cloudlens config -h'" % target_namespace,
            "warning")
    contents = read_yaml(file)
    if not contents:
        log("Error. Could not read file %s" % file, "error")
    bash(
        "kubectl label namespace %s sidecar-injector=enabled \
         --overwrite" % target_namespace,
        silent=True)
    try:
        if 'metadata' not in contents['spec']['template']:
            contents['spec']['template']['metadata'] = {}
        meta = contents['spec']['template']['metadata']
        if labels:
            if 'labels' not in meta:
                meta['labels'] = {}
            for label in labels:
                parsed = re.split('''=(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''',
                                  label)
                meta['labels'][parsed[0].strip("\'").strip(
                    '\"')] = parsed[1].strip("\'").strip('\"')
        if 'annotations' not in meta:
            meta['annotations'] = {}
        meta["namespace"] = target_namespace
        meta['annotations']['keysight.michawan.webhook/inject'] = "yes"
        yaml_content = yaml.dump(contents, default_flow_style=False)
        cmd = "cat <<EOF | kubectl create -f -\n" + yaml_content + "\nEOF"
        if bash(cmd, keep_format=True, silent=True):
            log("Successfully created deployment %s" % file, "success")
        else:
            log("Error upon starting deployment %s" % file, "error")
    except Exception as err:
        log("Error upon starting deployment %s" % str(err), "error")


def shutdown(name, labels=None, target_namespace=None, all_namespaces=False):
    """Shutdowns given deployment by name"""
    if target_namespace and target_namespace not in get_all_namespaces():
        log("Specified namespace is not a valid namespace", "error")
        return
    cur_namespace = get_current_namespace()
    all_ns = [target_namespace if target_namespace else "default"]
    if all_namespaces:
        log("Checking all namespaces...", "warning")
        all_ns = get_all_namespaces()
    elif target_namespace:
        log("%s specified as target namespace", "warning")
    else:
        log("No namespace specified. Using default", "warning")
    for namespace in all_ns:
        log("Checking namespace %s..." % namespace, "warning")
        if namespace != cur_namespace:
            switch_namespace(namespace)
            cur_namespace = namespace
        cmd = "kubectl delete deployment"
        if labels:
            cmd += " -l %s" % str(",".join(labels))
        elif name:
            cmd += " %s" % name
        if bash(cmd, silent=True, display_err=False):
            if name:
                log(
                    "Successfully deleted deployment with name %s in namespace %s" %
                    (name, namespace), "success")
            elif labels:
                log(
                    "Successfully deleted deployment with labels %s in namespace %s" %
                    (",".join(labels), namespace), "success")


def uninstall_cli():
    """Uninstalls the CLI and its dependencies."""
    cmds = [
        "echo 'Removing dependencies... '",
        "rm -rf ${HOME}/.%s" % DIR_NAME,
        "echo 'Success'",
        "echo ''",
        "echo 'Removing symlink...' ",
        "rm /usr/local/bin/cloudlens",
        "echo 'Success'",
        "echo ''",
    ]
    if all([bash(cmd) for cmd in cmds]):
        log("Successfully uninstalled Cloudlens CLI", "success")
    else:
        log("Error upon uninstalling CLI", "error")


def main():
    """Main function.

    Example:
        $ python cloudlens.py start webhook --apikey TESTAPIKEY
    """
    parser = cloudlens_cli_parser()
    args = parser.parse_args()

    handle_parse_errors(args, parser)

    if args.action == "uninstall":
        uninstall_cli()

    if not check_kubectl_installation():
        log(
            "Kubectl not installed. Please install by following \
            https://kubernetes.io/docs/tasks/tools/install-kubectl/", "error")
        exit()

    if args.action == "status":
        webhook_status()
        pods_status()
    if args.action == "start":
        obj = args.object
        if obj == "webhook":
            create_webhook()
        elif obj == "testapp":
            start(
                os.path.join(
                    os.getenv("HOME"), ".%s/sleep.yaml" % DIR_NAME),
                labels=args.labels,
                target_namespace=args.namespace)
        elif obj == "deployment":
            start(
                args.yaml, labels=args.labels, target_namespace=args.namespace)
    elif args.action == "shutdown":
        obj = args.object
        if obj == "webhook":
            remove_webhook()
        if obj == "testapp":
            shutdown(
                None,
                labels=["id=testapp"],
                target_namespace=args.namespace,
                all_namespaces=args.all_namespaces)
        elif obj == "deployment":
            shutdown(
                args.name,
                labels=args.labels,
                target_namespace=args.namespace,
                all_namespaces=args.all_namespaces)
    elif args.action == "config":
        obj = args.object
        if obj == "key":
            apikey = args.apikey
            namespace = args.namespace
            config_secret(apikey, namespace)


if __name__ == "__main__":
    main()


