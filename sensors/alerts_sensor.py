import requests
from st2reactor.sensor.base import PollingSensor

class PrometheusAlertsSensor(PollingSensor):
    def __init__(self, sensor_service, config=None, poll_interval=None):
        super(PrometheusAlertsSensor, self).__init__(sensor_service=sensor_service,config=config,poll_interval=poll_interval)
        self._logger = self._sensor_service.get_logger(__name__)
        self.url = self._config['prometheus_url']

    def setup(self):
        self._logger.debug('Prometheus Alerts Sensor initialized')

    def poll(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            alerts = response.json()['data']['alerts']
            for alert in alerts:
                if alert['status'] == 'firing':
                    self._logger.info('Received firing alert: %s', alert)
                    self._trigger_alert(alert)
        except Exception as e:
            self._logger.exception('Failed to fetch alerts from Prometheus: %s', str(e))

    def _trigger_alert(self, alert):
        payload = {
            'alertname': alert['labels']['alertname'],
            'severity': alert['labels']['severity'],
            'description': alert['annotations']['description'],
            'value': alert['annotations']['value'],
            'instance': alert['labels']['instance']
            # Add more fields as needed
        }
        self._sensor_service.dispatch(trigger='prometheus.alert',payload=payload)
