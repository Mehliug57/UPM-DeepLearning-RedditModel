# Step 1: Use a pre-built Python environment as the base image
FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy your project files into the container
COPY requirements.txt /app/requirements.txt
COPY main.py /app/main.py
COPY dataset.csv /app/dataset.csv

# Step 4: Install Python libraries listed in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Step 5: Define the default command to run the script
CMD ["python", "main.py", "train"]

