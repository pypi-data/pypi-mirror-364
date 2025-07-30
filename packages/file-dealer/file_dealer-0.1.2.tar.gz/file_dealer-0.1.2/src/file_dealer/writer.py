
def write_data():
    file_name = input("Enter file location: ").strip()
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            data = input("Enter the data you want to write: ")
            f.write(data)
            print("✅ File written successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None