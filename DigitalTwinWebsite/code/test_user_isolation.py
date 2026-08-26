import os
import sys
import json
import uuid
import unittest

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from App import app, ProjectService

class InMemoryCollection:
    def __init__(self, data_list):
        self.data_list = data_list

    def find(self, query=None):
        if not query:
            return list(self.data_list)
        results = []
        for item in self.data_list:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                results.append(item)
        return results

class InMemoryRepository:
    def __init__(self):
        self.collections = {}

    def connect_to_database(self):
        pass

    def create_record(self, collection_name, data):
        col = self.collections.setdefault(collection_name, [])
        doc = dict(data)
        doc['_id'] = str(uuid.uuid4())
        col.append(doc)
        return doc['_id']

    def read_record(self, collection_name, query):
        col = self.collections.get(collection_name, [])
        for item in col:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                return item
        return None

    def update_record(self, collection_name, query, update_data):
        col = self.collections.get(collection_name, [])
        matched = 0
        updated = 0
        for item in col:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                matched += 1
                if any(isinstance(k, str) and k.startswith("$") for k in update_data.keys()):
                    if "$set" in update_data:
                        item.update(update_data["$set"])
                    if "$inc" in update_data:
                        for ik, iv in update_data["$inc"].items():
                            item[ik] = item.get(ik, 0) + iv
                else:
                    item.update(update_data)
                updated += 1
        return {"matched_count": matched, "modified_count": updated}

    def delete_record(self, collection_name, query):
        col = self.collections.get(collection_name, [])
        to_remove = []
        for item in col:
            match = True
            for k, v in query.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                to_remove.append(item)
        for item in to_remove:
            col.remove(item)
        return {"deleted_count": len(to_remove)}

    def read_all_records(self, collection_name):
        col = self.collections.setdefault(collection_name, [])
        return InMemoryCollection(col)


class UserIsolationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.in_memory_repo = InMemoryRepository()
        cls.orig_repo = ProjectService.repo
        ProjectService.set_repository(cls.in_memory_repo)

    @classmethod
    def tearDownClass(cls):
        ProjectService.set_repository(cls.orig_repo)

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client1 = app.test_client()
        self.client2 = app.test_client()
        self.unauth_client = app.test_client()

        self.user1_id = "test_user_1_id"
        self.user2_id = "test_user_2_id"
        self.project_p1 = "AutomatedTest_P1_User1"
        self.project_p2 = "AutomatedTest_P2_User2"

        # Set sessions
        with self.client1.session_transaction() as sess:
            sess['logged_in_id'] = self.user1_id

        with self.client2.session_transaction() as sess:
            sess['logged_in_id'] = self.user2_id

    def tearDown(self):
        # Cleanup created projects
        ProjectService.delete_project(self.project_p1)
        ProjectService.delete_project(self.project_p2)

    def test_01_unauthenticated_requests_rejected(self):
        print("\n--- Running Test 01: Unauthenticated requests rejected ---")
        res = self.unauth_client.get('/getAllProjects')
        self.assertEqual(res.status_code, 401, f"Expected 401 for /getAllProjects, got {res.status_code}")

        res = self.unauth_client.post('/createProject', data={'project_name': 'TestUnauth', 'project_id': '123'})
        self.assertEqual(res.status_code, 401, f"Expected 401 for /createProject, got {res.status_code}")

        res = self.unauth_client.post('/upload_editor_data', data={'project_name': 'TestUnauth', 'myData': '{}'})
        self.assertEqual(res.status_code, 401, f"Expected 401 for /upload_editor_data, got {res.status_code}")

        res = self.unauth_client.get('/download_survey_responses?project_name=TestUnauth')
        self.assertEqual(res.status_code, 401, f"Expected 401 for /download_survey_responses, got {res.status_code}")

        res = self.unauth_client.get('/export_survey_csv?project_name=TestUnauth')
        self.assertEqual(res.status_code, 401, f"Expected 401 for /export_survey_csv, got {res.status_code}")
        print("Test 01 passed: All unauthenticated access returned 401.")

    def test_02_project_creation_and_isolation(self):
        print("\n--- Running Test 02: Project creation and isolation ---")
        # User 1 creates P1
        res1 = self.client1.post('/createProject', data={'project_name': self.project_p1, 'project_id': 'id_p1'})
        self.assertEqual(res1.status_code, 201)

        # User 2 creates P2
        res2 = self.client2.post('/createProject', data={'project_name': self.project_p2, 'project_id': 'id_p2'})
        self.assertEqual(res2.status_code, 201)

        # Check owner saved in saveData.txt and repo
        owner_p1 = ProjectService.get_project_owner(self.project_p1)
        owner_p2 = ProjectService.get_project_owner(self.project_p2)
        self.assertEqual(owner_p1, self.user1_id, f"P1 owner should be user1, got {owner_p1}")
        self.assertEqual(owner_p2, self.user2_id, f"P2 owner should be user2, got {owner_p2}")

        # User 1 gets all projects
        list1_res = self.client1.get('/getAllProjects')
        self.assertEqual(list1_res.status_code, 201)
        data1 = json.loads(list1_res.data.decode('utf-8'))
        p1_names = [p['projectName'] for p in data1['projects']]
        self.assertIn(self.project_p1, p1_names, "User 1 should see their own project P1")
        self.assertNotIn(self.project_p2, p1_names, "User 1 must NOT see User 2's project P2")

        # User 2 gets all projects
        list2_res = self.client2.get('/getAllProjects')
        self.assertEqual(list2_res.status_code, 201)
        data2 = json.loads(list2_res.data.decode('utf-8'))
        p2_names = [p['projectName'] for p in data2['projects']]
        self.assertIn(self.project_p2, p2_names, "User 2 should see their own project P2")
        self.assertNotIn(self.project_p1, p2_names, "User 2 must NOT see User 1's project P1")
        print("Test 02 passed: Projects strictly separated by owner.")

    def test_03_editor_data_upload_and_owner_preservation(self):
        print("\n--- Running Test 03: Editor upload permissions and owner preservation ---")
        # User 1 creates P1
        self.client1.post('/createProject', data={'project_name': self.project_p1, 'project_id': 'id_p1'})

        # User 2 attempts to upload editor data to User 1's project P1 -> should be 403
        hack_res = self.client2.post('/upload_editor_data', data={
            'project_name': self.project_p1,
            'myData': json.dumps({"projectName": self.project_p1, "projectId": "id_p1"})
        })
        self.assertEqual(hack_res.status_code, 403, f"Expected 403 when User 2 writes to P1, got {hack_res.status_code}")

        # User 1 uploads editor data (simulating Unity where 'owner' field might not be in payload)
        client_payload = {
            "projectName": self.project_p1,
            "projectId": "id_p1",
            "projectDescription": "Updated by editor without owner field",
            "projectImageID": "img123"
        }
        valid_res = self.client1.post('/upload_editor_data', data={
            'project_name': self.project_p1,
            'myData': json.dumps(client_payload)
        })
        self.assertEqual(valid_res.status_code, 201)

        # Verify owner is still user1
        owner = ProjectService.get_project_owner(self.project_p1)
        self.assertEqual(owner, self.user1_id, "Owner must be preserved after editor data upload")
        print("Test 03 passed: Editor upload protected and owner preserved.")

    def test_04_survey_permissions_and_export(self):
        print("\n--- Running Test 04: Survey authorization and CSV export ---")
        # User 1 creates P1
        self.client1.post('/createProject', data={'project_name': self.project_p1, 'project_id': 'id_p1'})

        # User 2 attempts to upload survey data to P1 -> 403
        hack_survey = self.client2.post('/upload_survey_data', data={
            'project_name': self.project_p1,
            'survey_data': json.dumps({"Questions": []})
        })
        self.assertEqual(hack_survey.status_code, 403)

        # User 1 uploads survey data -> 200/201
        survey_def = {
            "Questions": [
                {"Id": 1, "Title": "Jak se vám líbí projekt?", "QuestionType": 1, "Answers": [{"Text": "Super"}]}
            ]
        }
        res_survey = self.client1.post('/upload_survey_data', data={
            'project_name': self.project_p1,
            'survey_data': json.dumps(survey_def)
        })
        self.assertIn(res_survey.status_code, [200, 201])

        # Anonymous respondent submits survey response -> public, should succeed (201)
        response_payload = {
            "SurveyName": self.project_p1,
            "Responses": [
                {"QuestionId": 1, "SelectedIdx": 0}
            ]
        }
        anon_sub = self.unauth_client.post('/upload_survey_response', data={
            'project_name': self.project_p1,
            'response_data': json.dumps(response_payload)
        })
        self.assertEqual(anon_sub.status_code, 201)

        # User 2 tries to download responses -> 403
        res_u2_dl = self.client2.get(f'/download_survey_responses?project_name={self.project_p1}')
        self.assertEqual(res_u2_dl.status_code, 403)

        # User 2 tries to export CSV -> 403
        res_u2_csv = self.client2.get(f'/export_survey_csv?project_name={self.project_p1}')
        self.assertEqual(res_u2_csv.status_code, 403)

        # User 1 downloads responses -> 200
        res_u1_dl = self.client1.get(f'/download_survey_responses?project_name={self.project_p1}')
        self.assertEqual(res_u1_dl.status_code, 200)
        data_dl = json.loads(res_u1_dl.data.decode('utf-8'))
        self.assertTrue(len(data_dl) > 0)

        # User 1 exports CSV -> 200 with CSV headers
        res_u1_csv = self.client1.get(f'/export_survey_csv?project_name={self.project_p1}')
        self.assertEqual(res_u1_csv.status_code, 200)
        csv_text = res_u1_csv.data.decode('utf-8')
        self.assertIn("Jak se vám líbí projekt?", csv_text)
        print("Test 04 passed: Survey responses and CSV export strictly authorized.")

    def test_05_project_edit_duplicate_delete_permissions(self):
        print("\n--- Running Test 05: Edit, duplicate, and delete permissions ---")
        # User 1 creates P1
        self.client1.post('/createProject', data={'project_name': self.project_p1, 'project_id': 'id_p1'})

        # User 2 tries to rename P1 -> 403
        res_rename_hacker = self.client2.post('/editProjectName', data={
            'oldProjectName': self.project_p1,
            'newProjectName': 'RenamedByHacker'
        })
        self.assertEqual(res_rename_hacker.status_code, 403)

        # User 2 tries to duplicate P1 -> 403
        res_dup_hacker = self.client2.post('/duplicate_project', data={
            'project_name': self.project_p1
        })
        self.assertEqual(res_dup_hacker.status_code, 403)

        # User 2 tries to delete P1 -> 403
        res_del_hacker = self.client2.delete('/deleteProject', data={
            'project_name': self.project_p1
        })
        self.assertEqual(res_del_hacker.status_code, 403)

        # User 1 deletes P1 -> 200
        res_del_owner = self.client1.delete('/deleteProject', data={
            'project_name': self.project_p1
        })
        self.assertEqual(res_del_owner.status_code, 200)
        print("Test 05 passed: Edit, duplicate, and delete permissions enforced.")

    def test_06_survey_status_and_respondent_count(self):
        print("\n--- Running Test 06: Survey status and respondent count tracking ---")
        # 1. User 1 creates project
        create_res = self.client1.post('/createProject', data={'project_name': self.project_p1, 'project_id': 'id_p1'})
        self.assertEqual(create_res.status_code, 201)

        # Verify initial values via getAllProjects: hasSurvey = False, respondentCount = 0
        get_res = self.client1.get('/getAllProjects')
        self.assertEqual(get_res.status_code, 201)
        projects = json.loads(get_res.data.decode('utf-8'))['projects']
        p1 = next((p for p in projects if p['projectName'] == self.project_p1), None)
        self.assertIsNotNone(p1)
        self.assertFalse(p1.get('hasSurvey', False), "hasSurvey should initially be False")
        self.assertEqual(p1.get('respondentCount', 0), 0, "respondentCount should initially be 0")

        # 2. Upload survey data with questions -> hasSurvey should become True
        survey_json = json.dumps({
            "Questions": [
                {"Text": "Otázka 1?", "Answers": ["A", "B"]}
            ]
        })
        upload_s_res = self.client1.post('/upload_survey_data', data={
            'project_name': self.project_p1,
            'survey_data': survey_json
        })
        self.assertIn(upload_s_res.status_code, [200, 201])

        # Check that hasSurvey is now True
        get_res2 = self.client1.get('/getAllProjects')
        projects2 = json.loads(get_res2.data.decode('utf-8'))['projects']
        p1_after_survey = next((p for p in projects2 if p['projectName'] == self.project_p1), None)
        self.assertTrue(p1_after_survey.get('hasSurvey', False), "hasSurvey should be True after uploading questions")
        self.assertEqual(p1_after_survey.get('respondentCount', 0), 0, "respondentCount should still be 0 before responses")

        # 3. Submit 2 responses anonymously -> respondentCount should become 2
        for i in range(2):
            resp_sub = self.unauth_client.post('/upload_survey_response', data={
                'project_name': self.project_p1,
                'response_data': json.dumps({"answers": [i]})
            })
            self.assertEqual(resp_sub.status_code, 201)

        get_res3 = self.client1.get('/getAllProjects')
        projects3 = json.loads(get_res3.data.decode('utf-8'))['projects']
        p1_after_resps = next((p for p in projects3 if p['projectName'] == self.project_p1), None)
        self.assertTrue(p1_after_resps.get('hasSurvey', False))
        self.assertEqual(p1_after_resps.get('respondentCount', 0), 2, "respondentCount should be 2 after 2 submissions")

        # 4. Duplicate project -> duplicated project should keep hasSurvey = True, but respondentCount = 0
        dup_res = self.client1.post('/duplicate_project', data={'project_name': self.project_p1})
        self.assertEqual(dup_res.status_code, 201)

        get_res4 = self.client1.get('/getAllProjects')
        projects4 = json.loads(get_res4.data.decode('utf-8'))['projects']
        p1_dup = next((p for p in projects4 if p['projectName'].startswith(f"{self.project_p1} (")), None)
        self.assertIsNotNone(p1_dup, "Duplicated project should exist")
        self.assertTrue(p1_dup.get('hasSurvey', False), "Duplicated project should inherit hasSurvey = True")
        self.assertEqual(p1_dup.get('respondentCount', 0), 0, "Duplicated project respondentCount should be reset to 0")

        # Cleanup duplicated project
        self.client1.delete('/deleteProject', data={'project_name': p1_dup['projectName']})
        print("Test 06 passed: Survey status and respondent count correctly maintained and returned.")

if __name__ == '__main__':
    unittest.main()
