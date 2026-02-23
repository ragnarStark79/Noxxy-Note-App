"""
API Test Examples
Run the application first: uv run python run.py
Then run these tests to verify all endpoints work correctly.
"""
import requests
import json

BASE_URL = "http://localhost:5001"


def print_response(response, description=""):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    if description:
        print(f"📝 {description}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print('='*60)


def test_api():
    """Test all API endpoints."""

    print("\n🚀 Starting API Tests...\n")

    # Test 1: Create a folder
    print("\n1️⃣ Creating a folder...")
    response = requests.post(f"{BASE_URL}/folders", json={
        "name": "Work"
    })
    print_response(response, "Create Folder")
    folder_id = response.json()['data']['id']

    # Test 2: List folders
    print("\n2️⃣ Listing folders...")
    response = requests.get(f"{BASE_URL}/folders")
    print_response(response, "List Folders")

    # Test 3: Create a note
    print("\n3️⃣ Creating a note...")
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "My First Note",
        "content": "This is the content of my first note.",
    })
    print_response(response, "Create Note")
    note1_id = response.json()['data']['id']

    # Test 4: Create another note with folder
    print("\n4️⃣ Creating a note in folder...")
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "Work Task",
        "content": "Important work task",
        "folder_id": folder_id
    })
    print_response(response, "Create Note in Folder")
    note2_id = response.json()['data']['id']

    # Test 5: List all notes
    print("\n5️⃣ Listing all notes...")
    response = requests.get(f"{BASE_URL}/notes")
    print_response(response, "List All Notes")

    # Test 6: Get a specific note
    print("\n6️⃣ Getting specific note...")
    response = requests.get(f"{BASE_URL}/notes/{note1_id}")
    print_response(response, "Get Note by ID")

    # Test 7: Update note
    print("\n7️⃣ Updating note...")
    response = requests.put(f"{BASE_URL}/notes/{note1_id}", json={
        "title": "My Updated Note",
        "content": "Updated content here"
    })
    print_response(response, "Update Note")

    # Test 8: Pin note
    print("\n8️⃣ Pinning note...")
    response = requests.patch(f"{BASE_URL}/notes/{note1_id}/pin")
    print_response(response, "Pin Note")

    # Test 9: List notes (pinned should be first)
    print("\n9️⃣ Listing notes (pinned first)...")
    response = requests.get(f"{BASE_URL}/notes")
    print_response(response, "List Notes with Pinned First")

    # Test 10: Add note to folder
    print("\n🔟 Adding note to folder...")
    response = requests.patch(f"{BASE_URL}/folders/{folder_id}/notes/{note1_id}")
    print_response(response, "Add Note to Folder")

    # Test 11: List notes in folder
    print("\n1️⃣1️⃣ Listing notes in folder...")
    response = requests.get(f"{BASE_URL}/notes?folder_id={folder_id}")
    print_response(response, "List Notes in Folder")

    # Test 12: Soft delete note
    print("\n1️⃣2️⃣ Soft deleting note...")
    response = requests.delete(f"{BASE_URL}/notes/{note2_id}")
    print_response(response, "Soft Delete Note")

    # Test 13: List deleted notes (bin)
    print("\n1️⃣3️⃣ Listing bin...")
    response = requests.get(f"{BASE_URL}/bin")
    print_response(response, "List Bin")

    # Test 14: Restore note from bin
    print("\n1️⃣4️⃣ Restoring note from bin...")
    response = requests.patch(f"{BASE_URL}/bin/{note2_id}/restore")
    print_response(response, "Restore Note")

    # Test 15: Soft delete again
    print("\n1️⃣5️⃣ Soft deleting note again...")
    response = requests.delete(f"{BASE_URL}/notes/{note2_id}")
    print_response(response, "Soft Delete Note Again")

    # Test 16: Permanently delete note
    print("\n1️⃣6️⃣ Permanently deleting note...")
    response = requests.delete(f"{BASE_URL}/bin/{note2_id}")
    print_response(response, "Permanently Delete Note")

    # Test 17: Verify note is gone
    print("\n1️⃣7️⃣ Verifying note is permanently deleted...")
    response = requests.get(f"{BASE_URL}/notes/{note2_id}")
    print_response(response, "Try to Get Deleted Note (Should fail)")

    # Test 18: Remove note from folder
    print("\n1️⃣8️⃣ Removing note from folder...")
    response = requests.delete(f"{BASE_URL}/folders/{folder_id}/notes/{note1_id}")
    print_response(response, "Remove Note from Folder")

    # Test 19: Unpin note
    print("\n1️⃣9️⃣ Unpinning note...")
    response = requests.patch(f"{BASE_URL}/notes/{note1_id}/pin")
    print_response(response, "Unpin Note")

    # Test 20: List folders with note count
    print("\n2️⃣0️⃣ Listing folders with note counts...")
    response = requests.get(f"{BASE_URL}/folders")
    print_response(response, "List Folders with Note Count")

    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    try:
        # Test root endpoint
        print("🏥 Checking API health...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            test_api()
        else:
            print("❌ API is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")

