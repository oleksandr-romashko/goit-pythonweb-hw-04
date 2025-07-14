# Use official base Python image (Alpine = small & fast)
FROM python:3.10-alpine

# Space optimization: Prevent Python from writing .pyc files to disk (Python recompiles on-the-fly anyway)
# Prevents .pyc & __pycache__ from being generated (saves space)
ENV PYTHONDONTWRITEBYTECODE=1
# Logs show optimization: Ensure stdout/stderr is unbuffered (e.g. logs show up immediately)
# Ensures logs show up in real-time (great for Docker logs)
ENV PYTHONUNBUFFERED=1

# Set working directory for the app
WORKDIR /app

# Copy dependency file into container and install project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project file into container
COPY ./src .

# Space optimization: Clean up __pycache__
# Cleans up any bytecode just in case something generates it during copy or install
# Why do this if PYTHONDONTWRITEBYTECODE=1 is set?
# Sometimes tools or scripts (e.g. local dev environments, tests) may have generated
# .pyc files before we copied them into the container. This command ensures that 
# no stale bytecode files remain in the final image — just in case.
RUN find . -type d -name '__pycache__' -exec rm -rf {} +

# Expose container port for our app
EXPOSE 8000

# Start application
ENTRYPOINT ["python", "main.py"]