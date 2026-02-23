#!/bin/bash

# startup.sh - Script to initialize and start all MCP challenge servers

# Create necessary directories and files for challenges
echo "Setting up challenge environments..."

# Challenge 3 setup (file access)
mkdir -p /tmp/dvmcp_challenge3/public /tmp/dvmcp_challenge3/private
echo "Welcome to the public directory!" > /tmp/dvmcp_challenge3/public/welcome.txt
echo "This is a public file." > /tmp/dvmcp_challenge3/public/public_file.txt

cat > /tmp/dvmcp_challenge3/private/employee_salaries.txt << EOF
CONFIDENTIAL: Employee Salary Information
-----------------------------------------
CEO: $1,200,000/year
CTO: $950,000/year
CFO: $900,000/year
Senior Engineers: $180,000-$250,000/year
Mid-level Engineers: $120,000-$170,000/year
Junior Engineers: $80,000-$110,000/year
EOF

cat > /tmp/dvmcp_challenge3/private/acquisition_plans.txt << EOF
TOP SECRET: Upcoming Acquisition Plans
-------------------------------------
Target Company: InnoTech Solutions
Planned Offer: $500 million
Expected Closing: Q3 2025
Synergy Opportunities:
- Integrate their AI platform with our cloud services
- Consolidate sales and marketing teams (estimated 15% reduction)
- Migrate their customers to our infrastructure
EOF

cat > /tmp/dvmcp_challenge3/private/system_credentials.txt << EOF
SYSTEM CREDENTIALS - HIGHLY RESTRICTED
-------------------------------------
Production Database: 
  Host: db.acmecorp.internal
  Username: admin_prod
  Password: Pr0d-DB-S3cret!

Cloud Infrastructure:
  Account ID: ACME-CLOUD-92731
  API Key: ak_live_7y2JHGd8sKlM9nPzXqRt5vWx
  Secret: cs_live_bNp5T2vR8sKlM9nQzXwJhGf4
EOF

# Challenge 8 setup (code execution)
mkdir -p /tmp/dvmcp_challenge8/sensitive
cat > /tmp/dvmcp_challenge8/sensitive/credentials.txt << EOF
PRODUCTION CREDENTIALS
----------------------
Database:
  Host: db.acmecorp.internal
  Username: db_admin
  Password: Pr0d-DB-S3cur3!P@$$w0rd

AWS:
  Access Key ID: AKIAIOSFODNN7EXAMPLE
  Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  Region: us-west-2

API Gateway:
  Key: apg-prod-8a7b6c5d4e3f2g1h
  Secret: 9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g
EOF

# Challenge 10 setup (multi-vector attack)
mkdir -p /tmp/dvmcp_challenge10/config
cat > /tmp/dvmcp_challenge10/config/system.conf << EOF
SYSTEM CONFIGURATION
-------------------
Cloud Provider: AWS
Region: us-west-2
API Keys:
  - AWS_ACCESS_KEY_ID: AKIA5EXAMPLE12345678
  - AWS_SECRET_ACCESS_KEY: abcdef1234567890EXAMPLE/abcdefghijklmnopqrst
S3 Buckets:
  - customer-data-prod
  - financial-reports-2025
  - employee-records-confidential
EOF

cat > /tmp/dvmcp_challenge10/config/tokens.json << EOF
{
  "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBZG1pbiBVc2VyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNjUxODg0ODAwfQ.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",
  "service_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzZXJ2aWNlIiwibmFtZSI6IlNlcnZpY2UgQWNjb3VudCIsInJvbGUiOiJzZXJ2aWNlIiwiaWF0IjoxNjUxODg0ODAwfQ.7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f",
  "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwibmFtZSI6IlJlZ3VsYXIgVXNlciIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjUxODg0ODAwfQ.9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m"
}
EOF

# Challenge 6 setup (document processing)
mkdir -p /tmp/dvmcp_challenge6/user_uploads

# Challenge 4 setup (rug pull)
mkdir -p /tmp/dvmcp_challenge4/state
echo '{"weather_tool_calls": 0}' > /tmp/dvmcp_challenge4/state/state.json

echo "All challenge environments have been set up."
echo "Starting supervisord to launch all MCP challenge servers..."

# Start supervisord (this will be handled by the CMD in Dockerfile)
exec "$@"
