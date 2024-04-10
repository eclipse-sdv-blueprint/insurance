import numpy as np


def process_signal_data(condition, signal_data):
    method = condition["method"]
    context_length = condition["context_length"]
    if method:
        if context_length <= 1:
            raise ValueError("Context length must be above 1 when a method is applied.")
        if method == "prev":
            processed_signal_value = signal_data[-context_length]
        elif method == "mean":
            processed_signal_value = np.mean(signal_data[-context_length:])
        elif method == "min":
            processed_signal_value = min(signal_data[-context_length:])
        elif method == "max":
            processed_signal_value = max(signal_data[-context_length:])
        else:
            raise ValueError(
                f"Method {method} is not supported. Supported methods are: [prev, mean, min, max]."
            )

    else:
        if context_length != 1:
            raise ValueError("Context length must be 1 if no method is applied.")
        processed_signal_value = signal_data[-1]

    return processed_signal_value


def get_signal_value(cond, signal_dict, event_dict):
    signal_name = cond.get("signal_name", False)
    if signal_name:
        signal_data = signal_dict[signal_name]
        if len(signal_data) < cond["context_length"]:
            # Not enough data available
            return False
        signal_value = process_signal_data(cond, signal_data)
    else:
        event_name = cond.get("event_name", False)
        if not event_name:
            raise ValueError(
                "Either signal_name or event_name must be specified in a condition."
            )
        signal_value = 1 if event_dict[event_name].running else 0
    return signal_value


class EventDefinition:
    def __init__(
        self,
        name,
        eventId,
        riskLevel,
        startConditions,
        endConditions,
        eventData,
        timeout,
    ):
        self.name = name
        self.eventId = eventId
        self.riskLevel = riskLevel
        self.startConditions = startConditions
        self.endConditions = endConditions
        self.eventData = eventData
        self.timeout = timeout

        self.relevant_signals = list(
            set(
                [
                    c.get("signal_name", False)
                    for c in self.startConditions
                    if c.get("signal_name", False)
                ]
                + [
                    c.get("signal_name", False)
                    for c in self.endConditions
                    if c.get("signal_name", False)
                ]
            )
        )
        self.running = False

    def check_condition(self, event_dict, signal_dict):
        if self.running:
            relevant_conditions = self.endConditions
        else:
            relevant_conditions = self.startConditions

        for cond in relevant_conditions:
            signal_value = get_signal_value(cond, signal_dict, event_dict)

            if signal_value != signal_value:
                # Prevent positive events with nan
                return False
            elif cond["operator"] == "eq":
                if signal_value != cond["value"]:
                    return False
            elif cond["operator"] == "gt":
                if signal_value <= cond["value"]:
                    return False
            elif cond["operator"] == "lt":
                if signal_value >= cond["value"]:
                    return False
            elif cond["operator"] == "bt":
                cond_value = cond["value"]
                if type(cond_value) != tuple:
                    raise ValueError(
                        f"Value must be a tuple when operator is 'bt'. Given is: {cond_value}"
                    )
                if signal_value <= cond_value[0] or signal_value >= cond_value[1]:
                    return False
            else:
                raise ValueError(
                    f"Condition parameter {cond[0]} unsupported. Supported are [eq, gt, lt, bt]."
                )

        if len(self.endConditions) > 0:
            if self.running:
                self.running = False
            else:
                self.running = True
        return True

    def collect_callback_data(self, signal_dict):
        callback_data = {}
        for s, l in self.eventData.items():
            if l == 1:
                callback_data[s] = signal_dict[s][-1]
            elif l > 1:
                callback_data[s] = signal_dict[s][-l:]
            else:
                raise ValueError("Length of callback data must be greater 0.")
        if self.running:
            callback_data["start"] = True
        return callback_data


###### Speeding ###############################################################

speeding = EventDefinition(
    name="speeding",
    eventId=1,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 130,
        },
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 130,
        },
    ],
    endConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "lt",
            "value": 130,
        },
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": "prev",
            "context_length": 2,
            "operator": "gt",
            "value": 130,
        },
    ],
    eventData={
        "Vehicle_Speed_Speed": 60,
        # "OdometerValue": 1
    },
    timeout=0,
)


###### Massive Speeding #######################################################

massive_speeding = EventDefinition(
    name="massive_speeding",
    eventId=2,
    riskLevel=2,
    startConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 180,
        },
    ],
    endConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "lt",
            "value": 180,
        },
    ],
    eventData={
        "Vehicle_Speed_Speed": 60,
        # "Rain_Sensor_Activated",
        # "OdometerValue": 1
    },
    timeout=0,
)

###### Cruise Control #########################################################

cruise_control_activated = EventDefinition(
    name="cruise_control_activated",
    eventId=3,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "ADAS_CruiseControl_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
    ],
    endConditions=[
        {
            "signal_name": "ADAS_CruiseControl_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 0,
        },
    ],
    eventData={
        "ADAS_CruiseControl_IsActive": 1,
        "Vehicle_Speed_Speed": 20,
        # "OdometerValue": 1
    },
    timeout=0,
)

###### TCS ####################################################################

tcs_activated = EventDefinition(
    name="tcs_activated",
    eventId=4,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "ADAS_TCS_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
    ],
    endConditions=[
        {
            "signal_name": "ADAS_TCS_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 0,
        },
    ],
    eventData={
        "ADAS_TCS_IsActive": 1,
        # "OdometerValue": 1
    },
    timeout=0,
)

###### ESC ####################################################################

esc_activated = EventDefinition(
    name="esc_activated",
    eventId=5,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "ADAS_ESC_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
    ],
    endConditions=[
        {
            "signal_name": "ADAS_ESC_IsActive",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 0,
        },
    ],
    eventData={
        "ADAS_TCS_IsActive": 1,
        # "OdometerValue": 1
    },
    timeout=0,
)

###### Performance Mode #######################################################

performance_mode_activated = EventDefinition(
    name="performance_mode_activated",
    eventId=6,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Drivetrain_Transmission_PerformanceMode",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
    ],
    endConditions=[
        {
            "signal_name": "Drivetrain_Transmission_PerformanceMode",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 0,
        },
    ],
    eventData={
        "Drivetrain_Transmission_PerformanceMode": 1,
        # "OdometerValue": 1
    },
    timeout=0,
)

###### Autobahn ###############################################################

autobahn = EventDefinition(
    name="autobahn",
    eventId=7,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": "mean",
            "context_length": 60,
            "operator": "gt",
            "value": 80,
        },
        {
            "signal_name": "Chassis_SteeringWheel_Angle",
            "method": "mean",
            "context_length": 60,
            "operator": "lt",
            "value": 2,
        },
    ],
    endConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": "mean",
            "context_length": 60,
            "operator": "lt",
            "value": 80,
        },
        {
            "signal_name": "Chassis_SteeringWheel_Angle",
            "method": "mean",
            "context_length": 60,
            "operator": "gt",
            "value": 2,
        },
    ],
    eventData={
        "Vehicle_Speed_Speed": 60,
        "Chassis_SteeringWheel_Angle": 60,
        # "OdometerValue": 1
    },
    timeout=0,
)

###### Traffic Jam ############################################################

traffic_jam = EventDefinition(
    name="traffic_jam",
    eventId=8,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Body_Lights_IsHazardOn",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
        {
            "signal_name": "Chassis_Brake_Pressed",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
        {"event_name": "autobahn", "operator": "eq", "value": 1},
    ],
    endConditions=[],
    eventData={
        "Body_Lights_IsHazardOn": 10,
        "Vehicle_Speed_Speed": 60,
        "Chassis_Brake_Pressed": 60,
        # "OdometerValue": 1
    },
    timeout=60,
)

###### Seat Belted ############################################################

no_seatbelt = EventDefinition(
    name="no_seatbelt",
    eventId=9,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Vehicle_Speed_Speed",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 30,
        },
        {
            "signal_name": "Seat_Switch_IsBelted",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 0,
        },
    ],
    endConditions=[
        {
            "signal_name": "Seat_Switch_IsBelted",
            "method": False,
            "context_length": 1,
            "operator": "eq",
            "value": 1,
        },
    ],
    eventData={
        "Seat_Switch_IsBelted": 10,
        "Vehicle_Speed_Speed": 60,
        # "OdometerValue": 1
    },
    timeout=0,
)

###############################################################################

harsh_braking = EventDefinition(
    name="harsh_braking",
    eventId=10,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": -2,
        },
        {
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": -2,
        },
    ],
    endConditions=[],
    eventData={
        # Additional context information
        "Vehicle_Acceleration_Longitudinal": 20,
        "Vehicle_Speed_Speed": 20,
        # Lets collect data about the actions of the user, such as how hard the person is braking and any swerve for post analytics
        "Chassis_Brake_Pressure": 20,
        "Chassis_SteeringWheel_Angle": 20,
        "Vehicle_Acceleration_Lateral": 20,
        # Also lets collect some information about the car -Are the TCS and ABS system healthy and did they activate as part of the maneuver?
        "ADAS_ABS_Error": 20,
        "ADAS_ABS_IsEngaged": 20,
        "ADAS_TCS_IsEngaged": 20,
    },
    timeout=0,
)

###############################################################################

harsh_acceleration = EventDefinition(
    name="harsh_acceleration",
    eventId=11,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 2,
        },
        {
            "signal_name": "Vehicle_Acceleration_Longitudinal",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 2,
        },
    ],
    endConditions=[],
    eventData={
        # Additional context information
        "Vehicle_Acceleration_Longitudinal": 20,
        "Vehicle_Speed_Speed": 20,
        # Lets collect data about the actions of the user, such as how hard the person is braking and any swerve for post analytics
        "Chassis_Accelerator_PedalPosition": 20,
        "Chassis_SteeringWheel_Angle": 20,
        "Vehicle_Acceleration_Lateral": 20,
        # Also lets collect some information about the car -Are the TCS and ABS system healthy and did they activate as part of the maneuver?
        "ADAS_ABS_Error": 20,
        "ADAS_ABS_IsEngaged": 20,
        "ADAS_TCS_IsEngaged": 20,
    },
    timeout=0,
)

###############################################################################

harsh_cornering = EventDefinition(
    name="harsh_cornering",
    eventId=12,
    riskLevel=1,
    startConditions=[
        {
            "signal_name": "Vehicle_Acceleration_Lateral",
            "method": False,
            "context_length": 1,
            "operator": "gt",
            "value": 0.5,
        },
        {
            "signal_name": "Vehicle_Acceleration_Lateral",
            "method": "prev",
            "context_length": 2,
            "operator": "lt",
            "value": 0.5,
        },
    ],
    endConditions=[],
    eventData={
        # Additional context information: What were the G-Forces and what was the vehicle speed
        "Vehicle_Acceleration_Lateral": 20,
        "Vehicle_Acceleration_Longitudinal": 20,
        "Vehicle_Speed_Speed": 20,
        # Lets collect data about the harsh cornering, such as acceleration and braking profile, steering wheel angle and turn indicator used.
        "Chassis_Brake_Pressure": 20,
        "Chassis_Accelerator_PedalPosition": 20,
        "Chassis_SteeringWheel_Angle": 20,
        "Chassis_SteeringWheel_AngleSign": 20,
        "Body_Lights_IsRightIndicatorOn": 20,
        "Body_Lights_IsLeftIndicatorOn": 20,
        # Also lets collect some information about the car: Did the TCS engage? and lets get the wheel speeds too!
        "ADAS_TCS_IsEngaged": 20,
        "Vehicle_Speed_Wheel_FrontLeft": 20,
        "Vehicle_Speed_Wheel_FrontRight": 20,
        "Vehicle_Speed_Wheel_RearLeft": 20,
        "Vehicle_Speed_Wheel_RearRight": 20,
    },
    timeout=0,
)

###############################################################################

###############################################################################
