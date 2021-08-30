# Kubernetes

Adding Spice.ai to your [Kubernetes](https://kubernetes.io/) cluster is easy.

## Prerequisites

This example assumes you have a working Kubernetes cluster set up and can access it via `kubectl`. For help setting up a cluster, consult the [Kubernetes Documentation](https://kubernetes.io/docs/setup/).

Ensure this `samples` repository is cloned and you are in the `kubernetes` directory.

```bash
git clone https://github.com/spiceai/samples.git
cd samples/kubernetes
```

## Standalone

First, we will create a [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) that contains our Pod definition. A Pod definition tells Spice.ai which Dataspaces, Actions, and training parameters it should use to provide recommendations to your app. For this sample, we will use the CartPole Pod definition from the the Spice.ai Registry. Let's add it now:

```bash
kubectl apply -f trader-configmap.yaml
```

Next, we will create a Spice.ai [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) to start Spice.ai in our cluster:

```bash
kubectl apply -f spiceai-deployment.yaml
```

Once the deployment has finished, we can add a [Service](https://kubernetes.io/docs/concepts/services-networking/service/) to allow other apps within our cluster to access Spice.ai:

```bash
kubectl apply -f spiceai-service.yaml
```

This will create a [ClusterIP](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) Service that other apps within the cluster can access. To test this out, you can spin up a debug container and access it:

```bash
kubectl run -i --tty --rm debug --image=alpine --restart=Never -- sh

(inside the new container)
# apk add --no-cache curl
# curl http://spiceai:8000/api/v0.1/pods/trader/recommendation
{"response":{"result":"ok"},"start":1607886000,"end":1607907600,"action":"sell","tag":"latest"}
```

Cool! If you would like to access Spice.ai from outside the cluster, try changing the `type` of the Service in `spiceai-service.yaml` to either a `NodePort` or a `LoadBalancer`, depending on how your cluster is set up.

## Sidecar

If you would like to run Spice.ai as a sidecar, you can easily add it to your existing application. Simply modify your existing Deployment to include the Spice.ai runtime. The following is an example you can use from [spiceai-deployment.yaml](spiceai-deployment.yaml) in this sample:

```yaml
spec:
      <your application specific details here>

      containers:
      - name: spiceai
        image: ghcr.io/spiceai/spiced:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: userapp
          mountPath: /userapp
      initContainers:
      - name: spiceai-init
        image: busybox
        command: ['/bin/sh', '-c', 'mkdir -p /userapp/.spice/pods && cp /trader/trader.yaml /userapp/.spice/pods/trader.yaml && cp /trader/btcusd.csv /userapp/btcusd.csv']
        volumeMounts:
        - name: userapp
          mountPath: /userapp
        - name: trader-volume
          mountPath: /trader
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      volumes:
        - name: trader-volume
          configMap:
            name: trader
        - name: userapp
          emptyDir: {}

```

Once you've added this, Spice.ai will be reachable from your application at `http://localhost:8000`!

## Coming Soon

We are working to build a set of [Kubernetes Operators](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) to make your Spice.ai integration even easier. Stay tuned!
