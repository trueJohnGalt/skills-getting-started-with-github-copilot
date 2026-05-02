import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

import src.app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def reset_app_state():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)


def test_root_redirects_to_static_index():
    reset_app_state()
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    reset_app_state()
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success():
    reset_app_state()
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"

    response = client.post(url, params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404():
    reset_app_state()
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_400():
    reset_app_state()
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]
    url = f"/activities/{quote(activity_name)}/signup"

    response = client.post(url, params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_from_activity_success():
    reset_app_state()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/unregister"

    response = client.delete(url, params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    reset_app_state()
    activity_name = "Chess Club"
    url = f"/activities/{quote(activity_name)}/unregister"

    response = client.delete(url, params={"email": "missing@student.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
