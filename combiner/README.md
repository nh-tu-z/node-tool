## Combiner

### 1. Overview
As a developer, sometimes I want to avoid security problem regarding to publish or upload some files into outside environment. So I need a tool to combine the content of multi-files into a unique file, it has me to save the content of unique file at the clip board, and then paste to other outside file.

### 2. Rerequisite
- The tool is tested in python 3.10. And the tool should be used with python 3.10 or newer version.

### 3. Installation
T.B.D

### 4. Use cases
- Combine
    ```shell
    combiner combine -ed "Source Folder" -od "Destination folder"
    ```

- Spread
    ```shell
    combiner spread -ed "Source Folder" -od "Destination folder"
    ```

### 5 Test coverage
T.B.D

### 6. Dev
- Create a venv
   ```shell
    # Create a virtual environment
    py -m venv {env-name}
    ```
- Go to venv and find activate script and activate the venv
- Install all packages in requirements.txt
    ```shell
    cd combiner
    py -m pip install -r .\combiner\requirements.txt
    ```