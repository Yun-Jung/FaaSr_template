import json

def generate_yaml_file(jobs):
    yaml_content = """
    name: FaaSr Workflow

    on: [workflow_dispatch]

    jobs:
    """
    for job_name, container in jobs.items():
        yaml_content += f"""
      {job_name}:
        runs-on: ubuntu-latest
        steps:
          - name: Checkout code
            uses: actions/checkout@v2
          - name: Login to Docker Hub
            uses: docker/login-action@v2
            with:
                username: ${{ secrets.DOCKERHUB_USERNAME }}
                password: ${{ secrets.DOCKERHUB_PASSWORD }}
          - name: Setup Rclone
            uses: AnimMouse/setup-rclone@v1
            with:
                rclone_config: |
                [s3flare]
                type = {job_details['DataStores']['S3_A']['Type']}
                provider = {job_details['DataStores']['S3_A']['Provider']}
                endpoint = {job_details['DataStores']['S3_A']['Endpoint']}
                access_key_id = ${{ secrets.S3_USERNAME }}
                secret_access_key = ${{ secrets.S3_PASSWORD }}
        disable_base64: true
          - name: Run Container
            run: |
              docker run -rm {container}
    """

    return yaml_content

try:
    # Read the JSON file
    with open('./sequence.json', 'r') as file:
        job_details = json.load(file)
except FileNotFoundError:
    print("File not found. Please provide a valid JSON file path.")
    exit(1)
except json.JSONDecodeError:
    print("Invalid JSON format. Please provide a valid JSON file.")
    exit(1)

# Merge the job details into the jobs dictionary
jobs = {}
for function in job_details['FunctionList']:
    job_name = function
    container = job_details['ActionContainers'][job_name]
    jobs[job_name] = container

# Generate the YAML file
yaml_content = generate_yaml_file(jobs)

print(yaml_content)

# Write the YAML content to a file
with open('.github/workflows/FaaSr_workflow.yml', 'w') as file:
    file.write(yaml_content)

print("GitHub Actions YAML file created successfully.")
