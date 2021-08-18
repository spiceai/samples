# Kubernetes

Adding Spice AI to your [Kubernetes](https://kubernetes.io/) cluster is easy.

## Prerequisites

This example assumes you have a working Kubernetes cluster set up and can access it via `kubectl`.  For help setting up a cluster, consult the [Kubernetes Documentation](https://kubernetes.io/docs/setup/). 

Ensure this `samples` repository is cloned and you are in the `kubernetes` directory.

```bash
git clone https://github.com/spiceai/samples.git
cd samples/kubernetes
```

## Standalone

First, we will create a [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) that contains our Pod definition.  A Pod definition tells Spice AI which Datasources, Actions, and training parameters it should use to provide inferences to your app.  For this sample, we will use the [CartPole](https://github.com/spiceai/registry/blob/trunk/pods/samples/CartPole-v1/cartpole-v1.yaml) Pod definition from the the Spice AI Registry.  Let's add it now:

```bash
kubectl apply -f cartpole-configmap.yaml
```

Next, we will create a Spice AI [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) to start Spice AI in our cluster:

```bash
kubectl apply -f spiceai-deployment.yaml
```

Once the deployment has finished, we can add a [Service](https://kubernetes.io/docs/concepts/services-networking/service/) to allow other apps within our cluster to access Spice AI:

```bash
kubectl apply -f spiceai-service.yaml
```

This will create a [ClusterIP](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) Service that other apps within the cluster can access.  To test this out, you can spin up a debug container and access it:

```bash
kubectl run -i --tty --rm debug --image=alpine --restart=Never -- sh

(inside the new container)
# apk add --no-cache curl
# curl http://spiceai:8000/api/v0.1/pods/cartpole-v1/inference
{"action":"right","confidence":0.0,"end":"2021-08-18T20:59:10","start":"2021-08-18T20:59:00","tag":"latest"}
```

Cool!  If you would like to access Spice AI from outside the cluster, try changing the `type` of the Service in `spiceai-service.yaml` to either a `NodePort` or a `LoadBalancer`, depending on how your cluster is set up.
