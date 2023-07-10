import unittest
from unittest import TestCase
from infer import load_model, main

class TestInference(TestCase):
    def test_load_model(self):
        model = load_model()
        self.assertIsNotNone(model, "Model loading failed")
        print("Test 'test_load_model' passed")

    def test_main_valid_description(self):
        model = load_model()
        self.assertIsNotNone(model, "Model loading failed")

        description = "This is a movie description"
        genres = main(model, [f"--description={description}"])
        self.assertIsNotNone(genres, "Inference failed")
        self.assertIsInstance(genres, list, "Genres should be a list")
        self.assertTrue(all(isinstance(g, str) for g in genres), "Genres should be strings")
        print("Test 'test_main_valid_description' passed")

    def test_main_empty_description(self):
        model = load_model()
        self.assertIsNotNone(model, "Model loading failed")

        description = ""
        try:
            genres = main(model, [f"--description={description}"])
            self.fail("Expected ValueError to be raised")
        except ValueError as e:
            self.assertEqual(str(e), "Invalid description length. Description should be at least 10 characters.")
            print("Test 'test_main_empty_description' passed")

    def test_main_special_characters_description(self):
        model = load_model()
        self.assertIsNotNone(model, "Model loading failed")

        description = "This movie is awesome! 🎥🍿"
        try:
            genres = main(model, [f"--description={description}"])
            self.fail("Expected ValueError to be raised")
        except ValueError as e:
            self.assertEqual(str(e), "Invalid description. Special characters are not allowed.")
            print("Test 'test_main_special_characters_description' passed")

    def test_main_invalid_model(self):
        model = None
        description = "This is a movie description"
        try:
            genres = main(model, [f"--description={description}"])
            self.fail("Expected ValueError to be raised")
        except ValueError as e:
            self.assertEqual(str(e), "Invalid model. Model might not be loaded or is not provided")
            print("Test 'test_main_invalid_model' passed")
    
    def test_repeted_inference(self):
        model = load_model()
        self.assertIsNotNone(model, "Model loading failed")

        description = "This is a movie description"
        genres = main(model, [f"--description={description}"])
        self.assertIsNotNone(genres, "Inference failed")
        self.assertIsInstance(genres, list, "Genres should be a list")
        self.assertTrue(all(isinstance(g, str) for g in genres), "Genres should be strings")

        # Ensure that the inferred genres are consistent for the same input
        for _ in range(5):
            new_genres = main(model, [f"--description={description}"])
            self.assertEqual(genres, new_genres, "Inference results should be consistent for the same input")
            print("Test 'test_repeted_inference' passed")

    def test_main_valid_genres(self):
        model = load_model()
        self.assertIsNotNone(model, "Model loading failed")

        description = "This is a movie description about a comedy film"
        genres = main(model, [f"--description={description}"])
        self.assertIsNotNone(genres, "Inference failed")
        self.assertIsInstance(genres, list, "Genres should be a list")
        self.assertTrue(all(isinstance(g, str) for g in genres), "Genres should be strings")

        valid_genres = [
            "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy",
            "Foreign", "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "TV Movie",
            "Thriller", "War", "Western"
        ]

        for genre in genres:
            self.assertIn(genre, valid_genres, f"Invalid genre: {genre}")
        print("Test 'test_main_valid_genres' passed")


if __name__ == "__main__":
    unittest.main()
