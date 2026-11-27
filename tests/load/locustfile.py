
from locust import HttpUser, task, between, tag
import uuid


class GamingDigestUser(HttpUser):
    wait_time = between(1, 3)

    # Главная страница работает на том же хосте, что и Locust.
    @task(5)
    @tag("UC1")
    def open_homepage(self):
        self.client.get("/", name="UC1 - Homepage")

    # API работает на отдельном порту.
    @task(3)
    @tag("UC2")
    def health_check(self):
        self.client.get(
            "http://localhost:8000/api/health",
            name="UC2 - Health",
        )

    @task(1)
    @tag("UC3")
    def get_metrics(self):
        self.client.get(
            "http://localhost:8000/metrics",
            name="UC3 - Metrics",
        )

    @task(2)
    @tag("UC4")
    def generate_digest(self):
        user_id = f"load-test-{uuid.uuid4().hex[:12]}"

        with self.client.post(
            "http://localhost:8000/api/generate",
            json={"topic": "мобильный гейминг"},
            headers={"X-User-ID": user_id},
            name="UC4 - Generate digest",
            catch_response=True,
        ) as response:
            if response.status_code in (201, 429):
                response.success()
            else:
                response.failure(
                    f"Unexpected status: {response.status_code}"
                )
