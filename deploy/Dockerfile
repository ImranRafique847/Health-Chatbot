FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install
COPY app/requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy application code
COPY app/main.py ${LAMBDA_TASK_ROOT}/

# Copy frontend files
COPY frontend/ /app/frontend/

# Set the handler
CMD ["main.handler"]
