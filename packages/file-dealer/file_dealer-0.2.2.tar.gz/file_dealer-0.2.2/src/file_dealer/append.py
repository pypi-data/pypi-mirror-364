
def append_data():
    file_name = input("Enter file location to append data: ").strip()
    try:
        with open(file_name, 'a', encoding='utf-8') as f:
            data = input(
                    "Enter the data you want to append (or type 'exit' to finish): ")
            f.write('\n' + data)
            while True:
                data = input()
                if data.lower() == 'exit':
                    break
                f.write('\n' + data)

            print("✅ Data appended successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None
