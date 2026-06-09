import os
import tempfile
import unittest

import database


class DashboardStatsTest(unittest.TestCase):
    def setUp(self):
        self.original_database = database.DATABASE
        file_handle, self.test_database = tempfile.mkstemp(suffix=".db")
        os.close(file_handle)
        os.remove(self.test_database)

        database.DATABASE = self.test_database
        database.init_db()

    def tearDown(self):
        database.DATABASE = self.original_database
        if os.path.exists(self.test_database):
            os.remove(self.test_database)

    def test_dashboard_stats_count_requests_and_helpers(self):
        database.add_request({
            "resident_name": "Critical Resident",
            "phone_number": "111",
            "zone": "Zone A",
            "need_type": "Medical",
            "injury_level": "Serious",
            "mobility_status": "Cannot walk",
            "vulnerable_person": "Yes",
            "evacuation_need": "Yes",
            "safe_shelter": "No",
            "red_flags": ["severe_bleeding"],
            "urgency": "Critical",
            "priority_score": 100,
            "triage_reasons": ["Emergency warning sign"],
        })

        database.add_request({
            "resident_name": "Assigned Resident",
            "phone_number": "222",
            "zone": "Zone B",
            "need_type": "Food",
            "injury_level": "None",
            "mobility_status": "Can walk",
            "vulnerable_person": "No",
            "evacuation_need": "No",
            "safe_shelter": "Yes",
            "red_flags": [],
            "urgency": "Low",
            "priority_score": 10,
            "triage_reasons": ["Basic need"],
        })

        database.add_volunteer({
            "volunteer_name": "Community Helper",
            "phone_number": "333",
            "helper_type": "Community Volunteer",
            "zone": "Zone A",
            "resource_type": "Food",
            "availability": "Now",
        })

        database.add_volunteer({
            "volunteer_name": "Nurse Lee",
            "phone_number": "444",
            "helper_type": "Professional Responder",
            "zone": "Zone A",
            "resource_type": "Nurse",
            "availability": "Now",
        })

        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET status = 'Assigned' WHERE resident_name = ?", ("Assigned Resident",))
        cursor.execute("UPDATE volunteers SET status = 'Assigned' WHERE volunteer_name = ?", ("Community Helper",))
        conn.commit()
        conn.close()

        stats = database.get_dashboard_stats()

        self.assertEqual(stats["total_requests"], 2)
        self.assertEqual(stats["open_requests"], 1)
        self.assertEqual(stats["assigned_requests"], 1)
        self.assertEqual(stats["critical_requests"], 1)
        self.assertEqual(stats["total_helpers"], 2)
        self.assertEqual(stats["available_helpers"], 1)
        self.assertEqual(stats["community_volunteers"], 1)
        self.assertEqual(stats["professional_responders"], 1)

    def test_location_matching_ignores_case_and_extra_spaces(self):
        database.add_request({
            "resident_name": "Resident A",
            "phone_number": "111",
            "zone": " Main St Shelter ",
            "need_type": "Medical",
            "injury_level": "Minor",
            "mobility_status": "Can walk",
            "vulnerable_person": "No",
            "evacuation_need": "No",
            "safe_shelter": "Yes",
            "red_flags": [],
            "urgency": "Medium",
            "priority_score": 40,
            "triage_reasons": ["Medical request"],
        })

        database.add_volunteer({
            "volunteer_name": "Nurse Lee",
            "phone_number": "222",
            "helper_type": "Professional Responder",
            "zone": "main st shelter",
            "resource_type": "Nurse",
            "availability": "Now",
        })

        matches = database.find_matches()

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["resident_name"], "Resident A")
        self.assertEqual(matches[0]["volunteer_name"], "Nurse Lee")


if __name__ == "__main__":
    unittest.main()
