import os
import time
from typing import List

from dotenv import load_dotenv
import isilon_sdk.v9_4_0
from pydantic import BaseModel


# Load environment variables.
load_dotenv()
ISILON_IP_ADDRESS = os.getenv('ISILON_IP_ADDRESS')
ISILON_USERNAME = os.getenv('ISILON_USERNAME')
ISILON_PASSWORD = os.getenv('ISILON_PASSWORD')


# Dell Isilon configuration variables.
ISILON_CONFIG = isilon_sdk.v9_4_0.Configuration()
ISILON_CONFIG.host = f'https://{ISILON_IP_ADDRESS}'
ISILON_CONFIG.username = ISILON_USERNAME
ISILON_CONFIG.password = ISILON_PASSWORD
ISILON_CONFIG.verify_ssl = False

ISILON_API_CLIENT = isilon_sdk.v9_4_0.ApiClient(ISILON_CONFIG)
ISILON_HEALTHCHECK_API_CLIENT = isilon_sdk.v9_4_0.HealthcheckApi(ISILON_API_CLIENT)


class Alert(BaseModel):
    """
    Represents an alert that exists on a machine.

    Members:
        description (str): The description of the alert.
        affected_device (str): The device with the alert.
        severity (str): The severity of the alert.
    """

    description: str
    affected_device: str
    severity: str


def run_basic_healthcheck_evaluation() -> str:
    """
    Given any node IP address on a Dell Isilon cluster, run a basic healthcheck evaluation. Returns
    the evaluation ID needed to retrieve the results of the evaluation.

    Returns:
        str: The evaluation ID of the basic healthcheck evaluation.
    """

    # Run the basic healthcheck on the Dell Isilon.
    basic_healthcheck_evaluation_checklist = isilon_sdk.v9_4_0.HealthcheckEvaluationCreateParams(checklist_id="basic")
    basic_healthcheck_evaluation_response = ISILON_HEALTHCHECK_API_CLIENT.create_healthcheck_evaluation(basic_healthcheck_evaluation_checklist)
    
    # Extract the healthcheck evaluation ID from the response.
    basic_healthcheck_evaluation_id = basic_healthcheck_evaluation_response.id

    # Return the healthcheck evaluation ID.
    return basic_healthcheck_evaluation_id


def get_evaluation_results(evaluation_id: str) -> isilon_sdk.v9_4_0.HealthcheckEvaluationExtended:
    """
    Awaits the results of an evaluation given its ID. Returns the results once the evaluation successfully
    completes, otherwise returns "None".

    Args:
        evaluation_id (str): The evaluation ID to retrieve the results for.
    
    Returns:
        isilon_sdk.v9_4_0.HealthcheckEvaluationExtended: The evaluation results object.
    """

    # Keep checking this endpoint until the evaluation is complete.
    # Valid evaluation statuses: ["QUEUED", "RUNNING", "PAUSED", "FAILED", "COMPLETED"]
    evaluation_complete = False
    while not evaluation_complete:
        # Loop through all evaluations saved on the Isilon.
        all_healthchecks = ISILON_HEALTHCHECK_API_CLIENT.list_healthcheck_evaluations()
        for healthcheck in all_healthchecks.evaluations:
            # Check if this evaluation is the one that was provided.
            if healthcheck.id == evaluation_id:
                # Check if the evaluation has completed. Otherwise, wait a bit.
                if healthcheck.run_status == 'COMPLETED':
                    evaluation_complete = True
                else:
                    time.sleep(3)
                break

    # Return the completed healthcheck evaluation object.
    basic_healthcheck_results = ISILON_HEALTHCHECK_API_CLIENT.get_healthcheck_evaluation(evaluation_id)
    return basic_healthcheck_results.evaluations[0]


def cleanse_evaluation_results(evaluation: isilon_sdk.v9_4_0.HealthcheckEvaluationExtended) -> List[Alert]:
    """
    Convert the Dell Isilon SDK evaluation object into a list of alerts from the Isilon. Return the list.

    Args:
        evaluation (isilon_sdk.v9_4_0.HealthcheckEvaluationExtended): The evaluation object to extract alerts from.

    Returns:
        List[Alert]: The list of alerts we gathered from the evaluation object.
    """    

    # Loop through each alert in the evaluation.
    all_alerts = list[Alert]()
    for alert in evaluation.details:
        # Each alert's text is a list of strings. For each alert, join all the strings together.
        full_detail_string = ""
        for detail_substr in alert.details:
            full_detail_string += f'{detail_substr} '

        # Create an alert object from the concatenated alert text and other alert information.
        # Append this alert to the alerts return list.
        current_alert = Alert(description=full_detail_string, affected_device=alert.node, severity=alert.status, value=alert.value)
        all_alerts.append(current_alert)
    
    # Return all the alerts from this Isilon.
    return all_alerts


def get_alerts() -> List[Alert]:
    """
    Get the current alerts from this Dell Isilon. Return a list of the alerts.

    Returns:
        List[Alert]: Return a list of the alerts from this Dell Isilon.
    """

    # Get all alerts from the Dell Isilon.
    eval_id = run_basic_healthcheck_evaluation()

    # This is needed to prevent an SDK bug. More info: https://github.com/Isilon/isilon_sdk_python/issues/70
    # We are basically waiting until the evaluation completes.
    time.sleep(120) 

    # Recieve, serialize, and return the evaluation results from the Isilon.
    eval_obj = get_evaluation_results(eval_id)
    alerts = cleanse_evaluation_results(eval_obj)
    return alerts


def main():
    # Example of getting a list of alerts from the Isilon.
    all_isilon_alerts = get_alerts()

    # Print the list of alerts on the Isilon.
    for alert in all_isilon_alerts:
        print(alert)


if __name__ == "__main__":
    main()
