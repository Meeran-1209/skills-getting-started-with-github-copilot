import pytest


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activity_data(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) == 9
    assert activities["Chess Club"] == {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    }


def test_signup_accepts_query_email_and_case_insensitive_activity_name(
    client, activities
):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/chess%20club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_accepts_json_email(client, activities):
    # Arrange
    email = "jsonstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Soccer%20Team/signup",
        json={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Soccer Team"}
    assert email in activities["Soccer Team"]["participants"]


def test_signup_accepts_form_email(client, activities):
    # Arrange
    email = "formstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Soccer%20Team/signup",
        data={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Soccer Team"}
    assert email in activities["Soccer Team"]["participants"]


def test_signup_rejects_duplicate_email_case_insensitively(client, activities):
    # Arrange
    email = " MICHAEL@MERGINGTON.EDU "
    original_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == original_participants


def test_signup_rejects_full_activity(client, activities):
    # Arrange
    activity = activities["Soccer Team"]
    activity["participants"] = [
        f"student{index}@mergington.edu"
        for index in range(activity["max_participants"])
    ]
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert email not in activity["participants"]


@pytest.mark.parametrize("email", ["", "not-an-email"])
def test_signup_rejects_invalid_email(client, email):
    # Arrange

    # Act
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Valid email is required"}


def test_signup_rejects_missing_email(client):
    # Arrange

    # Act
    response = client.post("/activities/Soccer Team/signup")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Valid email is required"}


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_matching_email_case_insensitively(client, activities):
    # Arrange
    email = "MICHAEL@MERGINGTON.EDU"

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_when_student_is_not_signed_up(client):
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown%20Activity/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
