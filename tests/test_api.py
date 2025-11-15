import requests
import allure
from helpers import generate_unique_email, delete_user, api_post, BASE_URL

class TestUserCreation:

    @allure.title("Создание уникального пользователя")
    def test_create_unique_user(self):
        email = generate_unique_email()
        password = "Pass1234"
        name = "Test User"

        response = api_post("/auth/register", {
            "email": email,
            "password": password,
            "name": name
        })

        assert response.status_code == 200
        resp_json = response.json()
        assert resp_json["success"] is True
        assert "accessToken" in resp_json

        delete_user(resp_json["accessToken"])

    @allure.title("Создание пользователя, который уже зарегистрирован")
    def test_create_duplicate_user(self):
        email = generate_unique_email()
        password = "Pass1234"
        name = "Test User"

        r1 = api_post("/auth/register", {"email": email, "password": password, "name": name})
        assert r1.status_code == 200
        token = r1.json()["accessToken"]

        r2 = api_post("/auth/register", {"email": email, "password": password, "name": name})
        assert r2.status_code == 403
        assert r2.json()["message"] == "User already exists"

        delete_user(token)

    @allure.title("Создание пользователя без обязательного поля (email)")
    def test_create_user_missing_email(self):
        response = api_post("/auth/register", {
            "password": "Pass1234",
            "name": "Test User"
        })
        assert response.status_code == 403
        assert response.json()["success"] is False


class TestLogin:

    @allure.title("Вход под существующим пользователем")
    def test_login_existing_user(self):
        email = generate_unique_email()
        password = "Pass1234"
        name = "Test User"

        api_post("/auth/register", {"email": email, "password": password, "name": name})
        response = api_post("/auth/login", {"email": email, "password": password})

        assert response.status_code == 200
        resp_json = response.json()
        assert resp_json["success"] is True
        assert "accessToken" in resp_json

        delete_user(resp_json["accessToken"])

    @allure.title("Вход с неверным логином и паролем")
    def test_login_invalid_credentials(self):
        response = api_post("/auth/login", {
            "email": "fake@example.com",
            "password": "wrong"
        })
        assert response.status_code == 401
        assert response.json()["message"] == "email or password are incorrect"


class TestOrderCreation:

    @allure.title("Создание заказа с авторизацией и ингредиентами")
    def test_create_order_authorized_with_ingredients(self):
        email = generate_unique_email()
        password = "Pass1234"
        api_post("/auth/register", {"email": email, "password": password, "name": "Test"})
        login_resp = api_post("/auth/login", {"email": email, "password": password})
        token = login_resp.json()["accessToken"]

        ing_resp = requests.get(f"{BASE_URL}/ingredients")
        assert ing_resp.status_code == 200
        ingredients = ing_resp.json()["data"]
        assert len(ingredients) >= 2
        ingredient_ids = [ingredients[0]["_id"], ingredients[1]["_id"]]

        order_resp = api_post("/orders", {"ingredients": ingredient_ids}, headers={"Authorization": token})
        assert order_resp.status_code == 200
        assert order_resp.json()["success"] is True
        assert "number" in order_resp.json()["order"]

        delete_user(token)

    @allure.title("Создание заказа без авторизации")
    def test_create_order_unauthorized(self):
        ing_resp = requests.get(f"{BASE_URL}/ingredients")
        ingredient_ids = [ing_resp.json()["data"][0]["_id"]]
        resp = api_post("/orders", {"ingredients": ingredient_ids})
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert "number" in resp.json()["order"]

    @allure.title("Создание заказа без ингредиентов")
    def test_create_order_without_ingredients(self):
        email = generate_unique_email()
        password = "Pass1234"
        api_post("/auth/register", {"email": email, "password": password, "name": "Test"})
        login_resp = api_post("/auth/login", {"email": email, "password": password})
        token = login_resp.json()["accessToken"]

        resp = api_post("/orders", {"ingredients": []}, headers={"Authorization": token})
        assert resp.status_code == 400
        assert resp.json()["message"] == "Ingredient ids must be provided"

        delete_user(token)

    @allure.title("Создание заказа с неверным хешем ингредиентов")
    def test_create_order_with_invalid_ingredient_ids(self):
        email = generate_unique_email()
        password = "Pass1234"
        api_post("/auth/register", {"email": email, "password": password, "name": "Test"})
        login_resp = api_post("/auth/login", {"email": email, "password": password})
        token = login_resp.json()["accessToken"]

        resp = api_post("/orders", {"ingredients": ["invalid123", "xyz456"]}, headers={"Authorization": token})
        assert resp.status_code == 500

        delete_user(token)