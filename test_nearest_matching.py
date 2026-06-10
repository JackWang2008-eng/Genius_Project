from matching import find_nearest_helper_for_request


def test_finds_nearest_available_matching_helper():
    request = {
        "id": 1,
        "zone": "Shelter",
        "need_type": "Medical",
    }

    helpers = [
        {
            "id": 10,
            "volunteer_name": "Far Doctor",
            "zone": "Hospital",
            "resource_type": "Doctor",
            "status": "Available",
        },
        {
            "id": 11,
            "volunteer_name": "Near Nurse",
            "zone": "School",
            "resource_type": "Nurse",
            "status": "Available",
        },
        {
            "id": 12,
            "volunteer_name": "Wrong Resource",
            "zone": "Shelter",
            "resource_type": "Food",
            "status": "Available",
        },
    ]

    edges = [
        {"from": "Hospital", "to": "Shelter", "time": 20},
        {"from": "School", "to": "Shelter", "time": 5},
    ]

    match = find_nearest_helper_for_request(request, helpers, edges)

    assert match["helper"]["id"] == 11
    assert match["travel_time"] == 5
    assert match["path"] == ["School", "Shelter"]
