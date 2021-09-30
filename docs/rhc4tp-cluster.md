Release pipeline publishes the images to public registries, which are hosted at RHC4TP clusters.
To prepare the RHC4TP clusters to be used by the pipeline, for each of environments: 

0. Login to the chosen cluster

1. Create a service account

```bash
oc create sa operator-pipelines -n default
```

2. Create a Kubeconfig for the service account. It should be stored in the repository Ansible Vault.
```bash
clusterName=dev
namespace=default
serviceAccount=operator-pipelines
server=$(oc cluster-info | grep "is running at" | sed "s/Kubernetes master//" | sed "s/ is running at //")
# Sometimes the token secret is first in the serviceAccount, sometimes it's second after Dockerconfig
secretName=$(oc --namespace $namespace get serviceAccount $serviceAccount -o jsonpath='{.secrets[1].name}')
ca=$(oc --namespace $namespace get secret/$secretName -o jsonpath='{.data.ca\.crt}')
token=$(oc --namespace $namespace get secret/$secretName -o jsonpath='{.data.token}' | base64 --decode)

echo "
---
apiVersion: v1
kind: Config
clusters:
  - name: ${clusterName}
    cluster:
      certificate-authority-data: ${ca}
      server: ${server}
contexts:
  - name: ${serviceAccount}@${clusterName}
    context:
      cluster: ${clusterName}
      namespace: ${serviceAccount}
      user: ${serviceAccount}
users:
  - name: ${serviceAccount}
    user:
      token: ${token}
current-context: ${serviceAccount}@${clusterName}
"
```

3.  Grant the service account the permissions to create projects

```bash
oc adm policy add-cluster-role-to-user self-provisioner -z operator-pipelines -n default
```

4. Create the dockerconfig secret, containing the credentials to registry that stores the images to be published

```bash
cat << EOF > registry-secret.yml
apiVersion: v1
kind: Secret
metadata:
  name: registry-dockerconfig-secret
data:
  .dockerconfigjson: < BASE64 ENCODED DOCKER CONFIG >
type: kubernetes.io/dockerconfigjson
EOF

oc create -f registry-secret.yml
```

5. Link this secret with the created service account 

```bash
oc secret link operator-pipelines registry-dockerconfig-secret
```
