from unittest.mock import patch


class TestProgressEndpoints:
    def test_create_and_list_progress_entry(self, client):
        response = client.post("/progress", json={
            "weight_kg": 70.0,
            "entry_date": "2026-09-01",
            "notes": "starting point",
        })
        assert response.status_code == 200
        assert response.json()["weight_kg"] == 70.0

        list_response = client.get("/progress")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

    def test_create_entry_with_measurements(self, client):
        response = client.post("/progress", json={
            "weight_kg": 68.0,
            "entry_date": "2026-09-08",
            "waist_cm": 80.0,
            "chest_cm": 95.0,
            "arms_cm": 32.0,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["waist_cm"] == 80.0
        assert data["chest_cm"] == 95.0

    def test_delete_progress_entry(self, client):
        create_response = client.post("/progress", json={
            "weight_kg": 70.0,
            "entry_date": "2026-09-01",
        })
        entry_id = create_response.json()["id"]

        delete_response = client.delete(f"/progress/{entry_id}")
        assert delete_response.status_code == 200

        list_response = client.get("/progress")
        assert len(list_response.json()) == 0

    def test_cannot_delete_another_users_entry(self, client, other_user):
        create_response = client.post("/progress", json={
            "weight_kg": 70.0,
            "entry_date": "2026-09-01",
        })
        entry_id = create_response.json()["id"]

        delete_response = client.delete(
            f"/progress/{entry_id}",
            headers={"x-test-user": other_user.email},
        )
        assert delete_response.status_code == 404

    def test_set_and_get_goal_weight(self, client):
        set_response = client.put("/progress/goal", json={"goal_weight_kg": 65.0})
        assert set_response.status_code == 200
        assert set_response.json()["goal_weight_kg"] == 65.0

        get_response = client.get("/progress/goal")
        assert get_response.json()["goal_weight_kg"] == 65.0


class TestFeedbackEndpoints:
    def _create_chat_message(self, db_session, test_user):
        from chat_history import ChatHistory
        entry = ChatHistory(
            user_id=test_user.id,
            conversation_id="test-convo",
            coach_type="bodybuilding",
            question="What rep range is best?",
            answer="6-12 reps for hypertrophy.",
        )
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)
        return entry

    def test_submit_thumbs_up(self, client, db_session, test_user):
        message = self._create_chat_message(db_session, test_user)
        response = client.post("/feedback", json={
            "chat_history_id": message.id,
            "rating": "up",
        })
        assert response.status_code == 200
        assert response.json()["rating"] == "up"

    def test_submit_thumbs_down_with_reason(self, client, db_session, test_user):
        message = self._create_chat_message(db_session, test_user)
        response = client.post("/feedback", json={
            "chat_history_id": message.id,
            "rating": "down",
            "reason": "too_generic",
        })
        assert response.status_code == 200
        assert response.json()["reason"] == "too_generic"

    def test_resubmitting_feedback_updates_existing_rating(self, client, db_session, test_user):
        message = self._create_chat_message(db_session, test_user)
        client.post("/feedback", json={"chat_history_id": message.id, "rating": "up"})
        second_response = client.post("/feedback", json={"chat_history_id": message.id, "rating": "down"})

        summary = client.get("/feedback/summary").json()
        assert summary["bodybuilding"]["up"] == 0
        assert summary["bodybuilding"]["down"] == 1

    def test_feedback_summary_requires_admin(self, client, other_user, db_session, test_user):
        message = self._create_chat_message(db_session, test_user)
        client.post("/feedback", json={"chat_history_id": message.id, "rating": "up"})

        admin_response = client.get("/feedback/summary")
        assert admin_response.status_code == 200

        non_admin_response = client.get(
            "/feedback/summary", headers={"x-test-user": other_user.email}
        )
        assert non_admin_response.status_code == 403

    def test_downvoted_endpoint_requires_admin(self, client, other_user):
        response = client.get(
            "/feedback/downvoted", headers={"x-test-user": other_user.email}
        )
        assert response.status_code == 403

    def test_downvoted_endpoint_requires_admin(self, client, other_user):
        response = client.get(
            "/feedback/downvoted", headers={"x-test-user": other_user.email}
        )
        assert response.status_code == 403


class TestPlanEndpoints:
    @patch("workout_plan_routes.extract_plan_structure")
    def test_save_and_list_plan(self, mock_extract, client):
        mock_extract.return_value = {"days": [{"label": "Day 1", "items": ["Bench Press"]}]}

        save_response = client.post("/plans", json={
            "coach_type": "bodybuilding",
            "title": "Test Plan",
            "raw_text": "Day 1: Bench Press",
        })
        assert save_response.status_code == 200
        assert save_response.json()["plan_data"]["days"][0]["label"] == "Day 1"

        list_response = client.get("/plans")
        assert len(list_response.json()) == 1

    @patch("workout_plan_routes.extract_plan_structure")
    def test_delete_plan(self, mock_extract, client):
        mock_extract.return_value = None

        save_response = client.post("/plans", json={
            "coach_type": "bodybuilding",
            "title": "Test Plan",
            "raw_text": "some text",
        })
        plan_id = save_response.json()["id"]

        delete_response = client.delete(f"/plans/{plan_id}")
        assert delete_response.status_code == 200


