from databox import Client


def send_metrics_to_databox_service(metrics, databox_access_token):
    client = Client(databox_access_token)
    # Prepare the data for Databox
    metrics_data = [
        {
            'key': metric.name,
            'value': metric.value,
            'date': metric.date,
            'attributes': metric.attributes
        } for metric in metrics
    ]
    metric_keys = [metric['key'] for metric in metrics_data]
    try:
        # Send data to Databox
        for metric in metrics_data:
            client.push(metric['key'], metric['value'])
        return True, metric_keys
    except Exception as e:
        print(f"Failed to send metrics to Databox: {e}")
        return False, metric_keys
