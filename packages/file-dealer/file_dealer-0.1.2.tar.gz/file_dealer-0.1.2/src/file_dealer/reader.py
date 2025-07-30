

def get_data():
    file_name = input("Enter file location: ").strip()
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            if not data:
                print("❌ The file is empty.")
                return None
            print("📝 Your data is:")
            print(data)
            print("✅ Data read successfully.")
            print("📌 Your data was saved in the variable 'data'.")
            return data
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None


def read_data():
    file_name = input("Enter file location: ").strip()
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            print("📝 Your data is:")
            print(data)
            print("✅ File read successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None


