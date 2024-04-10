# Represents the Risk Event. This is the payload that will be send from the vehicle to the cloud
class RiskEvent:
    def __init__(self, name, eventId, riskLevel, timestamp, eventData):
        self.name = name
        self.eventId = eventId
        self.riskLevel = riskLevel
        self.timestamp = timestamp
        self.eventData = eventData


# For now, a risk detector needs to keep track of their own internal history.
def risk_event_detector(event_dict, timeout_dict, signal, signal_dict, callback):
    """
    Event detector
    """
    for event in event_dict.values():
        if signal.name in event.relevant_signals:
            if signal.timestamp > timeout_dict[event.name]:
                if event.check_condition(event_dict, signal_dict):
                    timeout_dict[event.name] = signal.timestamp + event.timeout
                    callback_data = event.collect_callback_data(signal_dict)
                    callback(
                        RiskEvent(
                            event.name,
                            event.eventId,
                            event.riskLevel,
                            signal.timestamp,
                            callback_data,
                        )
                    )
