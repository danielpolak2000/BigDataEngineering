kubectl delete pod grafana-5f58f894cf-2qz59 -n default

kubectl delete deployment my-deployment -n default

kubectl port-forward service/influxdb 8086:8086

kubectl port-forward -n default service/grafana 3000:80

influx bucket update -n your_bucket_name --retention 0

kubectl exec -it influxdb-<pod-id> -n default -- /bin/sh