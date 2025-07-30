
import os

def delete_data():
    file_name = input("Enter file location you want to delete: ").strip()
    try:
        os.remove(file_name)
        print("✅ Data was deleted successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None